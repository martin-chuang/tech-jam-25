import React, { Component, ReactNode } from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="flex items-center justify-center h-screen bg-chat-bg">
          <div className="max-w-md mx-auto p-8 text-center">
            <div className="w-16 h-16 mx-auto mb-4 bg-chat-error/10 rounded-full flex items-center justify-center">
              <AlertTriangle className="w-8 h-8 text-chat-error" />
            </div>
            
            <h1 className="text-xl font-semibold text-chat-text mb-2">
              Something went wrong
            </h1>
            
            <p className="text-chat-text-secondary mb-6">
              {this.state.error?.message || 'An unexpected error occurred. Please try refreshing the page.'}
            </p>
            
            <button
              onClick={this.handleReset}
              className="inline-flex items-center gap-2 px-4 py-2 bg-chat-accent text-white rounded-lg hover:bg-chat-accent/90 transition-colors"
            >
              <RefreshCw size={16} />
              Try Again
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}