"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { StandardsPolicyWorkspaceShell } from "@/features/standards/standards-policy-workspaces";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { listFoodHandlerCategories, listPolicyVersions } from "@/lib/api/standards";
import { CategoryFormDrawer } from "@/features/standards/category-form-drawer";
import type { FoodHandlerCategory } from "@/types/standards";

export default function FoodHandlerCategoriesPage() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerMode, setDrawerMode] = useState<"create" | "edit">("create");
  const [editing, setEditing] = useState<FoodHandlerCategory | null>(null);
  const [policyVersionId, setPolicyVersionId] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["standards-handler-categories"],
    queryFn: () => listFoodHandlerCategories(),
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
    if (draftVersions.length > 0) {
      setPolicyVersionId(draftVersions[0].id);
    }
    setEditing(null);
    setDrawerMode("create");
    setDrawerOpen(true);
  }

  function openEdit(row: FoodHandlerCategory) {
    setPolicyVersionId(row.policy_version);
    setEditing(row);
    setDrawerMode("edit");
    setDrawerOpen(true);
  }

  const columns: DataTableColumn<FoodHandlerCategory>[] = [
    {
      key: "name",
      header: "Category",
      render: (row) => (
        <button onClick={() => openEdit(row)} className="font-medium text-brand-700 hover:underline">
          {row.name}
        </button>
      ),
    },
    { key: "code", header: "Code", render: (row) => row.code },
    {
      key: "risk_level",
      header: "Risk Level",
      render: (row) => (
        <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${
          row.risk_level === "high" ? "bg-danger-50 text-danger-700" :
          row.risk_level === "medium" ? "bg-warning-50 text-warning-700" :
          "bg-brand-50 text-brand-700"
        }`}>
          {row.risk_level.charAt(0).toUpperCase() + row.risk_level.slice(1)}
        </span>
      ),
    },
    { key: "certificate_required", header: "Cert Required", render: (row) => row.certificate_required ? "Yes" : "No" },
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
    { key: "policy_version_code", header: "Policy Version", render: (row) => row.policy_version_code },
  ];

  return (
    <StandardsPolicyWorkspaceShell workspace="assessment-standards"
      title="Food Handler Categories"
      description="Define food handler categories covered by the national guideline."
    >
      <div className="grid gap-5">
        <section className="flex items-center justify-between rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <p className="text-sm text-neutral-600">{rows.length} categories</p>
          <button
            onClick={openCreate}
            disabled={draftVersions.length === 0}
            className="inline-flex h-10 items-center gap-2 rounded-md bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
          >
            Add Category
          </button>
        </section>

        {draftVersions.length === 0 && (
          <div className="rounded border border-warning-100 bg-warning-50 p-3 text-sm text-warning-700">
            Create a draft policy version before adding new categories.
          </div>
        )}

        {isLoading ? (
          <p className="text-sm text-neutral-500">Loading...</p>
        ) : (
          <DataTable<FoodHandlerCategory>
            columns={columns}
            rows={rows}
            empty="No food handler categories configured for this policy version."
          />
        )}
      </div>

      <CategoryFormDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        onSuccess={() => setDrawerOpen(false)}
        mode={drawerMode}
        entityType="handler"
        policyVersionId={policyVersionId}
        initial={editing}
      />
    </StandardsPolicyWorkspaceShell>
  );
}
