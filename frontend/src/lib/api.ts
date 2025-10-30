const API_BASE = "http://localhost:8000";

// Auth token management
let authToken: string | null = null;
let currentUser: Player | null = null;

export function setAuthToken(token: string | null) {
  authToken = token;
  if (token) {
    localStorage.setItem("authToken", token);
  } else {
    localStorage.removeItem("authToken");
  }
}

export function getAuthToken(): string | null {
  if (!authToken && typeof window !== "undefined") {
    authToken = localStorage.getItem("authToken");
  }
  return authToken;
}

export function clearAuthToken() {
  setAuthToken(null);
  setCurrentUser(null);
}

// Current user management
export function setCurrentUser(user: Player | null) {
  currentUser = user;
  if (user) {
    localStorage.setItem("currentUser", JSON.stringify(user));
  } else {
    localStorage.removeItem("currentUser");
  }
}

export function getCurrentUser(): Player | null {
  if (!currentUser && typeof window !== "undefined") {
    const stored = localStorage.getItem("currentUser");
    if (stored) {
      try {
        currentUser = JSON.parse(stored);
      } catch (e) {
        console.error("Failed to parse stored user", e);
      }
    }
  }
  return currentUser;
}

// Helper to add auth header
function getAuthHeaders(): HeadersInit {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };
  const token = getAuthToken();
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
  email: string;
  wins: number;
  losses: number;
  points: number;
}

// Auth types
export interface RegisterRequest {
  name: string;
  email: string;
}

export interface LoginRequest {
  name: string;
  email: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  player: Player;
}

// Auth functions
export async function register(data: RegisterRequest): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "Failed to register");
  }
  const authResponse = await res.json();
  setAuthToken(authResponse.access_token);
  setCurrentUser(authResponse.player);
  return authResponse;
}

export async function login(data: LoginRequest): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "Failed to login");
  }
  const authResponse = await res.json();
  setAuthToken(authResponse.access_token);
  setCurrentUser(authResponse.player);
  return authResponse;
}

export function logout() {
  clearAuthToken();
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

// API Functions
export async function getPlayers(): Promise<Player[]> {
  const res = await fetch(`${API_BASE}/api/players`);
  if (!res.ok) throw new Error("Failed to fetch players");
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
    headers: getAuthHeaders(),
    body: JSON.stringify(match),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "Failed to create match");
  }
  return res.json();
}
