import { FileValidationResult } from '@/types/chat'

export const FILE_SIZE_LIMIT = 10 * 1024 * 1024 // 10MB
export const ALLOWED_FILE_TYPES = [
  'text/plain',
  'text/markdown',
  'text/csv',
  'application/json',
  'application/pdf',
  'image/jpeg',
  'image/png',
  'image/gif',
  'image/webp',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
] as const

export const validateFile = (file: File): FileValidationResult => {
  if (file.size > FILE_SIZE_LIMIT) {
    return {
      isValid: false,
      error: `File size exceeds ${FILE_SIZE_LIMIT / 1024 / 1024}MB limit`
    }
  }

  if (!ALLOWED_FILE_TYPES.includes(file.type as any)) {
    return {
      isValid: false,
      error: 'File type not supported. Please upload text, image, PDF, or document files.'
    }
  }

  return { isValid: true }
}

export const validateTotalFileSize = (files: File[]): FileValidationResult => {
  const totalSize = files.reduce((sum, file) => sum + file.size, 0)
  
  if (totalSize > FILE_SIZE_LIMIT) {
    return {
      isValid: false,
      error: `Total file size exceeds ${FILE_SIZE_LIMIT / 1024 / 1024}MB limit`
    }
  }

  return { isValid: true }
}

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
}

export const getFileIcon = (mimeType: string): string => {
  if (mimeType.startsWith('image/')) return '🖼️'
  if (mimeType === 'application/pdf') return '📄'
  if (mimeType.includes('word')) return '📝'
  if (mimeType === 'text/csv') return '📊'
  if (mimeType === 'application/json') return '🔧'
  return '📎'
}