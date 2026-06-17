"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, RotateCcw, XCircle } from "lucide-react";

import { DataTable, type DataTableColumn } from "@/components/ui/data-table";
import { StandardsPolicyWorkspaceShell } from "@/features/standards/standards-policy-workspaces";
import { getApiErrorMessage } from "@/lib/api/client";
import {
  approveApproval,
  listApprovalQueue,
  rejectApproval,
  returnApproval,
} from "@/lib/api/standards";
import type { Approval, ApprovalStatus, ImpactLevel } from "@/types/standards";

function formatLabel(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase());
}

function impactClass(impact: ImpactLevel) {
  if (impact === "emergency") return "bg-danger-50 text-danger-700";
  if (impact === "high") return "bg-warning-50 text-warning-700";
  if (impact === "medium") return "bg-info-50 text-info-700";
  return "bg-neutral-100 text-neutral-600";
}

function statusClass(status: ApprovalStatus) {
  if (status === "approved") return "bg-brand-50 text-brand-700";
  if (status === "pending") return "bg-neutral-100 text-neutral-700";
  if (status === "rejected") return "bg-neutral-100 text-neutral-500";
  return "bg-warning-50 text-warning-700";
}

function prettyJson(value: Record<string, unknown>) {
  const keys = Object.keys(value ?? {});
  if (keys.length === 0) return "No captured values.";
  return JSON.stringify(value, null, 2);
}

