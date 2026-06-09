"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { HeartPulse, AlertCircle, CheckCircle2, X } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { FitnessStatusBadge } from "@/components/ui/fitness-status-badge";
import { apiClient, unwrap } from "@/lib/api/client";

type IllnessRow = {
  id: string;
  food_handler_id: string;
  food_handler_name: string;
  branch_name?: string;
  suspected_condition: string;
  symptoms: Record<string, boolean>;
  symptom_start_date?: string;
  exclusion_start_date?: string;
  earliest_return_date?: string;
  clearance_status: string;
  notes: string;
  created_at: string;
};

type HandlerOpt = { id: string; full_name: string; branch_name?: string };

const SYMPTOMS = [
  "jaundice", "diarrhoea", "vomiting", "fever",
  "sore_throat_with_fever", "infected_skin_lesions",
  "discharge_ear_eye_nose", "cough_or_flu", "other",
];

const CONDITIONS = [
  { value: "general_diarrhoea_vomiting", label: "Diarrhoea / Vomiting" },
  { value: "cholera", label: "Cholera" },
  { value: "shigella", label: "Shigella" },
  { value: "hepatitis_a", label: "Hepatitis A" },
  { value: "infected_skin_lesion", label: "Infected Skin Lesion" },
  { value: "other", label: "Other" },
];

