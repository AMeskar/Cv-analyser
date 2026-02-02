import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

export interface ApiError {
  message: string;
  detail?: string;
}

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for auth (JWT)
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        const apiError: ApiError = {
          message: error.message,
          detail: (error.response?.data as any)?.detail,
        };
        return Promise.reject(apiError);
      }
    );
  }

  async uploadCV(file: File): Promise<{ cv_id: string; filename: string; size_bytes: number; uploaded_at: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post('/api/v1/cv/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  async analyzeCV(cvId: string, provider?: string, promptVersion?: string): Promise<{ job_id: string; cv_id: string; status: string; created_at: string }> {
    const response = await this.client.post(`/api/v1/cv/${cvId}/analyze`, {
      provider,
      prompt_version: promptVersion,
    });

    return response.data;
  }

  async getJobStatus(jobId: string): Promise<{
    job_id: string;
    cv_id: string;
    status: string;
    created_at: string;
    updated_at: string;
    timeline: Array<{
      timestamp: string;
      event: string;
      message: string;
      metadata?: Record<string, any>;
    }>;
    error?: string;
  }> {
    const response = await this.client.get(`/api/v1/jobs/${jobId}`);
    return response.data;
  }

  async getReport(cvId: string): Promise<any> {
    const response = await this.client.get(`/api/v1/cv/${cvId}/report`);
    return response.data;
  }
}

export const apiClient = new ApiClient();
