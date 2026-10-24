"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { userAvatarUrl } from "@/lib/api";

export function Navbar() {
  const { session, logout } = useAuth();

  return (
    <header className="border-b border-white/10 bg-discord-dark/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href="/" className="text-lg font-semibold text-white">
          AIO Bot
        </Link>
        <nav className="flex items-center gap-4 text-sm">
          {session ? (
            <>
              <Link href="/dashboard" className="text-gray-300 hover:text-white">
                Dashboard
              </Link>
              <div className="flex items-center gap-2">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={userAvatarUrl(session.user.id, session.user.avatar, 32)}
                  alt=""
                  className="h-8 w-8 rounded-full"
                />
                <span className="text-gray-300">{session.user.username}</span>
              </div>
              <button
                type="button"
                onClick={logout}
                className="rounded-md bg-discord-panel px-3 py-1.5 text-gray-200 hover:bg-white/10"
              >
                Log out
              </button>
            </>
          ) : (
            <Link
              href="/login"
              className="rounded-md bg-discord-blurple px-4 py-2 font-medium text-white hover:bg-indigo-500"
            >
              Login with Discord
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
