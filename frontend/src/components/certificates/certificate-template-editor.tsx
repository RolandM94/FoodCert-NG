"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, Save } from "lucide-react";
import { useState } from "react";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import {
  createCertificateTemplate,
  listCertificateTemplates,
  setDefaultCertificateTemplate,
  updateCertificateTemplate,
  type CertificateTemplate,
} from "@/lib/api/certificates";

type Scope = "national" | "state";

const emptyTemplate = {
  name: "",
  ministry_name: "FoodCert NG",
  subtitle: "Official Food Handler Medical Fitness Certificate",
  logo_url: "",
  accent_color: "#0f5132",
  signatory_name: "",
  signatory_title: "Authorized Issuing Authority",
  footer_note: "This certificate confirms fitness status only. It does not disclose lab results, diagnosis, clinical notes, or full NIN.",
  is_active: true,
};

export function CertificateTemplateEditor({ scope }: { scope: Scope }) {
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState<CertificateTemplate | null>(null);
  const [form, setForm] = useState({ ...emptyTemplate });
  const templatesQuery = useQuery({
    queryKey: ["certificate-templates", scope],
    queryFn: () => listCertificateTemplates({ scope }),
  });
  const saveMutation = useMutation({
    mutationFn: () => {
      const payload = { ...form, scope };
      return editing ? updateCertificateTemplate(editing.id, payload) : createCertificateTemplate(payload);
    },
    onSuccess: () => {
      setEditing(null);
      setForm({ ...emptyTemplate });
      queryClient.invalidateQueries({ queryKey: ["certificate-templates"] });
    },
  });
  const defaultMutation = useMutation({
    mutationFn: setDefaultCertificateTemplate,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["certificate-templates"] }),
  });

  function edit(template: CertificateTemplate) {
    setEditing(template);
    setForm({
      name: template.name,
      ministry_name: template.ministry_name,
      subtitle: template.subtitle,
      logo_url: template.logo_url,
      accent_color: template.accent_color,
      signatory_name: template.signatory_name,
      signatory_title: template.signatory_title,
      footer_note: template.footer_note,
      is_active: template.is_active,
    });
  }

  const templates = templatesQuery.data || [];

  return (
    <div className="grid gap-5">
      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <div className="grid gap-4 md:grid-cols-2">
          <label className="grid gap-1 text-sm font-semibold text-slate-700">Template name<input className="h-10 rounded border border-slate-200 bg-slate-50 px-3" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} /></label>
          <label className="grid gap-1 text-sm font-semibold text-slate-700">Ministry name<input className="h-10 rounded border border-slate-200 bg-slate-50 px-3" value={form.ministry_name} onChange={(event) => setForm({ ...form, ministry_name: event.target.value })} /></label>
          <label className="grid gap-1 text-sm font-semibold text-slate-700">Subtitle<input className="h-10 rounded border border-slate-200 bg-slate-50 px-3" value={form.subtitle} onChange={(event) => setForm({ ...form, subtitle: event.target.value })} /></label>
          <label className="grid gap-1 text-sm font-semibold text-slate-700">Accent color<input className="h-10 rounded border border-slate-200 bg-slate-50 px-3" value={form.accent_color} onChange={(event) => setForm({ ...form, accent_color: event.target.value })} /></label>
          <label className="grid gap-1 text-sm font-semibold text-slate-700">Signatory name<input className="h-10 rounded border border-slate-200 bg-slate-50 px-3" value={form.signatory_name} onChange={(event) => setForm({ ...form, signatory_name: event.target.value })} /></label>
          <label className="grid gap-1 text-sm font-semibold text-slate-700">Signatory title<input className="h-10 rounded border border-slate-200 bg-slate-50 px-3" value={form.signatory_title} onChange={(event) => setForm({ ...form, signatory_title: event.target.value })} /></label>
        </div>
        <label className="mt-4 grid gap-1 text-sm font-semibold text-slate-700">Footer note<textarea className="min-h-24 rounded border border-slate-200 bg-slate-50 px-3 py-2" value={form.footer_note} onChange={(event) => setForm({ ...form, footer_note: event.target.value })} /></label>
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <label className="flex items-center gap-2 text-sm font-semibold text-slate-700"><input checked={form.is_active} onChange={(event) => setForm({ ...form, is_active: event.target.checked })} type="checkbox" /> Active</label>
          <button className="inline-flex h-10 items-center gap-2 rounded bg-brand-deep px-4 text-sm font-bold text-white disabled:bg-slate-300" disabled={!form.name || saveMutation.isPending} onClick={() => saveMutation.mutate()} type="button">
            <Save size={16} />
            {editing ? "Update template" : "Create template"}
          </button>
        </div>
        {saveMutation.isError ? <p className="mt-3 rounded bg-red-50 px-3 py-2 text-sm font-semibold text-red-700">Template could not be saved.</p> : null}
      </section>

      <section className="grid gap-3">
        <DataTable<CertificateTemplate>
          columns={[
            { key: "name", header: "Template", render: (row) => <div><p className="font-bold text-slate-950">{row.name}</p><p className="text-xs text-slate-500">{row.ministry_name}</p></div> },
            { key: "state", header: "Scope", render: (row) => row.state_name || row.scope },
            { key: "status", header: "Status", render: (row) => <StatusCell status={row.is_active ? "active" : "inactive"} /> },
            { key: "default", header: "Default", render: (row) => row.is_default ? <span className="font-bold text-emerald-700">Default</span> : "No" },
            { key: "actions", header: "Actions", render: (row) => (
              <div className="flex flex-wrap gap-2">
                <button className="h-8 rounded border border-slate-200 px-2 text-xs font-bold text-slate-700" onClick={() => edit(row)} type="button">Edit</button>
                <button className="inline-flex h-8 items-center gap-1 rounded border border-emerald-200 px-2 text-xs font-bold text-emerald-800 disabled:opacity-50" disabled={row.is_default || defaultMutation.isPending} onClick={() => defaultMutation.mutate(row.id)} type="button"><CheckCircle2 size={13} /> Default</button>
              </div>
            ) },
          ]}
          rows={templates}
          empty={templatesQuery.isLoading ? "Loading templates..." : "No certificate templates yet."}
        />
      </section>
    </div>
  );
}
