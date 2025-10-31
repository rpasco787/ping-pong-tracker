"use client";
import { type WeekInfo, type WeeklyArchive } from "@/lib/api";
import { calculateWinRate } from "@/lib/utils";

interface WeekArchiveCardProps {
  week: WeekInfo;
  dateRange: string;
  isExpanded: boolean;
  isLoading: boolean;
  leaderboard: WeeklyArchive[] | undefined;
  onToggle: () => void;
}

function getRankBadgeClass(rank: number): string {
  if (rank === 1) return 'bg-gradient-to-br from-yellow-500 to-orange-500 text-white shadow-lg';
  if (rank === 2) return 'bg-gradient-to-br from-slate-400 to-slate-500 text-white shadow-lg';
  if (rank === 3) return 'bg-gradient-to-br from-orange-700 to-orange-800 text-white shadow-lg';
  return 'bg-slate-800 text-slate-400';
}

export default function WeekArchiveCard({ 
  week, 
  dateRange, 
  isExpanded, 
  isLoading, 
  leaderboard, 
  onToggle 
}: WeekArchiveCardProps) {
  return (
    <div className="bg-gradient-to-br from-slate-900/90 to-slate-950/90 rounded-2xl shadow-2xl border border-slate-700/50 backdrop-blur-sm overflow-hidden transition-all duration-300 hover:border-slate-600/50">
      {/* Week header - clickable */}
      <button
        onClick={onToggle}
        className="w-full px-6 py-5 flex items-center justify-between hover:bg-slate-800/40 transition-all duration-200"
      >
        <div className="flex items-center gap-5">
          <div className="bg-gradient-to-br from-amber-500 to-orange-600 p-3 rounded-xl shadow-lg transition-transform duration-200">
            <span className="text-3xl">{isExpanded ? "📂" : "📁"}</span>
          </div>
          <div className="text-left">
            <h2 className="text-2xl font-bold text-white mb-1">
              {dateRange}
            </h2>
            <div className="flex items-center gap-3 text-sm">
              <div className="flex items-center gap-1.5">
                <span className="text-yellow-400">🏆</span>
                <span className="text-slate-400">Winner:</span>
                <span className="text-yellow-300 font-semibold">{week.winner_name}</span>
              </div>
              <span className="text-slate-600">•</span>
              <span className="text-slate-400">
                {week.total_players} {week.total_players === 1 ? "player" : "players"}
              </span>
            </div>
          </div>
        </div>
        <div className="text-slate-400">
          {isLoading ? (
            <div className="flex items-center gap-2">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-cyan-500"></div>
              <span className="text-sm">Loading...</span>
            </div>
          ) : (
            <span className="text-2xl transition-transform duration-200">{isExpanded ? "▼" : "▶"}</span>
          )}
        </div>
      </button>

      {/* Expanded leaderboard */}
      {isExpanded && leaderboard && (
        <div className="border-t border-slate-700/50 p-6 bg-slate-950/30">
          <div className="flex items-center gap-3 mb-5">
            <div className="bg-gradient-to-br from-cyan-500 to-blue-600 p-2 rounded-lg shadow-lg">
              <span className="text-xl">📊</span>
            </div>
            <h3 className="text-xl font-bold text-white">Weekly Leaderboard</h3>
          </div>
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
                {leaderboard.map((player) => {
                  const winRate = calculateWinRate(player.wins, player.losses);
                  const isWinner = player.player_id === week.winner_id;

                  return (
                    <tr
                      key={player.id}
                      className={`border-b border-slate-800/50 transition-colors duration-150 ${
                        isWinner ? "bg-gradient-to-r from-yellow-900/20 to-orange-900/20" : "hover:bg-slate-800/40"
                      }`}
                    >
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-2">
                          <div className={`inline-flex items-center justify-center w-10 h-10 rounded-lg font-bold ${getRankBadgeClass(player.rank)}`}>
                            #{player.rank}
                          </div>
                          {isWinner && <span className="text-yellow-400 text-xl">👑</span>}
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <div className="font-semibold text-white text-lg">{player.player_name}</div>
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
        </div>
      )}
    </div>
  );
}

