import axios from 'axios';

const DEFAULT_API = 'https://groupifyassist.onrender.com/api/';
// Prefer Vite env if provided, else default to Render backend
const BASE_URL = (import.meta?.env?.VITE_API_BASE_URL) || DEFAULT_API;

export const api = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach Authorization header if token exists
api.interceptors.request.use((config) => {
  // Ensure relative paths so baseURL '/api' isn't dropped when url starts with '/'
  if (config.url && config.url.startsWith('/')) {
    config.url = config.url.replace(/^\/+/, '');
  }
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Optional: handle 401 globally
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err?.response?.status === 401) {
      // Clear bad token and redirect to login
      try { localStorage.removeItem('access_token'); } catch {}
      if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) {
        window.location.replace('/login');
      }
    }
    return Promise.reject(err);
  }
);
