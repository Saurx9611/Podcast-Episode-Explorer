import { ApiClient } from './client';

export const episodesApi = {
  getEpisodes: () => ApiClient.get('/episodes'),
  
  getEpisode: (id: string) => ApiClient.get(`/episodes/${id}`),
  
  getTranscript: (id: string) => ApiClient.get(`/episodes/${id}/transcript`),
  
  getSpeakers: (id: string) => ApiClient.get(`/episodes/${id}/speakers`),
  
  getInsights: (id: string) => ApiClient.get(`/episodes/${id}/insights`),
  
  uploadEpisode: (file: File, projectId?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (projectId) {
      formData.append('project_id', projectId);
    }
    return ApiClient.post('/episodes', formData);
  },
  
  deleteEpisode: (id: string) => ApiClient.delete(`/episodes/${id}`)
};
