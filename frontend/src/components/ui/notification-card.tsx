"use client";

import { Archive, ArchiveRestore, Check, ExternalLink } from "lucide-react";
import Link from "next/link";
import type { NotificationRecord } from "@/types/notifications";

function formatDate(value: string) {
  return new Date(value).toLocaleString("en-NG", { dateStyle: "medium", timeStyle: "short" });
}

const priorityColors: Record<string, string> = {
  low: "border-l-slate-300",
  normal: "border-l-brand-green",
  high: "border-l-amber-500",
  critical: "border-l-rose-600",
};

export function NotificationCard({
  notification,
  onMarkRead,
  onArchive,
  onUnarchive,
}: {
  notification: NotificationRecord;
  onMarkRead?: (id: string) => void;
  onArchive?: (id: string) => void;
  onUnarchive?: (id: string) => void;
}) {
  const borderColor = priorityColors[notification.priority] || "border-l-slate-300";

  return (
    <article
      className={`border-l-4 bg-white px-4 py-4 ${borderColor} ${notification.is_read ? "opacity-70" : ""}`}
    >
      <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <h3 className="font-bold text-slate-950">{notification.title}</h3>
            {!notification.is_read ? (
              <span className="h-2 w-2 shrink-0 rounded-full bg-brand-green" />
            ) : null}
          </div>
          <p className="mt-1 text-sm leading-6 text-slate-600">{notification.message}</p>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <span className="rounded bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-600">
              {notification.category_display}
            </span>
            <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">
              {notification.priority_display}
            </span>
          </div>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <span className="text-xs font-semibold text-slate-500">{formatDate(notification.created_at)}</span>
          <div className="flex items-center gap-1">
            {!notification.is_read && onMarkRead ? (
              <button
                className="inline-flex h-8 w-8 items-center justify-center rounded text-slate-400 hover:bg-emerald-50 hover:text-brand-green"
                onClick={() => onMarkRead(notification.id)}
                title="Mark as read"
                type="button"
              >
                <Check aria-hidden="true" size={16} />
              </button>
            ) : null}
            {notification.action_url ? (
              <Link
                className="inline-flex h-8 w-8 items-center justify-center rounded text-slate-400 hover:bg-slate-100 hover:text-slate-700"
                href={notification.action_url}
                title="Open related record"
              >
                <ExternalLink aria-hidden="true" size={16} />
              </Link>
            ) : null}
            {notification.is_archived ? (
              onUnarchive ? (
                <button
                  className="inline-flex h-8 w-8 items-center justify-center rounded text-slate-400 hover:bg-amber-50 hover:text-amber-700"
                  onClick={() => onUnarchive(notification.id)}
                  title="Unarchive"
                  type="button"
                >
                  <ArchiveRestore aria-hidden="true" size={16} />
                </button>
              ) : null
            ) : onArchive ? (
              <button
                className="inline-flex h-8 w-8 items-center justify-center rounded text-slate-400 hover:bg-slate-100 hover:text-slate-700"
                onClick={() => onArchive(notification.id)}
                title="Archive"
                type="button"
              >
                <Archive aria-hidden="true" size={16} />
              </button>
            ) : null}
          </div>
        </div>
      </div>
    </article>
  );
}
