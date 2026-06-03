import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { getAccessToken, getUser } from '@/utils/tokenStorage';

export default function ProtectedRoute() {
  const { isAuthenticated } = useAuth();
  // Also check localStorage directly — covers the case where login() just ran
  // and React state hasn't propagated yet before navigate() fires
  const hasTokenInStorage = Boolean(getAccessToken() && getUser());

  if (!isAuthenticated && !hasTokenInStorage) {
    return <Navigate to="/login" replace />;
  }
  return <Outlet />;
}
