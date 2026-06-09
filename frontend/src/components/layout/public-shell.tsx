"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { LogOut, ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";
import { logout } from "@/lib/api/auth";

export function PublicShell({
  title,
  description,
  children
}: {
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  const router = useRouter();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);

  useEffect(() => {
    const token = window.localStorage.getItem("foodcert_access_token");
    setIsLoggedIn(!!token);
  }, []);

  function handleLogout() {
    setLoggingOut(true);
    const refresh = window.localStorage.getItem("foodcert_refresh_token") || "";
    window.localStorage.removeItem("foodcert_access_token");
    window.localStorage.removeItem("foodcert_refresh_token");
    window.localStorage.removeItem("foodcert_user_role");
    window.localStorage.removeItem("foodcert_user_meta");
    logout(refresh).catch(() => {});
    router.push("/login");
  }

  return (
    <main className="min-h-screen bg-neutral-50 text-neutral-900">
      <header className="border-b border-brand-100 bg-white">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <Link className="flex items-center gap-3" href="/">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-600 text-white">
              <ShieldCheck aria-hidden="true" size={22} />
            </div>
            <div>
              <p className="text-sm font-bold text-neutral-900">FoodCert NG</p>
              <p className="text-xs text-neutral-500">National certification registry</p>
            </div>
          </Link>
          <div className="flex items-center gap-2">
            <Link className="rounded px-3 py-2 text-sm font-semibold text-neutral-700 hover:bg-neutral-50" href="/facilities/approved">
              Facilities
            </Link>
            {isLoggedIn ? (
              <button
                className="inline-flex items-center gap-2 rounded bg-brand-600 px-3 py-2 text-sm font-bold text-white hover:bg-brand-700 disabled:opacity-60"
                disabled={loggingOut}
                onClick={handleLogout}
                type="button"
              >
                <LogOut aria-hidden="true" size={16} />
                Sign out
              </button>
            ) : (
              <Link className="rounded bg-brand-600 px-3 py-2 text-sm font-bold text-white" href="/login">
                Sign in
              </Link>
            )}
          </div>
        </div>
      </header>
      <section className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold tracking-tight text-neutral-900 sm:text-3xl">{title}</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-neutral-600">{description}</p>
        </div>
        {children}
      </section>
    </main>
  );
}
