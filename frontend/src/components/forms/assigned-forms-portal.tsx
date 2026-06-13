"use client";

import { useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ClipboardList, ExternalLink, FileText } from "lucide-react";
import { useState } from "react";
import { StatusBadge } from "@/components/status/status-badge";
import {
  createPortalFormResponse,
  fetchPortalAssignedForms,
  type PortalAssignedForm,
  type PortalContext,
} from "@/lib/api/forms";
import { getApiErrorMessage } from "@/lib/api/client";

const statusFilters = [
  { value: "", label: "All" },
  { value: "pending", label: "Pending" },
  { value: "in_progress", label: "In progress" },
  { value: "submitted", label: "Submitted" },
  { value: "returned", label: "Returned" },
];

function dateLabel(value?: string | null) {
  if (!value) return "";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

export function AssignedFormsPortal({
  portal,
  title = "Assigned Forms",
  description = "Complete forms assigned to you or your organization.",
}: {
  portal: PortalContext;
  title?: string;
  description?: string;
}) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState("");
  const [error, setError] = useState("");

  const formsQuery = useQuery({
    queryKey: ["portal-assigned-forms", portal, statusFilter],
    queryFn: () => fetchPortalAssignedForms(portal, statusFilter ? { status: statusFilter } : undefined),
  });

  const startMut = useMutation({
    mutationFn: (assignment: PortalAssignedForm) => createPortalFormResponse(portal, assignment.id),
    onSuccess: (formResponse) => {
      queryClient.invalidateQueries({ queryKey: ["portal-assigned-forms", portal] });
      router.push(`/forms/${formResponse.id}`);
    },
    onError: (err) => setError(getApiErrorMessage(err, "Could not start form.")),
  });

  const forms = formsQuery.data || [];
  const pending = forms.filter((f) => f.response_status === "not_started" || !f.response_id);
  const inProgress = forms.filter((f) => ["draft", "in_progress"].includes(f.response_status));
  const submitted = forms.filter((f) => ["submitted", "reviewed", "approved"].includes(f.response_status));
  const returned = forms.filter((f) => f.response_status === "returned");

  function handleOpen(assignment: PortalAssignedForm) {
    if (assignment.response_id) {
      router.push(`/forms/${assignment.response_id}`);
    } else {
      startMut.mutate(assignment);
    }
  }

  return (
    <div className="grid gap-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <ClipboardList className="text-brand-700" size={20} />
          <div>
            <h2 className="text-base font-bold text-neutral-900">{title}</h2>
            <p className="text-xs text-neutral-500">{description}</p>
          </div>
        </div>
        <select
          className="h-9 rounded border border-neutral-200 bg-white px-3 text-sm"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          {statusFilters.map((opt) => (
            <option key={opt.value || "all"} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      </div>

      {error ? <p className="rounded border border-danger-100 bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{error}</p> : null}

      <div className="grid gap-3 sm:grid-cols-4">
        <div className="rounded-lg border border-neutral-200 bg-white p-4">
          <p className="text-xs font-bold uppercase text-neutral-500">Pending</p>
          <p className="mt-1 text-2xl font-bold text-neutral-900">{pending.length}</p>
        </div>
        <div className="rounded-lg border border-neutral-200 bg-white p-4">
          <p className="text-xs font-bold uppercase text-brand-700">In progress</p>
          <p className="mt-1 text-2xl font-bold text-neutral-900">{inProgress.length}</p>
        </div>
        <div className="rounded-lg border border-neutral-200 bg-white p-4">
          <p className="text-xs font-bold uppercase text-info-700">Submitted</p>
          <p className="mt-1 text-2xl font-bold text-neutral-900">{submitted.length}</p>
        </div>
        <div className="rounded-lg border border-neutral-200 bg-white p-4">
          <p className="text-xs font-bold uppercase text-warning-700">Returned</p>
          <p className="mt-1 text-2xl font-bold text-neutral-900">{returned.length}</p>
        </div>
      </div>

      {formsQuery.isLoading ? (
        <p className="rounded-lg border border-neutral-200 bg-white p-6 text-sm text-neutral-500">Loading assigned forms...</p>
      ) : !forms.length ? (
        <p className="rounded-lg border border-dashed border-neutral-300 bg-white p-6 text-sm text-neutral-500">No forms have been assigned yet.</p>
      ) : (
        <div className="grid gap-3">
          {forms.map((assignment) => (
            <div
              key={assignment.id}
              className="flex flex-col gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between"
            >
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <FileText className="shrink-0 text-neutral-400" size={16} />
                  <p className="font-bold text-neutral-900">{assignment.template_title || assignment.title}</p>
                  <StatusBadge status={assignment.response_status || "not_started"} />
                </div>
                <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-neutral-500">
                  <span>Purpose: {(assignment.purpose || "general").replaceAll("_", " ")}</span>
                  {assignment.due_date ? <span>Due: {dateLabel(assignment.due_date)}</span> : null}
                  {assignment.created_at ? <span>Assigned: {dateLabel(assignment.created_at)}</span> : null}
                </div>
                {assignment.response_history?.length ? (
                  <div className="mt-3 flex flex-wrap gap-2 text-xs text-neutral-500">
                    {assignment.response_history.slice(0, 3).map((item) => (
                      <span className="rounded border border-neutral-200 bg-neutral-50 px-2 py-1" key={item.id}>
                        {item.status.replaceAll("_", " ")}{item.submitted_at ? ` / ${dateLabel(item.submitted_at)}` : ""}
                      </span>
                    ))}
                  </div>
                ) : null}
              </div>
              <button
                className="inline-flex h-9 shrink-0 items-center gap-2 rounded border border-brand-200 px-4 text-sm font-bold text-brand-700 hover:bg-brand-50 disabled:opacity-50"
                disabled={startMut.isPending}
                onClick={() => handleOpen(assignment)}
                type="button"
              >
                <ExternalLink size={14} />
                {assignment.response_id ? (
                  ["submitted", "reviewed", "approved"].includes(assignment.response_status) ? "View" : "Continue"
                ) : "Start"}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
