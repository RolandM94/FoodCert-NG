"use client";

import { useState } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { StandardsPolicyWorkspaceShell } from "@/features/standards/standards-policy-workspaces";
import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { listPolicyVersions } from "@/lib/api/standards";
import { CreatePolicyVersionForm } from "@/features/standards/create-policy-version-form";
import type { PolicyVersion } from "@/types/standards";

const columns: DataTableColumn<PolicyVersion>[] = [
  {
    key: "version_code",
    header: "Version",
    render: (row) => (
      <Link href={`/federal/standards-policy/policy-governance/policy-versions/${row.id}`} className="font-medium text-brand-700 hover:underline">
        {row.version_code}
      </Link>
    ),
  },
  {
    key: "title",
    header: "Title",
    render: (row) => row.title,
  },
  {
    key: "version_type",
    header: "Type",
    render: (row) => (
      <span className="inline-flex rounded-full bg-neutral-100 px-2.5 py-0.5 text-xs font-medium text-neutral-700">
        {row.version_type}
      </span>
    ),
  },
  {
    key: "status",
    header: "Status",
    render: (row) => (
      <span
        className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${
          row.status === "active"
            ? "bg-brand-50 text-brand-700"
            : row.status === "draft"
              ? "bg-neutral-100 text-neutral-700"
              : row.status === "under_review"
                ? "bg-info-50 text-info-700"
                : row.status === "retired"
                  ? "bg-neutral-100 text-neutral-500"
                  : "bg-warning-50 text-warning-700"
        }`}
      >
        {row.status.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
      </span>
    ),
  },
  {
    key: "effective_start_date",
    header: "Effective Date",
    render: (row) =>
      row.effective_start_date
        ? new Date(row.effective_start_date).toLocaleDateString()
        : "\u2014",
  },
  {
    key: "handler_category_count",
    header: "Categories",
    render: (row) => row.handler_category_count,
  },
  {
    key: "created_at",
    header: "Created",
    render: (row) => new Date(row.created_at).toLocaleDateString(),
  },
];

export default function PolicyVersionsPage() {
  const [showCreate, setShowCreate] = useState(false);
  const [statusFilter, setStatusFilter] = useState("");
  const { data, isLoading } = useQuery({
    queryKey: ["standards-policy-versions"],
    queryFn: () => listPolicyVersions(),
  });

  const allRows = Array.isArray(data) ? data : [];
  const rows = statusFilter ? allRows.filter((r) => r.status === statusFilter) : allRows;

  return (
    <StandardsPolicyWorkspaceShell workspace="policy-governance"
      title="Policy Versions"
      description="Manage national policy versions and their lifecycle."
    >
      <div className="grid gap-5">
        <section className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div className="flex items-center gap-3">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm"
            >
              <option value="">All Statuses</option>
              <option value="draft">Draft</option>
              <option value="under_review">Under Review</option>
              <option value="approved">Approved</option>
              <option value="active">Active</option>
              <option value="retired">Retired</option>
              <option value="archived">Archived</option>
            </select>
          </div>
          <button
            onClick={() => setShowCreate(!showCreate)}
            className="inline-flex h-10 items-center gap-2 rounded-md bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700"
          >
            {showCreate ? "Cancel" : "Create Policy Version"}
          </button>
        </section>

        {showCreate && (
          <CreatePolicyVersionForm
            onClose={() => setShowCreate(false)}
            onSuccess={() => setShowCreate(false)}
          />
        )}

        {isLoading ? (
          <p className="text-sm text-neutral-500">Loading...</p>
        ) : (
          <DataTable<PolicyVersion>
            columns={columns}
            rows={rows}
            empty="No policy versions yet. Create your first policy version to begin configuring national standards."
          />
        )}
      </div>
    </StandardsPolicyWorkspaceShell>
  );
}
