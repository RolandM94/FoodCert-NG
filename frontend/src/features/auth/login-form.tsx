"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { LogIn } from "lucide-react";
import { login } from "@/lib/api/auth";
import { getApiErrorMessage } from "@/lib/api/client";
import { ROLE_HOME } from "@/lib/navigation/portal-nav";
import type { UserRole } from "@/types/auth";

export function LoginForm() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const tokens = await login(username, password);
      window.localStorage.setItem("foodcert_access_token", tokens.access);
      window.localStorage.setItem("foodcert_refresh_token", tokens.refresh);
      window.localStorage.setItem("foodcert_user_role", tokens.user.role);
      router.push(ROLE_HOME[tokens.user.role as UserRole]);
    } catch (err) {
      setError(getApiErrorMessage(err, "Unable to sign in. Check your credentials and try again."));
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="grid gap-4 rounded-lg border border-neutral-200 bg-white p-5 shadow-sm" onSubmit={submit}>
      <label className="grid gap-1 text-sm font-semibold text-neutral-700">
        Username
        <input
          className="h-11 rounded border border-neutral-200 bg-neutral-50 px-3 outline-none ring-brand-600/20 focus:border-brand-600 focus:ring-2"
          onChange={(event) => setUsername(event.target.value)}
          required
          value={username}
        />
      </label>
      <label className="grid gap-1 text-sm font-semibold text-neutral-700">
        Password
        <input
          className="h-11 rounded border border-neutral-200 bg-neutral-50 px-3 outline-none ring-brand-600/20 focus:border-brand-600 focus:ring-2"
          onChange={(event) => setPassword(event.target.value)}
          required
          type="password"
          value={password}
        />
      </label>
      {error ? <p className="rounded bg-danger-50 p-3 text-sm font-semibold text-danger-700">{error}</p> : null}
      <button className="inline-flex h-11 items-center justify-center gap-2 rounded bg-brand-600 px-4 text-sm font-bold text-white disabled:opacity-60" disabled={loading} type="submit">
        <LogIn aria-hidden="true" size={18} />
        {loading ? "Signing in..." : "Sign in"}
      </button>
    </form>
  );
}
