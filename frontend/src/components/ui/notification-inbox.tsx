"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Bell, Loader2 } from "lucide-react";
import { useState, useCallback } from "react";
import {
  archiveNotification,
  listNotifications,
  markAllNotificationsRead,
  markNotificationRead,
  unarchiveNotification,
} from "@/lib/api/notifications";
import { NotificationCard } from "@/components/ui/notification-card";
import { NotificationFilters } from "@/components/ui/notification-filters";
import type { NotificationCategory, NotificationPriority } from "@/types/notifications";

type FilterState = {
  search: string;
  selectedCategories: NotificationCategory[];
  selectedPriorities: NotificationPriority[];
  readFilter: "all" | "unread" | "read";
  archivedFilter: "all" | "active" | "archived";
};

const DEFAULT_FILTERS: FilterState = {
  search: "",
  selectedCategories: [],
  selectedPriorities: [],
  readFilter: "all",
  archivedFilter: "active",
};

export function NotificationInbox() {
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);
  const queryClient = useQueryClient();

  const apiParams: Record<string, string | undefined> = {};
  if (filters.selectedCategories.length > 0) {
    filters.selectedCategories.forEach((c) => {
      apiParams[`category`] = apiParams[`category`]
        ? `${apiParams[`category`]}&category=${c}`
        : c;
    });
  }
  // Note: for simplicity we manually build params; use URLSearchParams in production
  const params = new URLSearchParams();
  filters.selectedCategories.forEach((c) => params.append("category", c));
  filters.selectedPriorities.forEach((p) => params.append("priority", p));
  if (filters.readFilter === "unread") params.set("is_read", "false");
  else if (filters.readFilter === "read") params.set("is_read", "true");
  if (filters.archivedFilter === "active") params.set("is_archived", "false");
  else if (filters.archivedFilter === "archived") params.set("is_archived", "true");
  if (filters.search) params.set("search", filters.search);

  const queryParams: Record<string, string> = {};
  params.forEach((value, key) => {
    queryParams[key] = value;
  });

  const { data: notifications = [], isLoading, isError, isFetching } = useQuery({
    queryKey: ["notifications", queryParams],
    queryFn: () => listNotifications(queryParams),
  });

  const markReadMutation = useMutation({
    mutationFn: markNotificationRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["notifications", "unread-count"] });
    },
  });

  const archiveMutation = useMutation({
    mutationFn: archiveNotification,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });

  const unarchiveMutation = useMutation({
    mutationFn: unarchiveNotification,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });

  const markAllReadMutation = useMutation({
    mutationFn: () => markAllNotificationsRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["notifications", "unread-count"] });
    },
  });

  const handleClearFilters = useCallback(() => {
    setFilters(DEFAULT_FILTERS);
  }, []);

  return (
    <div className="space-y-4">
      <NotificationFilters
        filters={filters}
        onChange={setFilters}
        onMarkAllRead={() => markAllReadMutation.mutate()}
        onClearFilters={handleClearFilters}
      />

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="animate-spin text-slate-400" size={24} />
        </div>
      ) : isError ? (
        <p className="rounded bg-rose-50 p-4 text-sm font-semibold text-rose-700">
          Could not load notifications. Please try again.
        </p>
      ) : (
        <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
          {notifications.length > 0 ? (
            <div className="divide-y divide-slate-100">
              {notifications.map((item) => (
                <NotificationCard
                  key={item.id}
                  notification={item}
                  onMarkRead={markReadMutation.mutate}
                  onArchive={archiveMutation.mutate}
                  onUnarchive={unarchiveMutation.mutate}
                />
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <Bell className="mb-3 text-slate-300" size={40} aria-hidden="true" />
              <p className="text-sm font-semibold text-slate-500">No notifications</p>
              <p className="mt-1 text-xs text-slate-400">
                {filters.archivedFilter === "archived"
                  ? "No archived notifications."
                  : "You're all caught up."}
              </p>
            </div>
          )}
          {isFetching && notifications.length > 0 ? (
            <div className="flex items-center justify-center border-t border-slate-100 py-2">
              <Loader2 className="animate-spin text-slate-400" size={16} />
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}
