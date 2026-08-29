import { ApiClient } from './client';

export const notificationsApi = {
  getNotifications: () => ApiClient.get('/notifications'),
  
  markRead: (id: string) => ApiClient.patch(`/notifications/${id}/read`, {}),
  
  markAllRead: () => ApiClient.post('/notifications/read-all', {})
};
