"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Navbar } from "@/components/Navbar";
import { fetchStats, guildIconUrl } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

export default function DashboardPage() {
  const { session, loading } = useAuth();
  const router = useRouter();
  const [stats, setStats] = useState<{
    commands_total: number;
    commands_today: number;
    guilds_configured: number;
    lavalink_connected?: boolean;
  } | null>(null);

  useEffect(() => {
    if (!loading && !session) router.replace("/login");
  }, [loading, session, router]);

  useEffect(() => {
    if (!session) return;
    fetchStats(session.token)
      .then(setStats)
      .catch(() => setStats(null));
  }, [session]);

  if (loading || !session) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        Loading…
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-6xl px-4 py-10">
        <h1 className="mb-2 text-2xl font-bold">Your servers</h1>
        <p className="mb-8 text-gray-400">
          Select a server to configure welcome messages, mod logs, and more.
        </p>

        {stats && (
          <div className="mb-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              ["Commands (all time)", stats.commands_total],
              ["Commands today", stats.commands_today],
              ["Guilds in DB", stats.guilds_configured],
              [
                "Lavalink",
                stats.lavalink_connected ? "Online" : "Offline",
              ],
            ].map(([label, value]) => (
              <div
                key={label as string}
                className="rounded-xl border border-white/10 bg-discord-panel p-4"
              >
                <p className="text-sm text-gray-400">{label}</p>
                <p className="text-2xl font-semibold text-white">{value}</p>
              </div>
            ))}
          </div>
        )}

        {session.guilds.length === 0 ? (
          <p className="rounded-lg border border-amber-500/30 bg-amber-500/10 p-4 text-amber-100">
            No manageable servers found. Invite the bot and ensure you have
            Manage Server permission.
          </p>
        ) : (
          <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {session.guilds.map((g) => {
              const icon = guildIconUrl(g);
              return (
                <li key={g.id}>
                  <Link
                    href={`/dashboard/${g.id}`}
                    className="flex items-center gap-4 rounded-xl border border-white/10 bg-discord-panel p-4 transition hover:border-discord-blurple/50 hover:bg-white/5"
                  >
                    {icon ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img src={icon} alt="" className="h-12 w-12 rounded-full" />
                    ) : (
                      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-discord-blurple text-lg font-bold">
                        {g.name.charAt(0)}
                      </div>
                    )}
                    <div>
                      <p className="font-semibold text-white">{g.name}</p>
                      <p className="text-xs text-gray-400">
                        {g.owner ? "Owner" : "Administrator"}
                      </p>
                    </div>
                  </Link>
                </li>
              );
            })}
          </ul>
        )}
      </main>
    </div>
  );
}
