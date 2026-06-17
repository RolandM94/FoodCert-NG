"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { StandardsPolicyWorkspaceShell } from "@/features/standards/standards-policy-workspaces";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { listStateConfigControls, listPolicyVersions } from "@/lib/api/standards";
import { StateConfigControlFormDrawer } from "@/features/standards/state-config-control-form-drawer";
import type { StateConfigurationControl } from "@/types/standards";

export default function StateConfigControlsPage() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerMode, setDrawerMode] = useState<"create" | "edit">("create");
  const [editing, setEditing] = useState<StateConfigurationControl | null>(null);
  const [policyVersionId, setPolicyVersionId] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["standards-state-config-controls"],
    queryFn: () => listStateConfigControls(),
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

  function openEdit(row: StateConfigurationControl) {
    setPolicyVersionId(row.policy_version);
    setEditing(row);
    setDrawerMode("edit");
    setDrawerOpen(true);
  }

  const columns: DataTableColumn<StateConfigurationControl>[] = [
    {
      key: "label",
      header: "Label",
      render: (row) => (
        <button onClick={() => openEdit(row)} className="font-medium text-brand-700 hover:underline">
          {row.label}
        </button>
      ),
    },
    {
      key: "config_domain",
      header: "Domain",
      render: (row) => <code className="text-xs text-neutral-600">{row.config_domain}</code>,
    },
    {
      key: "federal_locked",
      header: "Federal Control",
      render: (row) => (
        <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${
          row.federal_locked ? "bg-danger-50 text-danger-700" : "bg-brand-50 text-brand-700"
        }`}>
          {row.federal_locked ? "Locked" : "Unlocked"}
        </span>
      ),
    },
    {
      key: "state_editable",
      header: "State Editable",
      render: (row) => (
        <span className={row.state_editable ? "font-medium text-brand-700" : "text-neutral-500"}>
          {row.state_editable ? "Yes" : "No"}
        </span>
      ),
    },
    {
      key: "requires_federal_approval",
      header: "Fed. Approval",
      render: (row) => (
        <span className={row.requires_federal_approval ? "font-medium text-warning-700" : "text-neutral-500"}>
          {row.requires_federal_approval ? "Required" : "No"}
        </span>
      ),
    },
  ];

  return (
    <StandardsPolicyWorkspaceShell workspace="certification-facilities" title="State Configuration Controls" description="Define which implementation settings States can configure and which Federal rules are locked.">
      <div className="grid gap-5">        <section className="flex items-center justify-between rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <p className="text-sm text-neutral-600">{rows.length} controls</p>
          <button onClick={openCreate} disabled={draftVersions.length === 0} className="inline-flex h-10 items-center gap-2 rounded-md bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50">
            Add Control
          </button>
        </section>
        {draftVersions.length === 0 && (
          <div className="rounded border border-warning-100 bg-warning-50 p-3 text-sm text-warning-700">Create a draft policy version before adding state configuration controls.</div>
        )}
        {isLoading ? <p className="text-sm text-neutral-500">Loading...</p> : (
          <DataTable<StateConfigurationControl> columns={columns} rows={rows} empty="No state configuration controls configured." />
        )}
      </div>
      <StateConfigControlFormDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} onSuccess={() => setDrawerOpen(false)} mode={drawerMode} policyVersionId={policyVersionId} initial={editing} />
    </StandardsPolicyWorkspaceShell>
  );
}
