"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Download, Search } from "lucide-react";

import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { StandardsPolicyWorkspaceShell } from "@/features/standards/standards-policy-workspaces";
import { exportStandardsAuditLogs, listStandardsAuditLogs } from "@/lib/api/standards";
import type { StandardsAuditLog } from "@/types/standards";

const ACTIONS = [
  "create",
  "update",
  "delete",
  "workflow_transition",
  "security_event",
];

const TARGET_TYPES = [
  "PolicyVersion",
  "FoodHandlerCategory",
  "EstablishmentCategory",
  "MedicalTestRule",
  "PhysicalExaminationRule",
  "VaccinationRule",
  "CertificateTemplate",
  "CertificateValidityRule",
  "ReturnToWorkRule",
  "FacilityRequirementRule",
  "ReportingTemplate",
  "MEIndicator",
  "PolicyDocument",
  "Approval",
  "StateAcknowledgement",
  "StateConfigurationControl",
];

function formatLabel(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase());
}

function eventLabel(row: StandardsAuditLog) {
  return row.event || String(row.metadata?.event ?? "") || row.action;
}

function compactJson(value: Record<string, unknown> | null) {
  if (!value || Object.keys(value).length === 0) return "No captured values.";
  return JSON.stringify(value, null, 2);
}

function activeFilters(filters: Record<string, string>) {
  return Object.fromEntries(Object.entries(filters).filter(([, value]) => value.trim()));
}

