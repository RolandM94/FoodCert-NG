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

  return (
    <main className="min-h-screen bg-neutral-50 text-neutral-900">
      <header className="border-b border-brand-100 bg-white">
        <div className="mx-auto flex min-h-16 max-w-7xl flex-col gap-3 px-4 py-3 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <Link href="/" className="flex items-center gap-3">
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
            <div className="flex items-center gap-2">
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
          <nav className="flex gap-0 overflow-x-auto">
            {nav.map((item) => {
              const Icon = item.icon;
              const active = pathname === item.href;
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
        </div>
      </header>
      <section className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-6">
          <p className="text-xs font-bold uppercase tracking-wide text-brand-700">{ROLE_LABELS[role]}</p>
          <h1 className="mt-2 text-2xl font-bold tracking-tight text-neutral-900 sm:text-3xl">{title}</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-neutral-600">{description}</p>
        </div>
        {children}
      </section>
    </main>
  );
}
