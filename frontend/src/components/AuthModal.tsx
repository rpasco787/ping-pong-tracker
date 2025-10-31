"use client";
import { useState } from "react";

interface AuthModalProps {
  isOpen: boolean;
  mode: "login" | "register";
  onClose: () => void;
  onSubmit: (name: string, email: string, mode: "login" | "register") => Promise<void>;
  onToggleMode: () => void;
}

export default function AuthModal({ isOpen, mode, onClose, onSubmit, onToggleMode }: AuthModalProps) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit(name, email, mode);
    setName("");
    setEmail("");
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-gradient-to-br from-slate-900 to-slate-950 rounded-2xl p-8 max-w-md w-full border border-slate-700/50 shadow-2xl shadow-cyan-900/20">
        <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 mb-6">
          {mode === "login" ? "Welcome Back" : "Join the League"}
        </h2>
        
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-semibold mb-2 text-slate-300 uppercase tracking-wide">Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all duration-200"
              placeholder="Enter your name"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-semibold mb-2 text-slate-300 uppercase tracking-wide">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
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
              {mode === "login" ? "Login" : "Register"}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 bg-slate-800 text-slate-300 rounded-xl hover:bg-slate-700 font-semibold transition-all duration-200 border border-slate-700 hover:border-slate-600"
            >
              Cancel
            </button>
          </div>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={onToggleMode}
            className="text-cyan-400 hover:text-cyan-300 text-sm font-medium transition-colors duration-200"
          >
            {mode === "login" 
              ? "Need an account? Register here" 
              : "Already have an account? Login here"}
          </button>
        </div>
      </div>
    </div>
  );
}

