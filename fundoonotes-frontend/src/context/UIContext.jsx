import React, { createContext, useContext, useState } from 'react';

const UIContext = createContext(null);

export function UIProvider({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeLabelId, setActiveLabelId] = useState(null);

  const value = {
    sidebarOpen,
    setSidebarOpen,
    searchQuery,
    setSearchQuery,
    activeLabelId,
    setActiveLabelId,
  };

  return <UIContext.Provider value={value}>{children}</UIContext.Provider>;
}

export function useUI() {
  const ctx = useContext(UIContext);
  if (!ctx) throw new Error('useUI must be used within UIProvider');
  return ctx;
}
