'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { 
  Bell, 
  Check, 
  AlertCircle, 
  Clock, 
  Search, 
  FileText, 
  Info,
  CheckCircle2
} from 'lucide-react';

export type NotificationType = 'processing_complete' | 'processing_failed' | 'processing_started' | 'saved_search' | 'transcript_indexed' | 'system';

export interface NotificationItem {
  id: string;
  type: NotificationType;
  title: string;
  description: string;
  timestamp: string;
  read: boolean;
  link?: string;
}

const MOCK_NOTIFICATIONS: NotificationItem[] = [
  {
    id: '1',
    type: 'processing_complete',
    title: 'Episode processing completed',
    description: '"Scaling Distributed Systems Without Sacrificing Reliability" is ready to search.',
    timestamp: '2 min ago',
    read: false,
    link: '/episodes/scaling-distributed-systems'
  },
  {
    id: '2',
    type: 'processing_failed',
    title: 'Episode processing failed',
    description: '"AI Infrastructure at Scale" could not be processed.',
    timestamp: '18 min ago',
    read: false,
    link: '/processing'
  },
  {
    id: '3',
    type: 'saved_search',
    title: 'New saved search result',
    description: '"Database Bottlenecks" returned 4 new relevant segments.',
    timestamp: '1 hour ago',
    read: false,
    link: '/search'
  },
  {
    id: '4',
    type: 'transcript_indexed',
    title: 'Transcript indexed',
    description: '"Engineering Hiring in 2026" has been added to semantic search.',
    timestamp: '3 hours ago',
    read: true,
    link: '/episodes/engineering-hiring-2026'
  },
  {
    id: '5',
    type: 'processing_started',
    title: 'Processing started',
    description: '"Building Reliable Vector Search" is being transcribed.',
    timestamp: '5 hours ago',
    read: true,
    link: '/processing'
  }
];

