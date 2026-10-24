import Link from "next/link";
import { Navbar } from "@/components/Navbar";

export default function HomePage() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-4xl px-4 py-20 text-center">
        <p className="mb-2 text-sm uppercase tracking-widest text-discord-blurple">
          All-in-one Discord bot
        </p>
        <h1 className="mb-6 text-4xl font-bold tracking-tight md:text-5xl">
          Slash commands. Moderation. Dashboard.
        </h1>
        <p className="mx-auto mb-10 max-w-2xl text-lg text-gray-400">
          Host the Python bot on bot-hosting.net, manage welcome messages, mod
          logs, and stats from this Next.js dashboard on Vercel.
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          <Link
            href="/login"
            className="rounded-lg bg-discord-blurple px-6 py-3 font-semibold text-white shadow-lg shadow-indigo-900/40 hover:bg-indigo-500"
          >
            Open dashboard
          </Link>
          <a
            href="https://discord.com/developers/applications"
            target="_blank"
            rel="noreferrer"
            className="rounded-lg border border-white/20 px-6 py-3 font-semibold text-gray-200 hover:bg-white/5"
          >
            Developer portal
          </a>
        </div>
        <ul className="mx-auto mt-16 grid max-w-2xl gap-4 text-left text-gray-300 md:grid-cols-3">
          {[
            ["Slash commands", "Ping, help, mod tools, polls, embeds"],
            ["Lavalink music", "Play, queue, vinyl-style live dashboard"],
            ["MongoDB sync", "Settings and player state across bot and API"],
          ].map(([title, desc]) => (
            <li
              key={title}
              className="rounded-xl border border-white/10 bg-discord-panel p-4"
            >
              <h2 className="font-semibold text-white">{title}</h2>
              <p className="mt-1 text-sm text-gray-400">{desc}</p>
            </li>
          ))}
        </ul>
      </main>
    </div>
  );
}
