"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { GuildSubnav } from "@/components/GuildSubnav";
import { MusicPanel } from "@/components/MusicPanel";
import { Navbar } from "@/components/Navbar";
import {
  fetchGuildMusic,
  fetchLavalinkInfo,
  fetchStats,
  type GuildMusic,
  type LavalinkInfo,
} from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

const emptyMusic = (guildId: string): GuildMusic => ({
  guild_id: guildId,
  connected: false,
  channel_id: null,
  paused: false,
  volume: 100,
  position_ms: 0,
  current: null,
  queue: [],
  updated_at: null,
});

export default function GuildMusicPage() {
  const params = useParams();
  const guildId = params.guildId as string;
  const { session, loading } = useAuth();
  const router = useRouter();
  const guild = session?.guilds.find((g) => g.id === guildId);

  const [music, setMusic] = useState<GuildMusic | null>(null);
  const [lavalink, setLavalink] = useState<LavalinkInfo | null>(null);
  const [lavalinkConnected, setLavalinkConnected] = useState(false);

  const load = useCallback(async () => {
    if (!session) return;
    const [m, l, stats] = await Promise.all([
      fetchGuildMusic(session.token, guildId),
      fetchLavalinkInfo(session.token).catch(() => null),
      fetchStats(session.token).catch(() => null),
    ]);
    setMusic(m);
    setLavalink(l);
    setLavalinkConnected(Boolean(stats?.lavalink_connected));
  }, [session, guildId]);

  useEffect(() => {
    if (!loading && !session) router.replace("/login");
  }, [loading, session, router]);

  useEffect(() => {
    load().catch(() => setMusic(emptyMusic(guildId)));
  }, [load, guildId]);

  useEffect(() => {
    if (!session) return;
    const id = setInterval(() => {
      fetchGuildMusic(session.token, guildId)
        .then(setMusic)
        .catch(() => {});
    }, 5000);
    return () => clearInterval(id);
  }, [session, guildId]);

  if (loading || !session) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        Loading…
      </div>
    );
  }

  if (!guild) {
    return (
      <div className="min-h-screen">
        <Navbar />
        <main className="mx-auto max-w-lg px-4 py-20 text-center">
          <p className="text-gray-400">You cannot manage this server.</p>
          <Link href="/dashboard" className="mt-4 inline-block text-discord-blurple">
            Back
          </Link>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-4xl px-4 py-10">
        <Link href="/dashboard" className="text-sm text-gray-400 hover:text-white">
          ← All servers
        </Link>
        <h1 className="mt-4 text-2xl font-bold">{guild.name}</h1>
        <p className="mb-6 text-gray-400">Live Lavalink player</p>
        <GuildSubnav guildId={guildId} />
        {music && (
          <MusicPanel
            music={music}
            lavalink={lavalink}
            lavalinkConnected={lavalinkConnected}
          />
        )}
      </main>
    </div>
  );
}
