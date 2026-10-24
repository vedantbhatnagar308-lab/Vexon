"use client";

import {
  formatMs,
  type GuildMusic,
  type LavalinkInfo,
  type MusicTrack,
} from "@/lib/api";

type Props = {
  music: GuildMusic;
  lavalink: LavalinkInfo | null;
  lavalinkConnected: boolean;
};

function Equalizer({ active }: { active: boolean }) {
  return (
    <div
      className={`equalizer ${active ? "equalizer--live" : ""}`}
      aria-hidden
    >
      {Array.from({ length: 12 }).map((_, i) => (
        <span key={i} style={{ animationDelay: `${i * 0.07}s` }} />
      ))}
    </div>
  );
}

function Vinyl({ spinning, artwork }: { spinning: boolean; artwork: string | null }) {
  return (
    <div className={`vinyl-wrap ${spinning ? "vinyl-wrap--spin" : ""}`}>
      <div className="vinyl-disc">
        <div className="vinyl-grooves" />
        <div className="vinyl-label">
          {artwork ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={artwork} alt="" className="h-full w-full object-cover" />
          ) : (
            <span className="text-xs text-white/60">AIO</span>
          )}
        </div>
      </div>
    </div>
  );
}

function Progress({ position, length }: { position: number; length: number }) {
  const pct = length > 0 ? Math.min(100, (position / length) * 100) : 0;
  return (
    <div className="mt-4">
      <div className="h-1.5 overflow-hidden rounded-full bg-white/10">
        <div
          className="h-full rounded-full bg-gradient-to-r from-emerald-400 to-discord-blurple transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="mt-1 flex justify-between text-xs text-gray-500">
        <span>{formatMs(position)}</span>
        <span>{formatMs(length)}</span>
      </div>
    </div>
  );
}

function QueueItem({ track, index }: { track: MusicTrack; index: number }) {
  return (
    <li className="flex items-center gap-3 rounded-lg border border-white/5 bg-black/20 px-3 py-2">
      <span className="w-6 text-center text-xs font-mono text-emerald-400">
        {index}
      </span>
      {track.artwork ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={track.artwork}
          alt=""
          className="h-10 w-10 rounded-md object-cover"
        />
      ) : (
        <div className="h-10 w-10 rounded-md bg-white/10" />
      )}
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-white">{track.title}</p>
        <p className="truncate text-xs text-gray-500">{track.author}</p>
      </div>
      <span className="text-xs text-gray-500">{formatMs(track.length_ms)}</span>
    </li>
  );
}

export function MusicPanel({ music, lavalink, lavalinkConnected }: Props) {
  const playing = music.connected && music.current && !music.paused;
  const current = music.current;

  return (
    <div className="space-y-6">
      <div className="music-hero relative overflow-hidden rounded-2xl border border-white/10 p-6 md:p-8">
        <div className="music-hero-glow pointer-events-none absolute inset-0" />
        <div className="relative grid gap-8 md:grid-cols-[auto_1fr] md:items-center">
          <Vinyl spinning={!!playing} artwork={current?.artwork ?? null} />
          <div>
            <div className="mb-2 flex flex-wrap items-center gap-2">
              <span
                className={`rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wide ${
                  playing
                    ? "bg-emerald-500/20 text-emerald-300"
                    : music.paused
                      ? "bg-amber-500/20 text-amber-200"
                      : "bg-white/10 text-gray-400"
                }`}
              >
                {playing ? "Live" : music.paused ? "Paused" : "Idle"}
              </span>
              {music.connected && (
                <span className="text-xs text-gray-500">
                  Voice · Vol {music.volume}%
                </span>
              )}
            </div>
            <h2 className="text-2xl font-bold text-white md:text-3xl">
              {current?.title ?? "Nothing playing"}
            </h2>
            <p className="mt-1 text-gray-400">
              {current?.author ?? "Use /play in Discord to start"}
            </p>
            {current && (
              <Progress
                position={music.position_ms}
                length={current.length_ms}
              />
            )}
            <Equalizer active={!!playing} />
          </div>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-white/10 bg-discord-panel p-4 md:col-span-1">
          <h3 className="text-sm font-semibold text-gray-300">Lavalink</h3>
          {lavalink ? (
            <>
              <p className="mt-2 text-lg font-medium text-white">
                {lavalink.label}
              </p>
              <p className="font-mono text-xs text-gray-500">
                {lavalink.host}:{lavalink.port}
              </p>
            </>
          ) : (
            <p className="mt-2 text-sm text-gray-500">—</p>
          )}
          <p
            className={`mt-3 inline-flex items-center gap-2 text-sm ${
              lavalinkConnected ? "text-emerald-400" : "text-red-400"
            }`}
          >
            <span
              className={`h-2 w-2 rounded-full ${
                lavalinkConnected ? "bg-emerald-400 pulse-dot" : "bg-red-400"
              }`}
            />
            {lavalinkConnected ? "Bot connected" : "Bot not linked to node"}
          </p>
        </div>
        <div className="rounded-xl border border-white/10 bg-discord-panel p-4 md:col-span-2">
          <h3 className="text-sm font-semibold text-gray-300">Controls</h3>
          <p className="mt-2 text-sm text-gray-400">
            Playback is controlled in Discord:{" "}
            <code className="rounded bg-black/30 px-1.5 py-0.5 text-emerald-300">
              /play
            </code>{" "}
            <code className="rounded bg-black/30 px-1.5 py-0.5 text-emerald-300">
              /pause
            </code>{" "}
            <code className="rounded bg-black/30 px-1.5 py-0.5 text-emerald-300">
              /skip
            </code>{" "}
            <code className="rounded bg-black/30 px-1.5 py-0.5 text-emerald-300">
              /queue
            </code>
          </p>
          {music.updated_at && (
            <p className="mt-2 text-xs text-gray-600">
              Updated {new Date(music.updated_at).toLocaleString()}
            </p>
          )}
        </div>
      </div>

      <section>
        <h3 className="mb-3 text-lg font-semibold">
          Up next{" "}
          <span className="text-sm font-normal text-gray-500">
            ({music.queue.length})
          </span>
        </h3>
        {music.queue.length === 0 ? (
          <p className="rounded-xl border border-dashed border-white/10 py-10 text-center text-gray-500">
            Queue is empty
          </p>
        ) : (
          <ul className="space-y-2">{music.queue.map((t, i) => (
              <QueueItem key={`${t.uri}-${i}`} track={t} index={i + 1} />
            ))}</ul>
        )}
      </section>
    </div>
  );
}
