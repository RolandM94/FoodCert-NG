"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import {
  AlertTriangle, BadgeCheck, Banknote, Building2, ClipboardCheck,
  ExternalLink, FileCheck2, HeartPulse, Plus, Search, ShieldCheck, UsersRound,
} from "lucide-react";
import { useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchStateLgas, getStateMinistryDashboard, type StateDashboardParams } from "@/lib/api/state";

type QueueRow = { name?: string; status?: string; count?: number; href?: string };
type RequestRow = { id?: string; handler?: string; facility?: string; status?: string; created_at?: string };

const EMPLOYER_CATEGORIES = [
  ["", "All employer categories"],
  ["restaurant_cafe", "Restaurants and cafes"],
  ["bakery", "Bakeries"],
  ["hotel", "Hotels"],
  ["catering", "Catering services"],
  ["school_canteen", "School canteens"],
];

const CERTIFICATE_STATUSES = [
  ["", "All certificate statuses"],
  ["active", "Active"],
  ["expired", "Expired"],
  ["pending_validation", "Pending validation"],
  ["suspended", "Suspended"],
  ["revoked", "Revoked"],
];

function num(value: unknown): number {
  return typeof value === "number" ? value : Number(value) || 0;
}

function pct(part: unknown, total: unknown): string {
  const t = num(total);
  if (!t) return "0%";
  return `${((num(part) / t) * 100).toFixed(1)}%`;
}

function currency(value: unknown): string {
  const n = num(value);
  if (n >= 1_000_000) return `₦${(n / 1_000_000).toFixed(2)}M`;
  if (n >= 1_000) return `₦${(n / 1_000).toFixed(1)}K`;
  return `₦${n.toLocaleString()}`;
}

function metricLabel(count: number, singular: string, plural?: string) {
  return count === 1 ? singular : plural ?? `${singular}s`;
}

