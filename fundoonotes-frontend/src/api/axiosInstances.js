import axios from 'axios';

/**
 * djangoClient
 * Preconditions:  VITE_DJANGO_API_URL is set in .env
 * Postconditions: All requests include Authorization: Bearer <accessToken>
 *                 via the request interceptor attached in interceptors.js
 */
export const djangoClient = axios.create({
  baseURL: import.meta.env.VITE_DJANGO_API_URL ?? 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
});

/**
 * collabClient
 * Preconditions:  VITE_COLLAB_API_URL is set in .env
 * Postconditions: All requests include Authorization: Bearer <accessToken>
 *                 No refresh interceptor — collab service has no /token/refresh
 */
export const collabClient = axios.create({
  baseURL: import.meta.env.VITE_COLLAB_API_URL ?? 'http://localhost:8001',
  headers: { 'Content-Type': 'application/json' },
});
