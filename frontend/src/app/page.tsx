"use client";
import { useEffect, useState } from "react";
import { getHealth } from "@/lib/api";

export default function Home() {
  const [status, setStatus] = useState("checking…");
  useEffect(() => {
    getHealth()
      .then(d => setStatus(d.ok ? "✅ Connected" : "❌ Down"))
      .catch(() => setStatus("❌ Error"));
  }, []);

  return (
    <main className="p-6">
      <h1 className="text-2xl font-bold">Ping Pong Leaderboard</h1>
      <p className="mt-4">API Status: {status}</p>
    </main>
  );
}