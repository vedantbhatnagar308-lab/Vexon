"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export function GuildSubnav({ guildId }: { guildId: string }) {
  const path = usePathname();
  const base = `/dashboard/${guildId}`;
  const tabs = [
    { href: base, label: "Settings", exact: true },
    { href: `${base}/music`, label: "Music", exact: false },
  ];

  return (
    <nav className="mb-8 flex gap-2 rounded-xl border border-white/10 bg-discord-panel p-1">
      {tabs.map((tab) => {
        const active = tab.exact
          ? path === tab.href
          : path.startsWith(tab.href);
        return (
          <Link
            key={tab.href}
            href={tab.href}
            className={`flex-1 rounded-lg px-4 py-2 text-center text-sm font-medium transition ${
              active
                ? "bg-gradient-to-r from-emerald-600/80 to-discord-blurple text-white shadow-lg"
                : "text-gray-400 hover:bg-white/5 hover:text-white"
            }`}
          >
            {tab.label}
          </Link>
        );
      })}
    </nav>
  );
}
