import { apiClient } from './client';

export interface Project {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  episodes_count?: number;
  total_duration_formatted?: string;
}

export async function getProjects(): Promise<Project[]> {
  return apiClient<Project[]>('/projects');
}

export async function getProject(id: string): Promise<Project> {
  return apiClient<Project>(`/projects/${id}`);
}

export async function createProject(data: { name: string; description?: string }): Promise<Project> {
  return apiClient<Project>('/projects', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateProject(id: string, data: { name?: string; description?: string }): Promise<Project> {
  return apiClient<Project>(`/projects/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteProject(id: string): Promise<{ message: string; id: string }> {
  return apiClient<{ message: string; id: string }>(`/projects/${id}`, {
    method: 'DELETE',
  });
}
