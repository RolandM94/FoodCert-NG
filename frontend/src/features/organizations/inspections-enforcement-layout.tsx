"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Activity, AlertTriangle, BarChart3, ClipboardCheck, Download, ExternalLink,
  FileText, Plus, ShieldAlert, ShieldCheck,
} from "lucide-react";
import Link from "next/link";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { DashboardCard } from "@/components/ui/dashboard-card";
import {
  assignStateInspection,
  closeStateInspection,
  fetchStateEmployers,
  fetchStateInspections,
  fetchStateUsers,
  reviewStateInspection,
  type StateInspectionItem,
} from "@/lib/api/state";
import {
  closeCase,
  closeNotice,
  escalateCase,
  fetchStateEnforcementDashboard,
  listEnforcementCases,
  listEnforcementNotices,
} from "@/lib/api/inspections";
import { fetchFormTemplates } from "@/lib/api/forms";
import { getApiErrorMessage } from "@/lib/api/client";

type TabKey = "overview" | "inspections" | "cases" | "notices" | "reports";
const TABS: Record<TabKey, string> = {
  overview: "Overview",
  inspections: "Inspections",
  cases: "Cases",
  notices: "Notices",
  reports: "Reports",
};

function dateLabel(value?: string | null) {
  if (!value) return "—";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

function unwrapList(data: unknown): Record<string, unknown>[] {
  if (Array.isArray(data)) return data;
  if (data && typeof data === "object" && "data" in data) return (data as { data: Record<string, unknown>[] }).data || [];
  return [];
}

// ── Overview Tab ──
function OverviewTab() {
  const dashboardQuery = useQuery({
    queryKey: ["enforcement-dashboard"],
    queryFn: () => fetchStateEnforcementDashboard(),
  });
  const cards = (dashboardQuery.data?.cards || {}) as Record<string, number>;

  return (
    <div className="grid gap-5">
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <DashboardCard icon={ClipboardCheck} label="Total inspections" value={cards.total_inspections ?? 0} />
        <DashboardCard icon={Activity} label="This month" value={cards.inspections_this_month ?? 0} />
        <DashboardCard icon={ShieldCheck} label="Open cases" value={cards.open_cases ?? 0} />
        <DashboardCard icon={AlertTriangle} label="Notices issued" value={cards.notices_issued ?? 0} />
        <DashboardCard icon={ShieldAlert} label="Critical findings" value={cards.critical_findings ?? 0} />
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <DashboardCard icon={Activity} label="Follow-ups pending" value={cards.follow_ups_pending ?? 0} />
        <DashboardCard icon={BarChart3} label="Corrective actions" value={cards.overdue_corrective_actions ?? 0} />
        <DashboardCard icon={Activity} label="Active inspectors" value={cards.inspectors_active ?? 0} />
        <DashboardCard icon={ClipboardCheck} label="Branches inspected" value={cards.branches_inspected ?? 0} />
      </div>
      {dashboardQuery.isLoading ? <p className="rounded border border-neutral-200 bg-white p-6 text-sm text-neutral-500">Loading dashboard...</p> : null}
    </div>
  );
}

// ── Inspections Tab ──
function InspectionsTab() {
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState("");
  const [search, setSearch] = useState("");
  const [showAssign, setShowAssign] = useState(false);
  const [inspectorId, setInspectorId] = useState("");
  const [employerId, setEmployerId] = useState("");
  const [templateId, setTemplateId] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState("");

  const inspectionsQuery = useQuery({
    queryKey: ["state-inspections-enf", statusFilter, search],
    queryFn: () => fetchStateInspections({ status: statusFilter as "" | "draft", search }),
  });
  const usersQuery = useQuery({ queryKey: ["state-users-insp"], queryFn: fetchStateUsers });
  const employersQuery = useQuery({ queryKey: ["state-employers-insp"], queryFn: () => fetchStateEmployers() });
  const templatesQuery = useQuery({
    queryKey: ["insp-form-templates"],
    queryFn: () => fetchFormTemplates({ purpose: "inspection_checklist", status: "published" }),
  });

  const assignMut = useMutation({
    mutationFn: () => assignStateInspection({ inspector: inspectorId, employer: employerId, form_template: templateId || undefined, findings: notes }),
    onSuccess: () => { setShowAssign(false); setNotes(""); setError(""); queryClient.invalidateQueries({ queryKey: ["state-inspections-enf"] }); },
    onError: (err) => setError(getApiErrorMessage(err, "Could not assign inspection.")),
  });

  const inspectors = (usersQuery.data || []).filter((u) => u.role === "inspector");
  const rows = inspectionsQuery.data || [];

  return (
    <div className="grid gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-2">
          <input className="h-9 w-56 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" placeholder="Search employer, inspector..." value={search} onChange={(e) => setSearch(e.target.value)} />
          <select className="h-9 rounded border border-neutral-200 bg-white px-3 text-sm" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">All statuses</option>
            <option value="assigned">Assigned</option>
            <option value="in_progress">In Progress</option>
            <option value="submitted">Submitted</option>
            <option value="under_review">Under Review</option>
            <option value="closed">Closed</option>
          </select>
        </div>
        <button className="inline-flex h-9 items-center gap-2 rounded bg-brand-600 px-4 text-sm font-bold text-white" onClick={() => setShowAssign(!showAssign)} type="button"><Plus size={14} /> Create Inspection</button>
      </div>

      {showAssign && (
        <div className="grid gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm sm:grid-cols-2 lg:grid-cols-4">
          <select className="h-9 rounded border border-neutral-200 bg-white px-3 text-sm" value={inspectorId} onChange={(e) => setInspectorId(e.target.value)}>
            <option value="">Select inspector</option>
            {inspectors.map((u) => <option key={u.id} value={u.id}>{u.first_name} {u.last_name}</option>)}
          </select>
          <select className="h-9 rounded border border-neutral-200 bg-white px-3 text-sm" value={employerId} onChange={(e) => setEmployerId(e.target.value)}>
            <option value="">Select employer</option>
            {(employersQuery.data || []).map((emp) => <option key={emp.id} value={emp.id}>{emp.business_name}</option>)}
          </select>
          <select className="h-9 rounded border border-neutral-200 bg-white px-3 text-sm" value={templateId} onChange={(e) => setTemplateId(e.target.value)}>
            <option value="">No checklist template</option>
            {(templatesQuery.data || []).map((t) => <option key={t.id} value={t.id}>{t.title}</option>)}
          </select>
          <button className="h-9 rounded bg-brand-700 px-4 text-sm font-bold text-white disabled:opacity-50" disabled={!inspectorId || !employerId || assignMut.isPending} onClick={() => assignMut.mutate()} type="button">{assignMut.isPending ? "Assigning..." : "Assign"}</button>
          {error ? <p className="col-span-full text-xs font-semibold text-danger-700">{error}</p> : null}
        </div>
      )}

      <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-neutral-200 text-sm">
          <thead className="bg-neutral-50 text-left text-xs font-bold uppercase text-neutral-500">
            <tr>
              <th className="px-4 py-3">Employer</th>
              <th className="px-4 py-3">Inspector</th>
              <th className="px-4 py-3">Date</th>
              <th className="px-4 py-3">Score</th>
              <th className="px-4 py-3">Enforcement</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100">
            {rows.map((row) => (
              <tr key={row.id} className="hover:bg-neutral-50">
                <td className="px-4 py-3 font-semibold text-neutral-900">{row.employer_name}</td>
                <td className="px-4 py-3 text-neutral-600">{row.inspector_name || "Unassigned"}</td>
                <td className="px-4 py-3 text-neutral-600">{dateLabel(row.inspection_date)}</td>
                <td className="px-4 py-3 text-neutral-600">{row.compliance_score ? `${row.compliance_score}%` : "—"}</td>
                <td className="px-4 py-3"><StatusBadge status={row.enforcement_action} /></td>
                <td className="px-4 py-3"><StatusBadge status={row.status} /></td>
                <td className="px-4 py-3 text-right">
                  <Link className="inline-flex h-8 items-center gap-1 rounded border border-neutral-200 px-2 text-xs font-bold text-neutral-700 hover:bg-neutral-50" href={`/state/inspections-enforcement/${row.id}`}>
                    <ExternalLink size={12} /> View
                  </Link>
                </td>
              </tr>
            ))}
            {!rows.length && !inspectionsQuery.isLoading ? <tr><td className="px-4 py-6 text-neutral-500" colSpan={7}>No inspections match filters.</td></tr> : null}
            {inspectionsQuery.isLoading ? <tr><td className="px-4 py-6 text-neutral-500" colSpan={7}>Loading...</td></tr> : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ── Cases Tab ──
function CasesTab() {
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState("");
  const casesQuery = useQuery({
    queryKey: ["enforcement-cases-tab", statusFilter],
    queryFn: () => listEnforcementCases(statusFilter ? { status: statusFilter } : undefined),
  });
  const cases = unwrapList(casesQuery.data);

  const escalateMut = useMutation({
    mutationFn: (id: string) => escalateCase(id, "Escalated from cases tab."),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["enforcement-cases-tab"] }),
  });
  const closeMut = useMutation({
    mutationFn: (id: string) => closeCase(id, "Closed from enforcement module."),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["enforcement-cases-tab"] }),
  });

  return (
    <div className="grid gap-4">
      <div className="flex flex-wrap items-center gap-3">
        <select className="h-9 rounded border border-neutral-200 bg-white px-3 text-sm" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="">All statuses</option>
          <option value="open">Open</option>
          <option value="under_review">Under Review</option>
          <option value="escalated">Escalated</option>
          <option value="resolved">Resolved</option>
          <option value="closed">Closed</option>
        </select>
      </div>

      <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-neutral-200 text-sm">
          <thead className="bg-neutral-50 text-left text-xs font-bold uppercase text-neutral-500">
            <tr>
              <th className="px-4 py-3">Reference</th>
              <th className="px-4 py-3">Employer</th>
              <th className="px-4 py-3">Severity</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Opened</th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100">
            {cases.map((row) => (
              <tr key={String(row.id)} className="hover:bg-neutral-50">
                <td className="px-4 py-3 font-semibold text-neutral-900">{String(row.case_reference || row.id)}</td>
                <td className="px-4 py-3 text-neutral-600">{String(row.employer_name || row.employer || "—")}</td>
                <td className="px-4 py-3"><StatusBadge status={String(row.severity || "medium")} /></td>
                <td className="px-4 py-3"><StatusBadge status={String(row.status || "open")} /></td>
                <td className="px-4 py-3 text-neutral-600">{dateLabel(row.created_at as string)}</td>
                <td className="px-4 py-3 space-x-1">
                  {row.status !== "closed" && row.status !== "resolved" ? (
                    <>
                      <button className="h-7 rounded border border-warning-200 px-2 text-xs font-bold text-warning-700" onClick={() => escalateMut.mutate(String(row.id))} type="button">Escalate</button>
                      <button className="h-7 rounded border border-neutral-200 px-2 text-xs font-bold text-neutral-700" onClick={() => closeMut.mutate(String(row.id))} type="button">Close</button>
                    </>
                  ) : null}
                </td>
              </tr>
            ))}
            {!cases.length && !casesQuery.isLoading ? <tr><td className="px-4 py-6 text-neutral-500" colSpan={6}>No cases found.</td></tr> : null}
            {casesQuery.isLoading ? <tr><td className="px-4 py-6 text-neutral-500" colSpan={6}>Loading...</td></tr> : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ── Notices Tab ──
function NoticesTab() {
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState("");
  const noticesQuery = useQuery({
    queryKey: ["enforcement-notices-tab", statusFilter],
    queryFn: () => listEnforcementNotices(statusFilter ? { status: statusFilter } : undefined),
  });
  const notices = unwrapList(noticesQuery.data);

  const closeMut = useMutation({
    mutationFn: (id: string) => closeNotice(id, "Closed from enforcement module."),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["enforcement-notices-tab"] }),
  });

  return (
    <div className="grid gap-4">
      <div className="flex flex-wrap items-center gap-3">
        <select className="h-9 rounded border border-neutral-200 bg-white px-3 text-sm" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="">All statuses</option>
          <option value="draft">Draft</option>
          <option value="issued">Issued</option>
          <option value="acknowledged">Acknowledged</option>
          <option value="response_submitted">Response Submitted</option>
          <option value="closed">Closed</option>
        </select>
      </div>

      <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-neutral-200 text-sm">
          <thead className="bg-neutral-50 text-left text-xs font-bold uppercase text-neutral-500">
            <tr>
              <th className="px-4 py-3">Reference</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Employer</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Deadline</th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100">
            {notices.map((row) => (
              <tr key={String(row.id)} className="hover:bg-neutral-50">
                <td className="px-4 py-3 font-semibold text-neutral-900">{String(row.notice_reference || row.id)}</td>
                <td className="px-4 py-3 text-neutral-600">{String(row.notice_type || "—").replaceAll("_", " ")}</td>
                <td className="px-4 py-3 text-neutral-600">{String(row.employer_name || row.employer || "—")}</td>
                <td className="px-4 py-3"><StatusBadge status={String(row.status || "draft")} /></td>
                <td className="px-4 py-3 text-neutral-600">{dateLabel(row.deadline as string)}</td>
                <td className="px-4 py-3">
                  {row.status !== "closed" ? (
                    <button className="h-7 rounded border border-neutral-200 px-2 text-xs font-bold text-neutral-700" onClick={() => closeMut.mutate(String(row.id))} type="button">Close</button>
                  ) : null}
                </td>
              </tr>
            ))}
            {!notices.length && !noticesQuery.isLoading ? <tr><td className="px-4 py-6 text-neutral-500" colSpan={6}>No notices found.</td></tr> : null}
            {noticesQuery.isLoading ? <tr><td className="px-4 py-6 text-neutral-500" colSpan={6}>Loading...</td></tr> : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ── Reports Tab ──
function ReportsTab() {
  const dashboardQuery = useQuery({
    queryKey: ["enforcement-dashboard-reports"],
    queryFn: () => fetchStateEnforcementDashboard(),
  });
  const cards = (dashboardQuery.data?.cards || {}) as Record<string, number>;

  return (
    <div className="grid gap-5">
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <DashboardCard icon={ClipboardCheck} label="Total inspections" value={cards.total_inspections ?? 0} />
        <DashboardCard icon={ShieldCheck} label="Open cases" value={cards.open_cases ?? 0} />
        <DashboardCard icon={AlertTriangle} label="Critical findings" value={cards.critical_findings ?? 0} />
        <DashboardCard icon={FileText} label="Total notices" value={cards.total_notices_issued ?? cards.notices_issued ?? 0} />
      </div>
      <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
        <h3 className="mb-3 text-sm font-bold text-neutral-900">Export Reports</h3>
        <p className="text-sm text-neutral-600">Use the Inspections, Cases, and Notices tabs to filter records, then export using your browser or the platform export tools.</p>
        <div className="mt-4 flex gap-3">
          <button className="inline-flex h-9 items-center gap-2 rounded border border-neutral-200 px-3 text-sm font-bold text-neutral-700" type="button"><Download size={14} /> Inspection Summary (CSV)</button>
          <button className="inline-flex h-9 items-center gap-2 rounded border border-neutral-200 px-3 text-sm font-bold text-neutral-700" type="button"><Download size={14} /> Cases Report (CSV)</button>
          <button className="inline-flex h-9 items-center gap-2 rounded border border-neutral-200 px-3 text-sm font-bold text-neutral-700" type="button"><Download size={14} /> Notices Report (CSV)</button>
        </div>
      </div>
    </div>
  );
}

// ── Main Layout ──
export function InspectionsEnforcementLayout() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const tabParam = (searchParams.get("tab") ?? "overview") as TabKey;
  const activeTab = TABS[tabParam] ? tabParam : "overview";

  function setTab(tab: TabKey) {
    router.replace(`/state/inspections-enforcement?tab=${tab}`);
  }

  return (
    <PortalShell role="state_admin" title="Inspections & Enforcement" description="Plan inspections, track findings, issue notices, manage cases, and report on compliance.">
      <nav className="mb-6 flex gap-0 overflow-x-auto border-b border-neutral-200">
        {(Object.entries(TABS) as [TabKey, string][]).map(([key, label]) => (
          <button
            key={key}
            className={`shrink-0 border-b-2 px-4 py-3 text-sm font-medium ${activeTab === key ? "border-brand-600 text-brand-700" : "border-transparent text-neutral-500 hover:text-neutral-800"}`}
            onClick={() => setTab(key)}
            type="button"
          >
            {label}
          </button>
        ))}
      </nav>
      {activeTab === "overview" && <OverviewTab />}
      {activeTab === "inspections" && <InspectionsTab />}
      {activeTab === "cases" && <CasesTab />}
      {activeTab === "notices" && <NoticesTab />}
      {activeTab === "reports" && <ReportsTab />}
    </PortalShell>
  );
}