export default function ChangeHistoryPage() {
  const [filters, setFilters] = useState({
    search: "",
    action: "",
    target_type: "",
    target_id: "",
    policy_version: "",
    date_from: "",
    date_to: "",
  });
  const queryParams = useMemo(() => activeFilters(filters), [filters]);
  const [selectedId, setSelectedId] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["standards-change-history", queryParams],
    queryFn: () => listStandardsAuditLogs(queryParams),
  });

  const rows = useMemo(() => Array.isArray(data) ? data : [], [data]);
  const selected = rows.find((row) => row.id === selectedId) ?? rows[0] ?? null;

  const exportMutation = useMutation({
    mutationFn: () => exportStandardsAuditLogs(queryParams),
  });

  function updateFilter(field: keyof typeof filters, value: string) {
    setFilters((prev) => ({ ...prev, [field]: value }));
  }

  const columns: DataTableColumn<StandardsAuditLog>[] = [
    {
      key: "created_at",
      header: "Date",
      render: (row) => new Date(row.created_at).toLocaleString(),
    },
    {
      key: "actor_name",
      header: "Actor",
      render: (row) => row.actor_name || row.actor_email || "System",
    },
    {
      key: "action",
      header: "Action",
      render: (row) => (
        <span className="inline-flex rounded-full bg-neutral-100 px-2.5 py-0.5 text-xs font-medium text-neutral-700">
          {formatLabel(row.action)}
        </span>
      ),
    },
    {
      key: "target_type",
      header: "Entity",
      render: (row) => (
        <button onClick={() => setSelectedId(row.id)} className="text-left font-medium text-brand-700 hover:underline">
          {row.target_type}
        </button>
      ),
    },
    {
      key: "event",
      header: "Event",
      render: (row) => formatLabel(eventLabel(row)),
    },
    {
      key: "state_name",
      header: "Scope",
      render: (row) => row.state_name || "National",
    },
  ];

  return (
    <StandardsPolicyWorkspaceShell workspace="policy-governance" title="Change History" description="Review audit trail of all standards and policy configuration changes.">
      <div className="grid gap-5">
        <section className="grid gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm xl:grid-cols-[1.2fr_180px_220px_180px_180px]">
          <label className="text-sm font-medium text-neutral-700">
            Search
            <div className="mt-1 flex h-10 items-center gap-2 rounded border border-neutral-200 bg-neutral-50 px-3">
              <Search size={15} className="text-neutral-400" />
              <input className="w-full bg-transparent text-sm outline-none" value={filters.search} onChange={(event) => updateFilter("search", event.target.value)} placeholder="Actor, entity, event" />
            </div>
          </label>
          <label className="text-sm font-medium text-neutral-700">
            Action
            <select className="mt-1 h-10 w-full rounded border border-neutral-200 bg-white px-3 text-sm" value={filters.action} onChange={(event) => updateFilter("action", event.target.value)}>
              <option value="">All actions</option>
              {ACTIONS.map((action) => <option key={action} value={action}>{formatLabel(action)}</option>)}
            </select>
          </label>
          <label className="text-sm font-medium text-neutral-700">
            Entity
            <select className="mt-1 h-10 w-full rounded border border-neutral-200 bg-white px-3 text-sm" value={filters.target_type} onChange={(event) => updateFilter("target_type", event.target.value)}>
              <option value="">All entities</option>
              {TARGET_TYPES.map((target) => <option key={target} value={target}>{target}</option>)}
            </select>
          </label>
          <label className="text-sm font-medium text-neutral-700">
            From
            <input type="date" className="mt-1 h-10 w-full rounded border border-neutral-200 bg-white px-3 text-sm" value={filters.date_from} onChange={(event) => updateFilter("date_from", event.target.value)} />
          </label>
          <label className="text-sm font-medium text-neutral-700">
            To
            <input type="date" className="mt-1 h-10 w-full rounded border border-neutral-200 bg-white px-3 text-sm" value={filters.date_to} onChange={(event) => updateFilter("date_to", event.target.value)} />
          </label>
          <label className="text-sm font-medium text-neutral-700 xl:col-span-2">
            Policy Version ID
            <input className="mt-1 h-10 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" value={filters.policy_version} onChange={(event) => updateFilter("policy_version", event.target.value)} placeholder="Filter by policy version UUID" />
          </label>
          <label className="text-sm font-medium text-neutral-700 xl:col-span-2">
            Entity ID
            <input className="mt-1 h-10 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" value={filters.target_id} onChange={(event) => updateFilter("target_id", event.target.value)} placeholder="Filter by entity UUID" />
          </label>
          <div className="flex items-end">
            <button
              type="button"
              onClick={() => exportMutation.mutate()}
              disabled={exportMutation.isPending}
              className="inline-flex h-10 w-full items-center justify-center gap-2 rounded border border-neutral-200 px-3 text-sm font-semibold text-neutral-700 hover:bg-neutral-50 disabled:opacity-60"
            >
              <Download size={15} />
              CSV
            </button>
          </div>
        </section>

        <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_440px]">
          <DataTable<StandardsAuditLog>
            columns={columns}
            rows={rows}
            empty={isLoading ? "Loading change history..." : "No change history records match these filters."}
          />

          <aside className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            {selected ? (
              <div className="grid gap-4">
                <div>
                  <p className="text-xs font-semibold uppercase text-neutral-500">Audit Record</p>
                  <h2 className="mt-1 text-base font-semibold text-neutral-900">{formatLabel(eventLabel(selected))}</h2>
                  <p className="mt-1 text-sm text-neutral-500">{selected.target_type} {selected.target_id}</p>
                </div>

                <div className="grid gap-2 text-sm">
                  <div className="flex justify-between gap-3"><span className="text-neutral-500">Actor</span><span className="text-right text-neutral-900">{selected.actor_name || selected.actor_email || "System"}</span></div>
                  <div className="flex justify-between gap-3"><span className="text-neutral-500">Action</span><span className="text-neutral-900">{formatLabel(selected.action)}</span></div>
                  <div className="flex justify-between gap-3"><span className="text-neutral-500">Scope</span><span className="text-neutral-900">{selected.state_name || "National"}</span></div>
                  <div className="flex justify-between gap-3"><span className="text-neutral-500">IP Address</span><span className="text-neutral-900">{selected.ip_address || "-"}</span></div>
                  <div className="flex justify-between gap-3"><span className="text-neutral-500">Time</span><span className="text-right text-neutral-900">{new Date(selected.created_at).toLocaleString()}</span></div>
                </div>

                <div className="grid gap-3">
                  <div>
                    <p className="mb-1 text-xs font-semibold uppercase text-neutral-500">Old Value</p>
                    <pre className="max-h-52 overflow-auto rounded bg-neutral-950 p-3 text-xs text-neutral-50">{compactJson(selected.old_value)}</pre>
                  </div>
                  <div>
                    <p className="mb-1 text-xs font-semibold uppercase text-neutral-500">New Value</p>
                    <pre className="max-h-52 overflow-auto rounded bg-neutral-950 p-3 text-xs text-neutral-50">{compactJson(selected.new_value)}</pre>
                  </div>
                  <div>
                    <p className="mb-1 text-xs font-semibold uppercase text-neutral-500">Metadata</p>
                    <pre className="max-h-40 overflow-auto rounded bg-neutral-950 p-3 text-xs text-neutral-50">{compactJson(selected.metadata)}</pre>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-sm text-neutral-500">Select a change record to inspect old and new values.</p>
            )}
          </aside>
        </div>
      </div>
    </StandardsPolicyWorkspaceShell>
  );
}
