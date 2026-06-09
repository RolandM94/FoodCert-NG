"use client";

import Link from "next/link";
import { Bell } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { getUnreadCount } from "@/lib/api/notifications";

export function NotificationBell({ href }: { href: string }) {
  const { data } = useQuery({
    queryKey: ["notifications", "unread-count"],
    queryFn: () => getUnreadCount(),
    refetchInterval: 30_000,
  });

  const count = data?.unread_count ?? 0;

  return (
    <Link
      className="relative inline-flex h-10 w-10 items-center justify-center rounded border border-neutral-200 text-neutral-700 hover:bg-neutral-50"
      href={href}
      aria-label={`Notifications${count > 0 ? ` (${count} unread)` : ""}`}
    >
      <Bell aria-hidden="true" size={18} />
      {count > 0 ? (
        <span className="absolute -right-1 -top-1 min-w-5 rounded-full bg-danger-500 px-1.5 py-0.5 text-center text-[10px] font-bold text-white">
          {count > 99 ? "99+" : count}
        </span>
      ) : null}
    </Link>
  );
}
