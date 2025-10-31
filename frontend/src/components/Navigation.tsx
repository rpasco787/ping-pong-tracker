"use client";
import { useRouter } from "next/navigation";
import { type Player } from "@/lib/api";

interface NavigationProps {
  currentUser: Player | null;
  onLoginClick: () => void;
  onLogout: () => void;
}

export default function Navigation({ currentUser, onLoginClick, onLogout }: NavigationProps) {
  const router = useRouter();

  return (
    <nav className="sticky top-0 z-50 bg-slate-950/95 backdrop-blur-md border-b border-slate-800/50 shadow-2xl">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex justify-between items-center">
          {/* Logo/Title */}
          <div className="flex items-center gap-6">
            <div>
              <h1 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600">
                Hanszen Ping Pong League
              </h1>
            </div>
          </div>

          {/* Right side: Archives + Auth */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => router.push("/archives")}
              className="px-4 py-2 bg-slate-800/80 hover:bg-slate-700/80 text-slate-200 rounded-lg font-medium transition-all duration-200 border border-slate-700/50 hover:border-slate-600/50"
            >
              Archives
            </button>
            
            {currentUser ? (
              <div className="flex items-center gap-3">
                <div className="text-right px-3">
                  <p className="text-slate-500 text-xs tracking-wider">Welcome back</p>
                  <p className="font-bold text-white">{currentUser.name}</p>
                </div>
                <button
                  onClick={onLogout}
                  className="px-4 py-2 bg-gradient-to-r from-red-600 to-red-700 text-white rounded-lg hover:from-red-700 hover:to-red-800 font-semibold transition-all duration-200 shadow-lg shadow-red-900/50 hover:scale-105"
                >
                  Logout
                </button>
              </div>
            ) : (
              <button
                onClick={onLoginClick}
                className="px-5 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-lg hover:from-cyan-700 hover:to-blue-700 font-semibold transition-all duration-200 shadow-lg shadow-cyan-900/50 hover:scale-105"
              >
                Login / Register
              </button>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

