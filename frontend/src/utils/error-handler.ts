// import { ApiError } from '@/types/api'

export class ChatError extends Error {
  public code?: string;
  public details?: unknown;

  constructor(message: string, code?: string, details?: unknown) {
    super(message);
    this.name = 'ChatError';
    this.code = code;
    this.details = details;
  }
}

export const handleApiError = (error: unknown): ChatError => {
  if (error instanceof ChatError) {
    return error;
  }

  if (error instanceof Error) {
    // Handle fetch errors
    if (error.name === 'AbortError') {
      return new ChatError('Request was cancelled', 'ABORTED');
    }

    if (error.message.includes('Failed to fetch')) {
      return new ChatError(
        'Unable to connect to the server. Please check your internet connection.',
        'NETWORK_ERROR',
      );
    }

    if (error.message.includes('HTTP error')) {
      const statusMatch = error.message.match(/status: (\d+)/);
      if (statusMatch) {
        const status = parseInt(statusMatch[1]);
        switch (status) {
          case 400:
            return new ChatError(
              'Invalid request. Please check your input.',
              'BAD_REQUEST',
            );
          case 401:
            return new ChatError(
              'Authentication required. Please log in.',
              'UNAUTHORIZED',
            );
          case 403:
            return new ChatError('Access denied.', 'FORBIDDEN');
          case 404:
            return new ChatError('Service not found.', 'NOT_FOUND');
          case 429:
            return new ChatError(
              'Too many requests. Please try again later.',
              'RATE_LIMITED',
            );
          case 500:
            return new ChatError(
              'Server error. Please try again later.',
              'SERVER_ERROR',
            );
          default:
            return new ChatError(
              `Server error (${status}). Please try again.`,
              'HTTP_ERROR',
            );
        }
      }
    }

    return new ChatError(error.message, 'UNKNOWN_ERROR');
  }

  return new ChatError('An unexpected error occurred', 'UNKNOWN_ERROR', error);
};

export const isNetworkError = (error: ChatError): boolean => {
  return error.code === 'NETWORK_ERROR' || error.message.includes('fetch');
};

export const isRetryableError = (error: ChatError): boolean => {
  return ['NETWORK_ERROR', 'SERVER_ERROR', 'RATE_LIMITED'].includes(
    error.code || '',
  );
};

export const getErrorMessage = (error: unknown): string => {
  const chatError = handleApiError(error);
  return chatError.message;
};

export const logError = (error: unknown, context?: string) => {
  const chatError = handleApiError(error);
  console.error(`[${context || 'Error'}]`, {
    message: chatError.message,
    code: chatError.code,
    details: chatError.details,
    stack: chatError.stack,
  });
};
