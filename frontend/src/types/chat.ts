export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  files?: UploadedFile[]
  isStreaming?: boolean
  error?: string
}

export interface UploadedFile {
  id: string
  name: string
  size: number
  type: string
  data: string | ArrayBuffer
  url?: string
}

export interface ChatSession {
  id: string
  title: string
  messages: ChatMessage[]
  createdAt: Date
  updatedAt: Date
}

export interface ChatState {
  sessions: ChatSession[]
  activeSessionId: string | null
  isLoading: boolean
  error: string | null
}

export interface FileValidationResult {
  isValid: boolean
  error?: string
}

export interface StreamResponse {
  content: string
  done: boolean
  error?: string
}