export function NotificationCenter() {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>(MOCK_NOTIFICATIONS);
  const [filter, setFilter] = useState<'all' | 'unread'>('all');
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  
  const popoverRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const router = useRouter();

  const unreadCount = notifications.filter(n => !n.read).length;

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        popoverRef.current && 
        !popoverRef.current.contains(event.target as Node) &&
        triggerRef.current &&
        !triggerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }
    
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen]);

  const handleMarkAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    setToastMessage("All notifications marked as read.");
    setTimeout(() => setToastMessage(null), 3000);
  };

  const handleNotificationClick = (id: string, link?: string) => {
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
    if (link) {
      router.push(link);
      setIsOpen(false);
    }
  };

  const filteredNotifications = notifications.filter(n => {
    if (filter === 'unread') return !n.read;
    return true;
  });

  const getIcon = (type: NotificationType) => {
    switch (type) {
      case 'processing_complete': return <CheckCircle2 className="w-4 h-4 text-emerald-500" />;
      case 'processing_failed': return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'processing_started': return <Clock className="w-4 h-4 text-blue-400" />;
      case 'saved_search': return <Search className="w-4 h-4 text-[var(--color-accent)]" />;
      case 'transcript_indexed': return <FileText className="w-4 h-4 text-purple-400" />;
      default: return <Info className="w-4 h-4 text-[var(--color-secondary)]" />;
    }
  };

  return (
    <div className="relative">
      <button 
        ref={triggerRef}
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Notifications"
        aria-expanded={isOpen}
        className={cn(
          "p-2 text-[var(--color-secondary)] hover:text-[var(--color-primary)] hover:bg-[var(--color-border-subtle)] rounded-md relative transition-colors",
          isOpen && "bg-[var(--color-border-subtle)] text-[var(--color-primary)]"
        )}
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-[var(--color-accent)] rounded-full border border-[var(--color-surface)]"></span>
        )}
      </button>

      {isOpen && (
        <div 
          ref={popoverRef}
          className="absolute right-0 top-full mt-2 w-screen max-w-[calc(100vw-32px)] sm:w-[400px] sm:max-w-[400px] bg-[var(--color-surface)] border border-[var(--color-border)] shadow-2xl rounded-xl overflow-hidden z-50 animate-in fade-in slide-in-from-top-2 duration-150 origin-top-right flex flex-col max-h-[85vh] sm:max-h-[600px]"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--color-border)] shrink-0">
            <h3 className="text-sm font-semibold text-[var(--color-primary)]">Notifications</h3>
            {unreadCount > 0 && (
              <button 
                onClick={handleMarkAllAsRead}
                className="text-xs font-medium text-[var(--color-accent)] hover:text-[var(--color-accent-hover)] transition-colors"
              >
                Mark all as read
              </button>
            )}
          </div>

          {/* Filters */}
          <div className="flex items-center gap-4 px-4 py-2 border-b border-[var(--color-border-subtle)] shrink-0 bg-[#161618]/50">
            <button
              onClick={() => setFilter('all')}
              className={cn(
                "text-xs font-medium transition-colors border-b-2 px-1 pb-1 -mb-[9px]",
                filter === 'all' ? "border-[var(--color-accent)] text-[var(--color-primary)]" : "border-transparent text-[var(--color-secondary)] hover:text-[var(--color-primary)]"
              )}
            >
              All
            </button>
            <button
              onClick={() => setFilter('unread')}
              className={cn(
                "text-xs font-medium transition-colors border-b-2 px-1 pb-1 -mb-[9px] flex items-center gap-1.5",
                filter === 'unread' ? "border-[var(--color-accent)] text-[var(--color-primary)]" : "border-transparent text-[var(--color-secondary)] hover:text-[var(--color-primary)]"
              )}
            >
              Unread
              {unreadCount > 0 && (
                <span className="bg-[var(--color-accent-subtle)] text-[var(--color-accent)] px-1.5 py-0.5 rounded text-[10px] leading-none">
                  {unreadCount}
                </span>
              )}
            </button>
          </div>

          {/* List */}
          <div className="overflow-y-auto flex-1 overscroll-contain">
            {filteredNotifications.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
                <div className="w-12 h-12 rounded-full bg-[var(--color-border-subtle)] flex items-center justify-center mb-4">
                  <Bell className="w-5 h-5 text-[var(--color-secondary)]" />
                </div>
                <h4 className="text-sm font-medium text-[var(--color-primary)]">You&apos;re all caught up</h4>
                <p className="text-xs text-[var(--color-secondary)] mt-1 max-w-[200px]">New activity from your workspace will appear here.</p>
              </div>
            ) : (
              <div className="flex flex-col divide-y divide-[var(--color-border-subtle)]">
                {filteredNotifications.map((notification) => (
                  <button
                    key={notification.id}
                    onClick={() => handleNotificationClick(notification.id, notification.link)}
                    className={cn(
                      "flex items-start gap-3 p-4 w-full text-left transition-colors hover:bg-[var(--color-border-subtle)] relative",
                      !notification.read ? "bg-[#161618]/80" : ""
                    )}
                  >
                    {!notification.read && (
                      <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-[var(--color-accent)]" />
                    )}
                    <div className="mt-0.5 shrink-0">
                      {getIcon(notification.type)}
                    </div>
                    <div className="flex-1 min-w-0 space-y-1">
                      <div className="flex items-start justify-between gap-2">
                        <p className={cn(
                          "text-sm font-medium leading-tight truncate",
                          !notification.read ? "text-[var(--color-primary)]" : "text-[var(--color-secondary)]"
                        )}>
                          {notification.title}
                        </p>
                        <span className="text-[10px] text-[var(--color-secondary)] shrink-0 whitespace-nowrap pt-0.5">
                          {notification.timestamp}
                        </span>
                      </div>
                      <p className={cn(
                        "text-xs leading-relaxed line-clamp-2",
                        !notification.read ? "text-[#a0a0a5]" : "text-[#808085]"
                      )}>
                        {notification.description}
                      </p>
                      
                      {(notification.type === 'processing_failed' || notification.type === 'saved_search') && (
                        <div className="pt-1">
                          <span className="text-xs font-medium text-[var(--color-accent)] hover:underline">
                            {notification.type === 'processing_failed' ? 'View details' : 'View results'}
                          </span>
                        </div>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Global Toast - could be extracted to a centralized context, but keeping it localized for simplicity here since it's just for the notification mark all read */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-[100] bg-[var(--color-surface)] border border-[var(--color-border)] shadow-lg rounded-md px-4 py-3 flex items-center gap-2 animate-in slide-in-from-bottom-5">
          <Check className="w-4 h-4 text-emerald-400" />
          <span className="text-sm text-[var(--color-primary)]">{toastMessage}</span>
        </div>
      )}
    </div>
  );
}
