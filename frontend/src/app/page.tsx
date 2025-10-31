"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { 
  getPlayers, 
  createMatch, 
  getMatches,
  register,
  login,
  logout,
  getCurrentUser,
  getAuthToken,
  setCurrentUser as saveCurrentUser,
  type Player, 
  type Match,
  type MatchInput,
  type RegisterRequest,
  type LoginRequest
} from "@/lib/api";

export default function Home() {
  const router = useRouter();
  
  // State for data
  const [players, setPlayers] = useState<Player[]>([]);
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Auth state
  const [currentUser, setCurrentUser] = useState<Player | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  
  // Auth form state
  const [authName, setAuthName] = useState("");
  const [authEmail, setAuthEmail] = useState("");

  // Match form state
  const [showMatchForm, setShowMatchForm] = useState(false);
  const [homeId, setHomeId] = useState<number | "">("");
  const [awayId, setAwayId] = useState<number | "">("");
  const [gameScores, setGameScores] = useState<Array<{ home: number; away: number }>>([
    { home: 0, away: 0 }
  ]);

  // Load data on mount
  useEffect(() => {
    checkAuth();
    loadData();
  }, []);

  function checkAuth() {
    const token = getAuthToken();
    const user = getCurrentUser();
    
    if (user && token) {
      setCurrentUser(user);
    }
  }

  async function loadData() {
    try {
      const [playersData, matchesData] = await Promise.all([
        getPlayers(),
        getMatches()
      ]);
      setPlayers(playersData);
      setMatches(matchesData);
      
      // Update current user's data if they're logged in
      if (currentUser) {
        const updatedUser = playersData.find(p => p.id === currentUser.id);
        if (updatedUser) {
          setCurrentUser(updatedUser);
          saveCurrentUser(updatedUser); // Also save to localStorage
        }
      }
    } catch (error) {
      console.error("Failed to load data:", error);
    } finally {
      setLoading(false);
    }
  }

  async function handleAuth(e: React.FormEvent) {
    e.preventDefault();
    
    try {
      if (authMode === "register") {
        const data: RegisterRequest = {
          name: authName,
          email: authEmail
        };
        const response = await register(data);
        setCurrentUser(response.player);
      } else {
        const data: LoginRequest = {
          name: authName,
          email: authEmail
        };
        const response = await login(data);
        setCurrentUser(response.player);
      }
      
      // Reset form and close modal
      setAuthName("");
      setAuthEmail("");
      setShowAuthModal(false);
      loadData(); // Refresh data
    } catch (error: any) {
      alert(error.message || "Authentication failed");
    }
  }

  function handleLogout() {
    logout();
    setCurrentUser(null);
    setShowMatchForm(false);
  }

  async function handleCreateMatch(e: React.FormEvent) {
    e.preventDefault();
    if (!currentUser) {
      alert("You must be logged in to create a match");
      return;
    }
    if (awayId === "") {
      alert("Please select your opponent");
      return;
    }

    try {
      const matchInput: MatchInput = {
        played_at: new Date().toISOString(),
        home_id: Number(homeId),
        away_id: Number(awayId),
        games: gameScores
      };
      await createMatch(matchInput);
      
      // Reset form
      setHomeId("");
      setAwayId("");
      setGameScores([{ home: 0, away: 0 }]);
      setShowMatchForm(false);
      loadData(); // Refresh
    } catch (error: any) {
      alert("Failed to create match: " + error.message);
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

  // Get current week start date (Sunday)
  function getCurrentWeekStart(): Date {
    const today = new Date();
    const daysSinceSunday = (today.getDay() + 7) % 7; // 0 for Sunday, 1 for Monday, etc.
    const weekStart = new Date(today);
    weekStart.setDate(today.getDate() - daysSinceSunday);
    weekStart.setHours(0, 0, 0, 0);
    return weekStart;
  }

  function formatWeekStart(): string {
    const weekStart = getCurrentWeekStart();
    const options: Intl.DateTimeFormatOptions = { 
      month: "short", 
      day: "numeric", 
      year: "numeric" 
    };
    return weekStart.toLocaleDateString("en-US", options);
  }

  if (loading) {
    return (
      <main className="min-h-screen p-6 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-screen">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500 mb-4"></div>
              <p className="text-slate-400 text-lg">Loading...</p>
            </div>
          </div>
        </div>
      </main>
    );
  }

  // Sort players by points (descending)
  const sortedPlayers = [...players].sort((a, b) => b.points - a.points);

  return (
    <main className="min-h-screen p-6 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <div className="max-w-7xl mx-auto">
        {/* Header with Auth */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 mb-2">
              Hanszen Ping Pong League
            </h1>
            <p className="text-slate-500 text-sm font-medium tracking-wide">
              Compete • Track • Dominate
            </p>
          </div>
          <div>
            {currentUser ? (
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <p className="text-slate-400 text-xs uppercase tracking-wider mb-1">Welcome back</p>
                  <p className="font-bold text-white text-lg">{currentUser.name}</p>
                </div>
                <button
                  onClick={handleLogout}
                  className="px-5 py-2.5 bg-gradient-to-r from-red-600 to-red-700 text-white rounded-xl hover:from-red-700 hover:to-red-800 font-semibold transition-all duration-200 shadow-lg shadow-red-900/50 hover:shadow-red-900/70 hover:scale-105"
                >
                  Logout
                </button>
              </div>
            ) : (
              <button
                onClick={() => setShowAuthModal(true)}
                className="px-6 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-xl hover:from-cyan-700 hover:to-blue-700 font-semibold transition-all duration-200 shadow-lg shadow-cyan-900/50 hover:shadow-cyan-900/70 hover:scale-105"
              >
                Login / Register
              </button>
            )}
          </div>
        </div>

        {/* Week Info Banner */}
        <div className="relative mb-8 overflow-hidden rounded-2xl bg-gradient-to-r from-violet-900/40 via-purple-900/40 to-fuchsia-900/40 backdrop-blur-sm border border-purple-500/30 shadow-2xl shadow-purple-900/50">
          <div className="absolute inset-0 bg-gradient-to-r from-violet-600/10 to-fuchsia-600/10"></div>
          <div className="relative p-6 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="bg-gradient-to-br from-purple-500 to-fuchsia-600 p-3 rounded-xl shadow-lg">
                <span className="text-3xl">📅</span>
              </div>
              <div>
                <p className="text-white font-bold text-xl mb-1">Current Week: {formatWeekStart()}</p>
                <p className="text-purple-200/80 text-sm">Leaderboard resets every Sunday at midnight</p>
              </div>
            </div>
            <button
              onClick={() => router.push("/archives")}
              className="px-5 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-xl font-semibold transition-all duration-200 border border-white/20 hover:border-white/30 backdrop-blur-sm hover:scale-105"
            >
              📚 View Archives
            </button>
          </div>
        </div>

        {/* Auth Modal */}
        {showAuthModal && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-gradient-to-br from-slate-900 to-slate-950 rounded-2xl p-8 max-w-md w-full border border-slate-700/50 shadow-2xl shadow-cyan-900/20">
              <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 mb-6">
                {authMode === "login" ? "Welcome Back" : "Join the League"}
              </h2>
              
              <form onSubmit={handleAuth} className="space-y-5">
                <div>
                  <label className="block text-sm font-semibold mb-2 text-slate-300 uppercase tracking-wide">Name</label>
                  <input
                    type="text"
                    value={authName}
                    onChange={(e) => setAuthName(e.target.value)}
                    className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all duration-200"
                    placeholder="Enter your name"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-semibold mb-2 text-slate-300 uppercase tracking-wide">Email</label>
                  <input
                    type="email"
                    value={authEmail}
                    onChange={(e) => setAuthEmail(e.target.value)}
                    className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all duration-200"
                    placeholder="Enter your email"
                    required
                  />
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    type="submit"
                    className="flex-1 px-6 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-xl hover:from-cyan-700 hover:to-blue-700 font-semibold transition-all duration-200 shadow-lg shadow-cyan-900/50 hover:scale-105"
                  >
                    {authMode === "login" ? "Login" : "Register"}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowAuthModal(false)}
                    className="flex-1 px-6 py-3 bg-slate-800 text-slate-300 rounded-xl hover:bg-slate-700 font-semibold transition-all duration-200 border border-slate-700 hover:border-slate-600"
                  >
                    Cancel
                  </button>
                </div>
              </form>

              <div className="mt-6 text-center">
                <button
                  onClick={() => setAuthMode(authMode === "login" ? "register" : "login")}
                  className="text-cyan-400 hover:text-cyan-300 text-sm font-medium transition-colors duration-200"
                >
                  {authMode === "login" 
                    ? "Need an account? Register here" 
                    : "Already have an account? Login here"}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Leaderboard Table - Always visible */}
        <div className="bg-gradient-to-br from-slate-900/90 to-slate-950/90 rounded-2xl shadow-2xl p-8 mb-8 border border-slate-700/50 backdrop-blur-sm">
          <div className="flex justify-between items-center mb-6">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <div className="bg-gradient-to-br from-yellow-500 to-orange-600 p-2 rounded-lg shadow-lg">
                  <span className="text-2xl">🏆</span>
                </div>
                <h2 className="text-3xl font-bold text-white">
                  This Week&apos;s Leaderboard
                </h2>
              </div>
              <p className="text-sm text-slate-400 ml-14">
                Week starting {formatWeekStart()}
              </p>
            </div>
            <button
              onClick={() => router.push("/archives")}
              className="px-5 py-2.5 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl hover:from-purple-700 hover:to-pink-700 font-semibold transition-all duration-200 text-sm shadow-lg shadow-purple-900/50 hover:scale-105"
            >
              📚 View Past Weeks
            </button>
          </div>
          {sortedPlayers.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-slate-500 text-lg">No players yet. Be the first to join!</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700/50">
                    <th className="text-left py-4 px-4 text-slate-400 font-semibold uppercase tracking-wider text-xs">Rank</th>
                    <th className="text-left py-4 px-4 text-slate-400 font-semibold uppercase tracking-wider text-xs">Player</th>
                    <th className="text-center py-4 px-4 text-slate-400 font-semibold uppercase tracking-wider text-xs">Points</th>
                    <th className="text-center py-4 px-4 text-slate-400 font-semibold uppercase tracking-wider text-xs">Wins</th>
                    <th className="text-center py-4 px-4 text-slate-400 font-semibold uppercase tracking-wider text-xs">Losses</th>
                    <th className="text-center py-4 px-4 text-slate-400 font-semibold uppercase tracking-wider text-xs">Win Rate</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedPlayers.map((player, index) => {
                    const totalGames = player.wins + player.losses;
                    const winRate = totalGames > 0 
                      ? ((player.wins / totalGames) * 100).toFixed(1) 
                      : "0.0";
                    
                    return (
                      <tr key={player.id} className="border-b border-slate-800/50 hover:bg-slate-800/40 transition-colors duration-150">
                        <td className="py-4 px-4">
                          <div className={`inline-flex items-center justify-center w-10 h-10 rounded-lg font-bold ${
                            index === 0 ? 'bg-gradient-to-br from-yellow-500 to-orange-500 text-white shadow-lg' :
                            index === 1 ? 'bg-gradient-to-br from-slate-400 to-slate-500 text-white shadow-lg' :
                            index === 2 ? 'bg-gradient-to-br from-orange-700 to-orange-800 text-white shadow-lg' :
                            'bg-slate-800 text-slate-400'
                          }`}>
                            #{index + 1}
                          </div>
                        </td>
                        <td className="py-4 px-4">
                          <div className="font-semibold text-white text-lg">{player.name}</div>
                        </td>
                        <td className="text-center py-4 px-4">
                          <div className="inline-block px-4 py-2 bg-gradient-to-r from-cyan-900/50 to-blue-900/50 rounded-lg border border-cyan-700/50">
                            <span className="font-bold text-cyan-300 text-lg">{player.points}</span>
                          </div>
                        </td>
                        <td className="text-center py-4 px-4">
                          <span className="font-semibold text-emerald-400 text-lg">{player.wins}</span>
                        </td>
                        <td className="text-center py-4 px-4">
                          <span className="font-semibold text-rose-400 text-lg">{player.losses}</span>
                        </td>
                        <td className="text-center py-4 px-4">
                          <span className="font-medium text-slate-300 text-lg">{winRate}%</span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Record Match - Only visible when logged in */}
        {currentUser && (
          <div className="bg-gray-800 rounded-lg shadow-xl p-6 mb-8 border border-gray-700">
            <h2 className="text-2xl font-semibold mb-4 text-white">Record Match</h2>
            
            {!showMatchForm ? (
              <button
                onClick={() => {
                  setShowMatchForm(true);
                  setHomeId(currentUser.id); // Automatically set Player 1 to current user
                }}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium transition-colors disabled:bg-gray-600 disabled:cursor-not-allowed"
                disabled={players.length < 2}
              >
                {players.length < 2 ? "Need at least 2 players" : "Record New Match"}
              </button>
            ) : (
              <form onSubmit={handleCreateMatch} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-300">Player 1 (You)</label>
                    <div className="w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg">
                      {currentUser.name}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-300">Opponent</label>
                    <select
                      value={awayId}
                      onChange={(e) => setAwayId(Number(e.target.value))}
                      className="w-full px-4 py-2 bg-gray-700 border border-gray-600 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                      required
                    >
                      <option value="">Select opponent...</option>
                      {players.filter((p) => p.id !== currentUser.id).map((p) => (
                        <option key={p.id} value={p.id}>{p.name}</option>
                      ))}
                    </select>
                  </div>
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
                        placeholder="Opp"
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
                    onClick={() => {
                      setShowMatchForm(false);
                      setHomeId("");
                      setAwayId("");
                      setGameScores([{ home: 0, away: 0 }]);
                    }}
                    className="px-6 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 font-medium transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            )}
          </div>
        )}

        {/* Info message when not logged in */}
        {!currentUser && (
          <div className="bg-blue-900 bg-opacity-30 border border-blue-700 rounded-lg p-4 mb-8">
            <p className="text-blue-300 text-center">
              🔒 Login or register to record matches
            </p>
          </div>
        )}

        {/* Recent Matches - Always visible */}
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
