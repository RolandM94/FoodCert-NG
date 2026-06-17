"use client";

import Link from "next/link";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { getApiErrorMessage } from "@/lib/api/client";
import {
  activateReportingTemplate,
  listReportingTemplates,
} from "@/lib/api/standards";
import { StandardsPolicyWorkspaceShell } from "@/features/standards/standards-policy-workspaces";
import type { ReportingTemplate } from "@/types/standards";

const FORM_BUILDER_HREF = "/federal/standards-policy/reporting-me/form-builder?tab=templates&create=reporting-template";

export default function ReportingTemplatesPage() {
  const queryClient = useQueryClient();
  const [actionError, setActionError] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["standards-reporting-templates"],
    queryFn: () => listReportingTemplates(),
  });

  const rows = Array.isArray(data) ? data : [];

  const activateMutation = useMutation({
    mutationFn: activateReportingTemplate,
    onSuccess: () => {
      setActionError("");
      queryClient.invalidateQueries({ queryKey: ["standards-reporting-templates"] });
      queryClient.invalidateQueries({ queryKey: ["standards-policy-versions"] });
    },
    onError: (err) => setActionError(getApiErrorMessage(err, "Failed to activate reporting template.")),
  });

  const columns: DataTableColumn<ReportingTemplate>[] = [
    {
      key: "template_name",
      header: "Template Name",
      render: (row) => (
        <Link href="/federal/standards-policy/reporting-me/form-builder?tab=templates" className="font-medium text-brand-700 hover:underline">
          {row.template_name}
        </Link>
      ),
    },
    { key: "template_code", header: "Code", render: (row) => row.template_code },
    {
      key: "reporting_frequency",
      header: "Frequency",
      render: (row) => row.reporting_frequency.replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase()),
    },
    { key: "approval_required", header: "Approval Required", render: (row) => row.approval_required ? "Yes" : "No" },
    {
      key: "status",
      header: "Status",
      render: (row) => (
        <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${
          row.status === "active" ? "bg-brand-50 text-brand-700" :
          row.status === "draft" ? "bg-neutral-100 text-neutral-700" :
          row.status === "retired" ? "bg-neutral-100 text-neutral-500" :
          "bg-warning-50 text-warning-700"
        }`}>
          {row.status.replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase())}
        </span>
      ),
    },
    { key: "policy_version_code", header: "Policy Version", render: (row) => row.policy_version_code },
    {
      key: "id",
      header: "Action",
      render: (row) => row.status === "draft" ? (
        <button
          type="button"
          onClick={() => activateMutation.mutate(row.id)}
          className="rounded border border-brand-200 px-3 py-1.5 text-xs font-semibold text-brand-700 hover:bg-brand-50"
        >
          Activate
        </button>
      ) : "—",
    },
  ];

  return (
    <StandardsPolicyWorkspaceShell workspace="reporting-me" title="Reporting Templates" description="Configure templates that States use to submit periodic reports.">
      <div className="grid gap-5">
        <section className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div>
            <p className="text-sm font-semibold text-neutral-900">{rows.length} reporting templates</p>
            <p className="mt-1 text-sm text-neutral-500">Use the Forms Tool to build state reporting forms, required sections, uploads, and data collection fields.</p>
          </div>
          <Link href={FORM_BUILDER_HREF} className="inline-flex h-10 items-center rounded-md bg-brand-600 px-4 text-sm font-semibold text-white hover:bg-brand-700">
            Build Template
          </Link>
        </section>

        {actionError ? <div className="rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{actionError}</div> : null}

        {isLoading ? (
          <p className="text-sm text-neutral-500">Loading...</p>
        ) : (
          <DataTable<ReportingTemplate>
            columns={columns}
            rows={rows}
            empty="No reporting templates configured."
          />
        )}
      </div>
    </StandardsPolicyWorkspaceShell>
  );
}
