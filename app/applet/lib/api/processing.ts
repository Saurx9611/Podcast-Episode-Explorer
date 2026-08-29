import { ApiClient } from './client';

export const processingApi = {
  getJobs: () => ApiClient.get('/processing/jobs'),
  
  getEpisodeJobs: (episodeId: string) => ApiClient.get(`/processing/episodes/${episodeId}/jobs`)
};
