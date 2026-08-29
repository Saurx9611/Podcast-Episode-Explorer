const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';

export interface ApiError {
  code: string;
  message: string;
  details?: any;
}

export class ApiException extends Error {
  code: string;
  status: number;
  details?: any;

  constructor(status: number, error: ApiError) {
    super(error.message || 'API request failed');
    this.name = 'ApiException';
    this.status = status;
    this.code = error.code || 'UNKNOWN_ERROR';
    this.details = error.details;
  }
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  
  const headers: Record<string, string> = {
    Accept: 'application/json',
    ...(options.headers as Record<string, string>),
  };

  // Only set Content-Type to JSON if body is not FormData
  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorData: ApiError = {
      code: 'HTTP_ERROR',
      message: `HTTP Error ${response.status}: ${response.statusText}`,
    };
    try {
      const json = await response.json();
      if (json.error) {
        errorData = json.error;
      } else if (json.detail) {
        errorData = {
          code: 'API_ERROR',
          message: typeof json.detail === 'string' ? json.detail : JSON.stringify(json.detail),
        };
      }
    } catch {
      // Ignored if response is not JSON
    }
    throw new ApiException(response.status, errorData);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}
