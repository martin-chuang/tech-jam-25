import { useEffect, useState } from '@lynx-js/react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export const ErrorBoundary = ({ children, fallback }: ErrorBoundaryProps) => {
  const [hasError, setHasError] = useState(false);
  const [error, setError] = useState<Error | undefined>(undefined);

  // Note: LynxJS doesn't have the same error boundary lifecycle methods
  // This is a simplified version that handles basic error cases
  useEffect(() => {
    const handleError = (event: ErrorEvent) => {
      console.error('ErrorBoundary caught an error:', event.error);
      setHasError(true);
      setError(event.error);
    };

    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, []);

  const handleReset = () => {
    setHasError(false);
    setError(undefined);
  };

  if (hasError) {
    if (fallback) {
      return fallback;
    }

    return (
      <view className="flex items-center justify-center h-screen bg-chat-bg">
        <view className="max-w-md mx-auto p-8 text-center">
          <view className="w-16 h-16 mx-auto mb-4 bg-chat-error/10 rounded-full flex items-center justify-center">
            <AlertTriangle className="w-8 h-8 text-chat-error" />
          </view>

          <text className="text-xl font-semibold text-chat-text mb-2">
            Something went wrong
          </text>

          <text className="text-chat-text-secondary mb-6">
            {error?.message ||
              'An unexpected error occurred. Please try refreshing the page.'}
          </text>

          <view
            role="button"
            bindtap={handleReset}
            className="inline-flex items-center gap-2 px-4 py-2 bg-chat-accent text-white rounded-lg hover:bg-chat-accent/90 transition-colors"
          >
            <RefreshCw size={16} />
            <text>Try Again</text>
          </view>
        </view>
      </view>
    );
  }

  return children;
};
