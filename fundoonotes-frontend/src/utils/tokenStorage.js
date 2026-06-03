import { LOCAL_STORAGE_KEYS } from './constants';

export function getAccessToken() {
  return localStorage.getItem(LOCAL_STORAGE_KEYS.ACCESS_TOKEN);
}

export function getRefreshToken() {
  return localStorage.getItem(LOCAL_STORAGE_KEYS.REFRESH_TOKEN);
}

export function getUser() {
  const raw = localStorage.getItem(LOCAL_STORAGE_KEYS.USER);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function setTokens(pair, user) {
  localStorage.setItem(LOCAL_STORAGE_KEYS.ACCESS_TOKEN, pair.access);
  localStorage.setItem(LOCAL_STORAGE_KEYS.REFRESH_TOKEN, pair.refresh);
  localStorage.setItem(LOCAL_STORAGE_KEYS.USER, JSON.stringify(user));
}

export function clearTokens() {
  localStorage.removeItem(LOCAL_STORAGE_KEYS.ACCESS_TOKEN);
  localStorage.removeItem(LOCAL_STORAGE_KEYS.REFRESH_TOKEN);
  localStorage.removeItem(LOCAL_STORAGE_KEYS.USER);
}
