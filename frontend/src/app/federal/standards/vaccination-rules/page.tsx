"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { StandardsPolicyWorkspaceShell } from "@/features/standards/standards-policy-workspaces";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { listVaccinationRules, listPolicyVersions } from "@/lib/api/standards";
import { VaccinationRuleFormDrawer } from "@/features/standards/vaccination-rule-form-drawer";
import type { VaccinationRule } from "@/types/standards";

export default function VaccinationRulesPage() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerMode, setDrawerMode] = useState<"create" | "edit">("create");
  const [editing, setEditing] = useState<VaccinationRule | null>(null);
  const [policyVersionId, setPolicyVersionId] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["standards-vaccination-rules"],
    queryFn: () => listVaccinationRules(),
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

  function openEdit(row: VaccinationRule) {
    setPolicyVersionId(row.policy_version);
    setEditing(row);
    setDrawerMode("edit");
    setDrawerOpen(true);
  }

  const columns: DataTableColumn<VaccinationRule>[] = [
    {
      key: "vaccine_name",
      header: "Vaccine",
      render: (row) => (
        <button onClick={() => openEdit(row)} className="font-medium text-brand-700 hover:underline">
          {row.vaccine_name}
        </button>
      ),
    },
    { key: "vaccine_code", header: "Code", render: (row) => row.vaccine_code },
    {
      key: "required",
      header: "Required",
      render: (row) => (
        <span className={row.required ? "font-medium text-brand-700" : "text-neutral-500"}>
          {row.required ? "Yes" : "No"}
        </span>
      ),
    },
    {
      key: "dose_schedule",
      header: "Doses",
      render: (row) => {
        const doses = Array.isArray(row.dose_schedule) ? row.dose_schedule.length : 0;
        return `${doses} dose${doses !== 1 ? "s" : ""}`;
      },
    },
    {
      key: "validity_months",
      header: "Validity",
      render: (row) => row.validity_months !== null ? `${row.validity_months} mo` : "\u2014",
    },
    {
      key: "blocks_certification_if_missing",
      header: "Blocks if Missing",
      render: (row) => (
        <span className={row.blocks_certification_if_missing ? "font-medium text-danger-700" : "text-neutral-500"}>
          {row.blocks_certification_if_missing ? "Yes" : "No"}
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
      title="Vaccination Rules"
      description="Configure vaccine requirements, schedules, and certification impact."
    >
      <div className="grid gap-5">
        <section className="flex items-center justify-between rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <p className="text-sm text-neutral-600">{rows.length} vaccine rules</p>
          <button
            onClick={openCreate}
            disabled={draftVersions.length === 0}
            className="inline-flex h-10 items-center gap-2 rounded-md bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
          >
            Add Vaccine Rule
          </button>
        </section>

        {draftVersions.length === 0 && (
          <div className="rounded border border-warning-100 bg-warning-50 p-3 text-sm text-warning-700">
            Create a draft policy version before adding new vaccine rules.
          </div>
        )}

        {isLoading ? (
          <p className="text-sm text-neutral-500">Loading...</p>
        ) : (
          <DataTable<VaccinationRule>
            columns={columns}
            rows={rows}
            empty="No vaccination rules configured."
          />
        )}
      </div>

      <VaccinationRuleFormDrawer
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
