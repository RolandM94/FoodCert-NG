"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { StandardsPolicyWorkspaceShell } from "@/features/standards/standards-policy-workspaces";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { listFacilityRequirements, listPolicyVersions } from "@/lib/api/standards";
import { FacilityRequirementFormDrawer } from "@/features/standards/facility-requirement-form-drawer";
import type { FacilityRequirementRule } from "@/types/standards";

const CATEGORY_LABELS: Record<string, string> = {
  documentation: "Documentation",
  staffing: "Staffing",
  equipment: "Equipment",
  digital_infrastructure: "Digital Infrastructure",
  records: "Records Management",
  certification: "Certificate Capability",
  reaccreditation: "Re-accreditation",
};

export default function FacilityRequirementsPage() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerMode, setDrawerMode] = useState<"create" | "edit">("create");
  const [editing, setEditing] = useState<FacilityRequirementRule | null>(null);
  const [policyVersionId, setPolicyVersionId] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["standards-facility-requirements"],
    queryFn: () => listFacilityRequirements(),
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

  function openEdit(row: FacilityRequirementRule) {
    setPolicyVersionId(row.policy_version);
    setEditing(row);
    setDrawerMode("edit");
    setDrawerOpen(true);
  }

  const columns: DataTableColumn<FacilityRequirementRule>[] = [
    {
      key: "requirement_name",
      header: "Requirement",
      render: (row) => (
        <button onClick={() => openEdit(row)} className="font-medium text-brand-700 hover:underline">
          {row.requirement_name}
        </button>
      ),
    },
    { key: "requirement_code", header: "Code", render: (row) => row.requirement_code },
    {
      key: "category",
      header: "Category",
      render: (row) => (
        <span className="inline-flex rounded-full bg-neutral-100 px-2.5 py-0.5 text-xs font-medium text-neutral-700">
          {CATEGORY_LABELS[row.category] || row.category}
        </span>
      ),
    },
    {
      key: "mandatory",
      header: "Mandatory",
      render: (row) => (
        <span className={row.mandatory ? "font-medium text-brand-700" : "text-neutral-500"}>
          {row.mandatory ? "Yes" : "No"}
        </span>
      ),
    },
    {
      key: "evidence_type",
      header: "Evidence",
      render: (row) => row.evidence_type.charAt(0).toUpperCase() + row.evidence_type.slice(1),
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
    <StandardsPolicyWorkspaceShell workspace="certification-facilities" title="Medical Facility Requirements" description="Define minimum requirements for medical facilities conducting food handler assessments.">
      <div className="grid gap-5">        <section className="flex items-center justify-between rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <p className="text-sm text-neutral-600">{rows.length} requirements</p>
          <button onClick={openCreate} disabled={draftVersions.length === 0} className="inline-flex h-10 items-center gap-2 rounded-md bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50">
            Add Requirement
          </button>
        </section>
        {draftVersions.length === 0 && (
          <div className="rounded border border-warning-100 bg-warning-50 p-3 text-sm text-warning-700">Create a draft policy version before adding facility requirements.</div>
        )}
        {isLoading ? <p className="text-sm text-neutral-500">Loading...</p> : (
          <DataTable<FacilityRequirementRule> columns={columns} rows={rows} empty="No facility requirement rules configured." />
        )}
      </div>
      <FacilityRequirementFormDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} onSuccess={() => setDrawerOpen(false)} mode={drawerMode} policyVersionId={policyVersionId} initial={editing} />
    </StandardsPolicyWorkspaceShell>
  );
}
