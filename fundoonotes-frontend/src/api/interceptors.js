import axios from 'axios';
import { djangoClient, collabClient } from './axiosInstances';

// Queue of pending requests waiting for token refresh
let isRefreshing = false;
let refreshQueue = [];

function processQueue(error, token) {
  refreshQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error);
    else resolve(token);
  });
  refreshQueue = [];
}

/**
 * attachInterceptors
 *
 * Attaches request and response interceptors to djangoClient and collabClient.
 * Must be called once at application startup.
 */
export function attachInterceptors(
  getAccessToken,
  getRefreshToken,
  setAccessToken,
  clearAuth,
) {
  // ── Request interceptor: inject Bearer token on djangoClient ──────────────
  djangoClient.interceptors.request.use((config) => {
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  // ── Response interceptor: handle 401 with silent refresh ──────────────────
  djangoClient.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;

      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        if (isRefreshing) {
          // Queue this request until the ongoing refresh completes
          return new Promise((resolve, reject) => {
            refreshQueue.push({ resolve, reject });
          }).then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return djangoClient(originalRequest);
          }).catch((err) => Promise.reject(err));
        }

        isRefreshing = true;
        const refreshToken = getRefreshToken();

        if (!refreshToken) {
          isRefreshing = false;
          clearAuth();
          window.location.href = '/login';
          return Promise.reject(error);
        }

        try {
          const { data } = await axios.post(
            `${djangoClient.defaults.baseURL}/api/token/refresh/`,
            { refresh: refreshToken },
          );
          const newToken = data.access;
          setAccessToken(newToken);
          processQueue(null, newToken);
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return djangoClient(originalRequest);
        } catch (refreshError) {
          processQueue(refreshError, null);
          clearAuth();
          window.location.href = '/login';
          return Promise.reject(refreshError);
        } finally {
          isRefreshing = false;
        }
      }

      return Promise.reject(error);
    },
  );

  // ── Request interceptor: inject Bearer token on collabClient ──────────────
  collabClient.interceptors.request.use((config) => {
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });
}
