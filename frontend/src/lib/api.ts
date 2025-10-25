const API_BASE = "http://localhost:8000";

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