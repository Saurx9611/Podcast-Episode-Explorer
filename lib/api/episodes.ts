import { apiClient } from './client';

export interface Speaker {
  id: string;
  episode_id: string;
  label: string;
  display_name?: string;
  speaking_duration: number;
  segment_count: number;
}

export interface TranscriptSegment {
  id: string;
  episode_id: string;
  speaker_id?: string;
  start_time: number;
  end_time: number;
  text: string;
  sequence_number: number;
  confidence?: number;
  start?: string;
  startSec?: number;
  speaker?: Speaker;
}

export interface EpisodeInsight {
  id: string;
  episode_id: string;
  overview?: string;
  competencies: string[];
  technologies: string[];
  architecture: string[];
  resume_bullet?: string;
  created_at: string;
  updated_at: string;
}

export interface Episode {
  id: string;
  project_id?: string;
  project_name?: string;
  title: string;
  description?: string;
  original_filename?: string;
  audio_url?: string;
  mime_type?: string;
  file_size?: number;
  file_size_formatted?: string;
  duration?: number;
  duration_formatted?: string;
  date_formatted?: string;
  status: string; // 'uploaded' | 'queued' | 'transcribing' | 'completed' | 'failed' | 'Indexed' | 'Processing'
  processing_model?: string;
  index_time?: string;
  created_at: string;
  updated_at: string;
  processed_at?: string;
  speakers?: Speaker[];
  insight?: EpisodeInsight;
}

export interface EpisodeUploadResponse {
  id: string;
  status: string;
  title: string;
  message: string;
}

export async function getEpisodes(params?: {
  project_id?: string;
  status?: string;
  q?: string;
  skip?: number;
  limit?: number;
}): Promise<Episode[]> {
  const searchParams = new URLSearchParams();
  if (params?.project_id) searchParams.append('project_id', params.project_id);
  if (params?.status) searchParams.append('status', params.status);
  if (params?.q) searchParams.append('q', params.q);
  if (params?.skip !== undefined) searchParams.append('skip', String(params.skip));
  if (params?.limit !== undefined) searchParams.append('limit', String(params.limit));

  const queryStr = searchParams.toString();
  return apiClient<Episode[]>(`/episodes${queryStr ? `?${queryStr}` : ''}`);
}

export async function getEpisode(id: string): Promise<Episode> {
  return apiClient<Episode>(`/episodes/${id}`);
}

export async function uploadEpisode(
  file: File,
  metadata?: { title?: string; project_id?: string; description?: string }
): Promise<EpisodeUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  if (metadata?.title) formData.append('title', metadata.title);
  if (metadata?.project_id) formData.append('project_id', metadata.project_id);
  if (metadata?.description) formData.append('description', metadata.description);

  return apiClient<EpisodeUploadResponse>('/episodes', {
    method: 'POST',
    body: formData,
  });
}

export async function updateEpisode(id: string, updates: Partial<Episode>): Promise<Episode> {
  return apiClient<Episode>(`/episodes/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
}

export async function deleteEpisode(id: string): Promise<{ message: string; id: string }> {
  return apiClient<{ message: string; id: string }>(`/episodes/${id}`, {
    method: 'DELETE',
  });
}

export async function getTranscript(id: string): Promise<TranscriptSegment[]> {
  return apiClient<TranscriptSegment[]>(`/episodes/${id}/transcript`);
}

export async function getSpeakers(id: string): Promise<Speaker[]> {
  return apiClient<Speaker[]>(`/episodes/${id}/speakers`);
}

export async function renameSpeaker(
  episodeId: string,
  speakerId: string,
  displayName: string
): Promise<Speaker> {
  return apiClient<Speaker>(`/episodes/${episodeId}/speakers/${speakerId}`, {
    method: 'PATCH',
    body: JSON.stringify({ display_name: displayName }),
  });
}

export async function getInsights(id: string): Promise<EpisodeInsight> {
  return apiClient<EpisodeInsight>(`/episodes/${id}/insights`);
}
