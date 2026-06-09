"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Upload, AlertCircle, CheckCircle2, X, MapPin } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { apiClient, unwrap } from "@/lib/api/client";

type Row = {
  full_name: string;
  phone: string;
  email: string;
  food_handler_category: string;
  branch: string;
};

type ResultRow = {
  row: number;
  user_id?: string;
  email?: string;
  error?: string;
};

export default function Page() {
  const router = useRouter();
  const fileRef = useRef<HTMLInputElement>(null);
  const [employerId, setEmployerId] = useState<string | null>(null);
  const [rows, setRows] = useState<Row[]>([]);
  const [results, setResults] = useState<ResultRow[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [branchId, setBranchId] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("foodcert_access_token");
    if (!token) { router.push("/login"); return; }
    apiClient.get("/employers/me/").then((res) => {
      setEmployerId((unwrap(res.data) as { id: string }).id);
    }).catch(() => {});
  }, [router]);

  function parseCSV(text: string): Row[] {
    const lines = text.split("\n").filter((l) => l.trim());
    if (lines.length < 2) throw new Error("CSV must have a header row and at least one data row.");
    const headers = lines[0].toLowerCase().split(",").map((h) => h.trim().replace(/"/g, ""));
    const nameIdx = headers.findIndex((h) => h.includes("name") || h === "full_name");
    const phoneIdx = headers.findIndex((h) => h.includes("phone"));
    const emailIdx = headers.findIndex((h) => h.includes("email"));
    const catIdx = headers.findIndex((h) => h.includes("category"));
    if (nameIdx === -1 || phoneIdx === -1) throw new Error("CSV must have 'full_name' and 'phone' columns.");
    return lines.slice(1).map((line) => {
      const cols = line.split(",").map((c) => c.trim().replace(/"/g, ""));
      return {
        full_name: cols[nameIdx] || "",
        phone: cols[phoneIdx] || "",
        email: emailIdx >= 0 ? cols[emailIdx] || "" : "",
        food_handler_category: catIdx >= 0 ? cols[catIdx] || "kitchen_staff" : "kitchen_staff",
        branch: branchId,
      };
    }).filter((r) => r.full_name && r.phone);
  }

  function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    setError("");
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const parsed = parseCSV(reader.result as string);
        setRows(parsed);
        setResults(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to parse CSV.");
      }
    };
    reader.readAsText(file);
  }

  function removeRow(idx: number) {
    setRows((prev) => prev.filter((_, i) => i !== idx));
  }

  async function handleUpload() {
    if (!employerId || rows.length === 0) return;
    setLoading(true);
    setError("");
    try {
      const res = await apiClient.post(`/employers/${employerId}/food-handlers/bulk-upload/`, { rows, branch: branchId || undefined });
      const data = unwrap(res.data) as { created: ResultRow[]; errors: ResultRow[] };
      setResults([...data.created, ...data.errors.map((e) => ({ ...e, error: typeof e.error === "string" ? e.error : JSON.stringify(e.error) }))]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <PortalShell role="employer" title="Import Food Handlers" description="Upload a CSV file with food handler details to send bulk invitations.">
      <div className="max-w-2xl space-y-5">
        {/* Branch selector */}
        <label className="flex items-center gap-2 text-sm font-semibold text-neutral-700">
          <MapPin size={14} className="text-neutral-400" />
          Default branch for new handlers:
          <input className="h-10 rounded border border-neutral-200 bg-white px-2 text-sm flex-1" value={branchId} onChange={(e) => setBranchId(e.target.value)} placeholder="Leave blank for no branch assignment" />
        </label>

        {/* File upload */}
        <div className="rounded-lg border-2 border-dashed border-neutral-300 bg-neutral-50 p-8 text-center">
          <Upload size={32} className="mx-auto text-neutral-400" />
          <p className="mt-3 text-sm font-semibold text-neutral-700">Upload CSV file</p>
          <p className="mt-1 text-xs text-neutral-500">Columns: full_name, phone, email, category</p>
          <input ref={fileRef} type="file" accept=".csv" onChange={handleFile} className="hidden" />
          <button className="mt-4 inline-flex h-10 items-center gap-2 rounded bg-brand-600 px-4 text-sm font-bold text-white hover:bg-brand-700" onClick={() => fileRef.current?.click()}>
            Choose file
          </button>
        </div>

        {error && <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700"><AlertCircle size={16} className="mt-0.5" /><span>{error}</span></div>}

        {/* Preview */}
        {rows.length > 0 && !results && (
          <div>
            <div className="flex items-center justify-between mb-3">
              <p className="text-sm font-bold text-neutral-900">{rows.length} handlers ready to import</p>
              {rows.length > 0 && <span className="text-xs text-neutral-400">Click X to remove a row</span>}
            </div>
            <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white">
              <table className="w-full text-sm">
                <thead><tr className="border-b border-neutral-100 bg-neutral-50 text-left"><th className="px-3 py-2 text-xs font-bold uppercase text-neutral-500">Name</th><th className="px-3 py-2 text-xs font-bold uppercase text-neutral-500">Phone</th><th className="px-3 py-2 text-xs font-bold uppercase text-neutral-500">Email</th><th className="px-3 py-2 text-xs font-bold uppercase text-neutral-500">Category</th><th className="px-3 py-2"></th></tr></thead>
                <tbody className="divide-y divide-neutral-50">
                  {rows.map((r, i) => (
                    <tr key={i} className="hover:bg-neutral-50">
                      <td className="px-3 py-2 text-neutral-800">{r.full_name}</td>
                      <td className="px-3 py-2 text-neutral-600 font-mono text-xs">{r.phone}</td>
                      <td className="px-3 py-2 text-neutral-600 text-xs">{r.email || "—"}</td>
                      <td className="px-3 py-2 text-xs text-neutral-500 capitalize">{r.food_handler_category?.replace(/_/g, " ")}</td>
                      <td className="px-3 py-2"><button className="rounded p-1 hover:bg-danger-50 text-neutral-400 hover:text-danger-500" onClick={() => removeRow(i)}><X size={14} /></button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <button className="mt-4 inline-flex h-11 items-center gap-2 rounded-lg bg-brand-600 px-6 text-sm font-bold text-white hover:bg-brand-700 disabled:opacity-60" disabled={loading} onClick={handleUpload}>
              <CheckCircle2 size={16} />
              {loading ? "Uploading..." : `Import ${rows.length} handlers`}
            </button>
          </div>
        )}

        {/* Results */}
        {results && (
          <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
            <h3 className="text-sm font-bold text-neutral-900 mb-3">Import results</h3>
            <div className="flex gap-4 mb-4 text-sm">
              <span className="text-brand-700 font-semibold">{results.filter((r) => !r.error).length} created</span>
              <span className="text-danger-500 font-semibold">{results.filter((r) => r.error).length} errors</span>
            </div>
            {results.filter((r) => r.error).length > 0 && (
              <div className="space-y-1 text-xs">
                {results.filter((r) => r.error).map((r, i) => (
                  <div key={i} className="rounded bg-danger-50 px-3 py-1.5 text-danger-700">Row {r.row + 1}: {r.error}</div>
                ))}
              </div>
            )}
            <button className="mt-4 text-sm font-semibold text-brand-700 hover:underline" onClick={() => { setResults(null); setRows([]); }}>
              Import another file
            </button>
          </div>
        )}
      </div>
    </PortalShell>
  );
}
