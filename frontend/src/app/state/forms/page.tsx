"use client";

import Link from "next/link";
import { Suspense } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { FormsToolLayout } from "@/features/organizations/forms-tool-layout";

export default function Page() {
  return (
    <PortalShell
      role="state_admin"
      title="Forms Tool"
      description="Manage assigned forms, federal reporting templates, and state-specific data collection workflows."
    >
      <div className="grid gap-5">
        <section className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div>
            <p className="text-sm font-bold text-neutral-900">Assessment declaration templates</p>
            <p className="mt-1 text-sm text-neutral-500">Adopt federal health declaration templates and extend them for state assessment requirements.</p>
          </div>
          <Link className="inline-flex h-10 items-center rounded bg-brand-600 px-4 text-sm font-bold text-white" href="/state/assessments/forms">
            Open assessment templates
          </Link>
        </section>
        <Suspense fallback={null}>
          <FormsToolLayout />
        </Suspense>
      </div>
    </PortalShell>
  );
}
