import axios, { AxiosInstance, AxiosError } from 'axios';
import type { KeycloakInstance } from 'keycloak-js';

let keycloakInstance: KeycloakInstance | null = null;

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const client: AxiosInstance = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

client.interceptors.request.use(
  (config) => {
    if (keycloakInstance?.token) {
      config.headers.Authorization = `Bearer ${keycloakInstance.token}`;
    }
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

client.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    console.error('API Error:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      message: error.message,
      url: error.config?.url,
    });
    return Promise.reject(error);
  }
);

export const setKeycloakInstance = (instance: KeycloakInstance) => {
  keycloakInstance = instance;
  console.log('Keycloak instance initialized in API service');
};

export const apiService = {
  // Health check
  healthCheck: () =>
    axios.get(`${API_URL}/health`).then((res) => res.data).catch((err) => {
      console.error('Health check failed:', err);
      throw err;
    }),

  // Access Requests
  createAccessRequest: (data: any) =>
    client.post('/requests', data).then((res) => res.data),

  getAccessRequests: (params?: any) =>
    client.get('/requests', { params }).then((res) => res.data),

  getAccessRequest: (id: number) =>
    client.get(`/requests/${id}`).then((res) => res.data),

  updateAccessRequest: (id: number, data: any) =>
    client.patch(`/requests/${id}`, data).then((res) => res.data),

  approveAccessRequest: (id: number, comment?: string) =>
    client.post(`/requests/${id}/approve`, { approval_comment: comment }).then((res) => res.data),

  rejectAccessRequest: (id: number, reason: string) =>
    client.post(`/requests/${id}/reject`, { rejection_reason: reason }).then((res) => res.data),

  // Users
  getUserProfile: () =>
    client.get('/users/profile').then((res) => res.data),

  updateUserProfile: (data: any) =>
    client.put('/users/profile', data).then((res) => res.data),

  getAllUsers: () =>
    client.get('/admin/users').then((res) => res.data),

  updateUser: (id: number, data: any) =>
    client.put(`/admin/users/${id}`, data).then((res) => res.data),

  // Audit
  getAuditLogs: (params?: any) =>
    client.get('/audit', { params }).then((res) => res.data),

  // Admin
  getAdminStats: () =>
    client.get('/admin/stats').then((res) => res.data),

  // Configuration
  getPublicConfig: () =>
    client.get('/config/public').then((res) => res.data),

  getAdminConfig: () =>
    client.get('/config/admin').then((res) => res.data),
};
