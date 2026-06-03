import React, { createContext, useContext, useState, useCallback } from 'react';
import {
  getAccessToken,
  getRefreshToken,
  getUser,
  setTokens,
  clearTokens,
} from '@/utils/tokenStorage';
import { LOCAL_STORAGE_KEYS, SESSION_STORAGE_KEYS } from '@/utils/constants';

const AuthContext = createContext(null);

function buildInitialState() {
  const accessToken = getAccessToken();
  const refreshToken = getRefreshToken();
  const user = getUser();
  return {
    accessToken,
    refreshToken,
    user,
    isAuthenticated: Boolean(accessToken && user),
  };
}

export function AuthProvider({ children }) {
  const [state, setState] = useState(buildInitialState);

  const login = useCallback((tokens, user) => {
    setTokens(tokens, user);
    setState({
      accessToken: tokens.access,
      refreshToken: tokens.refresh,
      user,
      isAuthenticated: true,
    });
  }, []);

  const logout = useCallback(() => {
    clearTokens();
    // Clear chatbot session so the next user doesn't see a previous user's history
    sessionStorage.removeItem(SESSION_STORAGE_KEYS.CHAT_HISTORY);
    sessionStorage.removeItem(SESSION_STORAGE_KEYS.CHAT_DISPLAY);
    setState({
      accessToken: null,
      refreshToken: null,
      user: null,
      isAuthenticated: false,
    });
  }, []);

  const setAccessToken = useCallback((token) => {
    localStorage.setItem(LOCAL_STORAGE_KEYS.ACCESS_TOKEN, token);
    setState((prev) => ({ ...prev, accessToken: token }));
  }, []);

  const value = {
    ...state,
    login,
    logout,
    setAccessToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
