"use client";

import { useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Activity, BadgeCheck, BarChart3, CalendarDays, ClipboardCheck, ClipboardList,
  FileStack, FlaskConical, Landmark, Plus, Search, Settings, UsersRound, X, Pencil,
} from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { DashboardCard } from "@/components/ui/dashboard-card";
import {
  fetchFormTemplates, createFormTemplate, publishFormTemplate, archiveFormTemplate,
  fetchFormAssignments, createFormAssignment, cancelFormAssignment,
  fetchFormResponses, submitFormResponse, reviewFormResponse, returnFormResponse,
} from "@/lib/api/forms";
import { getApiErrorMessage } from "@/lib/api/client";
import type { FormTemplate, FormAssignment as FrmAssignment, FormResponse as FrmResponse } from "@/lib/api/forms";

type TabKey = "overview" | "templates" | "assignments" | "responses" | "reports" | "settings";

const TABS: Record<TabKey, string> = {
  overview: "Overview", templates: "Templates", assignments: "Assignments",
  responses: "Responses", reports: "Reports", settings: "Settings",
};

const PURPOSE_LABELS: Record<string, string> = {
  inspection_checklist: "Inspection Checklist",
  employer_data_collection: "Employer Data Collection",
  employer_compliance: "Compliance Self-Assessment",
  facility_data_collection: "Facility Data Collection",
  facility_monthly_report: "Monthly Report",
  accreditation_checklist: "Accreditation Checklist",
  re_accreditation_checklist: "Re-accreditation Checklist",
  food_handler_survey: "Food Handler Survey",
  food_handler_declaration: "Food Handler Declaration",
  incident_report: "Incident Report",
  training_feedback: "Training Feedback",
  general_data_collection: "General Data Collection",
};

function formatDate(v?: string) { if (!v) return "—"; return new Date(v).toLocaleDateString("en-NG", { dateStyle: "medium" }); }

// ── Overview Tab ──
function OverviewTab() {
  const { data: templates } = useQuery({ queryKey: ["form-templates"], queryFn: async () => fetchFormTemplates() });
  const { data: assignments } = useQuery({ queryKey: ["form-assignments"], queryFn: async () => fetchFormAssignments() });
  const { data: responses } = useQuery({ queryKey: ["form-responses"], queryFn: async () => fetchFormResponses() });
  const tl = Array.isArray(templates) ? templates : [];
  const al = Array.isArray(assignments) ? assignments : [];
  const rl = Array.isArray(responses) ? responses : [];

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <DashboardCard icon={FileStack} label="Templates" value={tl.length} />
        <DashboardCard icon={ClipboardList} label="Assignments" value={al.length} />
        <DashboardCard icon={ClipboardCheck} label="Submitted" value={rl.filter(r => r.status==="submitted").length} />
        <DashboardCard icon={Activity} label="Overdue" value={al.filter(a => a.status==="overdue").length} />
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm">
          <h3 className="text-sm font-bold text-neutral-900">Recent Templates</h3>
          <div className="mt-3 space-y-2">
            {tl.slice(0,5).map(t => (
              <div key={t.id} className="flex justify-between text-sm border-b border-neutral-50 pb-2">
                <span className="font-medium text-neutral-800">{t.title}</span>
                <StatusBadge status={t.status} />
              </div>
            ))}
            {tl.length === 0 && <p className="text-sm text-neutral-500">No templates yet.</p>}
          </div>
        </section>
        <section className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm">
          <h3 className="text-sm font-bold text-neutral-900">Recent Responses</h3>
          <div className="mt-3 space-y-2">
            {rl.slice(0,5).map(r => (
              <div key={r.id} className="flex justify-between text-sm border-b border-neutral-50 pb-2">
                <span className="font-medium text-neutral-800">{r.template_title}</span>
                <span className="text-xs text-neutral-500">{r.respondent_name} · {formatDate(r.submitted_at)}</span>
              </div>
            ))}
            {rl.length === 0 && <p className="text-sm text-neutral-500">No responses yet.</p>}
          </div>
        </section>
      </div>
    </div>
  );
}

