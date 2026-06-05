import React, { createContext, useContext, useState, useCallback } from 'react';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';

const ToastContext = createContext(null);

/**
 * ToastProvider
 * Wraps the app and provides a `useToast` hook.
 * Renders a single MUI Snackbar at the bottom of the screen.
 */
export function ToastProvider({ children }) {
  const [queue, setQueue] = useState([]);
  const [current, setCurrent] = useState(null);
  const [open, setOpen] = useState(false);

  // Pull the next item off the queue whenever the snackbar closes
  const processQueue = useCallback(() => {
    setQueue((prev) => {
      if (prev.length === 0) return prev;
      const [next, ...rest] = prev;
      setCurrent(next);
      setOpen(true);
      return rest;
    });
  }, []);

  const showToast = useCallback(
    (message, severity = 'info', duration = 4000) => {
      const entry = { message, severity, duration, key: Date.now() };
      setQueue((prev) => [...prev, entry]);
      // If nothing is showing, kick off immediately
      if (!open) {
        setCurrent(entry);
        setOpen(true);
      }
    },
    [open],
  );

  const toast = {
    success: (msg, duration) => showToast(msg, 'success', duration),
    error: (msg, duration) => showToast(msg, 'error', duration),
    info: (msg, duration) => showToast(msg, 'info', duration),
    warning: (msg, duration) => showToast(msg, 'warning', duration),
  };

  const handleClose = (_, reason) => {
    if (reason === 'clickaway') return;
    setOpen(false);
  };

  const handleExited = () => {
    setCurrent(null);
    processQueue();
  };

  return (
    <ToastContext.Provider value={toast}>
      {children}
      <Snackbar
        key={current?.key}
        open={open}
        autoHideDuration={current?.duration ?? 4000}
        onClose={handleClose}
        TransitionProps={{ onExited: handleExited }}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        {current ? (
          <Alert
            onClose={handleClose}
            severity={current.severity}
            variant="filled"
            sx={{ width: '100%', minWidth: 280 }}
          >
            {current.message}
          </Alert>
        ) : undefined}
      </Snackbar>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx;
}
