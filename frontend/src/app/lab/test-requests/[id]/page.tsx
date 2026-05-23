"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AlertCircle, ArrowLeft, Save, Upload } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { getLabRequest, markLabSampleCollected, submitLabResult, submitLabResultToDoctor, uploadLabResultDocument } from "@/lib/api/lab-tests";
import type { LabTest } from "@/types/assessments";

const RESULT_STATUSES = [
  ["negative", "Negative"],
  ["positive", "Positive"],
  ["inconclusive", "Inconclusive"],
  ["repeat_required", "Repeat required"],
];

function label(value?: string) {
  return value ? value.replaceAll("_", " ") : "Not set";
}

export default function Page() {
  const params = useParams<{ id: string }>();
  const [request, setRequest] = useState<LabTest | null>(null);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [form, setForm] = useState({ status: "negative", result_value: "", result_notes: "", lab_staff_notes: "" });
  const [file, setFile] = useState<File | null>(null);

  const loadData = useCallback(async () => {
    if (!params.id) return;
    setLoading(true);
    setError("");
    try {
      const row = await getLabRequest(params.id);
      setRequest(row);
      setForm({
        status: ["positive", "negative", "inconclusive", "repeat_required"].includes(row.status) ? row.status : "negative",
        result_value: row.result_value || "",
        result_notes: row.result_notes || "",
        lab_staff_notes: row.lab_staff_notes || "",
      });
    } catch {
      setError("Could not load lab request.");
    } finally {
      setLoading(false);
    }
  }, [params.id]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  async function collectSample() {
    if (!request) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      setRequest(await markLabSampleCollected(request.id, { lab_staff_notes: form.lab_staff_notes }));
      setSuccess("Sample marked collected.");
    } catch {
      setError("Could not mark sample collected.");
    } finally {
      setBusy(false);
    }
  }

  async function saveResult() {
    if (!request) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      setRequest(await submitLabResult(request.id, form));
      setSuccess("Result submitted to doctor.");
    } catch {
      setError("Could not save result.");
    } finally {
      setBusy(false);
    }
  }

  async function uploadDocument() {
    if (!request || !file) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      const payload = new FormData();
      payload.append("result_document", file);
      payload.append("lab_staff_notes", form.lab_staff_notes);
      setRequest(await uploadLabResultDocument(request.id, payload));
      setSuccess("Result document uploaded.");
    } catch {
      setError("Could not upload result document.");
    } finally {
      setBusy(false);
    }
  }

  async function submitToDoctor() {
    if (!request) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      setRequest(await submitLabResultToDoctor(request.id, { lab_staff_notes: form.lab_staff_notes }));
      setSuccess("Result submitted to doctor.");
    } catch {
      setError("Could not submit result to doctor.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <PortalShell role="lab_staff" title="Test Request Detail" description="Collect sample, enter result values, upload result documents, and submit to the doctor.">
      <div className="grid gap-5">
        <Link className="inline-flex w-fit items-center gap-2 rounded border border-slate-200 bg-white px-3 py-2 text-sm font-bold text-slate-700 shadow-sm" href="/lab/test-requests"><ArrowLeft size={16} /> Back to requests</Link>
        {loading ? <p className="rounded-lg border border-slate-200 bg-white p-4 text-sm font-semibold text-slate-600 shadow-sm">Loading request...</p> : null}
        {request ? (
          <>
            <section className="grid gap-3 md:grid-cols-4">
              <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"><p className="text-xs font-bold uppercase text-slate-500">Food handler</p><p className="mt-2 font-bold text-slate-950">{request.food_handler_name}</p></div>
              <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"><p className="text-xs font-bold uppercase text-slate-500">Test</p><p className="mt-2 font-bold capitalize text-slate-950">{request.test_name || label(request.test_type)}</p></div>
              <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"><p className="text-xs font-bold uppercase text-slate-500">Status</p><StatusBadge status={request.status} /></div>
              <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"><p className="text-xs font-bold uppercase text-slate-500">Doctor review</p><p className="mt-2 font-bold text-slate-950">{request.reviewed_at ? "Reviewed" : "Pending"}</p>{request.parent_lab_test ? <p className="text-xs font-semibold text-amber-700">Repeat request</p> : null}{request.is_flagged ? <p className="text-xs font-semibold text-amber-700">Flagged result</p> : null}</div>
            </section>
            {request.repeat_reason ? <p className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm font-semibold text-amber-900">{request.repeat_reason}</p> : null}
            <section className="grid gap-4 lg:grid-cols-2">
              <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
                <h2 className="text-sm font-bold text-slate-950">Sample And Result</h2>
                <div className="mt-4 grid gap-3">
                  <textarea className="min-h-20 rounded border border-slate-200 bg-slate-50 p-3 text-sm" placeholder="Lab staff notes" value={form.lab_staff_notes} onChange={(event) => setForm((current) => ({ ...current, lab_staff_notes: event.target.value }))} />
                  <button className="inline-flex h-10 w-fit items-center gap-2 rounded border border-slate-200 px-4 text-sm font-bold text-slate-700 disabled:opacity-60" disabled={busy} type="button" onClick={() => void collectSample()}><Save size={16} /> Mark sample collected</button>
                  <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={form.status} onChange={(event) => setForm((current) => ({ ...current, status: event.target.value }))}>{RESULT_STATUSES.map(([value, text]) => <option key={value} value={value}>{text}</option>)}</select>
                  <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" placeholder="Result value" value={form.result_value} onChange={(event) => setForm((current) => ({ ...current, result_value: event.target.value }))} />
                  <textarea className="min-h-20 rounded border border-slate-200 bg-slate-50 p-3 text-sm" placeholder="Result notes" value={form.result_notes} onChange={(event) => setForm((current) => ({ ...current, result_notes: event.target.value }))} />
                  <button className="inline-flex h-10 w-fit items-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white disabled:opacity-60" disabled={busy} type="button" onClick={() => void saveResult()}><Save size={16} /> Save result</button>
                  <button className="inline-flex h-10 w-fit items-center gap-2 rounded border border-emerald-300 px-4 text-sm font-bold text-emerald-800 disabled:opacity-60" disabled={busy || !["positive", "negative", "inconclusive", "repeat_required", "result_uploaded"].includes(request.status)} type="button" onClick={() => void submitToDoctor()}><Save size={16} /> Submit to doctor</button>
                </div>
              </div>
              <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
                <h2 className="text-sm font-bold text-slate-950">Result Document</h2>
                <div className="mt-4 grid gap-3">
                  <input className="rounded border border-slate-200 bg-slate-50 p-3 text-sm" type="file" accept="application/pdf,image/png,image/jpeg" onChange={(event) => setFile(event.target.files?.[0] || null)} />
                  <button className="inline-flex h-10 w-fit items-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white disabled:opacity-60" disabled={busy || !file} type="button" onClick={() => void uploadDocument()}><Upload size={16} /> Upload document</button>
                  <p className="text-sm text-slate-600">Current document: {request.result_document_url ? "Uploaded" : "Not uploaded"}</p>
                </div>
              </div>
            </section>
          </>
        ) : null}
        {error ? <div className="flex items-start gap-2 rounded-lg bg-rose-50 p-3 text-sm font-semibold text-rose-800"><AlertCircle size={16} />{error}</div> : null}
        {success ? <div className="rounded-lg bg-emerald-50 p-3 text-sm font-semibold text-emerald-800">{success}</div> : null}
      </div>
    </PortalShell>
  );
}