// ── Templates Tab ──
function TemplatesTab() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ title: "", description: "", purpose: "general_data_collection", target_respondent_type: "" });

  const { data: templates, isLoading } = useQuery({ queryKey: ["form-templates"], queryFn: async () => fetchFormTemplates() });
  const items = Array.isArray(templates) ? templates : [];

  const createMut = useMutation({
    mutationFn: () => createFormTemplate({ ...form, owner_organization: "00000000-0000-0000-0000-000000000000" }),
    onSuccess: () => { setShowForm(false); setForm({ title: "", description: "", purpose: "general_data_collection", target_respondent_type: "" }); setError(null); queryClient.invalidateQueries({ queryKey: ["form-templates"] }); },
    onError: (err) => setError(getApiErrorMessage(err, "Failed to create template.")),
  });
  const publishMut = useMutation({
    mutationFn: (id: string) => publishFormTemplate(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["form-templates"] }),
  });
  const archiveMut = useMutation({
    mutationFn: (id: string) => archiveFormTemplate(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["form-templates"] }),
  });

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <button className="inline-flex h-10 items-center gap-2 rounded-lg bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700" onClick={() => setShowForm(true)} type="button"><Plus size={16} />Create Template</button>
      </div>

      {showForm && (
        <div className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm space-y-3">
          <h3 className="text-sm font-bold text-neutral-900">New Template</h3>
          {error && <p className="text-sm font-semibold text-danger-700 bg-danger-50 rounded px-3 py-2">{error}</p>}
          <input className="h-10 w-full rounded-lg border border-neutral-200 px-3 text-sm" placeholder="Template title" value={form.title} onChange={e => setForm(p => ({...p, title: e.target.value}))} />
          <textarea className="w-full rounded-lg border border-neutral-200 px-3 py-2 text-sm" rows={2} placeholder="Description" value={form.description} onChange={e => setForm(p => ({...p, description: e.target.value}))} />
          <select className="h-10 w-full rounded-lg border border-neutral-200 px-3 text-sm" value={form.purpose} onChange={e => setForm(p => ({...p, purpose: e.target.value}))}>
            {Object.entries(PURPOSE_LABELS).map(([k,v]) => <option key={k} value={k}>{v}</option>)}
          </select>
          <div className="flex gap-2">
            <button className="h-10 rounded-lg bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60" disabled={!form.title || createMut.isPending} onClick={() => createMut.mutate()} type="button">{createMut.isPending ? "Creating..." : "Save"}</button>
            <button className="h-10 rounded-lg border border-neutral-200 px-4 text-sm font-medium text-neutral-700 hover:bg-neutral-50" onClick={() => setShowForm(false)} type="button">Cancel</button>
          </div>
        </div>
      )}

      <section className="overflow-hidden rounded-xl border border-neutral-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-neutral-200 text-sm">
          <thead className="bg-neutral-50"><tr>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Template</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Purpose</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Version</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Responses</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Status</th>
            <th className="px-4 py-3 text-right text-xs font-medium uppercase text-neutral-500">Actions</th>
          </tr></thead>
          <tbody className="divide-y divide-neutral-100">
            {isLoading ? <tr><td className="px-4 py-8 text-center text-neutral-500" colSpan={6}>Loading...</td></tr>
            : items.length === 0 ? <tr><td className="px-4 py-8 text-center text-neutral-500" colSpan={6}>No templates yet.</td></tr>
            : items.map(t => (
              <tr key={t.id} className="hover:bg-neutral-50">
                <td className="px-4 py-3"><p className="font-semibold text-neutral-900">{t.title}</p><p className="text-xs text-neutral-500">{t.description?.slice(0,80)}</p></td>
                <td className="px-4 py-3 text-xs text-neutral-600">{PURPOSE_LABELS[t.purpose] ?? t.purpose}</td>
                <td className="px-4 py-3 text-neutral-700">v{t.current_version}</td>
                <td className="px-4 py-3 text-neutral-700">{t.response_count}</td>
                <td className="px-4 py-3"><StatusBadge status={t.status} /></td>
                <td className="px-4 py-3 text-right">
                  {t.status === "draft" && <button className="h-8 rounded border border-brand-200 px-3 text-xs font-bold text-brand-700 hover:bg-brand-50 mr-1" onClick={() => publishMut.mutate(t.id)} type="button">Publish</button>}
                  {t.status === "published" && <button className="h-8 rounded border border-neutral-200 px-3 text-xs font-bold text-neutral-700 hover:bg-neutral-50" onClick={() => archiveMut.mutate(t.id)} type="button">Archive</button>}
                </td>
              </tr>
            ))}</tbody>
        </table>
      </section>
    </div>
  );
}

