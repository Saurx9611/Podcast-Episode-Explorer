import { ApiClient } from './client';

export const projectsApi = {
  getProjects: () => ApiClient.get('/projects'),
  
  getProject: (id: string) => ApiClient.get(`/projects/${id}`),
  
  createProject: (data: any) => ApiClient.post('/projects', data),
  
  updateProject: (id: string, data: any) => ApiClient.patch(`/projects/${id}`, data),
  
  deleteProject: (id: string) => ApiClient.delete(`/projects/${id}`)
};
