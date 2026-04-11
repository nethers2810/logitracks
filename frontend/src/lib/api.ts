import axios from 'axios';

const configuredBase = import.meta.env.VITE_API_BASE_URL?.trim();
const normalizedBase = configuredBase
  ? configuredBase.replace(/\/$/, '').endsWith('/api')
    ? configuredBase.replace(/\/$/, '')
    : `${configuredBase.replace(/\/$/, '')}/api`
  : '/api';

export const api = axios.create({
  baseURL: normalizedBase,
});
