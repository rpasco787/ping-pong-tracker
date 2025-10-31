"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getArchivedWeeks, getWeeklyLeaderboard, type WeekInfo, type WeeklyArchive } from "@/lib/api";
import { formatDateRange } from "@/lib/utils";
import WeekArchiveCard from "@/components/WeekArchiveCard";

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

  if (loading) {
    return (
      <main className="min-h-screen p-6 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-screen">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500 mb-4"></div>
              <p className="text-slate-400 text-lg">Loading archived weeks...</p>
            </div>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen p-6 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="bg-gradient-to-br from-purple-500 to-pink-600 p-3 rounded-xl shadow-lg">
                <span className="text-3xl">📚</span>
              </div>
              <h1 className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-500 to-fuchsia-600">
                Weekly Archives
              </h1>
            </div>
            <p className="text-slate-500 text-sm font-medium tracking-wide ml-16">
              Relive past victories and legendary matches
            </p>
          </div>
          <button
            onClick={() => router.push("/")}
            className="px-6 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-xl hover:from-cyan-700 hover:to-blue-700 font-semibold transition-all duration-200 shadow-lg shadow-cyan-900/50 hover:scale-105"
          >
            ← Back to Current Week
          </button>
        </div>

        {/* Info message */}
        <div className="relative mb-8 overflow-hidden rounded-2xl bg-gradient-to-r from-indigo-900/30 via-purple-900/30 to-pink-900/30 backdrop-blur-sm border border-indigo-700/30 shadow-lg">
          <div className="absolute inset-0 bg-gradient-to-r from-indigo-600/5 to-pink-600/5"></div>
          <div className="relative p-5">
            <p className="text-indigo-200 font-medium">
              💡 View past weekly leaderboards and see who won each week. Click on a week to expand and view the full rankings.
            </p>
          </div>
        </div>

        {/* Archived weeks list */}
        {weeks.length === 0 ? (
          <div className="bg-gradient-to-br from-slate-900/90 to-slate-950/90 rounded-2xl shadow-2xl p-12 border border-slate-700/50 backdrop-blur-sm text-center">
            <div className="text-6xl mb-4">📦</div>
            <p className="text-slate-400 text-xl font-medium mb-2">No archived weeks yet.</p>
            <p className="text-slate-500 text-sm">
              Weekly leaderboards will appear here after the first Sunday reset.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {weeks.map((week) => (
              <WeekArchiveCard
                key={week.week_start}
                week={week}
                dateRange={formatDateRange(week.week_start, week.week_end)}
                isExpanded={expandedWeek === week.week_start}
                isLoading={loadingWeek === week.week_start}
                leaderboard={leaderboards[week.week_start]}
                onToggle={() => toggleWeek(week.week_start)}
              />
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
