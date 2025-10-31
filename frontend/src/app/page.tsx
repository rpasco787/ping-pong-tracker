"use client";
import { useEffect, useState } from "react";
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
import { formatWeekStart } from "@/lib/utils";
import Navigation from "@/components/Navigation";
import AuthModal from "@/components/AuthModal";
import LeaderboardTable from "@/components/LeaderboardTable";
import MatchForm from "@/components/MatchForm";
import RecentMatches from "@/components/RecentMatches";

export default function Home() {
  // State for data
  const [players, setPlayers] = useState<Player[]>([]);
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Auth state
  const [currentUser, setCurrentUser] = useState<Player | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<"login" | "register">("login");

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
          saveCurrentUser(updatedUser);
        }
      }
    } catch (error) {
      console.error("Failed to load data:", error);
    } finally {
      setLoading(false);
    }
  }

  async function handleAuth(name: string, email: string, mode: "login" | "register") {
    try {
      if (mode === "register") {
        const data: RegisterRequest = { name, email };
        const response = await register(data);
        setCurrentUser(response.player);
      } else {
        const data: LoginRequest = { name, email };
        const response = await login(data);
        setCurrentUser(response.player);
      }
      
      setShowAuthModal(false);
      loadData();
    } catch (error: any) {
      alert(error.message || "Authentication failed");
    }
  }

  function handleLogout() {
    logout();
    setCurrentUser(null);
  }

  async function handleCreateMatch(matchInput: MatchInput) {
    if (!currentUser) {
      alert("You must be logged in to create a match");
      return;
    }

    try {
      await createMatch(matchInput);
      loadData();
    } catch (error: any) {
      alert("Failed to create match: " + error.message);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500 mb-4"></div>
            <p className="text-slate-400 text-lg">Loading...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <Navigation 
        currentUser={currentUser}
        onLoginClick={() => setShowAuthModal(true)}
        onLogout={handleLogout}
      />

      <main className="max-w-7xl mx-auto p-6">
        <AuthModal
          isOpen={showAuthModal}
          mode={authMode}
          onClose={() => setShowAuthModal(false)}
          onSubmit={handleAuth}
          onToggleMode={() => setAuthMode(authMode === "login" ? "register" : "login")}
        />

        <LeaderboardTable 
          players={players}
          weekStart={formatWeekStart()}
        />

        {currentUser && (
          <MatchForm
            currentUser={currentUser}
            players={players}
            onSubmit={handleCreateMatch}
          />
        )}

        {!currentUser && (
          <div className="relative mb-8 overflow-hidden rounded-2xl bg-gradient-to-r from-cyan-900/30 via-blue-900/30 to-indigo-900/30 backdrop-blur-sm border border-cyan-700/30 shadow-lg">
            <div className="absolute inset-0 bg-gradient-to-r from-cyan-600/5 to-blue-600/5"></div>
            <div className="relative p-5 flex items-center justify-center gap-3">
              <p className="text-cyan-300 font-medium text-lg">
                Login or register to record matches
              </p>
            </div>
          </div>
        )}

        <RecentMatches 
          matches={matches}
          players={players}
        />
      </main>
    </div>
  );
}
