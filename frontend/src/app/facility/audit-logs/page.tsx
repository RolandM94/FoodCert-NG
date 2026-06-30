"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { getApiErrorMessage } from "@/lib/api/client";
import { getCurrentMedicalFacility, listFacilityAuditLogs } from "@/lib/api/facilities";

type Filters = {
  actor: string;
  role: string;
  action: string;
  assessment_id: string;
  entity_type: string;
  date_from: string;
  date_to: string;
};

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export default function FacilityAuditLogsPage() {
  const [filters, setFilters] = useState<Filters>({
    actor: "",
    role: "",
    action: "",
    assessment_id: "",
    entity_type: "",
    date_from: "",
    date_to: "",
  });

  const facilityQuery = useQuery({
    queryKey: ["facility-current-profile", "audit-logs"],
    queryFn: getCurrentMedicalFacility,
  });

  const auditQuery = useQuery({
    queryKey: ["facility-audit-logs", facilityQuery.data?.id, filters],
    enabled: Boolean(facilityQuery.data?.id),
    queryFn: () =>
      listFacilityAuditLogs(
        facilityQuery.data!.id,
        Object.fromEntries(Object.entries(filters).filter(([, value]) => value))
      ),
  });

  const logs = useMemo(() => auditQuery.data ?? [], [auditQuery.data]);

  return (
    <PortalShell
      role="facility_admin"
      title="Audit Logs"
      description="Review facility-scoped operational, clinical, financial, and security activity with focused filters."
    >
      <div className="grid gap-6">
        <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Actor
              <input
                className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm"
                value={filters.actor}
                onChange={(event) => setFilters((prev) => ({ ...prev, actor: event.target.value }))}
                placeholder="Name or email"
              />
            </label>
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Role
              <input
                className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm"
                value={filters.role}
                onChange={(event) => setFilters((prev) => ({ ...prev, role: event.target.value }))}
                placeholder="Finance, Doctor, Compliance..."
              />
            </label>
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Action
              <select
                className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm"
                value={filters.action}
                onChange={(event) => setFilters((prev) => ({ ...prev, action: event.target.value }))}
              >
                <option value="">All actions</option>
                <option value="create">Create</option>
                <option value="update">Update</option>
                <option value="workflow_transition">Workflow transition</option>
                <option value="payment_event">Payment event</option>
                <option value="medical_record_access">Medical record access</option>
                <option value="certificate_event">Certificate event</option>
                <option value="security_event">Security event</option>
              </select>
            </label>
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Entity Type
              <input
                className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm"
                value={filters.entity_type}
                onChange={(event) => setFilters((prev) => ({ ...prev, entity_type: event.target.value }))}
                placeholder="Assessment, Certificate, PaymentTransaction..."
              />
            </label>
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Assessment ID
              <input
                className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm"
                value={filters.assessment_id}
                onChange={(event) => setFilters((prev) => ({ ...prev, assessment_id: event.target.value }))}
                placeholder="Assessment reference"
              />
            </label>
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Date From
              <input
                className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm"
                type="date"
                value={filters.date_from}
                onChange={(event) => setFilters((prev) => ({ ...prev, date_from: event.target.value }))}
              />
            </label>
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Date To
              <input
                className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm"
                type="date"
                value={filters.date_to}
                onChange={(event) => setFilters((prev) => ({ ...prev, date_to: event.target.value }))}
              />
            </label>
            <div className="flex items-end">
              <button
                className="h-11 rounded-lg border border-neutral-200 px-4 text-sm font-semibold text-neutral-700"
                type="button"
                onClick={() =>
                  setFilters({
                    actor: "",
                    role: "",
                    action: "",
                    assessment_id: "",
                    entity_type: "",
                    date_from: "",
                    date_to: "",
                  })
                }
              >
                Clear filters
              </button>
            </div>
          </div>
        </section>

        {auditQuery.isError ? (
          <div className="rounded-lg border border-danger-200 bg-danger-50 p-4 text-sm font-semibold text-danger-700">
            {getApiErrorMessage(auditQuery.error, "Could not load facility audit logs.")}
          </div>
        ) : null}

        <section className="overflow-hidden rounded-lg border border-neutral-200 bg-white shadow-sm">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-neutral-200 text-sm">
              <thead className="bg-neutral-50">
                <tr>
                  {["Date", "Actor", "Role", "Action", "Entity", "Status", "IP Address"].map((header) => (
                    <th key={header} className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-neutral-500">
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-100">
                {logs.map((log) => (
                  <tr key={log.id} className="bg-white">
                    <td className="px-4 py-3 text-neutral-600">{formatDateTime(log.created_at)}</td>
                    <td className="px-4 py-3">
                      <p className="font-semibold text-neutral-900">{log.actor_name || log.actor_email || "System"}</p>
                      <p className="text-xs text-neutral-500">{log.actor_email || "No email"}</p>
                    </td>
                    <td className="px-4 py-3 text-neutral-600">{log.actor_role || "System"}</td>
                    <td className="px-4 py-3">
                      <p className="font-semibold text-neutral-900">{log.event}</p>
                      <p className="text-xs text-neutral-500">{log.action}</p>
                    </td>
                    <td className="px-4 py-3 text-neutral-600">
                      {log.target_type || "Platform"} {log.target_id ? `#${log.target_id.slice(0, 8)}` : ""}
                    </td>
                    <td className="px-4 py-3"><StatusBadge status={log.status} /></td>
                    <td className="px-4 py-3 text-neutral-600">{log.ip_address || "-"}</td>
                  </tr>
                ))}
                {!auditQuery.isLoading && !logs.length ? (
                  <tr>
                    <td className="px-4 py-6 text-sm text-neutral-500" colSpan={7}>
                      No audit logs match these filters.
                    </td>
                  </tr>
                ) : null}
                {auditQuery.isLoading ? (
                  <tr>
                    <td className="px-4 py-6 text-sm text-neutral-500" colSpan={7}>
                      Loading audit logs...
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
