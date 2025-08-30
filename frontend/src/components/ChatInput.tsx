import { useRef, useState } from '@lynx-js/react';
import { Paperclip } from 'lucide-react';
import type { UploadedFile } from '@/types/chat';
import { cn } from '@/utils/cn';
import { FileUpload } from './FileUpload';

interface ChatInputProps {
  onSendMessage: (
    message: string,
    context: string,
    files: UploadedFile[],
  ) => void;
  isLoading: boolean;
  files: UploadedFile[];
  isUploading: boolean;
  uploadError: string | null;
  onFilesAdd: (files: FileList) => void;
  onFileRemove: (fileId: string) => void;
  getFileInfo: (file: UploadedFile) => { icon: string; sizeText: string };
}

export const ChatInput = ({
  onSendMessage,
  isLoading,
  files,
  isUploading,
  uploadError,
  onFilesAdd,
  onFileRemove,
  getFileInfo,
}: ChatInputProps) => {
  const [message, setMessage] = useState('');
  const [context, setContext] = useState('');
  const [showFileUpload, setShowFileUpload] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e?: React.FormEvent<HTMLFormElement>) => {
    e?.preventDefault();

    const trimmedMessage = message.trim();
    const trimmedContext = context.trim();
    if (!trimmedMessage && !trimmedContext && files.length === 0) return;
    if (isLoading || isUploading) return;

    onSendMessage(trimmedMessage, trimmedContext, files);
    setMessage('');
    setContext('');
    setShowFileUpload(false);

    if (textareaRef.current) {
      textareaRef.current.style = {
        ...textareaRef.current.style,
        height: 'auto',
      };
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleTextareaChange = (e: React.FormEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);

    // Auto-resize textarea
    const textarea = e.target;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight || 48, 200)}px`;
    }
  };

  const handleContextChange = (e: React.FormEvent<HTMLTextAreaElement>) => {
    setContext(e.target.value);
  };

  const toggleFileUpload = () => {
    setShowFileUpload(!showFileUpload);
  };

  const canSend =
    (message.trim() || context.trim() || files.length > 0) &&
    !isLoading &&
    !isUploading;

  return (
    <view className="bg-chat-bg p-4">
      {showFileUpload && (
        <view className="mb-4">
          <FileUpload
            files={files}
            isUploading={isUploading}
            error={uploadError}
            onFilesAdd={onFilesAdd}
            onFileRemove={onFileRemove}
            getFileInfo={getFileInfo}
          />
        </view>
      )}

      <form onSubmit={handleSubmit} className="flex items-stretch gap-2">
        <view
          role="button"
          bindtap={toggleFileUpload}
          className={cn(
            'p-3 rounded-xl transition-all flex-shrink-0 shadow-sm self-end',
            showFileUpload
              ? 'bg-gradient-to-br from-chat-accent to-chat-pink text-white shadow-md'
              : 'bg-chat-surface text-chat-text-secondary hover:bg-gradient-to-br hover:from-chat-accent hover:to-chat-pink hover:text-white hover:shadow-md',
          )}
          aria-label="Attach files"
        >
          <Paperclip size={24} />
        </view>

        <view className="flex-1 relative flex items-center">
          <textarea
            value={context}
            onInput={handleContextChange}
            onKeyDown={handleKeyDown}
            placeholder="Enter context here..."
            className={cn(
              'w-full px-4 py-3 pr-12 rounded-xl resize-none shadow-sm',
              'bg-chat-surface border-2 border-chat-border text-chat-text',
              'placeholder-chat-text-secondary',
              'focus:outline-none focus:ring-2 focus:ring-chat-accent focus:border-chat-accent transition-all',
              'disabled:opacity-50 disabled:cursor-not-allowed',
            )}
            disabled={isLoading}
            rows={1}
            style={{ minHeight: '48px' }}
          />
          <textarea
            ref={textareaRef}
            value={message}
            onInput={handleTextareaChange}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            className={cn(
              'w-full px-4 py-3 pr-12 rounded-xl resize-none shadow-sm',
              'bg-chat-surface border-2 border-chat-border text-chat-text',
              'placeholder-chat-text-secondary',
              'focus:outline-none focus:ring-2 focus:ring-chat-accent focus:border-chat-accent transition-all',
              'disabled:opacity-50 disabled:cursor-not-allowed',
            )}
            disabled={isLoading}
            rows={1}
            style={{ minHeight: '48px' }}
          />
        </view>

        <view
          role="button"
          bindtap={canSend ? handleSubmit : undefined}
          className={cn(
            'p-3 rounded-xl transition-all flex-shrink-0 shadow-sm self-end',
            canSend
              ? 'bg-gradient-to-br from-chat-accent to-chat-pink text-white shadow-md hover:shadow-lg hover:from-chat-accent-hover hover:to-rose-500 transform hover:scale-105'
              : 'bg-chat-surface text-chat-text-secondary cursor-not-allowed',
          )}
          aria-label="Send message"
        >
          <text>Send</text>
        </view>
      </form>
    </view>
  );
};
