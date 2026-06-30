"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, Building2, Filter, Landmark, Search, ShieldCheck, UsersRound } from "lucide-react";
import { fetchStateAuditLogs, type StateAuditLogItem } from "@/lib/api/state";
import { getApiErrorMessage } from "@/lib/api/client";

const ACTION_OPTIONS = [
  { value: "", label: "All actions" },
  { value: "create", label: "Create" },
  { value: "update", label: "Update" },
  { value: "delete", label: "Delete" },
  { value: "role_change", label: "Role change" },
  { value: "workflow_transition", label: "Workflow transition" },
  { value: "payment_event", label: "Payment event" },
  { value: "security_event", label: "Security event" },
  { value: "certificate_event", label: "Certificate event" },
];

const ROLE_OPTIONS = [
  { value: "", label: "All roles" },
  { value: "state_admin", label: "State admin" },
  { value: "inspector", label: "Inspector" },
  { value: "facility_admin", label: "Facility admin" },
  { value: "employer", label: "Employer" },
  { value: "doctor", label: "Doctor" },
  { value: "lab_staff", label: "Lab staff" },
];

type AuditFilters = {
  search: string;
  actor: string;
  role: string;
  action: string;
  entity: string;
  date_from: string;
  date_to: string;
  lga: string;
  facility: string;
};

const DEFAULT_FILTERS: AuditFilters = {
  search: "",
  actor: "",
  role: "",
  action: "",
  entity: "",
  date_from: "",
  date_to: "",
  lga: "",
  facility: "",
};

function toneForRisk(risk?: string) {
  if (risk === "high") return "bg-danger-50 text-danger-700 ring-danger-200";
  if (risk === "medium") return "bg-warning-50 text-warning-700 ring-warning-200";
  return "bg-brand-50 text-brand-700 ring-brand-200";
}

function toneForStatus(status?: string) {
  const value = (status || "").toLowerCase();
  if (value.includes("failed") || value.includes("error")) return "bg-danger-50 text-danger-700 ring-danger-200";
  if (value.includes("pending") || value.includes("review")) return "bg-warning-50 text-warning-700 ring-warning-200";
  return "bg-brand-50 text-brand-700 ring-brand-200";
}

function toParams(filters: AuditFilters) {
  return Object.fromEntries(Object.entries(filters).filter(([, value]) => value));
}

function StatCard({
  label,
  value,
  icon: Icon,
}: {
  label: string;
  value: number;
  icon: typeof ShieldCheck;
}) {
  return (
    <div className="rounded-xl border border-neutral-200 bg-white p-4 shadow-sm">
      <div className="flex items-center gap-3">
        <div className="rounded-lg bg-brand-50 p-2 text-brand-700">
          <Icon size={18} />
        </div>
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-neutral-500">{label}</p>
          <p className="mt-1 text-2xl font-bold text-neutral-950">{value}</p>
        </div>
      </div>
    </div>
  );
}

