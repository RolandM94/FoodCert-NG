"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { StandardsPolicyWorkspaceShell } from "@/features/standards/standards-policy-workspaces";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { listReturnToWorkRules, listPolicyVersions } from "@/lib/api/standards";
import { ReturnToWorkFormDrawer } from "@/features/standards/return-to-work-form-drawer";
import type { ReturnToWorkRule } from "@/types/standards";

export default function ReturnToWorkPage() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerMode, setDrawerMode] = useState<"create" | "edit">("create");
  const [editing, setEditing] = useState<ReturnToWorkRule | null>(null);
  const [policyVersionId, setPolicyVersionId] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["standards-return-to-work"],
    queryFn: () => listReturnToWorkRules(),
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

  function openEdit(row: ReturnToWorkRule) {
    setPolicyVersionId(row.policy_version);
    setEditing(row);
    setDrawerMode("edit");
    setDrawerOpen(true);
  }

  const columns: DataTableColumn<ReturnToWorkRule>[] = [
    {
      key: "condition_name",
      header: "Condition",
      render: (row) => (
        <button onClick={() => openEdit(row)} className="font-medium text-brand-700 hover:underline">
          {row.condition_name}
        </button>
      ),
    },
    { key: "condition_code", header: "Code", render: (row) => row.condition_code },
    { key: "default_exclusion_hours", header: "Exclusion (hrs)", render: (row) => row.default_exclusion_hours },
    {
      key: "requires_medical_clearance",
      header: "Medical Clearance",
      render: (row) => (
        <span className={row.requires_medical_clearance ? "font-medium text-brand-700" : "text-neutral-500"}>
          {row.requires_medical_clearance ? "Yes" : "No"}
        </span>
      ),
    },
    {
      key: "requires_lab_clearance",
      header: "Lab Clearance",
      render: (row) => (
        <span className={row.requires_lab_clearance ? "font-medium text-brand-700" : "text-neutral-500"}>
          {row.requires_lab_clearance ? "Yes" : "No"}
        </span>
      ),
    },
    {
      key: "requires_health_authority_approval",
      header: "Authority Approval",
      render: (row) => (
        <span className={row.requires_health_authority_approval ? "font-medium text-danger-700" : "text-neutral-500"}>
          {row.requires_health_authority_approval ? "Yes" : "No"}
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
    <StandardsPolicyWorkspaceShell workspace="assessment-standards" title="Return-to-Work Rules" description="Configure exclusion triggers and return-to-work clearance requirements.">
      <div className="grid gap-5">        <section className="flex items-center justify-between rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <p className="text-sm text-neutral-600">{rows.length} condition rules</p>
          <button onClick={openCreate} disabled={draftVersions.length === 0} className="inline-flex h-10 items-center gap-2 rounded-md bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50">
            Add Condition Rule
          </button>
        </section>
        {draftVersions.length === 0 && (
          <div className="rounded border border-warning-100 bg-warning-50 p-3 text-sm text-warning-700">Create a draft policy version before adding condition rules.</div>
        )}
        {isLoading ? <p className="text-sm text-neutral-500">Loading...</p> : (
          <DataTable<ReturnToWorkRule> columns={columns} rows={rows} empty="No return-to-work rules configured." />
        )}
      </div>
      <ReturnToWorkFormDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} onSuccess={() => setDrawerOpen(false)} mode={drawerMode} policyVersionId={policyVersionId} initial={editing} />
    </StandardsPolicyWorkspaceShell>
  );
}
