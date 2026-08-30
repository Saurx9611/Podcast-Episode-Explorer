import { apiClient } from './client';
import { Episode } from './episodes';

export interface Podcast {
  id: string;
  title: string;
  description?: string;
  author?: string;
  publisher?: string;
  artwork_url?: string;
  language?: string;
  feed_url?: string;
  website_url?: string;
  episode_count?: number;
  created_at: string;
  updated_at: string;
  episodes?: Episode[];
}

export interface PodcastImportRequest {
  feed_url: string;
  auto_download_latest?: boolean;
  auto_process_latest?: boolean;
  project_id?: string;
}

export interface PodcastImportResponse {
  podcast: Podcast;
  imported_episodes_count: number;
  message: string;
}

export async function getPodcasts(): Promise<Podcast[]> {
  return apiClient<Podcast[]>('/podcasts');
}

export async function getPodcast(id: string): Promise<Podcast> {
  return apiClient<Podcast>(`/podcasts/${id}`);
}

export async function importPodcast(data: PodcastImportRequest): Promise<PodcastImportResponse> {
  return apiClient<PodcastImportResponse>('/podcasts/import', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function deletePodcast(id: string): Promise<{ message: string; id: string }> {
  return apiClient<{ message: string; id: string }>(`/podcasts/${id}`, {
    method: 'DELETE',
  });
}
