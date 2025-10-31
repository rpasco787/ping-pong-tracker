"use client";
import { type Player } from "@/lib/api";

interface LeaderboardTableProps {
  players: Player[];
  weekStart: string;
}

function calculateWinRate(wins: number, losses: number): string {
  const totalGames = wins + losses;
  return totalGames > 0 ? ((wins / totalGames) * 100).toFixed(1) : "0.0";
}

function getRankBadgeClass(index: number): string {
  if (index === 0) return 'bg-gradient-to-br from-yellow-500 to-orange-500 text-white shadow-lg';
  if (index === 1) return 'bg-gradient-to-br from-slate-400 to-slate-500 text-white shadow-lg';
  if (index === 2) return 'bg-gradient-to-br from-orange-700 to-orange-800 text-white shadow-lg';
  return 'bg-slate-800 text-slate-400';
}

export default function LeaderboardTable({ players, weekStart }: LeaderboardTableProps) {
  // Sort players by points (descending)
  const sortedPlayers = [...players].sort((a, b) => b.points - a.points);

  return (
    <div className="bg-gradient-to-br from-slate-900/90 to-slate-950/90 rounded-2xl shadow-2xl p-8 mb-8 border border-slate-700/50 backdrop-blur-sm">
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="bg-gradient-to-br from-yellow-500 to-orange-600 p-2 rounded-lg shadow-lg">
            <span className="text-2xl">🏆</span>
          </div>
          <h2 className="text-3xl font-bold text-white">
            This Week&apos;s Leaderboard
          </h2>
        </div>
        <p className="text-sm text-slate-400 ml-14">
          Week starting {weekStart} • Resets every Sunday at midnight
        </p>
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
                const winRate = calculateWinRate(player.wins, player.losses);
                
                return (
                  <tr key={player.id} className="border-b border-slate-800/50 hover:bg-slate-800/40 transition-colors duration-150">
                    <td className="py-4 px-4">
                      <div className={`inline-flex items-center justify-center w-10 h-10 rounded-lg font-bold ${getRankBadgeClass(index)}`}>
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
  );
}

