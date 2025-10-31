"use client";
import { type Match, type Player } from "@/lib/api";

interface RecentMatchesProps {
  matches: Match[];
  players: Player[];
}

function findPlayer(players: Player[], id: number): Player | undefined {
  return players.find((p) => p.id === id);
}

function getMatchWinner(match: Match, homePlayer: Player | undefined, awayPlayer: Player | undefined) {
  const homeWins = match.games.filter(g => g.home > g.away).length;
  const awayWins = match.games.length - homeWins;
  return { homeWins, awayWins, winner: homeWins > awayWins ? homePlayer : awayPlayer };
}

export default function RecentMatches({ matches, players }: RecentMatchesProps) {
  return (
    <div className="bg-gradient-to-br from-slate-900/90 to-slate-950/90 rounded-2xl shadow-2xl p-8 border border-slate-700/50 backdrop-blur-sm">
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-gradient-to-br from-indigo-500 to-purple-600 p-2 rounded-lg shadow-lg">
          <span className="text-2xl">📋</span>
        </div>
        <h2 className="text-3xl font-bold text-white">Recent Matches</h2>
      </div>
      
      {matches.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-slate-500 text-lg">No matches recorded yet. Start your first match!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {matches.slice(0, 10).map((match) => {
            const homePlayer = findPlayer(players, match.home_id);
            const awayPlayer = findPlayer(players, match.away_id);
            const { homeWins, awayWins, winner } = getMatchWinner(match, homePlayer, awayPlayer);
            
            return (
              <div key={match.id} className="relative overflow-hidden rounded-xl bg-slate-800/40 border border-slate-700/50 hover:border-slate-600/50 transition-all duration-200 hover:shadow-lg hover:shadow-slate-900/50">
                <div className={`absolute left-0 top-0 bottom-0 w-1 ${homeWins > awayWins ? 'bg-gradient-to-b from-cyan-500 to-blue-600' : 'bg-gradient-to-b from-purple-500 to-pink-600'}`}></div>
                <div className="p-4 pl-5">
                  <div className="flex justify-between items-center mb-2">
                    <div className="text-slate-200 text-lg">
                      <span className={homeWins > awayWins ? "font-bold text-white" : "text-slate-300"}>
                        {homePlayer?.name || "Unknown"}
                      </span>
                      <span className="text-slate-500 mx-2">vs</span>
                      <span className={awayWins > homeWins ? "font-bold text-white" : "text-slate-300"}>
                        {awayPlayer?.name || "Unknown"}
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="px-3 py-1 bg-slate-900/50 rounded-lg border border-slate-700/50">
                        <span className="text-sm font-bold text-slate-300">
                          {homeWins}-{awayWins}
                        </span>
                      </div>
                      <span className="text-sm text-emerald-400 font-semibold">
                        🏆 {winner?.name}
                      </span>
                    </div>
                  </div>
                  <div className="text-xs text-slate-500 font-medium">
                    {new Date(match.played_at).toLocaleString()}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

