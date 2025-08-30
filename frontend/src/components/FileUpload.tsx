import { useRef } from '@lynx-js/react';
import { AlertCircle, Loader2, Upload } from 'lucide-react';
import type { UploadedFile } from '@/types/chat';
import { cn } from '@/utils/cn';

interface FileUploadProps {
  files: UploadedFile[];
  isUploading: boolean;
  error: string | null;
  onFilesAdd: (files: FileList) => void;
  onFileRemove: (fileId: string) => void;
  getFileInfo: (file: UploadedFile) => { icon: string; sizeText: string };
  className?: string;
}

export const FileUpload = ({
  files,
  isUploading,
  error,
  onFilesAdd,
  onFileRemove,
  getFileInfo,
  className,
}: FileUploadProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();

    if (e.dataTransfer?.files?.length > 0) {
      onFilesAdd(e.dataTransfer.files);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target?.files?.length > 0) {
      onFilesAdd(e.target.files);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <view className={cn('space-y-3', className)}>
      {files.length > 0 && (
        <view className="space-y-2">
          {files.map((file) => {
            const { sizeText } = getFileInfo(file);
            return (
              <view
                key={file.id}
                className="flex items-center justify-between p-3 bg-gradient-to-r from-chat-surface to-chat-accent/5 rounded-xl border-2 border-chat-accent/20 shadow-sm"
              >
                <view className="flex items-center justify-center flex-1 min-w-0">
                  <view className="text-center">
                    <text className="text-sm font-medium text-chat-text truncate">
                      {file.name}
                    </text>
                    <text className="text-xs text-chat-text-secondary">
                      {sizeText}
                    </text>
                  </view>
                </view>
                <view
                  role="button"
                  bindtap={() => onFileRemove(file.id)}
                  className="p-2 text-chat-text-secondary hover:text-chat-error transition-all rounded-full hover:bg-chat-error/10 hover:scale-110"
                  aria-label={`Remove ${file.name}`}
                >
                  <text className="text-lg">🗑️</text>
                </view>
              </view>
            );
          })}
        </view>
      )}

      {error && (
        <view className="flex items-center space-x-2 p-3 bg-gradient-to-r from-chat-error/10 to-rose-100 border-2 border-chat-error/30 rounded-xl shadow-sm">
          <AlertCircle size={20} className="text-chat-error flex-shrink-0" />
          <text className="text-sm text-chat-error font-medium">{error}</text>
        </view>
      )}

      <view
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        bindtap={handleUploadClick}
        className={cn(
          'border-3 border-dashed border-chat-accent/40 rounded-xl p-8 text-center cursor-pointer transition-all shadow-sm',
          'hover:border-chat-accent hover:bg-gradient-to-br hover:from-chat-accent/10 hover:to-chat-pink/10 hover:shadow-md',
          isUploading && 'pointer-events-none opacity-50',
        )}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={handleFileSelect}
          className="hidden"
          accept=".txt,.md,.csv,.json,.pdf,.jpg,.jpeg,.png,.gif,.webp,.doc,.docx"
        />

        <view className="flex flex-col items-center space-y-3">
          {isUploading ? (
            <Loader2 size={32} className="text-chat-accent animate-spin" />
          ) : (
            <Upload size={32} className="text-chat-text-secondary" />
          )}
          <view className="text-sm">
            <text className="text-chat-text font-medium">
              {isUploading
                ? 'Uploading your files...'
                : 'Drop files here or click to browse'}
            </text>
            <text className="text-chat-text-secondary mt-2">
              Supports text, images, PDFs, and documents (max 10MB)
            </text>
          </view>
        </view>
      </view>
    </view>
  );
};
