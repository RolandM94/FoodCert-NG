"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { LogOut, ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";
import { logout } from "@/lib/api/auth";
import { PORTAL_NAV } from "@/lib/navigation/portal-nav";
import { ROLE_LABELS } from "@/lib/permissions/roles";
import { NotificationBell } from "@/components/ui/notification-bell";
import { UnitScopeBadge } from "@/components/ui/unit-scope-badge";
import type { UserRole } from "@/types/auth";

function useAuthMeta() {
  const [meta, setMeta] = useState<{
    orgName?: string;
    unitName?: string;
    unitType?: string;
    stateName?: string;
  }>({});
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAuthChecked, setIsAuthChecked] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("foodcert_access_token");
    if (!token) {
      setIsLoggedIn(false);
      setIsAuthChecked(true);
      return;
    }
    setIsLoggedIn(true);
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      const userMeta = localStorage.getItem("foodcert_user_meta");
      const parsed = userMeta ? JSON.parse(userMeta) : {};
      setMeta({
        orgName: parsed.organization_name || parsed.org_name || payload.organization_name,
        unitName: parsed.unit_name || payload.unit_name,
        unitType: parsed.unit_type || payload.unit_type,
        stateName: parsed.state_name || payload.state_name,
      });
    } catch {
      // ignore parse errors
    }
    setIsAuthChecked(true);
  }, []);

  return { ...meta, isLoggedIn, isAuthChecked };
}

export function PortalShell({
  role,
  title,
  description,
  children
}: {
  role: UserRole;
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const nav = PORTAL_NAV[role];
  const { isLoggedIn, isAuthChecked, ...scopeMeta } = useAuthMeta();
  const [loggingOut, setLoggingOut] = useState(false);

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

  useEffect(() => {
    if (isAuthChecked && !isLoggedIn) {
      router.replace(`/login?next=${encodeURIComponent(pathname)}`);
    }
  }, [isAuthChecked, isLoggedIn, pathname, router]);

  const notificationHref = role === "employer" ? "/employer/notifications" : "/food-handler/notifications";

  const isNavActive = (href: string) => pathname === href || pathname.startsWith(`${href}/`);

  return (
    <main className="min-h-screen bg-neutral-50 text-neutral-900 lg:grid lg:grid-cols-[280px_minmax(0,1fr)]">
      <aside className="hidden border-r border-neutral-200 bg-white lg:sticky lg:top-0 lg:flex lg:h-screen lg:flex-col">
        <div className="border-b border-neutral-100 px-5 py-5">
          <Link href="/" className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-brand-600 text-white">
              <ShieldCheck aria-hidden="true" size={23} />
            </div>
            <div className="min-w-0">
              <p className="truncate text-sm font-bold text-neutral-900">FoodCert NG</p>
              <p className="truncate text-xs text-neutral-500">{ROLE_LABELS[role]}</p>
            </div>
          </Link>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
          {nav.map((item) => {
            const Icon = item.icon;
            const active = isNavActive(item.href);
            return (
              <Link
                key={item.href}
                className={`flex min-h-10 items-center gap-3 rounded-lg px-3 py-2 text-sm font-semibold transition-colors ${
                  active ? "bg-brand-50 text-brand-700" : "text-neutral-600 hover:bg-neutral-50 hover:text-neutral-950"
                }`}
                href={item.href}
              >
                <Icon aria-hidden="true" className="shrink-0" size={17} />
                <span className="min-w-0 truncate">{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </aside>

      <div className="min-w-0">
        <header className="sticky top-0 z-30 border-b border-neutral-200 bg-white/95 backdrop-blur">
          <div className="flex min-h-16 items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
            <div className="flex min-w-0 items-center gap-4">
              <Link href="/" className="flex items-center gap-3 lg:hidden">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-600 text-white">
                  <ShieldCheck aria-hidden="true" size={22} />
                </div>
                <div>
                  <p className="text-sm font-bold text-neutral-900">FoodCert NG</p>
                  <p className="text-xs text-neutral-500">{ROLE_LABELS[role]}</p>
                </div>
              </Link>
              <UnitScopeBadge
                orgName={scopeMeta.orgName}
                unitName={scopeMeta.unitName}
                unitType={scopeMeta.unitType}
                stateName={scopeMeta.stateName}
              />
            </div>
            <div className="flex shrink-0 items-center gap-2">
              <NotificationBell href={notificationHref} />
              {isLoggedIn ? (
                <button
                  className="inline-flex items-center gap-2 rounded border border-neutral-200 px-3 py-2 text-sm font-semibold text-neutral-700 hover:bg-neutral-50 disabled:opacity-60"
                  disabled={loggingOut}
                  onClick={handleLogout}
                  type="button"
                >
                  <LogOut aria-hidden="true" size={16} />
                  Sign out
                </button>
              ) : (
                <Link className="rounded border border-neutral-200 px-3 py-2 text-sm font-semibold text-neutral-700" href="/login">
                  Sign in
                </Link>
              )}
            </div>
          </div>
          <nav className="flex gap-1 overflow-x-auto border-t border-neutral-100 px-4 sm:px-6 lg:hidden">
            {nav.map((item) => {
              const Icon = item.icon;
              const active = isNavActive(item.href);
              return (
                <Link
                  key={item.href}
                  className={`flex shrink-0 items-center gap-2 border-b-2 px-3 py-3 text-sm font-medium ${
                    active ? "border-brand-600 text-brand-700" : "border-transparent text-neutral-500 hover:text-neutral-800"
                  }`}
                  href={item.href}
                >
                  <Icon aria-hidden="true" size={16} />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </header>

        <section className="w-full px-4 py-6 sm:px-6 lg:px-8 xl:px-10 2xl:px-12">
          <div className="mb-6">
            <p className="text-xs font-bold uppercase tracking-wide text-brand-700">{ROLE_LABELS[role]}</p>
            <h1 className="mt-2 text-2xl font-bold tracking-tight text-neutral-900 sm:text-3xl">{title}</h1>
            <p className="mt-2 max-w-4xl text-sm leading-6 text-neutral-600">{description}</p>
          </div>
          {children}
        </section>
      </div>
    </main>
  );
}
