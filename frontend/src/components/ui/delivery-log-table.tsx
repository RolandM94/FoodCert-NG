"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Loader2, RefreshCw } from "lucide-react";
import { retryDelivery, listDeliveries } from "@/lib/api/notifications";
import type { NotificationDelivery } from "@/types/notifications";

function formatDate(value: string | null) {
  if (!value) return "-";
  return new Date(value).toLocaleString("en-NG", { dateStyle: "medium", timeStyle: "short" });
}

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-slate-100 text-slate-600",
  queued: "bg-blue-100 text-blue-700",
  sending: "bg-amber-100 text-amber-700",
  sent: "bg-emerald-100 text-emerald-800",
  delivered: "bg-emerald-200 text-emerald-900",
  failed: "bg-rose-100 text-rose-800",
  bounced: "bg-orange-100 text-orange-800",
  rejected: "bg-red-100 text-red-800",
  opened: "bg-cyan-100 text-cyan-800",
  clicked: "bg-indigo-100 text-indigo-800",
  cancelled: "bg-slate-200 text-slate-500",
};

export function DeliveryLogTable() {
  const queryClient = useQueryClient();

  const { data: deliveries = [], isLoading } = useQuery({
    queryKey: ["notification-deliveries"],
    queryFn: () => listDeliveries(),
    refetchInterval: 15_000,
  });

  const retryMutation = useMutation({
    mutationFn: retryDelivery,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notification-deliveries"] }),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-slate-400" size={24} />
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
      <table className="w-full text-left text-sm">
        <thead className="bg-slate-50 text-xs font-bold uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-4 py-3">Notification</th>
            <th className="px-4 py-3">Channel</th>
            <th className="px-4 py-3">Destination</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Retries</th>
            <th className="px-4 py-3">Sent</th>
            <th className="px-4 py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {deliveries.map((d) => (
            <tr key={d.id} className="hover:bg-slate-50">
              <td className="px-4 py-3 max-w-xs truncate text-slate-900" title={d.notification_title}>
                {d.notification_title || d.id.slice(0, 8)}
              </td>
              <td className="px-4 py-3 text-slate-600 capitalize">{d.channel_display}</td>
              <td className="px-4 py-3 font-mono text-xs text-slate-600">{d.destination}</td>
              <td className="px-4 py-3">
                <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-semibold ${STATUS_COLORS[d.status] || "bg-slate-100 text-slate-600"}`}>
                  {d.status_display}
                </span>
              </td>
              <td className="px-4 py-3 text-slate-600">{d.retry_count}</td>
              <td className="px-4 py-3 text-xs text-slate-500">{formatDate(d.sent_at)}</td>
              <td className="px-4 py-3">
                <div className="flex items-center justify-end gap-1">
                  {(d.status === "failed" || d.status === "bounced") ? (
                    <button
                      className="inline-flex h-8 items-center gap-1 rounded border border-slate-200 px-2.5 text-xs font-semibold text-slate-700 hover:bg-amber-50 hover:text-amber-800 disabled:opacity-50"
                      disabled={retryMutation.isPending}
                      onClick={() => retryMutation.mutate(d.id)}
                      title="Retry delivery"
                      type="button"
                    >
                      {retryMutation.isPending ? <Loader2 className="animate-spin" size={14} /> : <RefreshCw size={14} />}
                      Retry
                    </button>
                  ) : null}
                </div>
              </td>
            </tr>
          ))}
          {!deliveries.length ? (
            <tr>
              <td className="px-4 py-8 text-center text-sm text-slate-500" colSpan={7}>
                No deliveries yet.
              </td>
            </tr>
          ) : null}
        </tbody>
      </table>
    </div>
  );
}
