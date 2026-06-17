"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { StandardsPolicyWorkspaceShell } from "@/features/standards/standards-policy-workspaces";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { listMedicalTestRules, listPolicyVersions } from "@/lib/api/standards";
import { MedicalTestRuleFormDrawer } from "@/features/standards/medical-test-rule-form-drawer";
import type { MedicalTestRule } from "@/types/standards";

export default function MedicalTestRulesPage() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerMode, setDrawerMode] = useState<"create" | "edit">("create");
  const [editing, setEditing] = useState<MedicalTestRule | null>(null);
  const [policyVersionId, setPolicyVersionId] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["standards-medical-test-rules"],
    queryFn: () => listMedicalTestRules(),
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

  function openEdit(row: MedicalTestRule) {
    setPolicyVersionId(row.policy_version);
    setEditing(row);
    setDrawerMode("edit");
    setDrawerOpen(true);
  }

  const columns: DataTableColumn<MedicalTestRule>[] = [
    {
      key: "name",
      header: "Test Name",
      render: (row) => (
        <button onClick={() => openEdit(row)} className="font-medium text-brand-700 hover:underline">
          {row.name}
        </button>
      ),
    },
    { key: "code", header: "Code", render: (row) => row.code },
    {
      key: "test_type",
      header: "Test Type",
      render: (row) => row.test_type.charAt(0).toUpperCase() + row.test_type.slice(1),
    },
    {
      key: "rule_type",
      header: "Rule Type",
      render: (row) => (
        <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${
          row.rule_type === "mandatory" ? "bg-danger-50 text-danger-700" :
          row.rule_type === "conditional" ? "bg-warning-50 text-warning-700" :
          row.rule_type === "emergency" ? "bg-info-50 text-info-700" :
          "bg-neutral-100 text-neutral-600"
        }`}>
          {row.rule_type.charAt(0).toUpperCase() + row.rule_type.slice(1)}
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
      title="Medical Test Rules"
      description="Configure required, conditional, optional, and emergency medical tests."
    >
      <div className="grid gap-5">
        <section className="flex items-center justify-between rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <p className="text-sm text-neutral-600">{rows.length} test rules</p>
          <button
            onClick={openCreate}
            disabled={draftVersions.length === 0}
            className="inline-flex h-10 items-center gap-2 rounded-md bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
          >
            Add Test Rule
          </button>
        </section>

        {draftVersions.length === 0 && (
          <div className="rounded border border-warning-100 bg-warning-50 p-3 text-sm text-warning-700">
            Create a draft policy version before adding new test rules.
          </div>
        )}

        {isLoading ? (
          <p className="text-sm text-neutral-500">Loading...</p>
        ) : (
          <DataTable<MedicalTestRule>
            columns={columns}
            rows={rows}
            empty="No medical test rules configured."
          />
        )}
      </div>

      <MedicalTestRuleFormDrawer
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
