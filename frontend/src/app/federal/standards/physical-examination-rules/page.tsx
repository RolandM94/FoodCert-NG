"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { StandardsPolicyWorkspaceShell } from "@/features/standards/standards-policy-workspaces";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { listPhysicalExaminationRules, listPolicyVersions } from "@/lib/api/standards";
import { PhysicalExamRuleFormDrawer } from "@/features/standards/physical-exam-rule-form-drawer";
import type { PhysicalExaminationRule } from "@/types/standards";

export default function PhysicalExaminationRulesPage() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerMode, setDrawerMode] = useState<"create" | "edit">("create");
  const [editing, setEditing] = useState<PhysicalExaminationRule | null>(null);
  const [policyVersionId, setPolicyVersionId] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["standards-physical-exam-rules"],
    queryFn: () => listPhysicalExaminationRules(),
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

  function openEdit(row: PhysicalExaminationRule) {
    setPolicyVersionId(row.policy_version);
    setEditing(row);
    setDrawerMode("edit");
    setDrawerOpen(true);
  }

  const columns: DataTableColumn<PhysicalExaminationRule>[] = [
    {
      key: "indicator_name",
      header: "Indicator",
      render: (row) => (
        <button onClick={() => openEdit(row)} className="font-medium text-brand-700 hover:underline">
          {row.indicator_name}
        </button>
      ),
    },
    { key: "code", header: "Code", render: (row) => row.code },
    {
      key: "severity",
      header: "Severity",
      render: (row) => (
        <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${
          row.severity === "critical" ? "bg-danger-50 text-danger-700" :
          row.severity === "high" ? "bg-warning-50 text-warning-700" :
          row.severity === "medium" ? "bg-info-50 text-info-700" :
          "bg-brand-50 text-brand-700"
        }`}>
          {row.severity.charAt(0).toUpperCase() + row.severity.slice(1)}
        </span>
      ),
    },
    {
      key: "blocks_certification",
      header: "Blocks Cert",
      render: (row) => (
        <span className={row.blocks_certification ? "font-medium text-danger-700" : "text-neutral-500"}>
          {row.blocks_certification ? "Yes" : "No"}
        </span>
      ),
    },
    {
      key: "requires_exclusion",
      header: "Exclusion",
      render: (row) => (
        <span className={row.requires_exclusion ? "font-medium text-warning-700" : "text-neutral-500"}>
          {row.requires_exclusion ? "Yes" : "No"}
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
    <StandardsPolicyWorkspaceShell workspace="assessment-standards"
      title="Physical Examination Rules"
      description="Define physical examination checklist items and symptom triggers."
    >
      <div className="grid gap-5">
        <section className="flex items-center justify-between rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <p className="text-sm text-neutral-600">{rows.length} indicators</p>
          <button
            onClick={openCreate}
            disabled={draftVersions.length === 0}
            className="inline-flex h-10 items-center gap-2 rounded-md bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
          >
            Add Indicator
          </button>
        </section>

        {draftVersions.length === 0 && (
          <div className="rounded border border-warning-100 bg-warning-50 p-3 text-sm text-warning-700">
            Create a draft policy version before adding new indicators.
          </div>
        )}

        {isLoading ? (
          <p className="text-sm text-neutral-500">Loading...</p>
        ) : (
          <DataTable<PhysicalExaminationRule>
            columns={columns}
            rows={rows}
            empty="No physical examination rules configured."
          />
        )}
      </div>

      <PhysicalExamRuleFormDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        onSuccess={() => setDrawerOpen(false)}
        mode={drawerMode}
        policyVersionId={policyVersionId}
        initial={editing}
      />
    </StandardsPolicyWorkspaceShell>
  );
}