export default function ApprovalQueuePage() {
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState<ApprovalStatus | "all">("pending");
  const [impactFilter, setImpactFilter] = useState<ImpactLevel | "all">("all");
  const [entityFilter, setEntityFilter] = useState("all");
  const [selectedId, setSelectedId] = useState("");
  const [comment, setComment] = useState("");
  const [actionError, setActionError] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["standards-approval-queue"],
    queryFn: () => listApprovalQueue(),
  });

  const rows = useMemo(() => Array.isArray(data) ? data : [], [data]);
  const entityTypes = useMemo(() => Array.from(new Set(rows.map((row) => row.entity_type))).sort(), [rows]);
  const filteredRows = useMemo(() => rows.filter((row) => {
    if (statusFilter !== "all" && row.status !== statusFilter) return false;
    if (impactFilter !== "all" && row.impact_level !== impactFilter) return false;
    if (entityFilter !== "all" && row.entity_type !== entityFilter) return false;
    return true;
  }), [entityFilter, impactFilter, rows, statusFilter]);
  const selected = rows.find((row) => row.id === selectedId) ?? filteredRows[0] ?? null;

  function refresh() {
    queryClient.invalidateQueries({ queryKey: ["standards-approval-queue"] });
    queryClient.invalidateQueries({ queryKey: ["standards-policy-versions"] });
  }

  const approveMutation = useMutation({
    mutationFn: (approval: Approval) => approveApproval(approval.id, comment),
    onSuccess: () => {
      setActionError("");
      setComment("");
      refresh();
    },
    onError: (err) => setActionError(getApiErrorMessage(err, "Failed to approve change.")),
  });

  const returnMutation = useMutation({
    mutationFn: (approval: Approval) => returnApproval(approval.id, comment),
    onSuccess: () => {
      setActionError("");
      setComment("");
      refresh();
    },
    onError: (err) => setActionError(getApiErrorMessage(err, "Failed to return change.")),
  });

  const rejectMutation = useMutation({
    mutationFn: (approval: Approval) => rejectApproval(approval.id, comment),
    onSuccess: () => {
      setActionError("");
      setComment("");
      refresh();
    },
    onError: (err) => setActionError(getApiErrorMessage(err, "Failed to reject change.")),
  });

  const columns: DataTableColumn<Approval>[] = [
    {
      key: "entity_label",
      header: "Change",
      render: (row) => (
        <button onClick={() => setSelectedId(row.id)} className="text-left font-medium text-brand-700 hover:underline">
          {row.entity_label || row.entity_type}
        </button>
      ),
    },
    { key: "entity_type", header: "Entity Type", render: (row) => row.entity_type },
    {
      key: "impact_level",
      header: "Impact",
      render: (row) => (
        <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${impactClass(row.impact_level)}`}>
          {formatLabel(row.impact_level)}
        </span>
      ),
    },
    { key: "requested_by_name", header: "Requested By", render: (row) => row.requested_by_name || "-" },
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
      key: "created_at",
      header: "Submitted",
      render: (row) => new Date(row.created_at).toLocaleDateString(),
    },
  ];

  return (
    <StandardsPolicyWorkspaceShell workspace="policy-governance" title="Approval Queue" description="Review and process pending configuration changes.">
      <div className="grid gap-5">
        <section className="grid gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm lg:grid-cols-4">
          <label className="text-sm font-medium text-neutral-700">
            Status
            <select className="mt-1 h-10 w-full rounded border border-neutral-200 bg-white px-3 text-sm" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value as ApprovalStatus | "all")}>
              <option value="pending">Pending</option>
              <option value="all">All</option>
              <option value="approved">Approved</option>
              <option value="returned">Returned</option>
              <option value="rejected">Rejected</option>
            </select>
          </label>
          <label className="text-sm font-medium text-neutral-700">
            Impact
            <select className="mt-1 h-10 w-full rounded border border-neutral-200 bg-white px-3 text-sm" value={impactFilter} onChange={(event) => setImpactFilter(event.target.value as ImpactLevel | "all")}>
              <option value="all">All</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="emergency">Emergency</option>
            </select>
          </label>
          <label className="text-sm font-medium text-neutral-700">
            Entity Type
            <select className="mt-1 h-10 w-full rounded border border-neutral-200 bg-white px-3 text-sm" value={entityFilter} onChange={(event) => setEntityFilter(event.target.value)}>
              <option value="all">All</option>
              {entityTypes.map((type) => <option key={type} value={type}>{type}</option>)}
            </select>
          </label>
          <div className="flex items-end">
            <div className="w-full rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm text-neutral-600">
              {filteredRows.length} approval item{filteredRows.length === 1 ? "" : "s"}
            </div>
          </div>
        </section>

        {actionError ? <div className="rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{actionError}</div> : null}

        <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_420px]">
          {isLoading ? (
            <p className="text-sm text-neutral-500">Loading...</p>
          ) : (
            <DataTable<Approval>
              columns={columns}
              rows={filteredRows}
              empty="There are no approvals matching these filters."
            />
          )}

          <aside className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            {selected ? (
              <div className="grid gap-4">
                <div>
                  <p className="text-xs font-semibold uppercase text-neutral-500">Review Detail</p>
                  <h2 className="mt-1 text-base font-semibold text-neutral-900">{selected.entity_label}</h2>
                  <p className="mt-1 text-sm text-neutral-500">{selected.request_comment || "No request comment provided."}</p>
                </div>

                <div className="grid gap-2 text-sm">
                  <div className="flex justify-between gap-3"><span className="text-neutral-500">Impact</span><span className={`rounded-full px-2 py-0.5 text-xs font-medium ${impactClass(selected.impact_level)}`}>{formatLabel(selected.impact_level)}</span></div>
                  <div className="flex justify-between gap-3"><span className="text-neutral-500">Status</span><span className={`rounded-full px-2 py-0.5 text-xs font-medium ${statusClass(selected.status)}`}>{formatLabel(selected.status)}</span></div>
                  <div className="flex justify-between gap-3"><span className="text-neutral-500">Requested By</span><span className="text-right text-neutral-900">{selected.requested_by_name || "-"}</span></div>
                  <div className="flex justify-between gap-3"><span className="text-neutral-500">Submitted</span><span className="text-neutral-900">{new Date(selected.created_at).toLocaleString()}</span></div>
                  {selected.action_url ? <Link className="font-semibold text-brand-700 hover:underline" href={selected.action_url}>Open policy version</Link> : null}
                </div>

                <div className="grid gap-3">
                  <div>
                    <p className="mb-1 text-xs font-semibold uppercase text-neutral-500">Old Values</p>
                    <pre className="max-h-48 overflow-auto rounded bg-neutral-950 p-3 text-xs text-neutral-50">{prettyJson(selected.change_diff?.old_value ?? {})}</pre>
                  </div>
                  <div>
                    <p className="mb-1 text-xs font-semibold uppercase text-neutral-500">New Values</p>
                    <pre className="max-h-48 overflow-auto rounded bg-neutral-950 p-3 text-xs text-neutral-50">{prettyJson(selected.change_diff?.new_value ?? {})}</pre>
                  </div>
                </div>

                <label className="text-sm font-medium text-neutral-700">
                  Review Comment
                  <textarea className="mt-1 min-h-24 w-full rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm" value={comment} onChange={(event) => setComment(event.target.value)} placeholder="Add approval notes or correction guidance." />
                </label>

                <div className="flex flex-wrap gap-2">
                  <button
                    type="button"
                    disabled={selected.status !== "pending" || approveMutation.isPending}
                    onClick={() => approveMutation.mutate(selected)}
                    className="inline-flex h-9 items-center gap-2 rounded bg-brand-600 px-3 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-50"
                  >
                    <CheckCircle2 size={15} />
                    Approve
                  </button>
                  <button
                    type="button"
                    disabled={selected.status !== "pending" || !comment.trim() || returnMutation.isPending}
                    onClick={() => returnMutation.mutate(selected)}
                    className="inline-flex h-9 items-center gap-2 rounded border border-warning-200 px-3 text-sm font-semibold text-warning-700 hover:bg-warning-50 disabled:opacity-50"
                  >
                    <RotateCcw size={15} />
                    Return
                  </button>
                  <button
                    type="button"
                    disabled={selected.status !== "pending" || !comment.trim() || rejectMutation.isPending}
                    onClick={() => rejectMutation.mutate(selected)}
                    className="inline-flex h-9 items-center gap-2 rounded border border-danger-200 px-3 text-sm font-semibold text-danger-700 hover:bg-danger-50 disabled:opacity-50"
                  >
                    <XCircle size={15} />
                    Reject
                  </button>
                </div>
              </div>
            ) : (
              <p className="text-sm text-neutral-500">Select an approval item to review details.</p>
            )}
          </aside>
        </div>
      </div>
    </StandardsPolicyWorkspaceShell>
  );
}
