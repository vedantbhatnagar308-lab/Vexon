const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type Guild = {
  id: string;
  name: string;
  icon: string | null;
  owner: boolean;
};

export type GuildSettings = {
  guild_id: string;
  welcome_enabled: boolean;
  welcome_channel_id: string | null;
  welcome_message: string;
  mod_log_channel_id: string | null;
  auto_mod_spam: boolean;
};

export type MusicTrack = {
  title: string;
  author: string;
  uri: string | null;
  artwork: string | null;
  length_ms: number;
};

export type GuildMusic = {
  guild_id: string;
  connected: boolean;
  channel_id: string | null;
  paused: boolean;
  volume: number;
  position_ms: number;
  current: MusicTrack | null;
  queue: MusicTrack[];
  updated_at: string | null;
};

export type LavalinkInfo = {
  label: string;
  host: string;
  port: number;
};

export type ModLog = {
  _id: string;
  action: string;
  moderator_id: number;
  target_id: number;
  reason: string | null;
  at: string;
};

function authHeaders(token: string): HeadersInit {
  return {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
}

export async function getDiscordAuthUrl(): Promise<string> {
  const res = await fetch(`${API_URL}/auth/discord/url`);
  const data = await res.json();
  return data.url as string;
}

export async function exchangeDiscordCode(code: string): Promise<{
  access_token: string;
  user: { id: string; username: string; avatar: string | null };
  guilds: Guild[];
}> {
  const res = await fetch(`${API_URL}/auth/discord/callback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code }),
  });
  if (!res.ok) throw new Error("Login failed");
  return res.json();
}

export async function fetchMe(token: string) {
  const res = await fetch(`${API_URL}/me`, { headers: authHeaders(token) });
  if (!res.ok) throw new Error("Session expired");
  return res.json();
}

export async function fetchStats(token: string) {
  const res = await fetch(`${API_URL}/stats`, { headers: authHeaders(token) });
  if (!res.ok) throw new Error("Failed to load stats");
  return res.json();
}

export async function fetchGuildSettings(
  token: string,
  guildId: string
): Promise<GuildSettings> {
  const res = await fetch(`${API_URL}/guilds/${guildId}/settings`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error("Failed to load settings");
  return res.json();
}

export async function updateGuildSettings(
  token: string,
  guildId: string,
  patch: Partial<GuildSettings>
): Promise<GuildSettings> {
  const res = await fetch(`${API_URL}/guilds/${guildId}/settings`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify(patch),
  });
  if (!res.ok) throw new Error("Failed to save settings");
  return res.json();
}

export async function fetchGuildMusic(
  token: string,
  guildId: string
): Promise<GuildMusic> {
  const res = await fetch(`${API_URL}/guilds/${guildId}/music`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error("Failed to load music state");
  return res.json();
}

export async function fetchLavalinkInfo(token: string): Promise<LavalinkInfo> {
  const res = await fetch(`${API_URL}/music/lavalink`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error("Failed to load Lavalink info");
  return res.json();
}

export function formatMs(ms: number): string {
  if (!ms || ms < 0) return "0:00";
  const s = Math.floor(ms / 1000);
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${m}:${r.toString().padStart(2, "0")}`;
}

export async function fetchModLogs(
  token: string,
  guildId: string
): Promise<ModLog[]> {
  const res = await fetch(`${API_URL}/guilds/${guildId}/mod-logs`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error("Failed to load mod logs");
  return res.json();
}

export function guildIconUrl(guild: Guild, size = 64): string | null {
  if (!guild.icon) return null;
  return `https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png?size=${size}`;
}

export function userAvatarUrl(
  userId: string,
  avatar: string | null,
  size = 64
): string {
  if (avatar)
    return `https://cdn.discordapp.com/avatars/${userId}/${avatar}.png?size=${size}`;
  const index = Number(BigInt(userId) >> BigInt(22)) % 6;
  return `https://cdn.discordapp.com/embed/avatars/${index}.png`;
}
