"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { exchangeDiscordCode } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

function CallbackInner() {
  const params = useSearchParams();
  const router = useRouter();
  const { setSession } = useAuth();
  const [message, setMessage] = useState("Completing login…");

  useEffect(() => {
    const code = params.get("code");
    const err = params.get("error");
    if (err) {
      setMessage("Discord authorization was denied.");
      return;
    }
    if (!code) {
      setMessage("Missing authorization code.");
      return;
    }
    exchangeDiscordCode(code)
      .then((data) => {
        setSession({
          token: data.access_token,
          user: data.user,
          guilds: data.guilds,
        });
        router.replace("/dashboard");
      })
      .catch(() => setMessage("Login failed. Check API redirect URI."));
  }, [params, router, setSession]);

  return (
    <div className="flex min-h-screen items-center justify-center text-gray-300">
      {message}
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center">
          Loading…
        </div>
      }
    >
      <CallbackInner />
    </Suspense>
  );
}
