import { Menu, MessageSquare, Plus, Trash2, X } from 'lucide-react';
import type { ChatSession } from '@/types/chat';
import { cn } from '@/utils/cn';

interface SidebarProps {
  sessions: ChatSession[];
  activeSessionId: string | null;
  onNewChat: () => void;
  onSelectSession: (sessionId: string) => void;
  onDeleteSession: (sessionId: string) => void;
  isOpen: boolean;
  onToggle: () => void;
  className?: string;
}

export const Sidebar = ({
  sessions,
  activeSessionId,
  onNewChat,
  onSelectSession,
  onDeleteSession,
  isOpen,
  onToggle,
  className,
}: SidebarProps) => {
  const handleDeleteSession = (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    onDeleteSession(sessionId);
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <view
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          bindtap={onToggle}
        />
      )}

      {/* Sidebar */}
      <view
        className={cn(
          'fixed lg:relative inset-y-0 left-0 z-50',
          'w-80 bg-chat-surface border-r-2 border-chat-border shadow-lg',
          'transform transition-transform duration-300 ease-in-out',
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
          className,
        )}
      >
        <view className="flex flex-col h-full">
          {/* Header */}
          <view className="flex items-center justify-between p-6 border-b-2 border-chat-border">
            <view className="flex items-center gap-3">
              <text className="text-2xl">🐱</text>
              <text className="text-2xl font-bold text-chat-text">
                JellyCat AI
              </text>
            </view>
            <view
              role="button"
              bindtap={onToggle}
              className="lg:hidden p-2 text-chat-text-secondary hover:text-chat-text rounded-lg hover:bg-chat-bg transition-colors"
            >
              <X size={20} />
            </view>
          </view>

          {/* New chat button */}
          <view className="p-4">
            <view
              role="button"
              bindtap={onNewChat}
              className="w-full flex items-center justify-center gap-3 p-4 bg-gradient-to-r from-chat-accent to-chat-pink text-white rounded-xl shadow-md hover:shadow-lg hover:from-chat-accent-hover hover:to-rose-500 transition-all transform hover:scale-105 font-semibold"
            >
              <Plus size={20} />
              <text>New Chat</text>
            </view>
          </view>

          {/* Sessions list */}
          <scrollview className="flex-1 overflow-y-auto p-4 pt-0">
            <view className="space-y-2">
              {sessions.length === 0 ? (
                <view className="text-center py-8">
                  <text className="text-chat-text-secondary text-sm">
                    No conversations yet
                  </text>
                  <text className="text-chat-text-secondary text-xs mt-1">
                    Click "New Chat" to start
                  </text>
                </view>
              ) : (
                sessions.map((session) => (
                  <view
                    key={session.id}
                    role="button"
                    bindtap={() => onSelectSession(session.id)}
                    className={cn(
                      'group flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-all',
                      session.id === activeSessionId
                        ? 'bg-gradient-to-r from-chat-accent/20 to-chat-pink/20 border border-chat-accent/30 shadow-sm animate-chat-bubble'
                        : 'hover:bg-chat-surface hover:shadow-sm',
                    )}
                  >
                    {session.id === activeSessionId ? (
                      <view className="w-8 h-8 bg-gradient-to-r from-chat-accent to-chat-pink rounded-full flex items-center justify-center shadow-md animate-pulse-gentle flex-shrink-0">
                        <MessageSquare size={16} className="text-white" />
                      </view>
                    ) : (
                      <MessageSquare
                        size={16}
                        className="flex-shrink-0 text-chat-text-secondary group-hover:text-chat-accent transition-colors ml-2"
                      />
                    )}
                    <view className="flex-1 min-w-0">
                      <text
                        className={cn(
                          'text-sm font-medium truncate',
                          session.id === activeSessionId
                            ? 'text-chat-accent'
                            : 'text-chat-text',
                        )}
                      >
                        {session.title}
                      </text>
                      <text className="text-xs text-chat-text-secondary">
                        {session.updatedAt.toLocaleDateString()} •{' '}
                        {session.updatedAt.toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </text>
                    </view>
                    <view
                      role="button"
                      bindtap={(e: React.MouseEvent) => handleDeleteSession(e, session.id)}
                      className="opacity-0 group-hover:opacity-100 p-1 text-chat-text-secondary hover:text-chat-error transition-all rounded"
                      aria-label={`Delete ${session.title}`}
                    >
                      <Trash2 size={14} />
                    </view>
                  </view>
                ))
              )}
            </view>
          </scrollview>

          {/* Footer */}
          <view className="p-4 border-t border-chat-border">
            <view className="text-xs text-chat-text-secondary text-center">
              <text>JellyCat AI v1.0</text>
              <text className="mt-1">Your confidential AI companion</text>
            </view>
          </view>
        </view>
      </view>

      {/* Mobile menu button */}
      <view
        role="button"
        bindtap={onToggle}
        className="lg:hidden fixed top-4 left-4 z-30 p-2 bg-chat-surface border border-chat-border text-chat-text rounded-lg hover:bg-chat-bg transition-colors"
      >
        <Menu size={20} />
      </view>
    </>
  );
};
