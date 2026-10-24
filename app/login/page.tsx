"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Navbar } from "@/components/Navbar";
import { getDiscordAuthUrl } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

export default function LoginPage() {
  const { session, loading } = useAuth();
  const router = useRouter();
  const [authUrl, setAuthUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && session) router.replace("/dashboard");
  }, [loading, session, router]);

  useEffect(() => {
    getDiscordAuthUrl()
      .then(setAuthUrl)
      .catch(() => setError("Could not reach API. Is FastAPI running?"));
  }, []);

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto flex max-w-md flex-col items-center px-4 py-24">
        <h1 className="mb-2 text-2xl font-bold">Sign in</h1>
        <p className="mb-8 text-center text-gray-400">
          Authorize with Discord to manage servers where you have Manage Server
          permission.
        </p>
        {error && (
          <p className="mb-4 rounded-md bg-red-500/20 px-4 py-2 text-sm text-red-200">
            {error}
          </p>
        )}
        <a
          href={authUrl ?? "#"}
          aria-disabled={!authUrl}
          className={`flex w-full items-center justify-center gap-2 rounded-lg px-6 py-3 font-semibold text-white ${
            authUrl
              ? "bg-discord-blurple hover:bg-indigo-500"
              : "cursor-not-allowed bg-gray-600"
          }`}
        >
          Continue with Discord
        </a>
      </main>
    </div>
  );
}
