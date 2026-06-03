import { LOCAL_STORAGE_KEYS } from './constants';
import type { TokenPair, UserProfile } from '@/types';

export function getAccessToken(): string | null {
  return localStorage.getItem(LOCAL_STORAGE_KEYS.ACCESS_TOKEN);
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(LOCAL_STORAGE_KEYS.REFRESH_TOKEN);
}

export function getUser(): UserProfile | null {
  const raw = localStorage.getItem(LOCAL_STORAGE_KEYS.USER);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as UserProfile;
  } catch {
    return null;
  }
}

export function setTokens(pair: TokenPair, user: UserProfile): void {
  localStorage.setItem(LOCAL_STORAGE_KEYS.ACCESS_TOKEN, pair.access);
  localStorage.setItem(LOCAL_STORAGE_KEYS.REFRESH_TOKEN, pair.refresh);
  localStorage.setItem(LOCAL_STORAGE_KEYS.USER, JSON.stringify(user));
}

export function clearTokens(): void {
  localStorage.removeItem(LOCAL_STORAGE_KEYS.ACCESS_TOKEN);
  localStorage.removeItem(LOCAL_STORAGE_KEYS.REFRESH_TOKEN);
  localStorage.removeItem(LOCAL_STORAGE_KEYS.USER);
}