export function StateAuditLogsPanel({ compact = false }: { compact?: boolean }) {
  const [filters, setFilters] = useState<AuditFilters>(DEFAULT_FILTERS);
  const logsQuery = useQuery({
    queryKey: ["state-audit-logs", filters],
    queryFn: () => fetchStateAuditLogs(toParams(filters)),
  });

  const logs = logsQuery.data;
  const metrics = useMemo(() => {
    const rows = logs || [];
    return {
      total: rows.length,
      governance: rows.filter((item) => item.module === "Stakeholder Management" || item.module === "Standards & Policy").length,
      facilities: rows.filter((item) => item.module === "Medical Facilities" || item.module === "Compliance").length,
      highRisk: rows.filter((item) => item.risk_level === "high").length,
    };
  }, [logs]);

  return (
    <div className="space-y-6">
      {!compact ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <StatCard label="Visible events" value={metrics.total} icon={Landmark} />
          <StatCard label="Governance" value={metrics.governance} icon={UsersRound} />
          <StatCard label="Facilities & Compliance" value={metrics.facilities} icon={Building2} />
          <StatCard label="High risk" value={metrics.highRisk} icon={AlertTriangle} />
        </div>
      ) : null}

      <section className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-brand-700">State oversight trail</p>
            <h3 className="mt-2 text-lg font-bold text-neutral-950">Audit logs</h3>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-neutral-500">
              Review officer activity, policy adoption, facility governance, compliance actions, reports, and public awareness publishing across this State workspace.
            </p>
          </div>
          <button
            className="inline-flex h-11 items-center gap-2 rounded-lg border border-neutral-200 bg-white px-4 text-sm font-semibold text-neutral-700 hover:border-neutral-300 hover:text-neutral-900"
            onClick={() => setFilters(DEFAULT_FILTERS)}
            type="button"
          >
            <Filter size={16} />
            Reset filters
          </button>
        </div>

        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <label className="grid gap-1 text-sm font-semibold text-neutral-700">
            Search
            <div className="flex h-11 items-center gap-2 rounded-lg border border-neutral-200 bg-neutral-50 px-3">
              <Search size={15} className="text-neutral-400" />
              <input
                className="w-full bg-transparent text-sm outline-none placeholder:text-neutral-400"
                placeholder="Event, target, actor"
                value={filters.search}
                onChange={(event) => setFilters((prev) => ({ ...prev, search: event.target.value }))}
              />
            </div>
          </label>
          <label className="grid gap-1 text-sm font-semibold text-neutral-700">
            Actor
            <input
              className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-brand-400"
              placeholder="Officer name or email"
              value={filters.actor}
              onChange={(event) => setFilters((prev) => ({ ...prev, actor: event.target.value }))}
            />
          </label>
          <label className="grid gap-1 text-sm font-semibold text-neutral-700">
            Role
            <select
              className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-brand-400"
              value={filters.role}
              onChange={(event) => setFilters((prev) => ({ ...prev, role: event.target.value }))}
            >
              {ROLE_OPTIONS.map((option) => (
                <option key={option.value || "all"} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <label className="grid gap-1 text-sm font-semibold text-neutral-700">
            Action
            <select
              className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-brand-400"
              value={filters.action}
              onChange={(event) => setFilters((prev) => ({ ...prev, action: event.target.value }))}
            >
              {ACTION_OPTIONS.map((option) => (
                <option key={option.value || "all"} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <label className="grid gap-1 text-sm font-semibold text-neutral-700">
            Entity
            <input
              className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-brand-400"
              placeholder="Template, BroadcastMessage, Role"
              value={filters.entity}
              onChange={(event) => setFilters((prev) => ({ ...prev, entity: event.target.value }))}
            />
          </label>
          <label className="grid gap-1 text-sm font-semibold text-neutral-700">
            Date from
            <input
              className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-brand-400"
              type="date"
              value={filters.date_from}
              onChange={(event) => setFilters((prev) => ({ ...prev, date_from: event.target.value }))}
            />
          </label>
          <label className="grid gap-1 text-sm font-semibold text-neutral-700">
            Date to
            <input
              className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-brand-400"
              type="date"
              value={filters.date_to}
              onChange={(event) => setFilters((prev) => ({ ...prev, date_to: event.target.value }))}
            />
          </label>
          <label className="grid gap-1 text-sm font-semibold text-neutral-700">
            LGA
            <input
              className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-brand-400"
              placeholder="Ikeja or LGA ID"
              value={filters.lga}
              onChange={(event) => setFilters((prev) => ({ ...prev, lga: event.target.value }))}
            />
          </label>
          <label className="grid gap-1 text-sm font-semibold text-neutral-700 md:col-span-2 xl:col-span-4">
            Facility
            <input
              className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm outline-none focus:border-brand-400"
              placeholder="Facility name or facility ID"
              value={filters.facility}
              onChange={(event) => setFilters((prev) => ({ ...prev, facility: event.target.value }))}
            />
          </label>
        </div>
      </section>

      <section className="overflow-hidden rounded-xl border border-neutral-200 bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-neutral-200 px-5 py-4">
          <div>
            <p className="text-sm font-bold text-neutral-950">Audit activity</p>
            <p className="mt-1 text-sm text-neutral-500">Showing the newest state-scoped events first.</p>
          </div>
          <div className="rounded-full bg-neutral-100 px-3 py-1 text-xs font-bold uppercase tracking-[0.16em] text-neutral-600">
            {logs?.length || 0} records
          </div>
        </div>

        {logsQuery.isError ? (
          <div className="px-5 py-6 text-sm text-danger-700">
            {getApiErrorMessage(logsQuery.error, "Could not load state audit logs.")}
          </div>
        ) : null}

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-neutral-200 text-sm">
            <thead className="bg-neutral-50">
              <tr>
                {["Timestamp", "Actor", "Role", "Event", "Module", "Entity", "Scope", "Status", "Risk"].map((header) => (
                  <th key={header} className="px-4 py-3 text-left text-xs font-bold uppercase tracking-[0.16em] text-neutral-500">
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100">
              {(logs || []).map((log: StateAuditLogItem) => (
                <tr key={log.id} className="align-top hover:bg-neutral-50/80">
                  <td className="px-4 py-3 text-neutral-600">
                    <div className="min-w-[144px]">{new Date(log.created_at).toLocaleString("en-NG")}</div>
                  </td>
                  <td className="px-4 py-3">
                    <p className="font-semibold text-neutral-900">{log.actor_name || log.actor_email || "System"}</p>
                    <p className="text-xs text-neutral-500">{log.actor_email || "Platform event"}</p>
                  </td>
                  <td className="px-4 py-3 text-neutral-600">{log.actor_role || "-"}</td>
                  <td className="px-4 py-3">
                    <p className="font-semibold text-neutral-900">{log.event}</p>
                    <p className="text-xs text-neutral-500">{log.action.replaceAll("_", " ")}</p>
                  </td>
                  <td className="px-4 py-3 text-neutral-600">{log.module}</td>
                  <td className="px-4 py-3">
                    <p className="text-neutral-800">{log.entity_label}</p>
                    <p className="text-xs text-neutral-500">{log.target_id ? `#${log.target_id.slice(0, 12)}` : "-"}</p>
                  </td>
                  <td className="px-4 py-3 text-neutral-600">
                    <p>{log.lga_name || "State-wide"}</p>
                    <p className="text-xs text-neutral-500">{log.facility_name || log.organization_name || "-"}</p>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-bold capitalize ring-1 ${toneForStatus(log.status)}`}>
                      {log.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-bold capitalize ring-1 ${toneForRisk(log.risk_level)}`}>
                      {log.risk_level}
                    </span>
                  </td>
                </tr>
              ))}
              {!logsQuery.isLoading && !(logs || []).length ? (
                <tr>
                  <td className="px-4 py-8 text-center text-sm text-neutral-500" colSpan={9}>
                    No audit logs match these filters yet.
                  </td>
                </tr>
              ) : null}
              {logsQuery.isLoading ? (
                <tr>
                  <td className="px-4 py-8 text-center text-sm text-neutral-500" colSpan={9}>
                    Loading audit logs...
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
