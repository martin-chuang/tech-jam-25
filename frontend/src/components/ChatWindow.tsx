import { useEffect, useRef } from '@lynx-js/react';
import { useFileUpload } from '@/hooks/useFileUpload';
import type {
  ChatMessage as ChatMessageType,
  UploadedFile,
} from '@/types/chat';
import { cn } from '@/utils/cn';
import { ChatInput } from './ChatInput';
import { ChatMessage } from './ChatMessage';

interface ChatWindowProps {
  messages: ChatMessageType[];
  isLoading: boolean;
  onSendMessage: (
    message: string,
    context: string,
    files: UploadedFile[],
  ) => void;
  onStopGeneration: () => void;
  className?: string;
}

export const ChatWindow = ({
  messages,
  isLoading,
  onSendMessage,
  onStopGeneration,
  className,
}: ChatWindowProps) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileUpload = useFileUpload();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView?.({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = (
    message: string,
    context: string,
    files: UploadedFile[],
  ) => {
    onSendMessage(message, context, files);
    fileUpload.clearFiles();
  };

  return (
    <view className={cn('flex flex-col h-full', className)}>
      {/* Messages area */}
      <scrollview className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <view className="flex items-center justify-center h-full text-center px-6">
            <view className="max-w-xl space-y-8">
              <view className="space-y-6">
                <view className="space-y-4">
                  <text className="text-3xl font-bold text-chat-text">
                    Welcome to{' '}
                    <text className="bg-gradient-to-r from-chat-accent to-chat-pink bg-clip-text text-transparent">
                      JellyCat AI!
                    </text>
                  </text>
                  <text className="text-lg text-chat-text-secondary font-medium">
                    Send a message or upload files to start a conversation
                  </text>
                </view>
                <view className="bg-chat-surface/50 border border-chat-border rounded-lg p-3">
                  <text className="text-xs font-medium text-chat-accent mb-1">
                    🔒 Privacy First
                  </text>
                  <text className="text-xs text-chat-text-secondary">
                    Your privacy matters to us. Personal information is
                    automatically masked before being sent to our servers,
                    ensuring your sensitive data stays protected.
                  </text>
                </view>
              </view>
            </view>
          </view>
        ) : (
          messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))
        )}
        <view ref={messagesEndRef} />
      </scrollview>

      {/* Stop generation button */}
      {isLoading && (
        <view className="px-4 pb-2">
          <view
            role="button"
            bindtap={onStopGeneration}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-chat-error/10 to-rose-100 text-chat-error border-2 border-chat-error/30 rounded-full hover:bg-chat-error/20 transition-all mx-auto shadow-sm hover:shadow-md"
          >
            <text className="text-lg">⏹️</text>
            <text>Stop JellyCat</text>
          </view>
        </view>
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
    </view>
  );
};
