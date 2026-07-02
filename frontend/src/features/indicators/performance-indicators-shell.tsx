"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { PortalShell } from "@/components/layout/portal-shell";

export type PIRole = "federal_admin" | "state_admin";

type PISidebarItem = { label: string; href: string };

export const FEDERAL_PI_BASE = "/federal/performance-indicators";
export const STATE_PI_BASE = "/state/performance-indicators";

const FEDERAL_ITEMS: PISidebarItem[] = [
  { label: "Overview", href: FEDERAL_PI_BASE },
  { label: "National Indicator Library", href: `${FEDERAL_PI_BASE}/library` },
  { label: "Targets & Thresholds", href: `${FEDERAL_PI_BASE}/targets` },
  { label: "State Adoption", href: `${FEDERAL_PI_BASE}/adoption` },
  { label: "Results", href: `${FEDERAL_PI_BASE}/results` },
  { label: "Settings", href: `${FEDERAL_PI_BASE}/settings` },
];

const STATE_ITEMS: PISidebarItem[] = [
  { label: "Overview", href: STATE_PI_BASE },
  { label: "Adopted National Indicators", href: `${STATE_PI_BASE}/adopted` },
  { label: "State Indicators", href: `${STATE_PI_BASE}/state-indicators` },
  { label: "Results", href: `${STATE_PI_BASE}/results` },
];

export function PerformanceIndicatorsShell({
  role,
  title,
  description,
  children,
}: {
  role: PIRole;
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const items = role === "federal_admin" ? FEDERAL_ITEMS : STATE_ITEMS;
  const base = role === "federal_admin" ? FEDERAL_PI_BASE : STATE_PI_BASE;

  // Longest-prefix match so the Overview item (the base path) does not swallow sub-pages.
  const activeItem =
    [...items]
      .sort((a, b) => b.href.length - a.href.length)
      .find((item) => pathname === item.href || pathname.startsWith(`${item.href}/`))?.href
    ?? items[0]?.href
    ?? pathname;

  return (
    <PortalShell role={role} title={title} description={description}>
      <div className="grid gap-5">
        <nav aria-label="Breadcrumb" className="flex flex-wrap items-center gap-2 text-sm">
          <Link href={base} className="font-medium text-neutral-600 hover:text-brand-700">
            Performance Indicators
          </Link>
        </nav>

        <div className="grid gap-5 lg:grid-cols-[260px_minmax(0,1fr)]">
          <aside className="rounded-lg border border-neutral-200 bg-white p-3 shadow-sm lg:sticky lg:top-24 lg:self-start">
            <nav className="hidden space-y-1 lg:block" aria-label="Performance Indicators menu">
              {items.map((item) => {
                const active = activeItem === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex min-h-10 items-center rounded-md px-3 py-2 text-sm font-semibold transition-colors ${
                      active ? "bg-brand-50 text-brand-700" : "text-neutral-600 hover:bg-neutral-50 hover:text-neutral-950"
                    }`}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </nav>
            <div className="lg:hidden">
              <label className="sr-only" htmlFor="performance-indicators-menu">Module menu</label>
              <select
                id="performance-indicators-menu"
                className="h-11 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm font-semibold text-neutral-800"
                value={activeItem}
                onChange={(event) => router.push(event.target.value)}
              >
                {items.map((item) => (
                  <option key={item.href} value={item.href}>
                    {item.label}
                  </option>
                ))}
              </select>
            </div>
          </aside>

          <div className="min-w-0">{children}</div>
        </div>
      </div>
    </PortalShell>
  );
}
