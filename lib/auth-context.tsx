"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import type { Guild } from "./api";
import { fetchMe } from "./api";

const STORAGE_KEY = "aio_bot_session";

type Session = {
  token: string;
  user: { id: string; username: string; avatar: string | null };
  guilds: Guild[];
};

type AuthContextValue = {
  session: Session | null;
  loading: boolean;
  setSession: (s: Session | null) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSessionState] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  const setSession = useCallback((s: Session | null) => {
    setSessionState(s);
    if (s) localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
    else localStorage.removeItem(STORAGE_KEY);
  }, []);

  const logout = useCallback(() => setSession(null), [setSession]);

  useEffect(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      setLoading(false);
      return;
    }
    try {
      const parsed = JSON.parse(raw) as Session;
      fetchMe(parsed.token)
        .then((me) => {
          setSessionState({
            token: parsed.token,
            user: {
              id: me.id,
              username: me.username,
              avatar: me.avatar,
            },
            guilds: me.guilds,
          });
        })
        .catch(() => localStorage.removeItem(STORAGE_KEY))
        .finally(() => setLoading(false));
    } catch {
      localStorage.removeItem(STORAGE_KEY);
      setLoading(false);
    }
  }, []);

  const value = useMemo(
    () => ({ session, loading, setSession, logout }),
    [session, loading, setSession, logout]
  );

  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