// ── Assignments Tab ──
function AssignmentsTab() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ title: "", template: "", purpose: "general_data_collection", assigned_to_type: "organization", due_date: "" });

  const { data: templates } = useQuery({ queryKey: ["form-templates"], queryFn: async () => fetchFormTemplates() });
  const { data: assignments, isLoading } = useQuery({ queryKey: ["form-assignments"], queryFn: async () => fetchFormAssignments() });
  const tl = Array.isArray(templates) ? templates : [];
  const al = Array.isArray(assignments) ? assignments : [];

  const createMut = useMutation({
    mutationFn: () => createFormAssignment({ ...form, assigned_to_id: "0" }),
    onSuccess: () => { setShowForm(false); setForm({ title: "", template: "", purpose: "general_data_collection", assigned_to_type: "organization", due_date: "" }); setError(null); queryClient.invalidateQueries({ queryKey: ["form-assignments"] }); },
    onError: (err) => setError(getApiErrorMessage(err, "Failed to create assignment.")),
  });
  const cancelMut = useMutation({
    mutationFn: (id: string) => cancelFormAssignment(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["form-assignments"] }),
  });

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <button className="inline-flex h-10 items-center gap-2 rounded-lg bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700" onClick={() => setShowForm(true)} type="button"><Plus size={16} />Create Assignment</button>
      </div>

      {showForm && (
        <div className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm space-y-3">
          <h3 className="text-sm font-bold text-neutral-900">New Assignment</h3>
          {error && <p className="text-sm font-semibold text-danger-700 bg-danger-50 rounded px-3 py-2">{error}</p>}
          <input className="h-10 w-full rounded-lg border border-neutral-200 px-3 text-sm" placeholder="Assignment title" value={form.title} onChange={e => setForm(p => ({...p, title: e.target.value}))} />
          <select className="h-10 w-full rounded-lg border border-neutral-200 px-3 text-sm" value={form.template} onChange={e => setForm(p => ({...p, template: e.target.value, purpose: tl.find(t=>t.id===e.target.value)?.purpose || p.purpose}))}>
            <option value="">Select template</option>
            {tl.filter(t => t.status==="published").map(t => <option key={t.id} value={t.id}>{t.title} (v{t.current_version})</option>)}
          </select>
          <select className="h-10 w-full rounded-lg border border-neutral-200 px-3 text-sm" value={form.purpose} onChange={e => setForm(p => ({...p, purpose: e.target.value}))}>
            {Object.entries(PURPOSE_LABELS).map(([k,v]) => <option key={k} value={k}>{v}</option>)}
          </select>
          <div className="flex gap-2">
            <button className="h-10 rounded-lg bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60" disabled={!form.title || !form.template || createMut.isPending} onClick={() => createMut.mutate()} type="button">{createMut.isPending ? "Creating..." : "Save"}</button>
            <button className="h-10 rounded-lg border border-neutral-200 px-4 text-sm font-medium text-neutral-700 hover:bg-neutral-50" onClick={() => setShowForm(false)} type="button">Cancel</button>
          </div>
        </div>
      )}

      <section className="overflow-hidden rounded-xl border border-neutral-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-neutral-200 text-sm">
          <thead className="bg-neutral-50"><tr>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Title</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Template</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Due</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Responses</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Status</th>
            <th className="px-4 py-3 text-right text-xs font-medium uppercase text-neutral-500">Actions</th>
          </tr></thead>
          <tbody className="divide-y divide-neutral-100">
            {isLoading ? <tr><td className="px-4 py-8 text-center text-neutral-500" colSpan={6}>Loading...</td></tr>
            : al.length === 0 ? <tr><td className="px-4 py-8 text-center text-neutral-500" colSpan={6}>No assignments yet.</td></tr>
            : al.map(a => (
              <tr key={a.id} className="hover:bg-neutral-50">
                <td className="px-4 py-3 font-semibold text-neutral-900">{a.title}</td>
                <td className="px-4 py-3 text-neutral-700">{a.template_title}</td>
                <td className="px-4 py-3 text-neutral-500 text-xs">{formatDate(a.due_date)}</td>
                <td className="px-4 py-3 text-neutral-700">{a.response_count}</td>
                <td className="px-4 py-3"><StatusBadge status={a.status} /></td>
                <td className="px-4 py-3 text-right">
                  {(a.status === "active" || a.status === "in_progress") && <button className="h-8 rounded border border-neutral-200 px-3 text-xs font-bold text-neutral-700 hover:bg-neutral-50" onClick={() => cancelMut.mutate(a.id)} type="button">Cancel</button>}
                </td>
              </tr>
            ))}</tbody>
        </table>
      </section>
    </div>
  );
}

