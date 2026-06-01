"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  LogIn,
  ShieldCheck,
  UsersRound,
  Building2,
  Landmark,
  Stethoscope,
  SearchCheck,
  FlaskConical,
  ArrowRight,
  AlertCircle,
} from "lucide-react";
import { login } from "@/lib/api/auth";
import { ROLE_HOME } from "@/lib/navigation/portal-nav";
import type { UserRole } from "@/types/auth";

const roleHints = [
  { label: "Food Handler", icon: UsersRound },
  { label: "Employer", icon: Building2 },
  { label: "Medical Facility", icon: Building2 },
  { label: "State MOH", icon: Landmark },
  { label: "Federal MOH", icon: ShieldCheck },
  { label: "Doctor", icon: Stethoscope },
  { label: "Lab Staff", icon: FlaskConical },
  { label: "Inspector", icon: SearchCheck },
];

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const token = window.localStorage.getItem("foodcert_access_token");
    const role = window.localStorage.getItem("foodcert_user_role");
    if (token && role) {
      const home = ROLE_HOME[role as UserRole];
      if (home) router.replace(home);
    }
  }, [router]);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const tokens = await login(username, password);
      window.localStorage.setItem("foodcert_access_token", tokens.access);
      window.localStorage.setItem("foodcert_refresh_token", tokens.refresh);
      window.localStorage.setItem("foodcert_user_role", tokens.user.role);

      // store org/unit meta for scope badge
      const meta: Record<string, string> = {};
      if (tokens.user.organization_name) meta.organization_name = tokens.user.organization_name;
      if (tokens.user.state_name) meta.state_name = tokens.user.state_name;
      window.localStorage.setItem("foodcert_user_meta", JSON.stringify(meta));

      router.push(ROLE_HOME[tokens.user.role as UserRole]);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unable to sign in. Check your credentials."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#f7faf8] flex items-center justify-center p-4">
      <div className="w-full max-w-5xl grid gap-0 rounded-2xl border border-slate-200 bg-white shadow-lg overflow-hidden lg:grid-cols-[1fr_1fr]">
        {/* Left panel — role cards */}
        <div className="hidden bg-slate-50 p-8 lg:flex lg:flex-col lg:justify-center">
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-green text-white">
                <ShieldCheck size={22} />
              </div>
              <div>
                <p className="text-sm font-bold text-slate-950">FoodCert NG</p>
                <p className="text-xs text-slate-500">National certification platform</p>
              </div>
            </div>
            <h1 className="text-xl font-bold tracking-tight text-slate-950">Welcome back</h1>
            <p className="mt-2 text-sm text-slate-600">
              Sign in to access your role-specific portal. The platform routes you automatically based on your account type.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {roleHints.map((hint) => {
              const Icon = hint.icon;
              return (
                <div
                  key={hint.label}
                  className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white p-3"
                >
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-emerald-50 text-brand-deep">
                    <Icon size={16} />
                  </div>
                  <span className="text-xs font-semibold text-slate-700">{hint.label}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right panel — sign in form */}
        <div className="flex flex-col justify-center p-8 sm:p-10">
          <div className="mb-6 lg:hidden">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-green text-white">
                <ShieldCheck size={22} />
              </div>
              <div>
                <p className="text-sm font-bold text-slate-950">FoodCert NG</p>
                <p className="text-xs text-slate-500">National certification platform</p>
              </div>
            </div>
            <h1 className="text-xl font-bold tracking-tight text-slate-950">Sign in</h1>
            <p className="mt-1 text-sm text-slate-600">Access your role-specific portal.</p>
          </div>

          <div className="hidden lg:block mb-6">
            <h2 className="text-lg font-bold text-slate-950">Sign in</h2>
            <p className="mt-1 text-sm text-slate-600">Enter your credentials to continue.</p>
          </div>

          <form className="grid gap-4" onSubmit={submit}>
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
              Username or email
              <input
                className="h-11 rounded-lg border border-slate-200 bg-slate-50 px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2"
                onChange={(e) => setUsername(e.target.value)}
                required
                value={username}
                autoComplete="username"
                autoFocus
              />
            </label>
            <label className="grid gap-1.5 text-sm font-semibold text-slate-700">
              Password
              <input
                className="h-11 rounded-lg border border-slate-200 bg-slate-50 px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2"
                onChange={(e) => setPassword(e.target.value)}
                required
                type="password"
                value={password}
                autoComplete="current-password"
              />
            </label>

            {error && (
              <div className="flex items-start gap-2 rounded-lg bg-rose-50 p-3 text-sm font-semibold text-rose-800">
                <AlertCircle size={16} className="mt-0.5 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <button
              className="mt-2 inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-brand-green text-sm font-bold text-white hover:bg-brand-deep disabled:opacity-60 transition-colors"
              disabled={loading}
              type="submit"
            >
              <LogIn size={18} />
              {loading ? "Signing in..." : "Sign in"}
              {!loading && <ArrowRight size={16} />}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-500">
            Don&apos;t have an account?{" "}
            <Link href="/register" className="font-semibold text-brand-deep hover:underline">
              Register as a Food Handler
            </Link>
          </p>

          <p className="mt-3 text-center text-xs text-slate-400">
            Employers, facilities, and government users are invited by an organization administrator.
          </p>
        </div>
      </div>
    </main>
  );
}
