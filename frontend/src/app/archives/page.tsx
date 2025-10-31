"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getArchivedWeeks, getWeeklyLeaderboard, type WeekInfo, type WeeklyArchive } from "@/lib/api";

export default function ArchivesPage() {
  const router = useRouter();
  const [weeks, setWeeks] = useState<WeekInfo[]>([]);
  const [expandedWeek, setExpandedWeek] = useState<string | null>(null);
  const [leaderboards, setLeaderboards] = useState<Record<string, WeeklyArchive[]>>({});
  const [loading, setLoading] = useState(true);
  const [loadingWeek, setLoadingWeek] = useState<string | null>(null);

  useEffect(() => {
    loadArchivedWeeks();
  }, []);

  async function loadArchivedWeeks() {
    try {
      const data = await getArchivedWeeks();
      setWeeks(data);
    } catch (error) {
      console.error("Failed to load archived weeks:", error);
    } finally {
      setLoading(false);
    }
  }

  async function toggleWeek(weekStart: string) {
    // If already expanded, collapse it
    if (expandedWeek === weekStart) {
      setExpandedWeek(null);
      return;
    }

    // If we already have the data, just expand
    if (leaderboards[weekStart]) {
      setExpandedWeek(weekStart);
      return;
    }

    // Otherwise, fetch the data
    setLoadingWeek(weekStart);
    try {
      const data = await getWeeklyLeaderboard(weekStart);
      setLeaderboards((prev) => ({ ...prev, [weekStart]: data }));
      setExpandedWeek(weekStart);
    } catch (error) {
      console.error("Failed to load weekly leaderboard:", error);
      alert("Failed to load leaderboard for this week");
    } finally {
      setLoadingWeek(null);
    }
  }

  function formatDateRange(weekStart: string, weekEnd: string): string {
    const start = new Date(weekStart);
    const end = new Date(weekEnd);
    
    const options: Intl.DateTimeFormatOptions = { month: "short", day: "numeric", year: "numeric" };
    const startStr = start.toLocaleDateString("en-US", options);
    const endStr = end.toLocaleDateString("en-US", options);
    
    return `${startStr} - ${endStr}`;
  }

  if (loading) {
    return (
      <main className="min-h-screen p-6 bg-gray-900">
        <div className="max-w-6xl mx-auto">
          <p className="text-gray-300">Loading archived weeks...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen p-6 bg-gray-900">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold text-white">📚 Weekly Archives</h1>
          <button
            onClick={() => router.push("/")}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors"
          >
            ← Back to Current Week
          </button>
        </div>

        {/* Info message */}
        <div className="bg-blue-900 bg-opacity-30 border border-blue-700 rounded-lg p-4 mb-6">
          <p className="text-blue-300 text-sm">
            View past weekly leaderboards and see who won each week. Click on a week to expand and view the full rankings.
          </p>
        </div>

        {/* Archived weeks list */}
        {weeks.length === 0 ? (
          <div className="bg-gray-800 rounded-lg shadow-xl p-8 border border-gray-700 text-center">
            <p className="text-gray-400 text-lg">No archived weeks yet.</p>
            <p className="text-gray-500 text-sm mt-2">
              Weekly leaderboards will appear here after the first Sunday reset.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {weeks.map((week) => {
              const isExpanded = expandedWeek === week.week_start;
              const isLoading = loadingWeek === week.week_start;
              const leaderboard = leaderboards[week.week_start];

              return (
                <div
                  key={week.week_start}
                  className="bg-gray-800 rounded-lg shadow-xl border border-gray-700 overflow-hidden"
                >
                  {/* Week header - clickable */}
                  <button
                    onClick={() => toggleWeek(week.week_start)}
                    className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-750 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <div className="text-3xl">
                        {isExpanded ? "📂" : "📁"}
                      </div>
                      <div className="text-left">
                        <h2 className="text-xl font-semibold text-white">
                          {formatDateRange(week.week_start, week.week_end)}
                        </h2>
                        <p className="text-sm text-gray-400 mt-1">
                          🏆 Winner: <span className="text-yellow-400 font-medium">{week.winner_name}</span>
                          {" • "}
                          {week.total_players} {week.total_players === 1 ? "player" : "players"}
                        </p>
                      </div>
                    </div>
                    <div className="text-gray-400">
                      {isLoading ? (
                        <span className="text-sm">Loading...</span>
                      ) : (
                        <span className="text-2xl">{isExpanded ? "▼" : "▶"}</span>
                      )}
                    </div>
                  </button>

                  {/* Expanded leaderboard */}
                  {isExpanded && leaderboard && (
                    <div className="border-t border-gray-700 p-6">
                      <h3 className="text-lg font-semibold text-white mb-4">Weekly Leaderboard</h3>
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
                          {leaderboard.map((player) => {
                            const totalGames = player.wins + player.losses;
                            const winRate = totalGames > 0
                              ? ((player.wins / totalGames) * 100).toFixed(1)
                              : "0.0";
                            const isWinner = player.player_id === week.winner_id;

                            return (
                              <tr
                                key={player.id}
                                className={`border-b border-gray-700 ${
                                  isWinner ? "bg-yellow-900 bg-opacity-20" : "hover:bg-gray-700"
                                }`}
                              >
                                <td className="py-3 px-4">
                                  <div className="flex items-center gap-2">
                                    <span className="font-bold text-gray-400">#{player.rank}</span>
                                    {isWinner && <span className="text-yellow-400">👑</span>}
                                  </div>
                                </td>
                                <td className="py-3 px-4">
                                  <div className="font-medium text-white">{player.player_name}</div>
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
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </main>
  );
}

