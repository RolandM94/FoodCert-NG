"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Archive, Download, FileUp, Send, Upload } from "lucide-react";

import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { PolicyDocumentFormDrawer } from "@/features/standards/policy-document-form-drawer";
import { StandardsPolicyWorkspaceShell } from "@/features/standards/standards-policy-workspaces";
import { getApiErrorMessage } from "@/lib/api/client";
import {
  archivePolicyDocument,
  listPolicyDocuments,
  listPolicyVersions,
  listStateAcknowledgements,
  publishPolicyDocument,
  retirePolicyDocument,
} from "@/lib/api/standards";
import type { PolicyDocument, StateAcknowledgement } from "@/types/standards";

function formatLabel(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase());
}

function statusClass(status: string) {
  if (status === "published" || status === "acknowledged") return "bg-brand-50 text-brand-700";
  if (status === "draft" || status === "pending") return "bg-neutral-100 text-neutral-700";
  if (status === "retired" || status === "archived") return "bg-neutral-100 text-neutral-500";
  return "bg-warning-50 text-warning-700";
}

export default function DocumentsPage() {
  const queryClient = useQueryClient();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerMode, setDrawerMode] = useState<"create" | "edit">("create");
  const [editing, setEditing] = useState<PolicyDocument | null>(null);
  const [policyVersionId, setPolicyVersionId] = useState("");
  const [actionError, setActionError] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["standards-documents"],
    queryFn: () => listPolicyDocuments(),
  });
  const { data: versions } = useQuery({
    queryKey: ["standards-policy-versions"],
    queryFn: () => listPolicyVersions(),
  });
  const { data: acknowledgements, isLoading: acknowledgementsLoading } = useQuery({
    queryKey: ["standards-state-acknowledgements"],
    queryFn: () => listStateAcknowledgements(),
  });

  const rows = Array.isArray(data) ? data : [];
  const acknowledgementRows = Array.isArray(acknowledgements) ? acknowledgements : [];
  const draftVersions = (Array.isArray(versions) ? versions : []).filter(
    (version) => version.status === "draft" || version.status === "returned"
  );

  const acknowledgementSummary = acknowledgementRows.reduce(
    (summary, acknowledgement) => {
      summary.total += 1;
      if (acknowledgement.status === "acknowledged") summary.acknowledged += 1;
      if (acknowledgement.status === "pending") summary.pending += 1;
      if (acknowledgement.status === "overdue") summary.overdue += 1;
      return summary;
    },
    { total: 0, acknowledged: 0, pending: 0, overdue: 0 }
  );

  function invalidateDocuments() {
    queryClient.invalidateQueries({ queryKey: ["standards-documents"] });
    queryClient.invalidateQueries({ queryKey: ["standards-policy-versions"] });
    queryClient.invalidateQueries({ queryKey: ["standards-state-acknowledgements"] });
  }

  const publishMutation = useMutation({
    mutationFn: publishPolicyDocument,
    onSuccess: () => {
      setActionError("");
      invalidateDocuments();
    },
    onError: (err) => setActionError(getApiErrorMessage(err, "Failed to publish document.")),
  });

  const retireMutation = useMutation({
    mutationFn: retirePolicyDocument,
    onSuccess: () => {
      setActionError("");
      invalidateDocuments();
    },
    onError: (err) => setActionError(getApiErrorMessage(err, "Failed to retire document.")),
  });

  const archiveMutation = useMutation({
    mutationFn: archivePolicyDocument,
    onSuccess: () => {
      setActionError("");
      invalidateDocuments();
    },
    onError: (err) => setActionError(getApiErrorMessage(err, "Failed to archive document.")),
  });

  function openCreate() {
    if (draftVersions.length > 0) setPolicyVersionId(draftVersions[0].id);
    setEditing(null);
    setDrawerMode("create");
    setDrawerOpen(true);
  }

  function openEdit(row: PolicyDocument) {
    setPolicyVersionId(row.policy_version ?? "");
    setEditing(row);
    setDrawerMode("edit");
    setDrawerOpen(true);
  }

  const columns: DataTableColumn<PolicyDocument>[] = [
    {
      key: "title",
      header: "Title",
      render: (row) => (
        <button onClick={() => openEdit(row)} className="text-left font-medium text-brand-700 hover:underline">
          {row.title}
        </button>
      ),
    },
    {
      key: "document_type",
      header: "Type",
      render: (row) => formatLabel(row.document_type),
    },
    { key: "version_label", header: "Version", render: (row) => row.version_label },
    {
      key: "requires_acknowledgement",
      header: "Ack Required",
      render: (row) => row.requires_acknowledgement ? "Yes" : "No",
    },
    {
      key: "status",
      header: "Status",
      render: (row) => (
        <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${statusClass(row.status)}`}>
          {formatLabel(row.status)}
        </span>
      ),
    },
    {
      key: "policy_version_code",
      header: "Policy Version",
      render: (row) => row.policy_version_code || "-",
    },
    {
      key: "id",
      header: "Actions",
      render: (row) => (
        <div className="flex flex-wrap gap-2">
          {row.file_url ? (
            <a
              className="inline-flex h-8 items-center gap-1 rounded border border-neutral-200 px-2 text-xs font-semibold text-neutral-700 hover:bg-neutral-50"
              href={row.file_url}
              rel="noreferrer"
              target="_blank"
            >
              <Download size={13} />
              File
            </a>
          ) : null}
          {row.status === "draft" ? (
            <button
              type="button"
              onClick={() => publishMutation.mutate(row.id)}
              className="inline-flex h-8 items-center gap-1 rounded border border-brand-200 px-2 text-xs font-semibold text-brand-700 hover:bg-brand-50"
            >
              <Send size={13} />
              Publish
            </button>
          ) : null}
          {row.status === "published" ? (
            <button
              type="button"
              onClick={() => retireMutation.mutate(row.id)}
              className="inline-flex h-8 items-center gap-1 rounded border border-warning-200 px-2 text-xs font-semibold text-warning-700 hover:bg-warning-50"
            >
              <Archive size={13} />
              Retire
            </button>
          ) : null}
          {row.status === "draft" || row.status === "retired" ? (
            <button
              type="button"
              onClick={() => archiveMutation.mutate(row.id)}
              className="inline-flex h-8 items-center gap-1 rounded border border-neutral-200 px-2 text-xs font-semibold text-neutral-700 hover:bg-neutral-50"
            >
              <Archive size={13} />
              Archive
            </button>
          ) : null}
        </div>
      ),
    },
  ];

  const acknowledgementColumns: DataTableColumn<StateAcknowledgement>[] = [
    { key: "state_name", header: "State", render: (row) => row.state_name },
    { key: "policy_version_code", header: "Policy Version", render: (row) => row.policy_version_code },
    {
      key: "status",
      header: "Status",
      render: (row) => (
        <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${statusClass(row.status)}`}>
          {formatLabel(row.status)}
        </span>
      ),
    },
    {
      key: "acknowledged_by_name",
      header: "Acknowledged By",
      render: (row) => row.acknowledged_by_name || "-",
    },
    {
      key: "acknowledged_at",
      header: "Acknowledged At",
      render: (row) => row.acknowledged_at ? new Date(row.acknowledged_at).toLocaleDateString() : "-",
    },
  ];

  return (
    <StandardsPolicyWorkspaceShell workspace="policy-governance" title="Documents & Circulars" description="Upload, publish, and manage policy documents, circulars, SOPs, and FAQs.">
      <div className="grid gap-5">
        <section className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div>
            <p className="text-sm font-semibold text-neutral-900">{rows.length} documents and circulars</p>
            <p className="mt-1 text-sm text-neutral-500">Classify documents, link them to policy versions, publish them, and monitor state acknowledgement.</p>
          </div>
          <button onClick={openCreate} disabled={draftVersions.length === 0} className="inline-flex h-10 items-center gap-2 rounded-md bg-brand-600 px-4 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-50">
            <Upload size={16} />
            Upload Document
          </button>
        </section>

        {draftVersions.length === 0 ? (
          <div className="rounded border border-warning-100 bg-warning-50 p-3 text-sm text-warning-700">
            Create a draft policy version before uploading linked policy documents.
          </div>
        ) : null}
        {actionError ? <div className="rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{actionError}</div> : null}

        <div className="grid gap-3 md:grid-cols-4">
          {[
            ["Acknowledged", acknowledgementSummary.acknowledged],
            ["Pending", acknowledgementSummary.pending],
            ["Overdue", acknowledgementSummary.overdue],
            ["Total Acknowledgements", acknowledgementSummary.total],
          ].map(([label, value]) => (
            <div key={label} className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <p className="text-xs font-semibold uppercase text-neutral-500">{label}</p>
              <p className="mt-2 text-2xl font-semibold text-neutral-900">{value}</p>
            </div>
          ))}
        </div>

        {isLoading ? (
          <p className="text-sm text-neutral-500">Loading...</p>
        ) : (
          <DataTable<PolicyDocument>
            columns={columns}
            rows={rows}
            empty="No documents or circulars uploaded."
          />
        )}

        <section className="grid gap-3">
          <div className="flex items-center gap-2">
            <FileUp size={16} className="text-brand-700" />
            <h2 className="text-base font-semibold text-neutral-900">Acknowledgement Dashboard</h2>
          </div>
          {acknowledgementsLoading ? (
            <p className="text-sm text-neutral-500">Loading acknowledgements...</p>
          ) : (
            <DataTable<StateAcknowledgement>
              columns={acknowledgementColumns}
              rows={acknowledgementRows}
              empty="No state acknowledgements generated yet."
            />
          )}
        </section>
      </div>

      <PolicyDocumentFormDrawer
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