function SummaryCard({ icon: Icon, title, metricValue, metricLabel, coverage, items, actionLabel, actionHref, color = "brand" }: {
  icon: typeof UsersRound;
  title: string;
  metricValue: string | number;
  metricLabel: string;
  coverage?: string;
  items: Array<{ label: string; value: string | number; severity?: "critical" | "high" | "medium" | "neutral" }>;
  actionLabel: string;
  actionHref: string;
  color?: "brand" | "warning" | "danger";
}) {
  const iconBg = color === "danger" ? "bg-danger-50 text-danger-700" : color === "warning" ? "bg-warning-50 text-warning-700" : "bg-brand-50 text-brand-700";
  return (
    <div className="flex min-h-[236px] flex-col rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="min-h-8 text-xs font-bold uppercase leading-4 tracking-wide text-neutral-500">{title}</p>
          <div className="mt-3 flex flex-wrap items-baseline gap-x-2 gap-y-1">
            <span className="text-2xl font-bold leading-none text-neutral-950">{metricValue}</span>
            <span className="text-sm font-bold leading-5 text-neutral-800">{metricLabel}</span>
          </div>
          {coverage ? <p className="mt-1 text-sm font-semibold text-brand-700">{coverage} coverage</p> : null}
        </div>
        <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full ${iconBg}`}><Icon size={21} /></div>
      </div>
      {items.length ? (
        <div className="mt-5 grid gap-2">
          <p className="text-[11px] font-bold uppercase tracking-wide text-neutral-400">Needs Attention</p>
          {items.map((item) => {
            const cls = item.severity === "critical" ? "text-danger-700" : item.severity === "high" ? "text-warning-700" : "text-neutral-600";
            return (
              <div key={item.label} className="flex items-center justify-between gap-3 text-sm">
                <span className="truncate text-neutral-600">{item.label}</span>
                <span className={`font-bold ${cls}`}>{item.value}</span>
              </div>
            );
          })}
        </div>
      ) : null}
      <Link className="mt-auto inline-flex items-center gap-1 pt-4 text-xs font-bold text-brand-700 hover:text-brand-600" href={actionHref}>
        {actionLabel} <ExternalLink size={12} />
      </Link>
    </div>
  );
}

function PriorityItem({ label, count, severity, href }: { label: string; count: number; severity: string; href: string }) {
  const badge = severity === "critical" ? "bg-danger-50 text-danger-700" : severity === "high" ? "bg-warning-50 text-warning-700" : "bg-neutral-100 text-neutral-700";
  const border = severity === "critical" ? "border-danger-100 bg-danger-50/50" : severity === "high" ? "border-warning-100 bg-warning-50/60" : "border-neutral-100 bg-white";
  return (
    <div className={`flex min-h-20 items-center justify-between gap-3 rounded-lg border px-4 py-3 ${border}`}>
      <div className="flex items-center gap-3">
        <span className={`inline-flex h-10 w-10 items-center justify-center rounded-full ${badge}`}><AlertTriangle size={18} /></span>
        <div>
          <p className="text-xs font-bold text-neutral-700">{label}</p>
          <p className="mt-1 text-2xl font-bold text-neutral-950">{count}</p>
        </div>
      </div>
      <Link className="shrink-0 text-xs font-bold text-brand-700 hover:underline" href={href}>View</Link>
    </div>
  );
}

function QuickActionButton({ href, icon: Icon, label, primary = false }: { href: string; icon: typeof Plus; label: string; primary?: boolean }) {
  return (
    <Link
      className={`inline-flex h-11 items-center justify-center gap-2 rounded-lg border px-3 text-sm font-bold ${
        primary
          ? "border-brand-600 bg-brand-600 text-white hover:bg-brand-700"
          : "border-neutral-200 bg-white text-neutral-700 hover:border-brand-200 hover:bg-brand-50 hover:text-brand-700"
      }`}
      href={href}
    >
      <Icon size={16} />
      {label}
    </Link>
  );
}

export default function Page() {
  const [filters, setFilters] = useState<StateDashboardParams>({});
  const [draftFilters, setDraftFilters] = useState<StateDashboardParams>({});
  const dashboardQuery = useQuery({
    queryKey: ["state-ministry-dashboard", filters],
    queryFn: () => getStateMinistryDashboard(filters),
  });
  const stateId = dashboardQuery.data?.state?.id;
  const lgasQuery = useQuery({
    queryKey: ["state-lgas", stateId],
    queryFn: () => fetchStateLgas(stateId!),
    enabled: Boolean(stateId),
  });

  const cards = dashboardQuery.data?.cards || {};
  const sections = dashboardQuery.data?.sections;
  const queueRows = (sections?.operational_queues || []) as QueueRow[];
  const certificateRows = (sections?.recent_certificate_requests || []) as RequestRow[];

  const totalHandlers = num(cards.registered_food_handlers);
  const certifiedHandlers = num(cards.certified_food_handlers);
  const totalBusinesses = num(cards.food_businesses_registered);
  const approvedFacilities = num(cards.approved_facilities);

  return (
    <PortalShell role="state_admin" title="State Dashboard" description="Monitor FoodCert NG compliance, facilities, certificates, inspections, and operational risks across your state.">
      <div className="grid gap-6">
        <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-[1fr_1fr_1fr_1.3fr_1.3fr_auto]">
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-neutral-500">
              LGA
              <select className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm font-semibold normal-case tracking-normal text-neutral-700" value={draftFilters.lga || ""} onChange={(e) => setDraftFilters((prev) => ({ ...prev, lga: e.target.value || undefined }))}>
                <option value="">All LGAs</option>
                {(lgasQuery.data || []).map((lga) => <option key={lga.id} value={lga.id}>{lga.name}</option>)}
              </select>
            </label>
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-neutral-500">
              From
              <input className="h-10 rounded-lg border border-neutral-200 bg-neutral-50 px-3 text-sm normal-case tracking-normal text-neutral-700" type="date" value={draftFilters.date_from || ""} onChange={(e) => setDraftFilters((prev) => ({ ...prev, date_from: e.target.value || undefined }))} />
            </label>
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-neutral-500">
              To
              <input className="h-10 rounded-lg border border-neutral-200 bg-neutral-50 px-3 text-sm normal-case tracking-normal text-neutral-700" type="date" value={draftFilters.date_to || ""} onChange={(e) => setDraftFilters((prev) => ({ ...prev, date_to: e.target.value || undefined }))} />
            </label>
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-neutral-500">
              Employer category
              <select className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm font-semibold normal-case tracking-normal text-neutral-700" value={draftFilters.employer_category || ""} onChange={(e) => setDraftFilters((prev) => ({ ...prev, employer_category: e.target.value || undefined }))}>
                {EMPLOYER_CATEGORIES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </label>
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-neutral-500">
              Certificate status
              <select className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm font-semibold normal-case tracking-normal text-neutral-700" value={draftFilters.certificate_status || ""} onChange={(e) => setDraftFilters((prev) => ({ ...prev, certificate_status: e.target.value || undefined }))}>
                {CERTIFICATE_STATUSES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </label>
            <button className="mt-5 inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-brand-600 px-4 text-sm font-bold text-white hover:bg-brand-700 md:col-span-2 xl:col-span-1" onClick={() => setFilters(draftFilters)} type="button">
              <Search size={15} />
              Apply filters
            </button>
          </div>
        </section>

        {dashboardQuery.isLoading ? <div className="rounded-lg border border-neutral-200 bg-white p-6 text-sm text-neutral-600">Loading state dashboard...</div> : null}
        {dashboardQuery.isError ? <div className="rounded-lg border border-danger-100 bg-danger-50 p-6 text-sm font-semibold text-danger-700">Could not load dashboard data.</div> : null}

        {!dashboardQuery.isLoading && !dashboardQuery.isError ? (
          <>
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
              <SummaryCard
                icon={UsersRound}
                title="Food Handler Compliance"
                metricValue={totalHandlers.toLocaleString()}
                metricLabel={metricLabel(totalHandlers, "Food Handler")}
                coverage={pct(certifiedHandlers, totalHandlers)}
                items={[
                  { label: "Certified", value: certifiedHandlers.toLocaleString(), severity: "neutral" },
                  { label: "Pending validation", value: num(cards.pending_certificate_validations), severity: "medium" },
                  { label: "Expired certificates", value: num(cards.expired_certificates), severity: "high" },
                ]}
                actionLabel="View Food Handlers"
                actionHref="/state/directory?tab=food-handlers"
              />
              <SummaryCard
                icon={HeartPulse}
                title="Employer Compliance"
                metricValue={totalBusinesses.toLocaleString()}
                metricLabel={metricLabel(totalBusinesses, "Food Business", "Food Businesses")}
                items={[
                  { label: "Active illness exclusions", value: num(cards.active_illness_exclusions), severity: "high" },
                  { label: "RTW pending", value: num(cards.return_to_work_pending), severity: "medium" },
                  { label: "Enforcement notices", value: num(cards.enforcement_notices), severity: "medium" },
                ]}
                actionLabel="View Employers"
                actionHref="/state/directory?tab=employers"
              />
              <SummaryCard
                icon={ShieldCheck}
                title="Medical Facility Readiness"
                metricValue={approvedFacilities.toLocaleString()}
                metricLabel={metricLabel(approvedFacilities, "Approved Facility", "Approved Facilities")}
                items={[
                  { label: "Pending accreditation", value: num(cards.pending_facility_applications), severity: "medium" },
                  { label: "Due for re-accreditation", value: num(cards.facilities_due_for_reaccreditation), severity: "high" },
                ]}
                actionLabel="View Facilities"
                actionHref="/state/medical-facilities"
              />
              <SummaryCard
                icon={ClipboardCheck}
                title="Inspections & Enforcement"
                metricValue={num(cards.inspections_conducted)}
                metricLabel={metricLabel(num(cards.inspections_conducted), "Inspection")}
                items={[
                  { label: "Enforcement notices", value: num(cards.enforcement_notices), severity: "medium" },
                ]}
                actionLabel="Open Inspections"
                actionHref="/state/inspections-enforcement"
              />
              <SummaryCard
                icon={Banknote}
                title="Revenue Summary"
                metricValue={currency(cards.state_revenue_collected)}
                metricLabel="Collected"
                items={[]}
                actionLabel="View Revenue"
                actionHref="/state/revenue"
              />
            </div>

            <section className="grid gap-4 xl:grid-cols-[1fr_360px]">
              <div className="rounded-lg border border-warning-100 bg-white p-4 shadow-sm">
                <div className="mb-3 flex items-center justify-between gap-3">
                  <h2 className="text-base font-bold text-neutral-900">Urgent Attention</h2>
                  <Link className="text-xs font-bold text-brand-700 hover:underline" href="/state/reports">View all alerts</Link>
                </div>
                <div className="grid gap-3 sm:grid-cols-2 2xl:grid-cols-3">
                  {num(cards.pending_facility_applications) > 0 ? <PriorityItem label="High-risk facilities pending review" count={num(cards.pending_facility_applications)} severity="high" href="/state/medical-facilities?tab=accreditation" /> : null}
                  {num(cards.pending_certificate_validations) > 0 ? <PriorityItem label="Pending certificate validation" count={num(cards.pending_certificate_validations)} severity="high" href="/state/certificates?status=pending_validation" /> : null}
                  {num(cards.expired_certificates) > 0 ? <PriorityItem label="Expired certificates" count={num(cards.expired_certificates)} severity="medium" href="/state/certificates?status=expired" /> : null}
                  {num(cards.facilities_due_for_reaccreditation) > 0 ? <PriorityItem label="Due for re-accreditation" count={num(cards.facilities_due_for_reaccreditation)} severity="medium" href="/state/medical-facilities?filter=reaccreditation_due" /> : null}
                  {num(cards.active_illness_exclusions) > 0 ? <PriorityItem label="Active illness exclusions" count={num(cards.active_illness_exclusions)} severity="critical" href="/state/illness-reports" /> : null}
                  {num(cards.return_to_work_pending) > 0 ? <PriorityItem label="Return-to-work pending clearance" count={num(cards.return_to_work_pending)} severity="high" href="/state/return-to-work-clearance" /> : null}
                </div>
              </div>

              <aside className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
                <h2 className="mb-3 text-base font-bold text-neutral-900">Quick Actions</h2>
                <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
                  <QuickActionButton href="/state/inspections-enforcement?tab=inspections" icon={Plus} label="Create Inspection" primary />
                  <QuickActionButton href="/state/certificates?status=pending_validation" icon={FileCheck2} label="Review Certificates" />
                  <QuickActionButton href="/state/medical-facilities" icon={Building2} label="View Facilities" />
                  <QuickActionButton href="/state/reports" icon={BadgeCheck} label="Open Reports" />
                </div>
              </aside>
            </section>

            <section className="grid items-stretch gap-5 xl:grid-cols-2">
              <div className="grid min-h-[300px] grid-rows-[auto_1fr] gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
                <h2 className="text-base font-bold text-neutral-900">Operational Queues</h2>
                <DataTable
                  columns={[
                    { key: "name", header: "Queue", render: (row) => row.href ? <Link className="font-bold text-brand-700 hover:underline" href={row.href}>{row.name}</Link> : row.name },
                    { key: "count", header: "Count", render: (row) => row.count ?? 0 },
                    { key: "status", header: "Status", render: (row) => <StatusCell status={row.status} /> },
                  ]}
                  rows={queueRows}
                  empty="No operational queue items."
                />
              </div>
              <div className="grid min-h-[300px] grid-rows-[auto_1fr] gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
                <h2 className="text-base font-bold text-neutral-900">Recent Certificate Requests</h2>
                <DataTable
                  columns={[
                    { key: "handler", header: "Handler", render: (row) => row.handler || "Unknown" },
                    { key: "facility", header: "Facility", render: (row) => row.facility || "Unknown" },
                    { key: "status", header: "Status", render: (row) => <StatusCell status={row.status} /> },
                  ]}
                  rows={certificateRows}
                  empty="No pending certificate requests."
                />
              </div>
            </section>
          </>
        ) : null}
      </div>
    </PortalShell>
  );
}
