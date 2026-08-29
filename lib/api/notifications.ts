import { apiClient } from './client';

export type NotificationType =
  | 'processing_complete'
  | 'processing_completed'
  | 'processing_failed'
  | 'processing_started'
  | 'saved_search'
  | 'saved_search_result'
  | 'transcript_indexed'
  | 'system';

export interface NotificationItem {
  id: string;
  user_id?: string;
  type: NotificationType;
  title: string;
  description: string;
  timestamp: string;
  read: boolean;
  link?: string;
  created_at?: string;
}

export async function getNotifications(unreadOnly = false): Promise<NotificationItem[]> {
  const query = unreadOnly ? '?unread_only=true' : '';
  return apiClient<NotificationItem[]>(`/notifications${query}`);
}

export async function markNotificationAsRead(id: string): Promise<NotificationItem> {
  return apiClient<NotificationItem>(`/notifications/${id}/read`, {
    method: 'PATCH',
  });
}

export async function markAllNotificationsAsRead(): Promise<{ message: string; count: number }> {
  return apiClient<{ message: string; count: number }>('/notifications/read-all', {
    method: 'POST',
  });
}
