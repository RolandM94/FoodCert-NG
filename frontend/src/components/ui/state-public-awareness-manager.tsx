"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Archive, Megaphone, Radio, Send, Users } from "lucide-react";
import {
  approveBroadcast,
  archiveBroadcast,
  createBroadcast,
  estimateBroadcastAudience,
  listBroadcasts,
  sendBroadcast,
  submitBroadcastForApproval,
} from "@/lib/api/notifications";
import { getApiErrorMessage } from "@/lib/api/client";
import { DashboardCard } from "@/components/ui/dashboard-card";

const AUDIENCE_OPTIONS = [
  { value: "all_facilities_in_state", label: "Medical facilities" },
  { value: "all_employers_in_state", label: "Food businesses" },
  { value: "all_food_handlers_in_state", label: "Food handlers" },
  { value: "all_inspectors_in_state", label: "Inspectors" },
  { value: "general_public", label: "General public" },
] as const;

const NOTICE_KIND_OPTIONS = [
  { value: "public_notice", label: "Public notice" },
  { value: "awareness_campaign", label: "Awareness campaign" },
] as const;

const STATUS_STYLES: Record<string, string> = {
  draft: "bg-neutral-100 text-neutral-700",
  pending_approval: "bg-warning-100 text-warning-800",
  approved: "bg-info-100 text-blue-800",
  sent: "bg-brand-100 text-brand-800",
  archived: "bg-neutral-200 text-neutral-600",
};

function audienceLabel(value: string) {
  return AUDIENCE_OPTIONS.find((option) => option.value === value)?.label ?? value.replaceAll("_", " ");
}

function noticeKindLabel(value: string) {
  return NOTICE_KIND_OPTIONS.find((option) => option.value === value)?.label ?? value.replaceAll("_", " ");
}

function statusLabel(status: string) {
  if (status === "pending_approval") return "Submitted";
  if (status === "sent") return "Published";
  return status.replaceAll("_", " ");
}

function dateTimeLabel(value?: string | null) {
  if (!value) return "Not set";
  return new Date(value).toLocaleString("en-NG", { dateStyle: "medium", timeStyle: "short" });
}

