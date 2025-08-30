export interface ApiError {
  message: string;
  code?: string;
  details?: unknown;
}

export interface ChatRequest {
  message: string;
  files?: File[];
  sessionId?: string;
}

export interface ChatResponse {
  sessionId: string;
  messageId: string;
}

export interface FileUploadResponse {
  id: string;
  url: string;
  name: string;
  size: number;
  type: string;
}
