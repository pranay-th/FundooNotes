export const DJANGO_API_URL =
  import.meta.env.VITE_DJANGO_API_URL ?? 'http://localhost:8000';

export const COLLAB_API_URL =
  import.meta.env.VITE_COLLAB_API_URL ?? 'http://localhost:8001';

export const ROUTES = {
  LOGIN: '/login',
  REGISTER: '/register',
  VERIFY_EMAIL: '/verify-email',
  RESET_PASSWORD: '/reset-password',
  NOTES: '/app/notes',
  ARCHIVE: '/app/archive',
  TRASH: '/app/trash',
  SHARED: '/app/shared',
  PROFILE: '/app/profile',
  LABEL: (id) => `/app/labels/${id}`,
};

export const LOCAL_STORAGE_KEYS = {
  ACCESS_TOKEN: 'fundoo_access_token',
  REFRESH_TOKEN: 'fundoo_refresh_token',
  USER: 'fundoo_user',
  THEME: 'fundoo_theme',
};

export const SESSION_STORAGE_KEYS = {
  CHAT_HISTORY: 'fundoo_chat_history',
  CHAT_DISPLAY: 'fundoo_chat_display',
};
