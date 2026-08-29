import { apiClient } from './client';

export interface ProcessingJob {
  id: string;
  episode_id: string;
  episode_title?: string;
  status: string; // 'queued' | 'transcribing' | 'speaker_detection' | 'chunking' | 'embedding' | 'indexing' | 'completed' | 'failed'
  current_stage: string;
  progress: number;
  error_message?: string;
  started_at?: string;
  started_formatted?: string;
  completed_at?: string;
  duration_formatted?: string;
  created_at: string;
  updated_at: string;
}

export interface ProcessingStats {
  active_jobs_count: number;
  has_active_jobs: boolean;
}

export async function getProcessingJobs(limit: number = 50): Promise<ProcessingJob[]> {
  return apiClient<ProcessingJob[]>(`/processing/jobs?limit=${limit}`);
}

export async function getProcessingJob(id: string): Promise<ProcessingJob> {
  return apiClient<ProcessingJob>(`/processing/jobs/${id}`);
}

export async function getEpisodeProcessingStatus(episodeId: string): Promise<ProcessingJob> {
  return apiClient<ProcessingJob>(`/episodes/${episodeId}/processing`);
}

export async function processEpisode(episodeId: string): Promise<ProcessingJob> {
  return apiClient<ProcessingJob>(`/episodes/${episodeId}/process`, {
    method: 'POST',
  });
}

export async function retryJob(jobId: string): Promise<ProcessingJob> {
  return apiClient<ProcessingJob>(`/processing/jobs/${jobId}/retry`, {
    method: 'POST',
  });
}

export async function cancelJob(jobId: string): Promise<ProcessingJob> {
  return apiClient<ProcessingJob>(`/processing/jobs/${jobId}/cancel`, {
    method: 'POST',
  });
}

export async function getProcessingStats(): Promise<ProcessingStats> {
  return apiClient<ProcessingStats>('/processing/stats');
}
