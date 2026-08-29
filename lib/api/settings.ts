import { apiClient } from './client';

export interface UserSettings {
  id: string;
  email: string;
  name?: string;
  role?: string;
  avatar_url?: string;
  preferences: {
    general?: {
      workspace_name?: string;
      default_playback_speed?: string;
    };
    processing?: {
      transcription_model?: string;
      language?: string;
      translate_to_english?: boolean;
      speaker_detection?: boolean;
      max_speakers?: string;
      speaker_labels?: string;
      chunking_strategy?: string;
      chunk_duration?: string;
      overlap?: string;
      embedding_model?: string;
      vector_index?: string;
      similarity_metric?: string;
      top_results?: string;
      auto_process?: boolean;
      generate_embeddings?: boolean;
      retry_failed_jobs?: boolean;
      max_retries?: string;
    };
    search?: {
      embedding_model?: string;
      similarity_metric?: string;
      search_mode?: string;
      default_results?: string;
      min_similarity?: string;
      show_similarity_score?: boolean;
      include_context?: boolean;
      context_window?: string;
      include_all_episodes?: boolean;
      search_speakers?: boolean;
      search_topics?: boolean;
      search_projects?: boolean;
      default_date_range?: string;
      open_result_in?: string;
      auto_play?: boolean;
      preserve_filters?: boolean;
      transcript_preview_length?: string;
      highlight_text?: boolean;
      show_speaker?: boolean;
      show_timestamp?: boolean;
      show_episode_metadata?: boolean;
    };
    account?: {
      language?: string;
      time_zone?: string;
      date_format?: string;
      notif_episode_processed?: boolean;
      notif_search_results?: boolean;
      notif_system_updates?: boolean;
      notif_email?: boolean;
      theme_mode?: string;
      accent_color?: string;
    };
    [key: string]: any;
  };
  created_at?: string;
  updated_at?: string;
}

export async function getSettings(): Promise<UserSettings> {
  return apiClient<UserSettings>('/settings');
}

export async function updateSettings(updates: Partial<UserSettings>): Promise<UserSettings> {
  return apiClient<UserSettings>('/settings', {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
}
