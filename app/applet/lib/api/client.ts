const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export class ApiClient {
  static async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_URL}${endpoint}`;
    
    const headers = new Headers(options.headers);
    if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
      headers.set('Content-Type', 'application/json');
    }
    
    // In a real app, add auth headers here
    
    const response = await fetch(url, { ...options, headers });
    
    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch (e) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }
      throw new Error(errorData.detail || errorData.error?.message || 'Unknown API error');
    }
    
    return response.json();
  }
  
  static async get<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }
  
  static async post<T>(endpoint: string, body: any, options: RequestInit = {}): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body instanceof FormData ? body : JSON.stringify(body),
    });
  }
  
  static async patch<T>(endpoint: string, body: any, options: RequestInit = {}): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: JSON.stringify(body),
    });
  }
  
  static async delete<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }
}
