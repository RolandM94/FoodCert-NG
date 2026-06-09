"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { ClipboardCheck, Eye, Filter, Search } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { listEmployers } from "@/lib/api/identity";
import { listEmployerInspections, type EmployerInspectionFilters } from "@/lib/api/inspections";
import type { EmployerInspectionSummary, InspectionStatus } from "@/types/inspections";

const statusOptions: Array<{ value: "" | InspectionStatus; label: string }> = [
  { value: "", label: "All statuses" },
  { value: "submitted", label: "Submitted" },
  { value: "employer_response_submitted", label: "Response submitted" },
  { value: "closed", label: "Closed" },
  { value: "in_progress", label: "In progress" },
  { value: "draft", label: "Draft" },
];

function formatDate(value?: string | null) {
  if (!value) return "Not set";
  return new Date(value).toLocaleDateString("en-NG", { day: "2-digit", month: "short", year: "numeric" });
}

function statusLabel(value: string) {
  return value.replaceAll("_", " ");
}

function StatusBadge({ status }: { status: InspectionStatus }) {
  const tone =
    status === "closed"
      ? "bg-neutral-100 text-neutral-700 ring-neutral-200"
      : status === "employer_response_submitted"
        ? "bg-brand-50 text-brand-700 ring-brand-200"
        : status === "submitted"
          ? "bg-warning-50 text-warning-700 ring-warning-100"
          : "bg-info-50 text-info-700 ring-info-100";
  return <span className={`rounded px-2 py-1 text-xs font-bold capitalize ring-1 ${tone}`}>{statusLabel(status)}</span>;
}

function ScoreBadge({ score }: { score?: string | null }) {
  if (!score) return <span className="text-sm font-semibold text-neutral-400">Not scored</span>;
  const value = Number(score);
  const tone = value >= 80 ? "text-brand-700" : value >= 60 ? "text-warning-700" : "text-danger-700";
  return <span className={`text-sm font-bold ${tone}`}>{value.toFixed(0)}%</span>;
}

function InspectionRow({ inspection }: { inspection: EmployerInspectionSummary }) {
  return (
    <tr>
      <td className="border-b border-neutral-50 py-4 pr-4 align-top">
        <p className="font-semibold text-neutral-900">{formatDate(inspection.inspection_date)}</p>
        <p className="mt-1 text-xs text-neutral-500">{inspection.inspector_name || "Inspector"}</p>
      </td>
      <td className="border-b border-neutral-50 py-4 pr-4 align-top">
        <p className="font-semibold text-neutral-800">{inspection.branch_name || "All branches"}</p>
        <p className="mt-1 line-clamp-2 max-w-xl text-sm leading-6 text-neutral-600">{inspection.findings_summary || "No findings recorded."}</p>
      </td>
      <td className="border-b border-neutral-50 py-4 pr-4 align-top">
        <ScoreBadge score={inspection.compliance_score} />
      </td>
      <td className="border-b border-neutral-50 py-4 pr-4 align-top">
        <StatusBadge status={inspection.status} />
        <p className="mt-2 text-xs font-semibold capitalize text-neutral-500">{inspection.enforcement_action.replaceAll("_", " ")}</p>
      </td>
      <td className="border-b border-neutral-50 py-4 pr-4 align-top text-sm text-neutral-600">{inspection.response_count}</td>
      <td className="border-b border-neutral-50 py-4 text-right align-top">
        <Link
          className="inline-flex h-9 items-center gap-2 rounded border border-neutral-200 px-3 text-sm font-bold text-brand-700 hover:bg-brand-50"
          href={`/employer/inspections/${inspection.id}`}
        >
          <Eye size={15} />
          View
        </Link>
      </td>
    </tr>
  );
}

