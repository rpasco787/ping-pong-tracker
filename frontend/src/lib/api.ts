const API_BASE = "http://localhost:8000";

// Helper to get auth token from localStorage
function getAuthToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('authToken');
  }
  return null;
}

// Helper to set auth headers
function getAuthHeaders(): HeadersInit {
  const token = getAuthToken();
  const headers: HeadersInit = { "Content-Type": "application/json" };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

// Health check
export async function getHealth() {
  const res = await fetch(`${API_BASE}/healthz`);
  if (!res.ok) throw new Error("API Error");
  return res.json();
}

// Player types (matching backend)
export interface Player {
  id: number;
  name: string;
  email?: string;
  wins: number;
  losses: number;
  points: number;
}

export interface PlayerInput {
  name: string;
  email?: string;
}

// Match types
export interface GameScore {
  home: number;
  away: number;
}

export interface Match {
  id: number;
  played_at: string;
  home_id: number;
  away_id: number;
  games: GameScore[];
}

export interface MatchInput {
  played_at: string;
  home_id: number;
  away_id: number;
  games: GameScore[];
}

// Auth types
export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  player_id?: number;
}

export interface LoginRequest {
  username: string;
  email: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

// API Functions
export async function getPlayers(): Promise<Player[]> {
  const res = await fetch(`${API_BASE}/api/players`);
  if (!res.ok) throw new Error("Failed to fetch players");
  return res.json();
}

export async function createPlayer(player: PlayerInput): Promise<Player> {
  const res = await fetch(`${API_BASE}/api/players`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(player),
  });
  if (!res.ok) throw new Error("Failed to create player");
  return res.json();
}

export async function getMatches(): Promise<Match[]> {
  const res = await fetch(`${API_BASE}/api/matches`);
  if (!res.ok) throw new Error("Failed to fetch matches");
  return res.json();
}

export async function createMatch(match: MatchInput): Promise<Match> {
  const res = await fetch(`${API_BASE}/api/matches`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(match),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "Failed to create match");
  }
  return res.json();
}

// Auth API Functions
export async function login(credentials: LoginRequest): Promise<TokenResponse> {
  const res = await fetch(`${API_BASE}/api/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(credentials),
  });
  
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "Failed to login");
  }
  
  const data = await res.json();
  // Store token in localStorage
  if (typeof window !== 'undefined') {
    localStorage.setItem('authToken', data.access_token);
  }
  return data;
}

export async function register(userData: RegisterRequest): Promise<User> {
  const res = await fetch(`${API_BASE}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(userData),
  });
  
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "Failed to register");
  }
  
  return res.json();
}

export async function getCurrentUser(): Promise<User> {
  const res = await fetch(`${API_BASE}/api/auth/users/me`, {
    headers: getAuthHeaders(),
  });
  
  if (!res.ok) {
    throw new Error("Failed to get current user");
  }
  
  return res.json();
}

export function logout(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('authToken');
  }
}

export function isAuthenticated(): boolean {
  return getAuthToken() !== null;
}