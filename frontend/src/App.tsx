import { useState } from 'react'
import { Sidebar } from '@/components/Sidebar'
import { ChatWindow } from '@/components/ChatWindow'
import { useChat } from '@/hooks/useChat'

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const {
    sessions,
    activeSession,
    isLoading,
    sendMessage,
    stopGeneration,
    createNewSession,
    deleteSession,
    selectSession,
  } = useChat()

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen)
  }

  const handleNewChat = () => {
    createNewSession()
    setSidebarOpen(false) // Close sidebar on mobile after creating new chat
  }

  const handleSelectSession = (sessionId: string) => {
    selectSession(sessionId)
    setSidebarOpen(false) // Close sidebar on mobile after selecting session
  }

  return (
    <div className="flex h-screen bg-chat-bg text-chat-text">
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSession?.id || null}
        onNewChat={handleNewChat}
        onSelectSession={handleSelectSession}
        onDeleteSession={deleteSession}
        isOpen={sidebarOpen}
        onToggle={toggleSidebar}
      />
      
      <main className="flex-1 flex flex-col lg:ml-0">
        <ChatWindow
          messages={activeSession?.messages || []}
          isLoading={isLoading}
          onSendMessage={(message, context, files) => sendMessage(message, context, files)}
          onStopGeneration={stopGeneration}
          className="lg:pl-0 pl-0"
        />
      </main>
    </div>
  )
}