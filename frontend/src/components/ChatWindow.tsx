import React, { useEffect, useRef } from 'react'
import { ChatMessage } from './ChatMessage'
import { ChatInput } from './ChatInput'
import { ChatMessage as ChatMessageType, UploadedFile } from '@/types/chat'
import { useFileUpload } from '@/hooks/useFileUpload'
import { cn } from '@/utils/cn'

interface ChatWindowProps {
  messages: ChatMessageType[]
  isLoading: boolean
  onSendMessage: (message: string, files: UploadedFile[]) => void
  onStopGeneration: () => void
  className?: string
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  isLoading,
  onSendMessage,
  onStopGeneration,
  className,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileUpload = useFileUpload()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = (message: string, files: UploadedFile[]) => {
    onSendMessage(message, files)
    fileUpload.clearFiles()
  }

  return (
    <div className={cn('flex flex-col h-full', className)}>
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-center px-6">
            <div className="max-w-xl space-y-8">
              <div className="space-y-6">
                <div className="space-y-4">
                  <h1 className="text-3xl font-bold text-chat-text">
                    Welcome to <span className="bg-gradient-to-r from-chat-accent to-chat-pink bg-clip-text text-transparent">JellyCat AI!</span>
                  </h1>
                  <p className="text-lg text-chat-text-secondary font-medium">
                    Send a message or upload files to start a conversation
                  </p>
                </div>
                <div className="bg-chat-surface/50 border border-chat-border rounded-lg p-3">
                  <p className="text-xs font-medium text-chat-accent mb-1">🔒 Privacy First</p>
                  <p className="text-xs text-chat-text-secondary">
                    Your privacy matters to us. Personal information is automatically masked before being sent to our servers, ensuring your sensitive data stays protected.
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Stop generation button */}
      {isLoading && (
        <div className="px-4 pb-2">
          <button
            onClick={onStopGeneration}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-chat-error/10 to-rose-100 text-chat-error border-2 border-chat-error/30 rounded-full hover:bg-chat-error/20 transition-all mx-auto shadow-sm hover:shadow-md"
          >
            <span className="text-lg">⏹️</span>
            Stop JellyCat
          </button>
        </div>
      )}

      {/* Input area */}
      <ChatInput
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        files={fileUpload.files}
        isUploading={fileUpload.isUploading}
        uploadError={fileUpload.error}
        onFilesAdd={fileUpload.addFiles}
        onFileRemove={fileUpload.removeFile}
        getFileInfo={fileUpload.getFileInfo}
      />
    </div>
  )
}