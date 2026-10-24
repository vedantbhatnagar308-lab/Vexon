"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { GuildSubnav } from "@/components/GuildSubnav";
import { Navbar } from "@/components/Navbar";
import {
  fetchGuildSettings,
  fetchModLogs,
  type GuildSettings,
  type ModLog,
  updateGuildSettings,
} from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

export default function GuildSettingsPage() {
  const params = useParams();
  const guildId = params.guildId as string;
  const { session, loading } = useAuth();
  const router = useRouter();
  const guild = session?.guilds.find((g) => g.id === guildId);

  const [settings, setSettings] = useState<GuildSettings | null>(null);
  const [logs, setLogs] = useState<ModLog[]>([]);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!session) return;
    const [s, l] = await Promise.all([
      fetchGuildSettings(session.token, guildId),
      fetchModLogs(session.token, guildId),
    ]);
    setSettings(s);
    setLogs(l);
  }, [session, guildId]);

  useEffect(() => {
    if (!loading && !session) router.replace("/login");
  }, [loading, session, router]);

  useEffect(() => {
    load().catch(() => setError("Failed to load guild data"));
  }, [load]);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!session || !settings) return;
    setSaving(true);
    setSaved(false);
    setError(null);
    try {
      const updated = await updateGuildSettings(session.token, guildId, {
        welcome_enabled: settings.welcome_enabled,
        welcome_channel_id: settings.welcome_channel_id,
        welcome_message: settings.welcome_message,
        mod_log_channel_id: settings.mod_log_channel_id,
        auto_mod_spam: settings.auto_mod_spam,
      });
      setSettings(updated);
      setSaved(true);
    } catch {
      setError("Save failed");
    } finally {
      setSaving(false);
    }
  }

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
      <main className="mx-auto max-w-3xl px-4 py-10">
        <Link href="/dashboard" className="text-sm text-gray-400 hover:text-white">
          ← All servers
        </Link>
        <h1 className="mt-4 text-2xl font-bold">{guild.name}</h1>
        <p className="mb-4 text-gray-400">Guild ID: {guildId}</p>
        <GuildSubnav guildId={guildId} />

        {error && (
          <p className="mb-4 rounded-md bg-red-500/20 px-4 py-2 text-red-200">
            {error}
          </p>
        )}

        {settings && (
          <form
            onSubmit={handleSave}
            className="space-y-8 rounded-xl border border-white/10 bg-discord-panel p-6"
          >
            <section>
              <h2 className="mb-4 text-lg font-semibold">Welcome messages</h2>
              <label className="mb-4 flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={settings.welcome_enabled}
                  onChange={(e) =>
                    setSettings({ ...settings, welcome_enabled: e.target.checked })
                  }
                  className="h-4 w-4 rounded"
                />
                <span>Enable welcome messages</span>
              </label>
              <label className="mb-2 block text-sm text-gray-400">
                Welcome channel ID
              </label>
              <input
                type="text"
                value={settings.welcome_channel_id ?? ""}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    welcome_channel_id: e.target.value || null,
                  })
                }
                placeholder="Discord channel snowflake ID"
                className="mb-4 w-full rounded-lg border border-white/10 bg-discord-darker px-3 py-2"
              />
              <label className="mb-2 block text-sm text-gray-400">
                Message ({`{user}`}, {`{server}`})
              </label>
              <textarea
                value={settings.welcome_message}
                onChange={(e) =>
                  setSettings({ ...settings, welcome_message: e.target.value })
                }
                rows={3}
                className="w-full rounded-lg border border-white/10 bg-discord-darker px-3 py-2"
              />
            </section>

            <section>
              <h2 className="mb-4 text-lg font-semibold">Moderation</h2>
              <label className="mb-2 block text-sm text-gray-400">
                Mod log channel ID
              </label>
              <input
                type="text"
                value={settings.mod_log_channel_id ?? ""}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    mod_log_channel_id: e.target.value || null,
                  })
                }
                className="mb-4 w-full rounded-lg border border-white/10 bg-discord-darker px-3 py-2"
              />
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={settings.auto_mod_spam}
                  onChange={(e) =>
                    setSettings({ ...settings, auto_mod_spam: e.target.checked })
                  }
                  className="h-4 w-4 rounded"
                />
                <span>Auto-mod spam (placeholder — extend in bot)</span>
              </label>
            </section>

            <div className="flex items-center gap-4">
              <button
                type="submit"
                disabled={saving}
                className="rounded-lg bg-discord-blurple px-6 py-2 font-semibold text-white hover:bg-indigo-500 disabled:opacity-50"
              >
                {saving ? "Saving…" : "Save changes"}
              </button>
              {saved && (
                <span className="text-sm text-green-400">Saved — bot picks up on next action.</span>
              )}
            </div>
          </form>
        )}

        <section className="mt-10">
          <h2 className="mb-4 text-lg font-semibold">Recent mod logs</h2>
          {logs.length === 0 ? (
            <p className="text-gray-400">No moderation entries yet.</p>
          ) : (
            <ul className="divide-y divide-white/10 rounded-xl border border-white/10 bg-discord-panel">
              {logs.map((log) => (
                <li key={log._id} className="px-4 py-3 text-sm">
                  <span className="font-medium uppercase text-discord-blurple">
                    {log.action}
                  </span>
                  <span className="text-gray-400">
                    {" "}
                    — mod {log.moderator_id} → user {log.target_id}
                    {log.reason ? ` (${log.reason})` : ""}
                  </span>
                  <p className="text-xs text-gray-500">{log.at}</p>
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>
    </div>
  );
}
