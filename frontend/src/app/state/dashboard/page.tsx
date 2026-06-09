"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { AlertTriangle, BadgeCheck, Banknote, Building2, ClipboardCheck, FileCheck2, HeartPulse, ShieldCheck, UsersRound } from "lucide-react";
import { useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DashboardCard } from "@/components/ui/dashboard-card";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchStateLgas, getStateMinistryDashboard, type StateDashboardParams } from "@/lib/api/state";

type QueueRow = {
  name?: string;
  status?: string;
  count?: number;
  href?: string;
};

type RequestRow = {
  id?: string;
  handler?: string;
  facility?: string;
  status?: string;
  created_at?: string;
};

type FacilityRow = {
  id?: string;
  facility?: string;
  status?: string;
  created_at?: string;
};

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

function dateLabel(value?: string) {
  if (!value) return "Not set";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

export default function Page() {
  const [filters, setFilters] = useState<StateDashboardParams>({});
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
  const facilityRows = (sections?.recent_facility_applications || []) as FacilityRow[];

  return (
    <PortalShell role="state_admin" title="State dashboard" description="Monitor FoodCert NG compliance, facilities, certificates, inspections, and illness events in your state.">
      <div className="grid gap-6">
        <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 md:grid-cols-5">
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-neutral-500">
              LGA
              <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm font-semibold normal-case tracking-normal text-neutral-700" value={filters.lga || ""} onChange={(event) => setFilters((prev) => ({ ...prev, lga: event.target.value || undefined }))}>
                <option value="">All LGAs</option>
                {(lgasQuery.data || []).map((lga) => <option key={lga.id} value={lga.id}>{lga.name}</option>)}
              </select>
            </label>
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-neutral-500">
              From
              <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm normal-case tracking-normal text-neutral-700" type="date" value={filters.date_from || ""} onChange={(event) => setFilters((prev) => ({ ...prev, date_from: event.target.value || undefined }))} />
            </label>
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-neutral-500">
              To
              <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm normal-case tracking-normal text-neutral-700" type="date" value={filters.date_to || ""} onChange={(event) => setFilters((prev) => ({ ...prev, date_to: event.target.value || undefined }))} />
            </label>
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-neutral-500">
              Employer category
              <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm font-semibold normal-case tracking-normal text-neutral-700" value={filters.employer_category || ""} onChange={(event) => setFilters((prev) => ({ ...prev, employer_category: event.target.value || undefined }))}>
                {EMPLOYER_CATEGORIES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </label>
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-neutral-500">
              Certificate status
              <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm font-semibold normal-case tracking-normal text-neutral-700" value={filters.certificate_status || ""} onChange={(event) => setFilters((prev) => ({ ...prev, certificate_status: event.target.value || undefined }))}>
                {CERTIFICATE_STATUSES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </label>
          </div>
        </section>

        {dashboardQuery.isLoading ? <div className="rounded-lg border border-neutral-200 bg-white p-6 text-sm text-neutral-600">Loading state dashboard...</div> : null}
        {dashboardQuery.isError ? <div className="rounded-lg border border-danger-100 bg-danger-50 p-6 text-sm font-semibold text-danger-700">State dashboard data needs a signed-in state ministry user.</div> : null}

        {!dashboardQuery.isLoading && !dashboardQuery.isError ? (
          <>
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <DashboardCard label="Food handlers" value={cards.registered_food_handlers} icon={UsersRound} />
              <DashboardCard label="Certified handlers" value={cards.certified_food_handlers} icon={BadgeCheck} />
              <DashboardCard label="Food businesses" value={cards.food_businesses_registered} icon={Building2} />
              <DashboardCard label="Approved facilities" value={cards.approved_facilities} icon={ShieldCheck} />
              <DashboardCard label="Pending accreditation" value={cards.pending_facility_applications} icon={Building2} detail="Facility applications awaiting state review" />
              <DashboardCard label="Pending certificate validation" value={cards.pending_certificate_validations} icon={FileCheck2} detail="Fit assessments awaiting certificate approval" />
              <DashboardCard label="Active illness exclusions" value={cards.active_illness_exclusions} icon={HeartPulse} />
              <DashboardCard label="Enforcement notices" value={cards.enforcement_notices} icon={AlertTriangle} />
              <DashboardCard label="Inspections" value={cards.inspections_conducted} icon={ClipboardCheck} />
              <DashboardCard label="Expired certificates" value={cards.expired_certificates} icon={AlertTriangle} />
              <DashboardCard label="Due for reaccreditation" value={cards.facilities_due_for_reaccreditation} icon={Building2} />
              <DashboardCard label="State revenue" value={cards.state_revenue_collected} icon={Banknote} />
            </div>

            <section className="grid gap-5 xl:grid-cols-[1fr_1fr]">
              <div className="grid gap-3">
                <h2 className="text-base font-bold text-neutral-900">Operational queues</h2>
                <DataTable
                  columns={[
                    { key: "name", header: "Queue", render: (row) => row.href ? <Link className="font-bold text-brand-700 hover:underline" href={row.href}>{row.name}</Link> : row.name },
                    { key: "count", header: "Count", render: (row) => row.count ?? 0 },
                    { key: "status", header: "Status", render: (row) => <StatusCell status={row.status} /> },
                  ]}
                  rows={queueRows}
                  empty="No operational queue items for the current filters."
                />
              </div>
              <div className="grid gap-3">
                <h2 className="text-base font-bold text-neutral-900">Pending certificate requests</h2>
                <DataTable
                  columns={[
                    { key: "handler", header: "Handler", render: (row) => row.handler || "Unknown" },
                    { key: "facility", header: "Facility", render: (row) => row.facility || "Unknown" },
                    { key: "status", header: "Status", render: (row) => <StatusCell status={row.status} /> },
                    { key: "created", header: "Created", render: (row) => dateLabel(row.created_at) },
                  ]}
                  rows={certificateRows}
                  empty="No pending certificate validation requests."
                />
              </div>
            </section>

            <section className="grid gap-3">
              <h2 className="text-base font-bold text-neutral-900">Pending facility applications</h2>
              <DataTable
                columns={[
                  { key: "facility", header: "Facility", render: (row) => row.facility || "Unknown" },
                  { key: "status", header: "Status", render: (row) => <StatusCell status={row.status} /> },
                  { key: "created", header: "Created", render: (row) => dateLabel(row.created_at) },
                ]}
                rows={facilityRows}
                empty="No pending facility accreditation applications."
              />
            </section>
          </>
        ) : null}
      </div>
    </PortalShell>
  );
}
