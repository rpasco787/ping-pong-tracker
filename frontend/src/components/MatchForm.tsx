"use client";
import { useState } from "react";
import { type Player, type MatchInput } from "@/lib/api";

interface MatchFormProps {
  currentUser: Player;
  players: Player[];
  onSubmit: (matchInput: MatchInput) => Promise<void>;
}

export default function MatchForm({ currentUser, players, onSubmit }: MatchFormProps) {
  const [showForm, setShowForm] = useState(false);
  const [awayId, setAwayId] = useState<number | "">("");
  const [gameScores, setGameScores] = useState<Array<{ home: number; away: number }>>([
    { home: 0, away: 0 }
  ]);

  const addGame = () => {
    setGameScores([...gameScores, { home: 0, away: 0 }]);
  };

  const updateGame = (index: number, field: "home" | "away", value: number) => {
    const updated = [...gameScores];
    updated[index][field] = value;
    setGameScores(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (awayId === "") {
      alert("Please select your opponent");
      return;
    }

    const matchInput: MatchInput = {
      played_at: new Date().toISOString(),
      home_id: currentUser.id,
      away_id: Number(awayId),
      games: gameScores
    };

    await onSubmit(matchInput);
    
    // Reset form
    setAwayId("");
    setGameScores([{ home: 0, away: 0 }]);
    setShowForm(false);
  };

  const handleCancel = () => {
    setShowForm(false);
    setAwayId("");
    setGameScores([{ home: 0, away: 0 }]);
  };

  return (
    <div className="bg-gradient-to-br from-slate-900/90 to-slate-950/90 rounded-2xl shadow-2xl p-8 mb-8 border border-slate-700/50 backdrop-blur-sm">
      <div className="flex items-center gap-3 mb-6">
        <h2 className="text-3xl font-bold text-white">Record Match</h2>
      </div>
      
      {!showForm ? (
        <button
          onClick={() => setShowForm(true)}
          className="px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 font-semibold transition-all duration-200 shadow-lg shadow-green-900/50 hover:scale-105 disabled:from-slate-700 disabled:to-slate-800 disabled:cursor-not-allowed disabled:shadow-none disabled:scale-100"
          disabled={players.length < 2}
        >
          {players.length < 2 ? "Need at least 2 players" : "Record New Match"}
        </button>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold mb-2 text-slate-300 uppercase tracking-wide">Player 1 (You)</label>
              <div className="w-full px-4 py-3 bg-gradient-to-r from-cyan-900/30 to-blue-900/30 border border-cyan-700/50 text-white rounded-xl font-medium">
                {currentUser.name}
              </div>
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2 text-slate-300 uppercase tracking-wide">Opponent</label>
              <select
                value={awayId}
                onChange={(e) => setAwayId(Number(e.target.value))}
                className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
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
            <label className="block text-sm font-semibold mb-3 text-slate-300 uppercase tracking-wide">Games (best of {gameScores.length})</label>
            <div className="space-y-3">
              {gameScores.map((game, index) => (
                <div key={index} className="flex gap-4 items-center bg-slate-800/30 p-3 rounded-xl border border-slate-700/50">
                  <span className="text-sm font-semibold text-slate-400 w-20">Game {index + 1}:</span>
                  <input
                    type="number"
                    min="0"
                    placeholder="You"
                    value={game.home}
                    onChange={(e) => updateGame(index, "home", Number(e.target.value))}
                    className="w-24 px-4 py-2 bg-slate-800 border border-slate-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200 text-center font-semibold"
                    required
                  />
                  <span className="text-slate-500 font-bold">-</span>
                  <input
                    type="number"
                    min="0"
                    placeholder="Opp"
                    value={game.away}
                    onChange={(e) => updateGame(index, "away", Number(e.target.value))}
                    className="w-24 px-4 py-2 bg-slate-800 border border-slate-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200 text-center font-semibold"
                    required
                  />
                </div>
              ))}
            </div>
            <button
              type="button"
              onClick={addGame}
              className="mt-3 text-sm text-cyan-400 hover:text-cyan-300 font-medium transition-colors duration-200"
            >
              + Add another game
            </button>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              className="flex-1 px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 font-semibold transition-all duration-200 shadow-lg shadow-green-900/50 hover:scale-105"
            >
              💾 Save Match
            </button>
            <button
              type="button"
              onClick={handleCancel}
              className="px-6 py-3 bg-slate-800 text-slate-300 rounded-xl hover:bg-slate-700 font-semibold transition-all duration-200 border border-slate-700 hover:border-slate-600"
            >
              Cancel
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

