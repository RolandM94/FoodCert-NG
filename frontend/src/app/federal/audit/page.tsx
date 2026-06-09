"use client";

import { useQuery } from "@tanstack/react-query";
import { History } from "lucide-react";
import { useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchFederalAuditLogs, type FederalAuditLogItem } from "@/lib/api/federal";

function dateLabel(value?: string | null) {
  if (!value) return "Not set";
  return new Date(value).toLocaleString("en-NG", { dateStyle: "medium", timeStyle: "short" });
}

export default function Page() {
  const [search, setSearch] = useState("");
  const [action, setAction] = useState("");
  const logsQuery = useQuery({
    queryKey: ["federal-audit-logs", search, action],
    queryFn: () => fetchFederalAuditLogs({ search, action }),
  });
  const rows = logsQuery.data || [];

  return (
    <PortalShell role="federal_admin" title="Audit" description="Search privacy-safe national audit summaries for ministry, payment, certificate, and security activity.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 md:grid-cols-[1fr_240px]">
            <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search target, id, or metadata" />
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={action} onChange={(event) => setAction(event.target.value)}>
              <option value="">All actions</option>
              <option value="workflow_transition">Workflow transition</option>
              <option value="payment_event">Payment event</option>
              <option value="certificate_event">Certificate event</option>
              <option value="security_event">Security event</option>
              <option value="medical_record_access">Medical record access</option>
            </select>
          </div>
        </section>
        <section className="grid gap-3">
          <div className="flex items-center gap-2"><History className="text-brand-700" size={18} /><h2 className="text-base font-bold text-neutral-900">Recent Audit Activity</h2></div>
          <DataTable<FederalAuditLogItem>
            columns={[
              { key: "time", header: "Time", render: (row) => dateLabel(row.created_at) },
              { key: "actor", header: "Actor", render: (row) => <div><p className="font-bold text-neutral-900">{row.actor_name || "System"}</p><p className="text-xs text-neutral-500">{row.actor_email}</p></div> },
              { key: "action", header: "Action", render: (row) => <StatusCell status={row.action} /> },
              { key: "target", header: "Target", render: (row) => `${row.target_type}:${row.target_id}` },
              { key: "state", header: "State", render: (row) => row.state_name || "National" },
              { key: "risk", header: "Risk", render: (row) => <StatusCell status={row.risk_level} /> },
            ]}
            rows={rows}
            empty={logsQuery.isLoading ? "Loading audit logs..." : "No audit logs match the current filters."}
          />
        </section>
      </div>
    </PortalShell>
  );
}
