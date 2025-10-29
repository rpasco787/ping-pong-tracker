"use client";
import { useEffect, useState } from "react";
import { 
  getPlayers, 
  createMatch, 
  getMatches,
  type Player, 
  type Match,
  type MatchInput 
} from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

export default function Home() {
  const { user, loading: authContextLoading, login, register, logout } = useAuth();
  // State for data
  const [players, setPlayers] = useState<Player[]>([]);
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);

  // Auth form state
  const [showLogin, setShowLogin] = useState(true);
  const [authError, setAuthError] = useState("");
  const [authFormLoading, setAuthFormLoading] = useState(false);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");

  // Match form state
  const [showMatchForm, setShowMatchForm] = useState(false);
  const [awayId, setAwayId] = useState<number | "">("");
  const [gameScores, setGameScores] = useState<Array<{ home: number; away: number }>>([
    { home: 0, away: 0 }
  ]);

  // Load data on mount
  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const [playersData, matchesData] = await Promise.all([
        getPlayers(),
        getMatches()
      ]);
      setPlayers(playersData);
      setMatches(matchesData);
    } catch (error) {
      console.error("Failed to load data:", error);
    } finally {
      setLoading(false);
    }
  }

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setAuthError("");
    setAuthFormLoading(true);
    try {
      await login(username, password);
      setUsername("");
      setPassword("");
    } catch (error) {
      setAuthError(error instanceof Error ? error.message : "Failed to login");
    } finally {
      setAuthFormLoading(false);
    }
  }

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    setAuthError("");
    if (!email.trim()) {
      setAuthError("Email is required");
      return;
    }
    setAuthFormLoading(true);
    try {
      await register(username, email, password);
      setUsername("");
      setEmail("");
      setPassword("");
    } catch (error) {
      setAuthError(error instanceof Error ? error.message : "Failed to register");
    } finally {
      setAuthFormLoading(false);
    }
  }

  async function handleCreateMatch(e: React.FormEvent) {
    e.preventDefault();
    if (!user?.player_id) {
      alert("Your account is not linked to a player. Please contact an administrator.");
      return;
    }
    if (awayId === "") {
      alert("Please select an opponent");
      return;
    }

    try {
      const matchInput: MatchInput = {
        played_at: new Date().toISOString(),
        home_id: user.player_id, // Logged-in user is always the home player
        away_id: Number(awayId),
        games: gameScores
      };
      await createMatch(matchInput);
      
      // Reset form
      setAwayId("");
      setGameScores([{ home: 0, away: 0 }]);
      setShowMatchForm(false);
      loadData(); // Refresh
    } catch (error) {
      alert("Failed to create match: " + error);
    }
  }

  function addGame() {
    setGameScores([...gameScores, { home: 0, away: 0 }]);
  }

  function updateGame(index: number, field: "home" | "away", value: number) {
    const updated = [...gameScores];
    updated[index][field] = value;
    setGameScores(updated);
  }

  if (authContextLoading || loading) {
    return (
      <main className="min-h-screen p-6 bg-gray-900">
        <div className="max-w-6xl mx-auto">
          <p className="text-gray-300">Loading...</p>
        </div>
      </main>
    );
  }

  // Sort players by points (descending)
  const sortedPlayers = [...players].sort((a, b) => b.points - a.points);

  return (
    <main className="min-h-screen p-6 bg-gray-900">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold text-white">🏓 Ping Pong Leaderboard</h1>
          {user ? (
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-white font-medium">{user.username}</div>
                <div className="text-sm text-gray-400">{user.email}</div>
              </div>
              <button
                onClick={logout}
                className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 font-medium transition-colors"
              >
                Logout
              </button>
            </div>
          ) : (
            <div className="text-right">
              <p className="text-sm text-gray-400">Login to record matches</p>
            </div>
          )}
        </div>

        {/* Login/Register Form - Only show when not authenticated */}
        {!user && (
          <div className="bg-gray-800 rounded-lg shadow-xl p-6 mb-8 border border-gray-700">
            <div className="flex gap-4 mb-6 border-b border-gray-700">
              <button
                onClick={() => { setShowLogin(true); setAuthError(""); }}
                className={`flex-1 py-2 font-medium transition-colors ${
                  showLogin
                    ? "text-blue-400 border-b-2 border-blue-400"
                    : "text-gray-400 hover:text-gray-300"
                }`}
              >
                Login
              </button>
              <button
                onClick={() => { setShowLogin(false); setAuthError(""); }}
                className={`flex-1 py-2 font-medium transition-colors ${
                  !showLogin
                    ? "text-blue-400 border-b-2 border-blue-400"
                    : "text-gray-400 hover:text-gray-300"
                }`}
              >
                Register
              </button>
            </div>

            {authError && (
              <div className="mb-4 p-3 bg-red-900/50 border border-red-700 text-red-200 rounded-lg text-sm">
                {authError}
              </div>
            )}

            {showLogin ? (
              <form onSubmit={handleLogin} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-300">Username</label>
                    <input
                      type="text"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      className="w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-300">Password</label>
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                </div>
                <button
                  type="submit"
                  disabled={authFormLoading}
                  className="w-full px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors disabled:bg-gray-600 disabled:cursor-not-allowed"
                >
                  {authFormLoading ? "Logging in..." : "Login"}
                </button>
              </form>
            ) : (
              <form onSubmit={handleRegister} className="space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-300">Username</label>
                    <input
                      type="text"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      className="w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-300">Email</label>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-300">Password</label>
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                </div>
                <button
                  type="submit"
                  disabled={authFormLoading}
                  className="w-full px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors disabled:bg-gray-600 disabled:cursor-not-allowed"
                >
                  {authFormLoading ? "Registering..." : "Register"}
                </button>
              </form>
            )}
          </div>
        )}

        {/* Leaderboard Table */}
        <div className="bg-gray-800 rounded-lg shadow-xl p-6 mb-8 border border-gray-700">
          <h2 className="text-2xl font-semibold mb-4 text-white">Leaderboard</h2>
          {sortedPlayers.length === 0 ? (
            <p className="text-gray-400">No players yet.</p>
          ) : (
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="text-left py-2 px-4 text-gray-300">Rank</th>
                  <th className="text-left py-2 px-4 text-gray-300">Player</th>
                  <th className="text-center py-2 px-4 text-gray-300">Points</th>
                  <th className="text-center py-2 px-4 text-gray-300">Wins</th>
                  <th className="text-center py-2 px-4 text-gray-300">Losses</th>
                  <th className="text-center py-2 px-4 text-gray-300">Win Rate</th>
                </tr>
              </thead>
              <tbody>
                {sortedPlayers.map((player, index) => {
                  const totalGames = player.wins + player.losses;
                  const winRate = totalGames > 0 
                    ? ((player.wins / totalGames) * 100).toFixed(1) 
                    : "0.0";
                  
                  return (
                    <tr key={player.id} className="border-b border-gray-700 hover:bg-gray-700">
                      <td className="py-3 px-4 font-bold text-gray-400">#{index + 1}</td>
                      <td className="py-3 px-4">
                        <div className="font-medium text-white">{player.name}</div>
                        {player.email && (
                          <div className="text-sm text-gray-400">{player.email}</div>
                        )}
                      </td>
                      <td className="text-center py-3 px-4 font-bold text-blue-400">
                        {player.points}
                      </td>
                      <td className="text-center py-3 px-4 text-green-400">{player.wins}</td>
                      <td className="text-center py-3 px-4 text-red-400">{player.losses}</td>
                      <td className="text-center py-3 px-4 text-gray-300">{winRate}%</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>

        {/* Record Match - Only for logged-in users */}
        {user && (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6 mb-8 border border-gray-700">
          <h2 className="text-2xl font-semibold mb-4 text-white">Record Match</h2>
          
          {!user.player_id ? (
            <div className="p-4 bg-yellow-900/30 border border-yellow-700 rounded-lg text-yellow-200">
              <p>Your account is not linked to a player. Please contact an administrator to link your account.</p>
            </div>
          ) : !showMatchForm ? (
            <div>
              <button
                onClick={() => setShowMatchForm(true)}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium transition-colors disabled:bg-gray-600 disabled:cursor-not-allowed"
                disabled={players.length < 2}
              >
                {players.length < 2 ? "Need at least 2 players" : "Record New Match"}
              </button>
            </div>
          ) : (
            <form onSubmit={handleCreateMatch} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-300">You (Home)</label>
                <div className="px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg">
                  {players.find(p => p.id === user.player_id)?.name || "Unknown Player"}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-300">Opponent (Away)</label>
                <select
                  value={awayId}
                  onChange={(e) => setAwayId(Number(e.target.value))}
                  className="w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  required
                >
                  <option value="">Select opponent...</option>
                  {players
                    .filter(p => p.id !== user.player_id)
                    .map((p) => (
                      <option key={p.id} value={p.id}>{p.name}</option>
                    ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 text-gray-300">Games (best of {gameScores.length})</label>
                {gameScores.map((game, index) => (
                  <div key={index} className="flex gap-4 mb-2 items-center">
                    <span className="text-sm text-gray-400 w-16">Game {index + 1}:</span>
                    <input
                      type="number"
                      min="0"
                      placeholder="You"
                      value={game.home}
                      onChange={(e) => updateGame(index, "home", Number(e.target.value))}
                      className="w-20 px-3 py-1 bg-gray-700 border border-gray-600 text-white rounded focus:outline-none focus:ring-2 focus:ring-green-500"
                      required
                    />
                    <span className="text-gray-400">-</span>
                    <input
                      type="number"
                      min="0"
                      placeholder="Opponent"
                      value={game.away}
                      onChange={(e) => updateGame(index, "away", Number(e.target.value))}
                      className="w-20 px-3 py-1 bg-gray-700 border border-gray-600 text-white rounded focus:outline-none focus:ring-2 focus:ring-green-500"
                      required
                    />
                  </div>
                ))}
                <button
                  type="button"
                  onClick={addGame}
                  className="text-sm text-blue-400 hover:text-blue-300 hover:underline"
                >
                  + Add another game
                </button>
              </div>

              <div className="flex gap-4">
                <button
                  type="submit"
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium transition-colors"
                >
                  Save Match
                </button>
                <button
                  type="button"
                  onClick={() => setShowMatchForm(false)}
                  className="px-6 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 font-medium transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}
        </div>
        )}

        {/* Recent Matches */}
        <div className="bg-gray-800 rounded-lg shadow-xl p-6 border border-gray-700">
          <h2 className="text-2xl font-semibold mb-4 text-white">Recent Matches</h2>
          {matches.length === 0 ? (
            <p className="text-gray-400">No matches recorded yet.</p>
          ) : (
            <div className="space-y-3">
              {matches.slice(0, 10).map((match) => {
                const homePlayer = players.find((p) => p.id === match.home_id);
                const awayPlayer = players.find((p) => p.id === match.away_id);
                const homeWins = match.games.filter(g => g.home > g.away).length;
                const awayWins = match.games.length - homeWins;
                const winner = homeWins > awayWins ? homePlayer : awayPlayer;
                
                return (
                  <div key={match.id} className="border-l-4 border-blue-500 pl-4 py-2 bg-gray-750 rounded-r">
                    <div className="flex justify-between items-center">
                      <div className="text-gray-200">
                        <span className={homeWins > awayWins ? "font-bold text-white" : ""}>
                          {homePlayer?.name || "Unknown"}
                        </span>
                        {" vs "}
                        <span className={awayWins > homeWins ? "font-bold text-white" : ""}>
                          {awayPlayer?.name || "Unknown"}
                        </span>
                      </div>
                      <div className="text-sm text-gray-400">
                        {homeWins}-{awayWins} • {winner?.name} wins
                      </div>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {new Date(match.played_at).toLocaleString()}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}