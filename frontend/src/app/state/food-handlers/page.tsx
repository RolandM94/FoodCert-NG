"use client";

import { useQuery } from "@tanstack/react-query";
import { Download, UsersRound } from "lucide-react";
import { useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { fetchStateFoodHandlers, type StateFoodHandlerMonitoringItem } from "@/lib/api/state";
import { downloadCsv } from "@/lib/export/csv";

function dateLabel(value?: string | null) {
  if (!value) return "Not issued";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

export default function Page() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [certificateStatus, setCertificateStatus] = useState("");
  const handlersQuery = useQuery({
    queryKey: ["state-food-handlers-monitoring", search, status, certificateStatus],
    queryFn: () => fetchStateFoodHandlers({ search, status, certificate_status: certificateStatus }),
  });
  const rows = handlersQuery.data || [];

  return (
    <PortalShell role="state_admin" title="Food handlers" description="Search food handler registry without exposing private medical details unnecessarily.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 md:grid-cols-[1fr_220px_220px_auto]">
            <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search name or system ID" />
            <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={status} onChange={(event) => setStatus(event.target.value)}>
              <option value="">All handler statuses</option>
              <option value="fit">Fit</option>
              <option value="certification_pending">Certification pending</option>
              <option value="temporarily_excluded">Temporarily excluded</option>
              <option value="temporarily_not_fit">Temporarily not fit</option>
              <option value="excluded">Excluded</option>
            </select>
            <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={certificateStatus} onChange={(event) => setCertificateStatus(event.target.value)}>
              <option value="">All certificate statuses</option>
              <option value="active">Active</option>
              <option value="expired">Expired</option>
              <option value="suspended">Suspended</option>
              <option value="revoked">Revoked</option>
              <option value="not_issued">Not issued</option>
            </select>
            <button
              className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-deep px-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-300"
              disabled={!rows.length}
              onClick={() =>
                downloadCsv("state-food-handlers-monitoring.csv", rows, [
                  { header: "Handler", value: (row) => row.full_name },
                  { header: "System ID", value: (row) => row.system_identifier },
                  { header: "Employer", value: (row) => row.employer_name },
                  { header: "Branch", value: (row) => row.branch_name },
                  { header: "LGA", value: (row) => row.lga_name },
                  { header: "Category", value: (row) => row.food_handler_category },
                  { header: "Fitness status", value: (row) => row.current_status },
                  { header: "Certificate status", value: (row) => row.certificate_status },
                  { header: "Certificate number", value: (row) => row.certificate_number },
                  { header: "Certificate expiry", value: (row) => row.certificate_expiry_date },
                  { header: "Active illness status", value: (row) => row.active_illness_status },
                ])
              }
              type="button"
            >
              <Download size={16} />
              Export
            </button>
          </div>
        </section>
        <section className="grid gap-3">
          <div className="flex items-center gap-2"><UsersRound className="text-brand-deep" size={18} /><h2 className="text-base font-bold text-slate-950">Food Handler Monitoring</h2></div>
          <DataTable<StateFoodHandlerMonitoringItem>
            columns={[
              { key: "handler", header: "Handler", render: (row) => <div><p className="font-bold text-slate-950">{row.full_name}</p><p className="text-xs text-slate-500">{row.system_identifier}</p></div> },
              { key: "employer", header: "Employer", render: (row) => row.employer_name || "Not linked" },
              { key: "category", header: "Category", render: (row) => row.food_handler_category.replaceAll("_", " ") },
              { key: "fitness", header: "Fitness", render: (row) => <StatusCell status={row.current_status} /> },
              { key: "certificate", header: "Certificate", render: (row) => <div><StatusCell status={row.certificate_status} /><p className="mt-1 text-xs text-slate-500">{row.certificate_number || "No certificate"} / {dateLabel(row.certificate_expiry_date)}</p></div> },
              { key: "illness", header: "Illness", render: (row) => row.active_illness_status ? <StatusCell status={row.active_illness_status} /> : "None active" },
            ]}
            rows={rows}
            empty={handlersQuery.isLoading ? "Loading food handlers..." : "No food handlers match the current filters."}
          />
        </section>
      </div>
    </PortalShell>
  );
}
