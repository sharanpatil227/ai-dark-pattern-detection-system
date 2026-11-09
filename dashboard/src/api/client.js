import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE + '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'An unexpected error occurred';
    console.error('[API Error]', message);
    return Promise.reject(error);
  }
);

export const scanUrl = async (scanData) => {
  const { data } = await apiClient.post('/scan', scanData);
  return data;
};

export const getReports = async (page = 1, limit = 20, search = '') => {
  const params = { page, limit };
  if (search) params.search = search;
  const { data } = await apiClient.get('/reports', { params });
  return data;
};

export const getReport = async (scanId) => {
  const { data } = await apiClient.get(`/reports/${scanId}`);
  return data;
};

export const getDashboardStats = async () => {
  const { data } = await apiClient.get('/dashboard/stats');
  return data;
};

export default apiClient;
