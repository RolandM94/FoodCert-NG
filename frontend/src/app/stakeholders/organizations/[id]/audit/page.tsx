"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Activity, UserPlus, UsersRound, ShieldCheck, Settings, Clock, AlertTriangle, FileText } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";

const MOCK_EVENTS = [
  { id: "1", action: "Organization created", actor: "system@foodcert.ng", timestamp: "2025-06-01T08:00:00Z", target: "Initial setup" },
  { id: "2", action: "Status changed to active", actor: "admin@foodcert.ng", timestamp: "2025-06-01T08:05:00Z", target: "Activation" },
];

const ACTION_ICONS: Record<string, typeof Activity> = {
  "Organization created": Settings,
  "Status changed": ShieldCheck,
  "User invited": UserPlus,
  "User joined": UsersRound,
  "Role changed": Settings,
  "Unit created": Activity,
  "Unit updated": Activity,
  default: FileText,
};

function formatDate(value?: string) {
  if (!value) return "N/A";
  return new Date(value).toLocaleString("en-NG", { dateStyle: "medium", timeStyle: "short" });
}

export default function OrganizationAuditPage() {
  const params = useParams<{ id: string }>();
  const organizationId = params.id;
  const [logs, setLogs] = useState(MOCK_EVENTS);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setTimeout(() => setLoading(false), 600);
  }, []);

  return (
    <PortalShell
      role="super_admin"
      title="Audit Logs"
      description="Track all administrative actions, role changes, unit modifications, and security events for this organization."
    >
      <div className="space-y-6">
        <div className="flex flex-wrap gap-3">
          <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm text-slate-700">
            <option value="">All actions</option>
            <option value="org">Organization changes</option>
            <option value="unit">Unit changes</option>
            <option value="user">User changes</option>
            <option value="role">Role changes</option>
            <option value="invite">Invite events</option>
          </select>
          <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm text-slate-700">
            <option value="">All dates</option>
            <option value="today">Today</option>
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
          </select>
        </div>

        <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-500">Action</th>
                  <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-500">Actor</th>
                  <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-500">Target</th>
                  <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-500">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading ? (
                  <tr>
                    <td className="px-4 py-8 text-center text-slate-500" colSpan={4}>
                      Loading audit log data...
                    </td>
                  </tr>
                ) : logs.length === 0 ? (
                  <tr>
                    <td className="px-4 py-8 text-center text-slate-500" colSpan={4}>
                      No audit events recorded yet.
                    </td>
                  </tr>
                ) : (
                  logs.map((log) => {
                    const matchedKey = Object.keys(ACTION_ICONS).find((key) =>
                      log.action.startsWith(key)
                    );
                    const Icon = matchedKey ? ACTION_ICONS[matchedKey] : ACTION_ICONS.default;
                    return (
                      <tr key={log.id} className="hover:bg-slate-50">
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <Icon size={14} className="text-slate-400 shrink-0" />
                            <span className="font-semibold text-slate-800">{log.action}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-slate-600">{log.actor}</td>
                        <td className="px-4 py-3 text-slate-600">{log.target}</td>
                        <td className="px-4 py-3 text-slate-500">{formatDate(log.timestamp)}</td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </section>

        <p className="text-xs text-slate-400">
          Audit logs for organization ID: {organizationId}. Backend integration required for production audit events.
        </p>
      </div>
    </PortalShell>
  );
}