export function StatePublicAwarenessManager() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    title: "",
    message: "",
    audience_type: "all_facilities_in_state",
    notice_kind: "public_notice",
  });

  const broadcastsQuery = useQuery({
    queryKey: ["state-public-awareness-broadcasts"],
    queryFn: listBroadcasts,
  });

  const broadcasts = broadcastsQuery.data ?? [];
  const metrics = useMemo(() => ({
    drafts: broadcasts.filter((item) => item.status === "draft").length,
    submitted: broadcasts.filter((item) => item.status === "pending_approval").length,
    published: broadcasts.filter((item) => item.status === "sent").length,
    archived: broadcasts.filter((item) => item.status === "archived").length,
  }), [broadcasts]);

  const createMutation = useMutation({
    mutationFn: () =>
      createBroadcast({
        title: form.title,
        message: form.message,
        category: "system",
        priority: "high",
        audience_type: form.audience_type,
        audience_filters: { notice_kind: form.notice_kind },
        channels: ["in_app"],
      }),
    onSuccess: () => {
      setForm({ title: "", message: "", audience_type: "all_facilities_in_state", notice_kind: "public_notice" });
      return queryClient.invalidateQueries({ queryKey: ["state-public-awareness-broadcasts"] });
    },
  });

  const estimateMutation = useMutation({
    mutationFn: estimateBroadcastAudience,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["state-public-awareness-broadcasts"] }),
  });

  const submitMutation = useMutation({
    mutationFn: submitBroadcastForApproval,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["state-public-awareness-broadcasts"] }),
  });

  const approveMutation = useMutation({
    mutationFn: approveBroadcast,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["state-public-awareness-broadcasts"] }),
  });

  const publishMutation = useMutation({
    mutationFn: sendBroadcast,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["state-public-awareness-broadcasts"] }),
  });

  const archiveMutation = useMutation({
    mutationFn: archiveBroadcast,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["state-public-awareness-broadcasts"] }),
  });

  const latestPublished = broadcasts.find((item) => item.status === "sent");
  const actionError =
    createMutation.error ||
    estimateMutation.error ||
    submitMutation.error ||
    approveMutation.error ||
    publishMutation.error ||
    archiveMutation.error;

  return (
    <div className="grid gap-5">
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <DashboardCard icon={Megaphone} label="Draft notices" value={metrics.drafts} />
        <DashboardCard icon={Send} label="Submitted" value={metrics.submitted} />
        <DashboardCard icon={Radio} label="Published" value={metrics.published} />
        <DashboardCard icon={Archive} label="Archived" value={metrics.archived} />
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.05fr_0.95fr]">
        <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-brand-700">Compose Notice</p>
          <h2 className="mt-1 text-lg font-bold text-neutral-900">Publish state awareness updates with approval control</h2>
          <p className="mt-2 max-w-3xl text-sm text-neutral-500">
            Create operational notices and public awareness campaigns for facilities, food businesses, handlers, inspectors, or the general public. Published items trigger in-app notifications where a logged-in audience exists.
          </p>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Notice title
              <input
                className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm"
                value={form.title}
                onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))}
              />
            </label>
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Audience
              <select
                className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm"
                value={form.audience_type}
                onChange={(event) => setForm((current) => ({ ...current, audience_type: event.target.value }))}
              >
                {AUDIENCE_OPTIONS.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
              </select>
            </label>
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Notice type
              <select
                className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm"
                value={form.notice_kind}
                onChange={(event) => setForm((current) => ({ ...current, notice_kind: event.target.value }))}
              >
                {NOTICE_KIND_OPTIONS.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
              </select>
            </label>
            <div className="rounded-lg border border-dashed border-neutral-200 bg-neutral-50 px-4 py-3 text-sm text-neutral-500">
              Approval path: Draft {"->"} Submitted {"->"} Approved {"->"} Published {"->"} Archived
            </div>
            <label className="md:col-span-2 grid gap-1 text-sm font-semibold text-neutral-700">
              Notice body
              <textarea
                className="min-h-[140px] rounded-lg border border-neutral-200 bg-white px-3 py-3 text-sm"
                value={form.message}
                onChange={(event) => setForm((current) => ({ ...current, message: event.target.value }))}
              />
            </label>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <button
              className="inline-flex h-10 items-center justify-center rounded-lg bg-brand-700 px-4 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-neutral-300"
              disabled={createMutation.isPending || !form.title.trim() || !form.message.trim()}
              onClick={() => createMutation.mutate()}
              type="button"
            >
              {createMutation.isPending ? "Saving..." : "Create draft"}
            </button>
          </div>
          {actionError ? (
            <p className="mt-3 rounded-lg bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">
              {getApiErrorMessage(actionError, "Could not complete the notice action.")}
            </p>
          ) : null}
        </div>

        <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-brand-700">Dashboard Visibility</p>
          <h2 className="mt-1 text-lg font-bold text-neutral-900">Latest published awareness item</h2>
          <div className="mt-4 rounded-lg border border-neutral-200 bg-neutral-50 px-4 py-4">
            {latestPublished ? (
              <div className="space-y-2">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full bg-brand-100 px-2.5 py-1 text-xs font-semibold text-brand-800">Published</span>
                  <span className="text-xs font-semibold uppercase tracking-[0.16em] text-neutral-500">
                    {noticeKindLabel(String(latestPublished.audience_filters.notice_kind || "public_notice"))}
                  </span>
                </div>
                <p className="text-base font-bold text-neutral-900">{latestPublished.title}</p>
                <p className="text-sm text-neutral-600">{latestPublished.message}</p>
                <p className="text-xs text-neutral-500">
                  Audience: {audienceLabel(latestPublished.audience_type)} • Published {dateTimeLabel(latestPublished.sent_at)}
                </p>
              </div>
            ) : (
              <p className="text-sm text-neutral-500">No published state awareness item yet.</p>
            )}
          </div>
          <div className="mt-4 rounded-lg border border-brand-100 bg-brand-50 px-4 py-3 text-sm text-brand-900">
            Published notices stay visible in the State workspace and trigger in-app notifications for matching platform audiences.
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
        <div className="border-b border-neutral-200 px-5 py-4">
          <p className="text-sm font-bold text-neutral-900">Notice register</p>
          <p className="mt-1 text-sm text-neutral-500">Track creation, approval, publication, audience size, and archival state for all state awareness activity.</p>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-neutral-200 text-sm">
            <thead className="bg-neutral-50 text-left text-xs font-bold uppercase tracking-[0.16em] text-neutral-500">
              <tr>
                <th className="px-5 py-3">Notice</th>
                <th className="px-5 py-3">Audience</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3">Recipients</th>
                <th className="px-5 py-3">Timeline</th>
                <th className="px-5 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200 bg-white">
              {broadcastsQuery.isLoading ? (
                <tr><td className="px-5 py-6 text-neutral-500" colSpan={6}>Loading public awareness notices...</td></tr>
              ) : null}
              {!broadcastsQuery.isLoading && broadcasts.length === 0 ? (
                <tr><td className="px-5 py-6 text-neutral-500" colSpan={6}>No state awareness notices yet.</td></tr>
              ) : null}
              {broadcasts.map((item) => (
                <tr key={item.id}>
                  <td className="px-5 py-4 align-top">
                    <p className="font-semibold text-neutral-900">{item.title}</p>
                    <p className="mt-1 line-clamp-2 text-sm text-neutral-500">{item.message}</p>
                    <p className="mt-2 text-xs uppercase tracking-[0.16em] text-neutral-400">
                      {noticeKindLabel(String(item.audience_filters.notice_kind || "public_notice"))}
                    </p>
                  </td>
                  <td className="px-5 py-4 align-top">
                    <p className="font-medium text-neutral-900">{audienceLabel(item.audience_type)}</p>
                    <p className="mt-1 text-xs text-neutral-500">In-app delivery enabled where a platform audience exists.</p>
                  </td>
                  <td className="px-5 py-4 align-top">
                    <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${STATUS_STYLES[item.status] ?? "bg-neutral-100 text-neutral-700"}`}>
                      {statusLabel(item.status)}
                    </span>
                  </td>
                  <td className="px-5 py-4 align-top">
                    <div className="inline-flex items-center gap-2 rounded-full bg-neutral-100 px-2.5 py-1 text-xs font-semibold text-neutral-700">
                      <Users size={12} />
                      {item.estimated_recipient_count || item.sent_count || 0}
                    </div>
                  </td>
                  <td className="px-5 py-4 align-top text-sm text-neutral-500">
                    <p>Created {dateTimeLabel(item.created_at)}</p>
                    <p className="mt-1">{item.sent_at ? `Published ${dateTimeLabel(item.sent_at)}` : "Not yet published"}</p>
                  </td>
                  <td className="px-5 py-4 align-top">
                    <div className="flex flex-wrap justify-end gap-2">
                      {item.status === "draft" ? (
                        <>
                          <button
                            className="inline-flex h-9 items-center rounded-lg border border-neutral-200 px-3 text-xs font-semibold text-neutral-700"
                            disabled={estimateMutation.isPending}
                            onClick={() => estimateMutation.mutate(item.id)}
                            type="button"
                          >
                            Estimate
                          </button>
                          <button
                            className="inline-flex h-9 items-center rounded-lg border border-warning-200 px-3 text-xs font-semibold text-warning-800"
                            disabled={submitMutation.isPending}
                            onClick={() => submitMutation.mutate(item.id)}
                            type="button"
                          >
                            Submit
                          </button>
                        </>
                      ) : null}
                      {item.status === "pending_approval" ? (
                        <button
                          className="inline-flex h-9 items-center rounded-lg border border-brand-200 px-3 text-xs font-semibold text-brand-800"
                          disabled={approveMutation.isPending}
                          onClick={() => approveMutation.mutate(item.id)}
                          type="button"
                        >
                          Approve
                        </button>
                      ) : null}
                      {item.status === "approved" ? (
                        <button
                          className="inline-flex h-9 items-center rounded-lg bg-brand-700 px-3 text-xs font-semibold text-white"
                          disabled={publishMutation.isPending}
                          onClick={() => publishMutation.mutate(item.id)}
                          type="button"
                        >
                          Publish
                        </button>
                      ) : null}
                      {item.status !== "archived" ? (
                        <button
                          className="inline-flex h-9 items-center rounded-lg border border-neutral-200 px-3 text-xs font-semibold text-neutral-700"
                          disabled={archiveMutation.isPending}
                          onClick={() => archiveMutation.mutate(item.id)}
                          type="button"
                        >
                          Archive
                        </button>
                      ) : null}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
