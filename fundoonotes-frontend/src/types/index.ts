// ─── API Response Shapes ────────────────────────────────────────────────────

export interface ApiResponse<T> {
  message: string;
  payload: T;
  status: number;
}

export interface TokenPair {
  access: string;
  refresh: string;
}

export interface UserProfile {
  id?: number;
  username: string;
  email: string;
  phone_number: string;
  is_verified: boolean;
  created_at?: string; // ISO 8601
}

export interface Label {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Note {
  id: number;
  title: string;
  content: string;
  color: NoteColor;
  is_archived: boolean;
  is_trashed: boolean;
  labels: Label[];
  created_at: string;
  updated_at: string;
}

export type NoteColor =
  | 'default' | 'red'    | 'orange' | 'yellow' | 'green'
  | 'teal'    | 'blue'   | 'purple' | 'pink'   | 'brown'
  | 'gray';

export type AccessLevel = 'read' | 'read_write';

export interface Collaborator {
  user_id: number;
  username: string;
  email: string;
  access_level: AccessLevel;
  created_at: string;
}

export interface SharedNote {
  id: number;
  title: string;
  content: string;
  color: NoteColor;
  access_level: AccessLevel;
}

// ─── Request Payloads ────────────────────────────────────────────────────────

export interface RegisterPayload {
  username: string;
  email: string;
  phone_number: string;
  password: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface OtpPayload {
  email: string;
  otp: string;
}

export interface CreateNotePayload {
  title: string;
  content: string;
  color: NoteColor;
  label_ids: number[];
}

export interface UpdateNotePayload extends Partial<CreateNotePayload> {
  is_archived?: boolean;
  is_trashed?: boolean;
}

export interface InviteCollaboratorPayload {
  collaborator_email: string;
  access_level: AccessLevel;
}

export interface UpdateCollaboratorPayload {
  access_level: AccessLevel;
}

// ─── Auth Store Shape ────────────────────────────────────────────────────────

export interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: UserProfile | null;
  isAuthenticated: boolean;
}

export interface AuthContextValue extends AuthState {
  login: (tokens: TokenPair, user: UserProfile) => void;
  logout: () => void;
  setAccessToken: (token: string) => void;
}

// ─── UI State Shape ──────────────────────────────────────────────────────────

export interface UIContextValue {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  activeLabelId: number | null;
  setActiveLabelId: (id: number | null) => void;
}

export interface ThemeContextValue {
  mode: 'light' | 'dark';
  toggleTheme: () => void;
}
