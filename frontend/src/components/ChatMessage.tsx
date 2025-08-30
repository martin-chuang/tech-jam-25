import React from 'react'
import { ChatMessage as ChatMessageType } from '@/types/chat'
import { cn } from '@/utils/cn'

interface ChatMessageProps {
  message: ChatMessageType
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user'
  const isError = !!message.error

  if (isUser) {
    // User message - right aligned bubble
    return (
      <div className="flex justify-end mb-4 animate-fade-in pr-12">
        <div className="max-w-md lg:max-w-2xl">
          {message.files && message.files.length > 0 && (
            <div className="mb-2 space-y-1">
              {message.files.map((file) => (
                <div
                  key={file.id}
                  className="flex items-center gap-2 text-sm text-chat-text-secondary bg-gradient-to-r from-chat-accent/10 to-chat-pink/10 border border-chat-accent/20 rounded-full px-3 py-1 w-fit ml-auto"
                >
                  <span>📎</span>
                  <span className="truncate max-w-xs">{file.name}</span>
                </div>
              ))}
            </div>
          )}
          {message.content && (
            <div className="bg-gradient-to-br from-chat-accent to-chat-pink text-white p-3 rounded-2xl rounded-br-md shadow-md">
              <div className="text-sm whitespace-pre-wrap break-words">
                {message.content}
              </div>
            </div>
          )}
        </div>
      </div>
    )
  } else {
    // AI message - left aligned with cat avatar
    return (
      <div className="flex gap-3 mb-4 animate-fade-in pl-12 items-center">
        <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-chat-purple to-chat-pink flex items-center justify-center shadow-md mt-0">
          <span className="text-lg">🐱</span>
        </div>
        <div className="max-w-md lg:max-w-2xl">
          <div className={cn(
            'p-3 rounded-2xl rounded-bl-md shadow-md',
            isError ? 'bg-chat-error/10 border border-chat-error/20' : 'bg-chat-surface border border-chat-border'
          )}>
            <div className={cn(
              'text-sm whitespace-pre-wrap break-words',
              isError ? 'text-chat-error' : 'text-chat-text'
            )}>
              {isError ? message.error : message.content}
              {message.isStreaming && (
                <span className="inline-block w-2 h-4 bg-gradient-to-t from-chat-accent to-chat-pink ml-1 animate-typing rounded-full" />
              )}
            </div>
          </div>
        </div>
      </div>
    )
  }
}