export default function Page() {
  const router = useRouter();
  const [employerId, setEmployerId] = useState<string | null>(null);
  const [reports, setReports] = useState<IllnessRow[]>([]);
  const [handlers, setHandlers] = useState<HandlerOpt[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [sending, setSending] = useState(false);

  // Form state
  const [fhId, setFhId] = useState("");
  const [symptoms, setSymptoms] = useState<Record<string, boolean>>({});
  const [condition, setCondition] = useState("general_diarrhoea_vomiting");
  const [startDate, setStartDate] = useState("");
  const [notes, setNotes] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("foodcert_access_token");
    if (!token) { router.push("/login"); return; }
    apiClient.get("/employers/me/").then((res) => {
      const empId = (unwrap(res.data) as { id: string }).id;
      setEmployerId(empId);
      // Load handlers and reports
      apiClient.get(`/employers/${empId}/food-handlers/`).then((r2) => {
        const hds = unwrap(r2.data) as HandlerOpt[];
        setHandlers(hds);
      }).catch(() => {});
      apiClient.get(`/employers/${empId}/illness-reports/`).then((r3) => {
        setReports(unwrap(r3.data) as IllnessRow[]);
      }).catch(() => {}).finally(() => setLoading(false));
    }).catch(() => setLoading(false));
  }, [router]);

  function toggleSymptom(s: string) {
    setSymptoms((prev) => ({ ...prev, [s]: !prev[s] }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!employerId || !fhId) return;
    setSending(true);
    setError("");
    try {
      const res = await apiClient.post(`/employers/${employerId}/illness-reports/`, {
        food_handler: fhId,
        symptoms,
        suspected_condition: condition,
        symptom_start_date: startDate || undefined,
        notes,
      });
      const newReport = unwrap(res.data) as IllnessRow;
      setReports((prev) => [newReport, ...prev]);
      setSuccess("Illness reported. Food handler has been excluded from food handling.");
      setShowForm(false);
      resetForm();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit report.");
    } finally {
      setSending(false);
    }
  }

  function resetForm() {
    setFhId("");
    setSymptoms({});
    setCondition("general_diarrhoea_vomiting");
    setStartDate("");
    setNotes("");
  }

  return (
    <PortalShell role="employer" title="Illness Reports" description="Report illness among food handlers and monitor exclusion and return-to-work status.">
      <div className="flex items-center justify-between mb-5">
        <span className="text-sm text-neutral-500">{reports.length} report{reports.length !== 1 ? "s" : ""}</span>
        {!showForm && (
          <button className="inline-flex h-10 items-center gap-2 rounded-lg bg-brand-600 px-4 text-sm font-bold text-white hover:bg-brand-700" onClick={() => setShowForm(true)}>
            <HeartPulse size={16} />
            Report Illness
          </button>
        )}
      </div>

      {error && <div className="mb-4 flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700"><AlertCircle size={16} className="mt-0.5" /><span>{error}</span></div>}
      {success && <div className="mb-4 flex items-start gap-2 rounded-lg bg-brand-50 p-3 text-sm font-semibold text-brand-800"><CheckCircle2 size={16} className="mt-0.5" /><span>{success}</span></div>}

      {/* Form */}
      {showForm && (
        <form className="mb-6 rounded-lg border border-neutral-200 bg-white p-5 shadow-sm" onSubmit={handleSubmit}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-neutral-900">Report Illness</h3>
            <button type="button" className="rounded p-1 hover:bg-neutral-50" onClick={() => setShowForm(false)}><X size={16} className="text-neutral-400" /></button>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
              Food handler <span className="text-danger-500">*</span>
              <select className="h-11 rounded-lg border border-neutral-200 bg-white px-3" value={fhId} onChange={(e) => setFhId(e.target.value)} required>
                <option value="">Select handler...</option>
                {handlers.map((h) => <option key={h.id} value={h.id}>{h.full_name}{h.branch_name ? ` (${h.branch_name})` : ""}</option>)}
              </select>
            </label>
            <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
              Suspected condition <span className="text-danger-500">*</span>
              <select className="h-11 rounded-lg border border-neutral-200 bg-white px-3" value={condition} onChange={(e) => setCondition(e.target.value)}>
                {CONDITIONS.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
              </select>
            </label>
            <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
              Symptom start date
              <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3" type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
            </label>
          </div>
          <div className="mt-4">
            <p className="text-sm font-semibold text-neutral-700 mb-2">Symptoms observed or reported</p>
            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {SYMPTOMS.map((s) => (
                <label key={s} className="flex items-center gap-2 rounded border border-neutral-100 bg-neutral-50 px-3 py-2 text-sm cursor-pointer hover:bg-white">
                  <input type="checkbox" checked={!!symptoms[s]} onChange={() => toggleSymptom(s)} className="h-4 w-4 rounded border-neutral-300 text-brand-600" />
                  <span className="text-neutral-700 capitalize">{s.replace(/_/g, " ")}</span>
                </label>
              ))}
            </div>
          </div>
          <label className="mt-4 grid gap-1.5 text-sm font-semibold text-neutral-700">
            Notes
            <textarea className="rounded-lg border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm" rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} />
          </label>
          <div className="mt-4 flex items-center gap-2">
            <input type="checkbox" id="exclusion" className="h-4 w-4 rounded border-neutral-300 text-brand-600" required />
            <label htmlFor="exclusion" className="text-sm font-semibold text-neutral-700">I confirm that this food handler must be excluded from food handling duties.</label>
          </div>
          <div className="mt-5 flex gap-3">
            <button className="inline-flex h-11 items-center gap-2 rounded-lg bg-brand-600 px-6 text-sm font-bold text-white hover:bg-brand-700 disabled:opacity-60" disabled={sending} type="submit">
              {sending ? "Submitting..." : "Submit Report"}
            </button>
            <button type="button" className="inline-flex h-11 items-center gap-2 rounded-lg border border-neutral-200 px-4 text-sm font-semibold text-neutral-600 hover:bg-neutral-50" onClick={() => setShowForm(false)}>Cancel</button>
          </div>
        </form>
      )}

      {/* List */}
      {loading && <p className="text-sm text-neutral-500">Loading...</p>}
      {!loading && reports.length === 0 && !showForm && (
        <div className="rounded-lg border border-neutral-200 bg-white p-10 text-center">
          <HeartPulse size={32} className="mx-auto text-neutral-300" />
          <p className="mt-3 text-sm font-semibold text-neutral-500">No illness reports yet</p>
          <p className="mt-1 text-xs text-neutral-400">When a food handler shows symptoms, report it here to trigger exclusion and medical review.</p>
        </div>
      )}
      {reports.length > 0 && (
        <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white shadow-sm">
          <table className="w-full text-sm">
            <thead><tr className="border-b border-neutral-100 bg-neutral-50 text-left"><th className="px-4 py-2 text-xs font-bold uppercase text-neutral-500">Handler</th><th className="px-4 py-2 text-xs font-bold uppercase text-neutral-500 hidden sm:table-cell">Condition</th><th className="px-4 py-2 text-xs font-bold uppercase text-neutral-500 hidden md:table-cell">Symptoms</th><th className="px-4 py-2 text-xs font-bold uppercase text-neutral-500">Excluded</th><th className="px-4 py-2 text-xs font-bold uppercase text-neutral-500">Clearance</th><th className="px-4 py-2 text-xs font-bold uppercase text-neutral-500 hidden lg:table-cell">RTW Date</th></tr></thead>
            <tbody className="divide-y divide-neutral-50">
              {reports.map((r) => (
                <tr key={r.id} className="hover:bg-neutral-50/50">
                  <td className="px-4 py-2"><span className="text-xs text-neutral-700 font-medium">{r.food_handler_name}</span>{r.branch_name && <span className="text-[10px] text-neutral-400 block">{r.branch_name}</span>}</td>
                  <td className="px-4 py-2 hidden sm:table-cell"><span className="text-xs text-neutral-600 capitalize">{r.suspected_condition?.replace(/_/g, " ")}</span></td>
                  <td className="px-4 py-2 hidden md:table-cell"><span className="text-xs text-neutral-500">{Object.entries(r.symptoms || {}).filter(([, v]) => v).map(([k]) => k.replace(/_/g, " ")).join(", ") || "—"}</span></td>
                  <td className="px-4 py-2"><span className="text-xs text-neutral-600">{r.exclusion_start_date ? new Date(r.exclusion_start_date).toLocaleDateString() : "—"}</span></td>
                  <td className="px-4 py-2"><FitnessStatusBadge status={r.clearance_status || "pending"} /></td>
                  <td className="px-4 py-2 hidden lg:table-cell"><span className="text-xs text-neutral-500">{r.earliest_return_date ? new Date(r.earliest_return_date).toLocaleDateString() : "—"}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </PortalShell>
  );
}
