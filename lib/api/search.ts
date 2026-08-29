import { apiClient } from './client';

export interface SearchRequest {
  query: string;
  project_id?: string;
  episode_ids?: string[];
  speaker_ids?: string[];
  similarity_threshold?: number;
  limit?: number;
}

export interface SearchResultItem {
  id: string;
  episode_id: string;
  episode_title: string;
  project?: string;
  speaker?: string;
  speaker_color?: string;
  start_time: number;
  end_time: number;
  timestamp: string; // "18:42"
  time_sec: number; // 1122
  text: string;
  highlight?: string;
  context_before?: string;
  context_after?: string;
  score: number;
  match_score: number; // 98
}

export interface SearchResponse {
  query: string;
  total_matches: number;
  execution_time_ms: number;
  results: SearchResultItem[];
}

export interface SavedSearch {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  query: string;
  filters: any[];
  created_at: string;
  updated_at: string;
  last_run_at?: string;
  last_run_formatted?: string;
  run_count: number;
}

export async function performSearch(params: SearchRequest): Promise<SearchResponse> {
  return apiClient<SearchResponse>('/search', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

export async function getSavedSearches(): Promise<SavedSearch[]> {
  return apiClient<SavedSearch[]>('/search/saved');
}

export async function createSavedSearch(data: { name: string; query: string; description?: string; filters?: any[] }): Promise<SavedSearch> {
  return apiClient<SavedSearch>('/search/saved', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getSavedSearch(id: string): Promise<SavedSearch> {
  return apiClient<SavedSearch>(`/search/saved/${id}`);
}

export async function updateSavedSearch(id: string, data: Partial<SavedSearch>): Promise<SavedSearch> {
  return apiClient<SavedSearch>(`/search/saved/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteSavedSearch(id: string): Promise<{ message: string; id: string }> {
  return apiClient<{ message: string; id: string }>(`/search/saved/${id}`, {
    method: 'DELETE',
  });
}

export async function runSavedSearch(id: string): Promise<SearchResponse> {
  return apiClient<SearchResponse>(`/search/saved/${id}/run`, {
    method: 'POST',
  });
}
