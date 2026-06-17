"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { StandardsPolicyWorkspaceShell } from "@/features/standards/standards-policy-workspaces";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { listCertificateValidityRules, listPolicyVersions } from "@/lib/api/standards";
import { CertificateValidityFormDrawer } from "@/features/standards/certificate-validity-form-drawer";
import type { CertificateValidityRule } from "@/types/standards";

export default function CertificateValidityPage() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerMode, setDrawerMode] = useState<"create" | "edit">("create");
  const [editing, setEditing] = useState<CertificateValidityRule | null>(null);
  const [policyVersionId, setPolicyVersionId] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["standards-validity-rules"],
    queryFn: () => listCertificateValidityRules(),
  });

  const { data: versions } = useQuery({
    queryKey: ["standards-policy-versions"],
    queryFn: () => listPolicyVersions(),
  });

  const draftVersions = (Array.isArray(versions) ? versions : []).filter(
    (v) => v.status === "draft" || v.status === "returned"
  );
  const rows = Array.isArray(data) ? data : [];

  function openCreate() {
    if (draftVersions.length > 0) setPolicyVersionId(draftVersions[0].id);
    setEditing(null);
    setDrawerMode("create");
    setDrawerOpen(true);
  }

  function openEdit(row: CertificateValidityRule) {
    setPolicyVersionId(row.policy_version);
    setEditing(row);
    setDrawerMode("edit");
    setDrawerOpen(true);
  }

  const columns: DataTableColumn<CertificateValidityRule>[] = [
    {
      key: "certificate_validity_days",
      header: "Validity",
      render: (row) => (
        <button onClick={() => openEdit(row)} className="font-medium text-brand-700 hover:underline">
          {row.certificate_validity_days} days
        </button>
      ),
    },
    { key: "routine_assessment_interval_days", header: "Assessment Interval", render: (row) => `${row.routine_assessment_interval_days} days` },
    { key: "renewal_window_days", header: "Renewal Window", render: (row) => `${row.renewal_window_days} days` },
    { key: "grace_period_days", header: "Grace Period", render: (row) => `${row.grace_period_days} days` },
    {
      key: "expiry_reminder_days",
      header: "Reminders",
      render: (row) => Array.isArray(row.expiry_reminder_days) ? row.expiry_reminder_days.join(", ") + " days" : "\u2014",
    },
    {
      key: "illness_suspension_enabled",
      header: "Illness Suspension",
      render: (row) => (
        <span className={row.illness_suspension_enabled ? "font-medium text-brand-700" : "text-neutral-500"}>
          {row.illness_suspension_enabled ? "Enabled" : "Disabled"}
        </span>
      ),
    },
    {
      key: "status",
      header: "Status",
      render: (row) => (
        <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${
          row.status === "active" ? "bg-brand-50 text-brand-700" :
          row.status === "draft" ? "bg-neutral-100 text-neutral-700" :
          "bg-neutral-100 text-neutral-500"
        }`}>
          {row.status.charAt(0).toUpperCase() + row.status.slice(1)}
        </span>
      ),
    },
  ];

  return (
    <StandardsPolicyWorkspaceShell workspace="certification-facilities" title="Certificate Validity & Expiry Rules" description="Configure certificate validity duration, assessment intervals, and expiry rules.">
      <div className="grid gap-5">        <section className="flex items-center justify-between rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <p className="text-sm text-neutral-600">{rows.length} validity rules</p>
          <button onClick={openCreate} disabled={draftVersions.length === 0} className="inline-flex h-10 items-center gap-2 rounded-md bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50">
            Add Validity Rule
          </button>
        </section>
        {draftVersions.length === 0 && (
          <div className="rounded border border-warning-100 bg-warning-50 p-3 text-sm text-warning-700">Create a draft policy version before adding validity rules.</div>
        )}
        {isLoading ? <p className="text-sm text-neutral-500">Loading...</p> : (
          <DataTable<CertificateValidityRule> columns={columns} rows={rows} empty="No certificate validity rules configured." />
        )}
      </div>
      <CertificateValidityFormDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} onSuccess={() => setDrawerOpen(false)} mode={drawerMode} policyVersionId={policyVersionId} initial={editing} />
    </StandardsPolicyWorkspaceShell>
  );
}