export default function Page() {
  const [status, setStatus] = useState<"" | InspectionStatus>("");
  const [branch, setBranch] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const employersQuery = useQuery({
    queryKey: ["employers", "me"],
    queryFn: listEmployers,
  });
  const employer = employersQuery.data?.[0];

  const filters = useMemo<EmployerInspectionFilters>(() => {
    const next: EmployerInspectionFilters = {};
    if (status) next.status = status;
    if (branch) next.branch = branch;
    if (dateFrom) next.date_from = dateFrom;
    if (dateTo) next.date_to = dateTo;
    return next;
  }, [branch, dateFrom, dateTo, status]);

  const inspectionsQuery = useQuery({
    queryKey: ["employer-inspections", employer?.id, filters],
    queryFn: () => listEmployerInspections(employer!.id, filters),
    enabled: Boolean(employer?.id),
  });

  const inspections = inspectionsQuery.data || [];
  const needsResponse = inspections.filter((inspection) => inspection.status === "submitted").length;
  const scoredInspections = inspections.filter((inspection) => inspection.compliance_score !== null && inspection.compliance_score !== undefined);
  const averageScore = scoredInspections.length
    ? Math.round(scoredInspections.reduce((sum, inspection) => sum + Number(inspection.compliance_score || 0), 0) / scoredInspections.length)
    : 0;

  return (
    <PortalShell role="employer" title="Inspections" description="Review inspection reports, enforcement notices, evidence, and response history.">
      <div className="grid gap-6">
        <section className="grid gap-4 md:grid-cols-3">
          <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-wide text-brand-700">Reports</p>
            <p className="mt-2 text-3xl font-bold text-neutral-900">{inspections.length}</p>
          </div>
          <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-wide text-brand-700">Need Response</p>
            <p className="mt-2 text-3xl font-bold text-warning-700">{needsResponse}</p>
          </div>
          <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-wide text-brand-700">Average Score</p>
            <p className="mt-2 text-3xl font-bold text-brand-700">{averageScore}%</p>
          </div>
        </section>

        <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex items-center gap-2">
            <Filter className="text-brand-700" size={18} />
            <h2 className="text-base font-bold text-neutral-900">Filters</h2>
          </div>
          <div className="grid gap-3 md:grid-cols-4">
            <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
              Status
              <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={status} onChange={(event) => setStatus(event.target.value as "" | InspectionStatus)}>
                {statusOptions.map((option) => (
                  <option key={option.value || "all"} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
            <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
              Branch ID
              <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" value={branch} onChange={(event) => setBranch(event.target.value)} />
            </label>
            <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
              From
              <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" type="date" value={dateFrom} onChange={(event) => setDateFrom(event.target.value)} />
            </label>
            <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
              To
              <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" type="date" value={dateTo} onChange={(event) => setDateTo(event.target.value)} />
            </label>
          </div>
        </section>

        <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <ClipboardCheck className="text-brand-700" size={18} />
              <h2 className="text-base font-bold text-neutral-900">Inspection History</h2>
            </div>
            <span className="text-sm font-semibold text-neutral-500">{inspectionsQuery.isFetching ? "Loading..." : `${inspections.length} shown`}</span>
          </div>
          {inspectionsQuery.isError ? (
            <div className="rounded-lg bg-danger-50 p-4 text-sm font-semibold text-danger-700">Could not load inspection history.</div>
          ) : null}
          <div className="overflow-x-auto">
            <table className="w-full min-w-[820px] text-left text-sm">
              <thead className="text-xs font-bold uppercase tracking-wide text-neutral-500">
                <tr>
                  <th className="border-b border-neutral-100 py-2 pr-4">Date</th>
                  <th className="border-b border-neutral-100 py-2 pr-4">Branch & Findings</th>
                  <th className="border-b border-neutral-100 py-2 pr-4">Score</th>
                  <th className="border-b border-neutral-100 py-2 pr-4">Status</th>
                  <th className="border-b border-neutral-100 py-2 pr-4">Responses</th>
                  <th className="border-b border-neutral-100 py-2 text-right">Action</th>
                </tr>
              </thead>
              <tbody>
                {inspections.map((inspection) => (
                  <InspectionRow inspection={inspection} key={inspection.id} />
                ))}
                {!inspections.length && !inspectionsQuery.isFetching ? (
                  <tr>
                    <td className="py-8 text-center text-neutral-500" colSpan={6}>
                      <Search className="mx-auto mb-2 text-neutral-300" size={24} />
                      No inspections match the current filters.
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </PortalShell>
  );
}
