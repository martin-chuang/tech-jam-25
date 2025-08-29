import React, { useRef } from 'react'
import { Upload, AlertCircle, Loader2 } from 'lucide-react'
import { UploadedFile } from '@/types/chat'
import { cn } from '@/utils/cn'

interface FileUploadProps {
  files: UploadedFile[]
  isUploading: boolean
  error: string | null
  onFilesAdd: (files: FileList) => void
  onFileRemove: (fileId: string) => void
  getFileInfo: (file: UploadedFile) => { icon: string; sizeText: string }
  className?: string
}

export const FileUpload: React.FC<FileUploadProps> = ({
  files,
  isUploading,
  error,
  onFilesAdd,
  onFileRemove,
  getFileInfo,
  className,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (e.dataTransfer.files.length > 0) {
      onFilesAdd(e.dataTransfer.files)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFilesAdd(e.target.files)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleUploadClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className={cn('space-y-3', className)}>
      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((file) => {
            const { sizeText } = getFileInfo(file)
            return (
              <div
                key={file.id}
                className="flex items-center justify-between p-3 bg-gradient-to-r from-chat-surface to-chat-accent/5 rounded-xl border-2 border-chat-accent/20 shadow-sm"
              >
                <div className="flex items-center justify-center flex-1 min-w-0">
                  <div className="text-center">
                    <p className="text-sm font-medium text-chat-text truncate">
                      {file.name}
                    </p>
                    <p className="text-xs text-chat-text-secondary">
                      {sizeText}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => onFileRemove(file.id)}
                  className="p-2 text-chat-text-secondary hover:text-chat-error transition-all rounded-full hover:bg-chat-error/10 hover:scale-110"
                  aria-label={`Remove ${file.name}`}
                >
                  <span className="text-lg">🗑️</span>
                </button>
              </div>
            )
          })}
        </div>
      )}

      {error && (
        <div className="flex items-center space-x-2 p-3 bg-gradient-to-r from-chat-error/10 to-rose-100 border-2 border-chat-error/30 rounded-xl shadow-sm">
          <AlertCircle size={20} className="text-chat-error flex-shrink-0" />
          <span className="text-sm text-chat-error font-medium">{error}</span>
        </div>
      )}

      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={handleUploadClick}
        className={cn(
          'border-3 border-dashed border-chat-accent/40 rounded-xl p-8 text-center cursor-pointer transition-all shadow-sm',
          'hover:border-chat-accent hover:bg-gradient-to-br hover:from-chat-accent/10 hover:to-chat-pink/10 hover:shadow-md',
          isUploading && 'pointer-events-none opacity-50'
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
        
        <div className="flex flex-col items-center space-y-3">
          {isUploading ? (
            <Loader2 size={32} className="text-chat-accent animate-spin" />
          ) : (
            <Upload size={32} className="text-chat-text-secondary" />
          )}
          <div className="text-sm">
            <p className="text-chat-text font-medium">
              {isUploading ? 'Uploading your files...' : 'Drop files here or click to browse'}
            </p>
            <p className="text-chat-text-secondary mt-2">
              Supports text, images, PDFs, and documents (max 10MB)
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}