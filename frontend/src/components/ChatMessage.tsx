import type { ChatMessage as ChatMessageType } from '@/types/chat';
import { cn } from '@/utils/cn';

interface ChatMessageProps {
  message: ChatMessageType;
}

export const ChatMessage = ({ message }: ChatMessageProps) => {
  const isUser = message.role === 'user';
  const isError = !!message.error;

  if (isUser) {
    // User message - right aligned bubble
    return (
      <view className="flex justify-end mb-4 animate-fade-in pr-12">
        <view className="max-w-md lg:max-w-2xl">
          {message.files && message.files.length > 0 && (
            <view className="mb-2 space-y-1">
              {message.files.map((file) => (
                <view
                  key={file.id}
                  className="flex items-center gap-2 text-sm text-chat-text-secondary bg-gradient-to-r from-chat-accent/10 to-chat-pink/10 border border-chat-accent/20 rounded-full px-3 py-1 w-fit ml-auto"
                >
                  <text>📎</text>
                  <text className="truncate max-w-xs">{file.name}</text>
                </view>
              ))}
            </view>
          )}
          {message.content && (
            <view className="bg-gradient-to-br from-chat-accent to-chat-pink text-white p-3 rounded-2xl rounded-br-md shadow-md">
              <text className="text-sm whitespace-pre-wrap break-words">
                {message.content}
              </text>
            </view>
          )}
        </view>
      </view>
    );
  } else {
    // AI message - left aligned with cat avatar
    return (
      <view className="flex gap-3 mb-4 animate-fade-in pl-12 items-start">
        <view className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-chat-purple to-chat-pink flex items-center justify-center shadow-md mt-0">
          <text className="text-lg">🐱</text>
        </view>
        <view className="max-w-md lg:max-w-2xl w-full">
          {message.thoughts && message.thoughts.length > 0 && (
            <view className="mb-2 space-y-2">
              {message.thoughts.map((thought, index) => (
                <view
                  key={index}
                  className="flex items-center gap-2 text-sm text-chat-text-secondary animate-fade-in"
                >
                  <text className="text-lg">🤔</text>
                  <text className="p-2 bg-chat-surface border border-chat-border rounded-lg w-full">
                    {thought}
                  </text>
                </view>
              ))}
            </view>
          )}
          {(message.content || (isError && message.error)) && (
            <view
              className={cn(
                'p-3 rounded-2xl rounded-bl-md shadow-md',
                isError
                  ? 'bg-chat-error/10 border border-chat-error/20'
                  : 'bg-chat-surface border border-chat-border',
              )}
            >
              <text
                className={cn(
                  'text-sm whitespace-pre-wrap break-words',
                  isError ? 'text-chat-error' : 'text-chat-text',
                )}
              >
                {isError ? message.error : message.content}
                {message.isStreaming && (
                  <text className="inline-block w-2 h-4 bg-gradient-to-t from-chat-accent to-chat-pink ml-1 animate-typing rounded-full" />
                )}
              </text>
            </view>
          )}
          {message.isStreaming &&
            !message.content &&
            (!message.thoughts || message.thoughts.length === 0) && (
              <view className="p-3 bg-chat-surface border border-chat-border rounded-2xl rounded-bl-md shadow-md">
                <text className="text-sm text-chat-text-secondary animate-pulse">
                  Thinking...
                </text>
              </view>
            )}
        </view>
      </view>
    );
  }
};
