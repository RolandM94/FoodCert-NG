"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, Edit3, Eye, Loader2, Send, Archive, Plus } from "lucide-react";
import { useState } from "react";
import {
  approveTemplate,
  archiveTemplate,
  listTemplates,
  submitTemplateForApproval,
} from "@/lib/api/notifications";
import type { NotificationTemplate } from "@/types/notifications";

function formatDate(value: string) {
  return new Date(value).toLocaleString("en-NG", { dateStyle: "medium" });
}

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-slate-100 text-slate-700",
  pending_approval: "bg-amber-100 text-amber-800",
  active: "bg-emerald-100 text-emerald-800",
  archived: "bg-slate-200 text-slate-500",
  rejected: "bg-rose-100 text-rose-800",
};

export function NotificationTemplateTable({
  onEdit,
  onCreate,
}: {
  onEdit?: (template: NotificationTemplate) => void;
  onCreate?: () => void;
}) {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");

  const { data: templates = [], isLoading } = useQuery({
    queryKey: ["notification-templates"],
    queryFn: () => listTemplates(),
  });

  const submitMutation = useMutation({
    mutationFn: submitTemplateForApproval,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notification-templates"] }),
  });

  const approveMutation = useMutation({
    mutationFn: approveTemplate,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notification-templates"] }),
  });

  const archiveMutation = useMutation({
    mutationFn: archiveTemplate,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notification-templates"] }),
  });

  const filtered = search
    ? templates.filter(
        (t) =>
          t.name.toLowerCase().includes(search.toLowerCase()) ||
          t.template_key.toLowerCase().includes(search.toLowerCase())
      )
    : templates;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <input
          className="h-10 w-64 rounded border border-slate-200 bg-slate-50 px-3 text-sm outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2"
          placeholder="Search templates..."
          type="search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        {onCreate ? (
          <button
            className="inline-flex h-10 items-center gap-1.5 rounded bg-brand-green px-4 text-sm font-bold text-white hover:bg-brand-deep"
            onClick={onCreate}
            type="button"
          >
            <Plus aria-hidden="true" size={16} />
            New Template
          </button>
        ) : null}
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="animate-spin text-slate-400" size={24} />
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs font-bold uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Key</th>
                <th className="px-4 py-3">Channel</th>
                <th className="px-4 py-3">Category</th>
                <th className="px-4 py-3">Version</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Updated</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((t) => (
                <tr key={t.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-semibold text-slate-900">{t.name}</td>
                  <td className="px-4 py-3 font-mono text-xs text-slate-600">{t.template_key}</td>
                  <td className="px-4 py-3 text-slate-600">{t.channel_display}</td>
                  <td className="px-4 py-3 text-slate-600">{t.category_display}</td>
                  <td className="px-4 py-3 text-slate-600">v{t.version}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-semibold ${STATUS_COLORS[t.status] || "bg-slate-100 text-slate-600"}`}>
                      {t.status_display}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-500">{formatDate(t.updated_at)}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-1">
                      {onEdit ? (
                        <button
                          className="inline-flex h-8 w-8 items-center justify-center rounded text-slate-400 hover:bg-slate-100 hover:text-slate-700"
                          onClick={() => onEdit(t)}
                          title="Edit"
                          type="button"
                        >
                          <Edit3 aria-hidden="true" size={15} />
                        </button>
                      ) : null}
                      {t.status === "draft" ? (
                        <button
                          className="inline-flex h-8 w-8 items-center justify-center rounded text-slate-400 hover:bg-amber-50 hover:text-amber-700"
                          onClick={() => submitMutation.mutate(t.id)}
                          title="Submit for approval"
                          type="button"
                        >
                          <Send aria-hidden="true" size={15} />
                        </button>
                      ) : t.status === "pending_approval" ? (
                        <button
                          className="inline-flex h-8 w-8 items-center justify-center rounded text-slate-400 hover:bg-emerald-50 hover:text-brand-green"
                          onClick={() => approveMutation.mutate(t.id)}
                          title="Approve"
                          type="button"
                        >
                          <Check aria-hidden="true" size={15} />
                        </button>
                      ) : null}
                      {t.status !== "archived" ? (
                        <button
                          className="inline-flex h-8 w-8 items-center justify-center rounded text-slate-400 hover:bg-slate-100 hover:text-slate-700"
                          onClick={() => archiveMutation.mutate(t.id)}
                          title="Archive"
                          type="button"
                        >
                          <Archive aria-hidden="true" size={15} />
                        </button>
                      ) : null}
                    </div>
                  </td>
                </tr>
              ))}
              {!filtered.length ? (
                <tr>
                  <td className="px-4 py-8 text-center text-sm text-slate-500" colSpan={8}>
                    No templates found.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
