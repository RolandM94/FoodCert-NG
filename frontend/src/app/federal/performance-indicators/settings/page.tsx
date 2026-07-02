"use client";

import Link from "next/link";

import { PerformanceIndicatorsShell } from "@/features/indicators/performance-indicators-shell";

const SETTINGS = [
  { label: "Scheduled calculation", value: "Daily at 02:45 (automatic and hybrid indicators)" },
  { label: "Alert triggers", value: "Below target, critical band, missing result, calculation failed" },
  { label: "Alert recipients", value: "Federal programme officers; state admins for state-scoped indicators" },
  { label: "Alert channels", value: "In-app and email (M&E category)" },
  { label: "Default performance bands", value: "Green ≥ 90 · Amber 70–89 · Red < 70 (per-indicator overrides in Targets & Thresholds)" },
];

export default function FederalPISettingsPage() {
  return (
    <PerformanceIndicatorsShell
      role="federal_admin"
      title="Indicator Settings"
      description="Module defaults for calculation scheduling, alerting, and performance bands."
    >
      <div className="grid gap-5">
        <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <h3 className="text-sm font-semibold text-neutral-900">Module defaults</h3>
          <dl className="mt-3 grid gap-3">
            {SETTINGS.map((setting) => (
              <div key={setting.label} className="grid gap-0.5">
                <dt className="text-xs font-semibold uppercase tracking-wide text-neutral-500">{setting.label}</dt>
                <dd className="text-sm text-neutral-800">{setting.value}</dd>
              </div>
            ))}
          </dl>
        </section>
        <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <h3 className="text-sm font-semibold text-neutral-900">Related configuration</h3>
          <ul className="mt-2 list-disc pl-5 text-sm text-brand-700">
            <li><Link className="hover:underline" href="/federal/standards-policy/reporting-me/me-indicators">KPI builder (Standards &amp; Policy → Reporting &amp; M&amp;E)</Link></li>
            <li><Link className="hover:underline" href="/federal/account-settings">Notification rules (Account Settings)</Link></li>
          </ul>
        </section>
      </div>
    </PerformanceIndicatorsShell>
  );
}
