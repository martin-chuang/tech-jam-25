import { useState, useCallback, useRef } from 'react'
import { ChatMessage, UploadedFile, ChatSession } from '@/types/chat'

// const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001'

export const useChat = () => {
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  const activeSession = sessions.find(s => s.id === activeSessionId)

  const createNewSession = useCallback(() => {
    const newSession: ChatSession = {
      id: `session-${Date.now()}`,
      title: 'New Chat',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    setSessions(prev => [newSession, ...prev])
    setActiveSessionId(newSession.id)
    return newSession
  }, [])

  const updateSessionTitle = useCallback((sessionId: string, message: string) => {
    const title = message.length > 50 
      ? message.substring(0, 50) + '...' 
      : message
    
    setSessions(prev => prev.map(session => 
      session.id === sessionId 
        ? { ...session, title, updatedAt: new Date() }
        : session
    ))
  }, [])

  const addMessage = useCallback((sessionId: string, message: ChatMessage) => {
    setSessions(prev => prev.map(session => 
      session.id === sessionId 
        ? { 
            ...session, 
            messages: [...session.messages, message],
            updatedAt: new Date()
          }
        : session
    ))
  }, [])

  const updateMessage = useCallback((sessionId: string, messageId: string, updates: Partial<ChatMessage>) => {
    setSessions(prev => prev.map(session => 
      session.id === sessionId 
        ? {
            ...session,
            messages: session.messages.map(msg => 
              msg.id === messageId ? { ...msg, ...updates } : msg
            ),
            updatedAt: new Date()
          }
        : session
    ))
  }, [])

  const sendMessage = useCallback(async (content: string, files: UploadedFile[]) => {
    if (!content.trim() && files.length === 0) return
    
    setError(null)
    setIsLoading(true)

    // Cancel any existing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    abortControllerRef.current = new AbortController()

    let currentSession = activeSession
    if (!currentSession) {
      currentSession = createNewSession()
    }

    // Add user message
    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
      files: files.length > 0 ? files : undefined,
    }

    addMessage(currentSession.id, userMessage)

    // Update session title if it's the first message
    if (currentSession.messages.length === 0 && content.trim()) {
      updateSessionTitle(currentSession.id, content)
    }

    // Add assistant message placeholder
    const assistantMessageId = `msg-${Date.now() + 1}`
    const assistantMessage: ChatMessage = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true,
    }

    addMessage(currentSession.id, assistantMessage)

    try {
      // Create FormData for the request
      const formData = new FormData()
      formData.append('message', content)
      formData.append('sessionId', currentSession.id)
      
      files.forEach((file, index) => {
        if (file.data instanceof File) {
          formData.append(`file-${index}`, file.data)
        }
      })

      const response = await fetch(`/api/chat`, {
        method: 'POST',
        body: formData,
        signal: abortControllerRef.current.signal,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      if (!response.body) {
        throw new Error('ReadableStream not supported')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let accumulatedContent = ''

      while (true) {
        const { done, value } = await reader.read()
        
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n').filter(line => line.trim())
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            
            if (data === '[DONE]') {
              updateMessage(currentSession.id, assistantMessageId, {
                isStreaming: false,
              })
              return
            }

            try {
              const parsed = JSON.parse(data)
              
              if (parsed.error) {
                throw new Error(parsed.error)
              }
              
              if (parsed.content) {
                accumulatedContent += parsed.content
                updateMessage(currentSession.id, assistantMessageId, {
                  content: accumulatedContent,
                })
              }
            } catch (parseError) {
              console.warn('Failed to parse SSE data:', data)
            }
          }
        }
      }
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        return
      }

      const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred'
      setError(errorMessage)
      
      updateMessage(currentSession.id, assistantMessageId, {
        content: '',
        error: errorMessage,
        isStreaming: false,
      })
    } finally {
      setIsLoading(false)
      abortControllerRef.current = null
    }
  }, [activeSession, createNewSession, addMessage, updateMessage, updateSessionTitle])

  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    setIsLoading(false)
  }, [])

  const deleteSession = useCallback((sessionId: string) => {
    setSessions(prev => prev.filter(s => s.id !== sessionId))
    if (activeSessionId === sessionId) {
      setActiveSessionId(null)
    }
  }, [activeSessionId])

  const selectSession = useCallback((sessionId: string) => {
    setActiveSessionId(sessionId)
    setError(null)
  }, [])

  // Don't auto-create sessions - let user create them when needed

  return {
    sessions,
    activeSession,
    isLoading,
    error,
    sendMessage,
    stopGeneration,
    createNewSession,
    deleteSession,
    selectSession,
  }
}