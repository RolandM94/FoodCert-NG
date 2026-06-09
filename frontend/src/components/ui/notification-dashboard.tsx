"use client";

import { useQuery } from "@tanstack/react-query";
import { BarChart3, Bell, CheckCircle2, Loader2, Mail, MessageSquare, Radio, RefreshCw, Send, Smartphone, Users } from "lucide-react";
import { apiClient, unwrap, type ApiEnvelope } from "@/lib/api/client";

type DashboardStats = {
  total_today: number;
  emails_today: number;
  sms_today: number;
  whatsapp_today: number;
  in_app_today: number;
  delivery_success_rate: number;
  failed_deliveries: number;
  pending_retries: number;
  critical_sent: number;
  broadcasts_sent: number;
  provider_failures: number;
  by_channel: Record<string, number>;
  by_category: Record<string, number>;
  by_status: Record<string, number>;
};

async function getDashboardStats(): Promise<DashboardStats> {
  const response = await apiClient.get<ApiEnvelope<DashboardStats>>("/admin/notifications/dashboard");
  return unwrap(response.data);
}

function formatNumber(n: number | null | undefined): string {
  if (n == null) return "0";
  return n >= 1000 ? `${(n / 1000).toFixed(1)}k` : String(n);
}

function StatCard({ label, value, icon: Icon, color }: { label: string; value: number; icon: React.ComponentType<{ size?: number; "aria-hidden"?: boolean }>; color?: string }) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">{label}</p>
          <p className="mt-2 text-2xl font-bold text-neutral-900">{formatNumber(value)}</p>
        </div>
        <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${color || "bg-brand-50 text-brand-700"}`}>
          <Icon aria-hidden={true} size={20} />
        </div>
      </div>
    </div>
  );
}

export function NotificationDashboard() {
  const { data: stats, isLoading, isError } = useQuery({
    queryKey: ["notification-dashboard"],
    queryFn: getDashboardStats,
    refetchInterval: 60_000,
  });

  if (isLoading) {
    return <div className="flex justify-center py-12"><Loader2 className="animate-spin text-neutral-400" size={32} /></div>;
  }

  if (isError || !stats) {
    return <p className="rounded bg-danger-50 p-4 text-sm font-semibold text-danger-700">Could not load dashboard.</p>;
  }

  const topCategories = Object.entries(stats.by_category)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4 lg:grid-cols-6">
        <StatCard label="Today" value={stats.total_today} icon={Bell} />
        <StatCard label="Email" value={stats.emails_today} icon={Mail} color="bg-info-50 text-blue-600" />
        <StatCard label="SMS" value={stats.sms_today} icon={Smartphone} color="bg-neutral-100 text-purple-600" />
        <StatCard label="WhatsApp" value={stats.whatsapp_today} icon={MessageSquare} color="bg-brand-100 text-brand-700" />
        <StatCard label="Success Rate" value={stats.delivery_success_rate} icon={CheckCircle2} color="bg-brand-50 text-brand-700" />
        <StatCard label="Failed" value={stats.failed_deliveries} icon={RefreshCw} color="bg-danger-50 text-danger-500" />
        <StatCard label="Pending Retries" value={stats.pending_retries} icon={RefreshCw} color="bg-warning-50 text-amber-600" />
        <StatCard label="Critical" value={stats.critical_sent} icon={Radio} color="bg-danger-50 text-danger-500" />
        <StatCard label="Broadcasts" value={stats.broadcasts_sent} icon={Send} color="bg-indigo-50 text-indigo-600" />
        <StatCard label="In-App" value={stats.in_app_today} icon={Users} />
      </div>

      {topCategories.length > 0 ? (
        <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex items-center gap-2">
            <BarChart3 className="text-brand-700" size={18} />
            <h3 className="text-base font-bold text-neutral-900">Top Categories</h3>
          </div>
          <div className="space-y-2">
            {topCategories.map(([cat, count]) => (
              <div key={cat} className="flex items-center gap-3">
                <span className="w-32 text-sm font-semibold text-neutral-700 capitalize">{cat.replaceAll("_", " ")}</span>
                <div className="flex-1 h-5 rounded bg-neutral-100 overflow-hidden">
                  <div className="h-full rounded bg-brand-600" style={{ width: `${Math.min(100, (count / Math.max(1, topCategories[0][1])) * 100)}%` }} />
                </div>
                <span className="text-xs font-bold text-neutral-500 w-10 text-right">{count}</span>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
