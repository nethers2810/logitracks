import axios from 'axios';
import { getToken } from './auth';

const TOKEN_KEY = 'logitracks.token';
const USER_KEY = 'logitracks.user';

export type AuthUser = {
  user_id: number;
  email: string;
  full_name?: string;
  role: string;
  is_active: boolean;
};

export const authStore = {
  getToken: () => localStorage.getItem(TOKEN_KEY),
  setSession: (token: string, user: AuthUser) => {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },
  clear: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },
  getUser: (): AuthUser | null => {
    const raw = localStorage.getItem(USER_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw) as AuthUser;
    } catch {
      return null;
    }
  },
};

const configuredBase = import.meta.env.VITE_API_BASE_URL?.trim();
const normalizedBase = configuredBase
  ? configuredBase.replace(/\/$/, '').endsWith('/api')
    ? configuredBase.replace(/\/$/, '')
    : `${configuredBase.replace(/\/$/, '')}/api`
  : '/api';

export const api = axios.create({
  baseURL: normalizedBase,
});

api.interceptors.request.use((config) => {
  const token = authStore.getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
