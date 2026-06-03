import React, { createContext, useContext, useState, useCallback, useMemo } from 'react';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { lightTheme, darkTheme } from '@/theme/theme';
import { LOCAL_STORAGE_KEYS } from '@/utils/constants';

const ThemeContext = createContext(null);

function readPersistedMode() {
  const stored = localStorage.getItem(LOCAL_STORAGE_KEYS.THEME);
  return stored === 'dark' ? 'dark' : 'light';
}

export function ThemeProvider({ children }) {
  const [mode, setMode] = useState(readPersistedMode);

  const toggleTheme = useCallback(() => {
    setMode((prev) => {
      const next = prev === 'light' ? 'dark' : 'light';
      localStorage.setItem(LOCAL_STORAGE_KEYS.THEME, next);
      return next;
    });
  }, []);

  const muiTheme = useMemo(
    () => (mode === 'light' ? lightTheme : darkTheme),
    [mode],
  );

  const value = { mode, toggleTheme };

  return (
    <ThemeContext.Provider value={value}>
      <MuiThemeProvider theme={muiTheme}>
        <CssBaseline />
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider');
  return ctx;
}