// ── Responses Tab ──
function ResponsesTab() {
  const queryClient = useQueryClient();
  const { data: responses, isLoading } = useQuery({ queryKey: ["form-responses"], queryFn: async () => fetchFormResponses() });
  const items = Array.isArray(responses) ? responses : [];

  const reviewMut = useMutation({
    mutationFn: ({ id, notes }: { id: string; notes?: string }) => reviewFormResponse(id, notes),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["form-responses"] }),
  });
  const returnMut = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason?: string }) => returnFormResponse(id, reason),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["form-responses"] }),
  });

  return (
    <div className="space-y-4">
      <section className="overflow-hidden rounded-xl border border-neutral-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-neutral-200 text-sm">
          <thead className="bg-neutral-50"><tr>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Form</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Assignment</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Respondent</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Submitted</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-neutral-500">Status</th>
            <th className="px-4 py-3 text-right text-xs font-medium uppercase text-neutral-500">Actions</th>
          </tr></thead>
          <tbody className="divide-y divide-neutral-100">
            {isLoading ? <tr><td className="px-4 py-8 text-center text-neutral-500" colSpan={6}>Loading...</td></tr>
            : items.length === 0 ? <tr><td className="px-4 py-8 text-center text-neutral-500" colSpan={6}>No responses yet.</td></tr>
            : items.map(r => (
              <tr key={r.id} className="hover:bg-neutral-50">
                <td className="px-4 py-3 font-semibold text-neutral-900">{r.template_title || r.template}</td>
                <td className="px-4 py-3 text-neutral-600 text-xs">{r.assignment_title}</td>
                <td className="px-4 py-3 text-neutral-700">{r.respondent_name || r.respondent_email}</td>
                <td className="px-4 py-3 text-neutral-500 text-xs">{formatDate(r.submitted_at)}</td>
                <td className="px-4 py-3"><StatusBadge status={r.status} /></td>
                <td className="px-4 py-3 text-right">
                  {r.status === "submitted" && (
                    <>
                      <button className="h-8 rounded border border-brand-200 px-3 text-xs font-bold text-brand-700 hover:bg-brand-50 mr-1" onClick={() => reviewMut.mutate({ id: r.id })} type="button">Review</button>
                      <button className="h-8 rounded border border-neutral-200 px-3 text-xs font-bold text-neutral-700 hover:bg-neutral-50" onClick={() => returnMut.mutate({ id: r.id })} type="button">Return</button>
                    </>
                  )}
                </td>
              </tr>
            ))}</tbody>
        </table>
      </section>
    </div>
  );
}

// ── Reports / Settings placeholder ──
function PlaceholderTab({ icon: Icon, title, desc }: { icon: typeof Activity; title: string; desc: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
      <Icon size={32} className="text-neutral-300" />
      <p className="text-sm font-semibold text-neutral-500">{title}</p>
      <p className="text-xs text-neutral-400">{desc}</p>
    </div>
  );
}

// ── Main Layout ──
export function FormsToolLayout() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const tabParam = (searchParams.get("tab") ?? "overview") as TabKey;
  const activeTab = TABS[tabParam] ? tabParam : "overview";

  function setTab(tab: TabKey) { router.replace(`/state/forms?tab=${tab}`); }

  return (
    <PortalShell role="state_admin" title="Forms Tool" description="Create, assign, and track form templates, responses, and reports across all modules.">
      <nav className="mb-6 flex gap-0 overflow-x-auto border-b border-neutral-200">
        {(Object.entries(TABS) as [TabKey, string][]).map(([key, label]) => (
          <button key={key} className={`shrink-0 border-b-2 px-4 py-3 text-sm font-medium ${activeTab===key?"border-brand-600 text-brand-700":"border-transparent text-neutral-500 hover:text-neutral-800"}`} onClick={() => setTab(key)} type="button">{label}</button>
        ))}
      </nav>
      {activeTab === "overview" && <OverviewTab />}
      {activeTab === "templates" && <TemplatesTab />}
      {activeTab === "assignments" && <AssignmentsTab />}
      {activeTab === "responses" && <ResponsesTab />}
      {activeTab === "reports" && <PlaceholderTab icon={BarChart3} title="Reports" desc="Form analytics and exports will be available here." />}
      {activeTab === "settings" && <PlaceholderTab icon={Settings} title="Settings" desc="Category and field type configuration will be available here." />}
    </PortalShell>
  );
}
