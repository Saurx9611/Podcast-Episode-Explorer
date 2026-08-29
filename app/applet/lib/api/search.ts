import { ApiClient } from './client';

export const searchApi = {
  search: (query: string, options?: any) => ApiClient.post('/search', { query, ...options }),
  
  getSavedSearches: () => ApiClient.get('/search/saved'),
  
  createSavedSearch: (data: any) => ApiClient.post('/search/saved', data),
  
  updateSavedSearch: (id: string, data: any) => ApiClient.patch(`/search/saved/${id}`, data),
  
  deleteSavedSearch: (id: string) => ApiClient.delete(`/search/saved/${id}`),
  
  runSavedSearch: (id: string) => ApiClient.post(`/search/saved/${id}/run`, {})
};
