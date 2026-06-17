"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { PortalShell } from "@/components/layout/portal-shell";

export type StandardsPolicySidebarItem = {
  label: string;
  href: string;
};

export function StandardsPolicyWorkspaceLayout({
  title,
  description,
  breadcrumb,
  sidebarItems,
  children,
}: {
  title: string;
  description: string;
  breadcrumb?: StandardsPolicySidebarItem[];
  sidebarItems: StandardsPolicySidebarItem[];
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const activeItem = sidebarItems.find((item) => pathname === item.href || pathname.startsWith(`${item.href}/`))?.href
    ?? sidebarItems[0]?.href
    ?? pathname;

  return (
    <PortalShell role="federal_admin" title={title} description={description}>
      <div className="grid gap-5">
        {breadcrumb && breadcrumb.length > 0 ? (
          <nav aria-label="Breadcrumb" className="flex flex-wrap items-center gap-2 text-sm">
            {breadcrumb.map((item, index) => (
              <span key={item.href} className="flex items-center gap-2">
                {index > 0 ? <span className="text-neutral-300">/</span> : null}
                <Link href={item.href} className="font-medium text-neutral-600 hover:text-brand-700">
                  {item.label}
                </Link>
              </span>
            ))}
          </nav>
        ) : null}

        <div className="grid gap-5 lg:grid-cols-[260px_minmax(0,1fr)]">
          <aside className="rounded-lg border border-neutral-200 bg-white p-3 shadow-sm lg:sticky lg:top-24 lg:self-start">
            <nav className="hidden space-y-1 lg:block" aria-label={`${title} menu`}>
              {sidebarItems.map((item) => {
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
              <label className="sr-only" htmlFor="standards-policy-workspace-menu">Workspace menu</label>
              <select
                id="standards-policy-workspace-menu"
                className="h-11 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm font-semibold text-neutral-800"
                value={activeItem}
                onChange={(event) => router.push(event.target.value)}
              >
                {sidebarItems.map((item) => (
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
