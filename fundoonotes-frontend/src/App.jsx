import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import { ThemeProvider } from '@/context/ThemeContext';
import { UIProvider } from '@/context/UIContext';
import { ToastProvider } from '@/context/ToastContext';
import { attachInterceptors } from '@/api/interceptors';
import { LOCAL_STORAGE_KEYS } from '@/utils/constants';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import AppLayout from '@/components/layout/AppLayout';

// Pages
import LoginPage from '@/pages/LoginPage';
import RegisterPage from '@/pages/RegisterPage';
import VerifyEmailPage from '@/pages/VerifyEmailPage';
import ResetPasswordPage from '@/pages/ResetPasswordPage';
import NotesPage from '@/pages/NotesPage';
import ArchivePage from '@/pages/ArchivePage';
import TrashPage from '@/pages/TrashPage';
import SharedNotesPage from '@/pages/SharedNotesPage';
import LabelPage from '@/pages/LabelPage';
import ProfilePage from '@/pages/ProfilePage';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1 } },
});

function InterceptorSetup() {
  const auth = useAuth();

  useEffect(() => {
    // Read directly from localStorage so the interceptor always gets
    // the current token, not a stale closure over React state
    attachInterceptors(
      () => localStorage.getItem(LOCAL_STORAGE_KEYS.ACCESS_TOKEN),
      () => localStorage.getItem(LOCAL_STORAGE_KEYS.REFRESH_TOKEN),
      auth.setAccessToken,
      auth.logout,
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return null;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <UIProvider>
            <ToastProvider>
            <BrowserRouter>
              <InterceptorSetup />
              <Routes>
                {/* Public routes */}
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/verify-email" element={<VerifyEmailPage />} />
                <Route path="/reset-password" element={<ResetPasswordPage />} />

                {/* Protected routes */}
                <Route element={<ProtectedRoute />}>
                  <Route element={<AppLayout />}>
                    <Route path="/app/notes" element={<NotesPage />} />
                    <Route path="/app/archive" element={<ArchivePage />} />
                    <Route path="/app/trash" element={<TrashPage />} />
                    <Route path="/app/shared" element={<SharedNotesPage />} />
                    <Route path="/app/labels/:labelId" element={<LabelPage />} />
                    <Route path="/app/profile" element={<ProfilePage />} />
                  </Route>
                </Route>

                {/* Catch-all */}
                <Route path="*" element={<Navigate to="/app/notes" replace />} />
              </Routes>
            </BrowserRouter>
            </ToastProvider>
          </UIProvider>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
