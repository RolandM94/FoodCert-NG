"use client";

import { useQuery } from "@tanstack/react-query";
import { Bell } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { listEmployerNotifications } from "@/lib/api/employer-management";
import { listEmployers } from "@/lib/api/identity";

function formatDate(value: string) {
  return new Date(value).toLocaleString("en-NG", { dateStyle: "medium", timeStyle: "short" });
}

export default function Page() {
  const employersQuery = useQuery({ queryKey: ["employers", "me"], queryFn: listEmployers });
  const employer = employersQuery.data?.[0];
  const notificationsQuery = useQuery({
    queryKey: ["employer-notifications", employer?.id],
    queryFn: () => listEmployerNotifications(employer!.id),
    enabled: Boolean(employer?.id),
  });

  const payload = notificationsQuery.data;
  const notifications = payload?.notifications || [];

  return (
    <PortalShell role="employer" title="Notifications" description="Review invite, certification, illness, inspection, compliance, and subscription notices.">
      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <div className="mb-5 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Bell className="text-brand-deep" size={18} />
            <h2 className="text-base font-bold text-slate-950">Notification Center</h2>
          </div>
          <span className="rounded bg-emerald-50 px-3 py-1 text-xs font-bold text-brand-deep ring-1 ring-emerald-200">
            {payload?.unread_count || 0} unread
          </span>
        </div>
        {notificationsQuery.isError ? <p className="rounded bg-rose-50 p-3 text-sm font-semibold text-rose-700">Could not load notifications.</p> : null}
        <div className="divide-y divide-slate-100">
          {notifications.map((item) => (
            <article key={item.id} className="py-4">
              <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
                <div>
                  <p className="font-bold text-slate-950">{item.subject}</p>
                  <p className="mt-1 text-sm leading-6 text-slate-600">{item.body}</p>
                  <p className="mt-2 text-xs font-semibold uppercase tracking-wide text-slate-400">{item.notification_type.replaceAll("_", " ")}</p>
                </div>
                <span className="shrink-0 text-xs font-semibold text-slate-500">{formatDate(item.created_at)}</span>
              </div>
            </article>
          ))}
          {!notifications.length && !notificationsQuery.isFetching ? <p className="py-8 text-center text-sm text-slate-500">No notifications yet.</p> : null}
        </div>
      </section>
    </PortalShell>
  );
}
