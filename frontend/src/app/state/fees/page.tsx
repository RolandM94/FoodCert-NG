"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Banknote, Plus } from "lucide-react";
import { useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import {
  createStateAssessmentFee,
  fetchStateAssessmentFees,
  updateStateAssessmentFee,
  type AssessmentFee,
  type StateAssessmentFeePayload,
} from "@/lib/api/state";

const FACILITY_TYPES = [
  ["clinic", "Clinic"],
  ["hospital", "Hospital"],
  ["diagnostic_centre", "Diagnostic centre"],
  ["primary_health_centre", "Primary health centre"],
  ["mobile_health_unit", "Mobile health unit"],
];

const blankForm: StateAssessmentFeePayload = {
  facility_type: "clinic",
  amount: "",
  state_fee: "",
  facility_fee: "",
  platform_fee: "",
  currency: "NGN",
  effective_from: new Date().toISOString().slice(0, 10),
  effective_to: "",
  status: "active",
};

function money(value: string) {
  const amount = Number(value || 0);
  return new Intl.NumberFormat("en-NG", { style: "currency", currency: "NGN" }).format(amount);
}

function dateLabel(value?: string | null) {
  if (!value) return "Open-ended";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

function splitMatches(form: StateAssessmentFeePayload) {
  const gross = Number(form.amount || 0);
  const split = Number(form.state_fee || 0) + Number(form.facility_fee || 0) + Number(form.platform_fee || 0);
  return gross > 0 && gross === split;
}

export default function Page() {
  const queryClient = useQueryClient();
  const [status, setStatus] = useState("");
  const [facilityType, setFacilityType] = useState("");
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<AssessmentFee | null>(null);
  const [form, setForm] = useState<StateAssessmentFeePayload>(blankForm);

  const feesQuery = useQuery({
    queryKey: ["state-fees", status, facilityType],
    queryFn: () => fetchStateAssessmentFees({ status: status || undefined, facility_type: facilityType || undefined }),
  });

  const saveMutation = useMutation({
    mutationFn: () => {
      const payload = { ...form, effective_to: form.effective_to || null };
      return editing ? updateStateAssessmentFee(editing.id, payload) : createStateAssessmentFee(payload);
    },
    onSuccess: () => {
      setFormOpen(false);
      setEditing(null);
      setForm(blankForm);
      queryClient.invalidateQueries({ queryKey: ["state-fees"] });
    },
  });

  const fees = feesQuery.data || [];

  return (
    <PortalShell role="state_admin" title="Assessment fees" description="Configure state assessment fee splits and active pricing.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 md:grid-cols-[220px_220px_1fr_auto] md:items-end">
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-slate-500">
              Status
              <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm normal-case tracking-normal text-slate-700" value={status} onChange={(event) => setStatus(event.target.value)}>
                <option value="">All statuses</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </label>
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-slate-500">
              Facility type
              <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm normal-case tracking-normal text-slate-700" value={facilityType} onChange={(event) => setFacilityType(event.target.value)}>
                <option value="">All facility types</option>
                {FACILITY_TYPES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </label>
            <div />
            <button
              className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white hover:bg-brand-deep"
              onClick={() => {
                setEditing(null);
                setForm(blankForm);
                setFormOpen(true);
              }}
              type="button"
            >
              <Plus size={16} />
              New fee
            </button>
          </div>
        </section>

        <section className="grid gap-3">
          <div className="flex items-center gap-2">
            <Banknote className="text-brand-deep" size={18} />
            <h2 className="text-base font-bold text-slate-950">State Fee Rules</h2>
          </div>
          <DataTable<AssessmentFee>
            columns={[
              { key: "facility_type", header: "Facility type", render: (row) => row.facility_type.replaceAll("_", " ") },
              { key: "amount", header: "Gross", render: (row) => money(row.amount) },
              { key: "split", header: "Split", render: (row) => `${money(row.facility_fee)} facility / ${money(row.state_fee)} state / ${money(row.platform_fee)} platform` },
              { key: "effective", header: "Effective period", render: (row) => `${dateLabel(row.effective_from)} - ${dateLabel(row.effective_to)}` },
              { key: "status", header: "Status", render: (row) => <StatusCell status={row.status} /> },
              {
                key: "action",
                header: "Action",
                render: (row) => (
                  <button
                    className="h-8 rounded border border-slate-200 px-3 text-xs font-bold text-slate-700 hover:bg-slate-50"
                    onClick={() => {
                      setEditing(row);
                      setForm({
                        facility_type: row.facility_type,
                        amount: row.amount,
                        state_fee: row.state_fee,
                        facility_fee: row.facility_fee,
                        platform_fee: row.platform_fee,
                        currency: row.currency,
                        effective_from: row.effective_from,
                        effective_to: row.effective_to || "",
                        status: row.status,
                      });
                      setFormOpen(true);
                    }}
                    type="button"
                  >
                    Edit
                  </button>
                ),
              },
            ]}
            rows={fees}
            empty={feesQuery.isLoading ? "Loading assessment fees..." : "No assessment fees match the current filters."}
          />
        </section>
      </div>

      {formOpen ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">
          <div className="w-full max-w-2xl rounded-lg border border-slate-200 bg-white shadow-xl">
            <div className="border-b border-slate-100 px-6 py-4">
              <h2 className="text-lg font-bold text-slate-950">{editing ? "Edit assessment fee" : "New assessment fee"}</h2>
              <p className="mt-1 text-sm text-slate-500">Gross amount must equal facility, state, and platform splits.</p>
            </div>
            <form
              className="grid gap-4 p-6"
              onSubmit={(event) => {
                event.preventDefault();
                saveMutation.mutate();
              }}
            >
              <div className="grid gap-3 md:grid-cols-2">
                <label className="grid gap-1 text-sm font-semibold text-slate-700">
                  Facility type
                  <select className="h-10 rounded border border-slate-200 bg-white px-3" value={form.facility_type} onChange={(event) => setForm((prev) => ({ ...prev, facility_type: event.target.value }))}>
                    {FACILITY_TYPES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                  </select>
                </label>
                <label className="grid gap-1 text-sm font-semibold text-slate-700">
                  Gross amount
                  <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3" required type="number" min="0" step="0.01" value={form.amount} onChange={(event) => setForm((prev) => ({ ...prev, amount: event.target.value }))} />
                </label>
                <label className="grid gap-1 text-sm font-semibold text-slate-700">
                  Facility amount
                  <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3" required type="number" min="0" step="0.01" value={form.facility_fee} onChange={(event) => setForm((prev) => ({ ...prev, facility_fee: event.target.value }))} />
                </label>
                <label className="grid gap-1 text-sm font-semibold text-slate-700">
                  State amount
                  <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3" required type="number" min="0" step="0.01" value={form.state_fee} onChange={(event) => setForm((prev) => ({ ...prev, state_fee: event.target.value }))} />
                </label>
                <label className="grid gap-1 text-sm font-semibold text-slate-700">
                  Platform amount
                  <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3" required type="number" min="0" step="0.01" value={form.platform_fee} onChange={(event) => setForm((prev) => ({ ...prev, platform_fee: event.target.value }))} />
                </label>
                <label className="grid gap-1 text-sm font-semibold text-slate-700">
                  Status
                  <select className="h-10 rounded border border-slate-200 bg-white px-3" value={form.status} onChange={(event) => setForm((prev) => ({ ...prev, status: event.target.value as "active" | "inactive" }))}>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </label>
                <label className="grid gap-1 text-sm font-semibold text-slate-700">
                  Effective from
                  <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3" required type="date" value={form.effective_from} onChange={(event) => setForm((prev) => ({ ...prev, effective_from: event.target.value }))} />
                </label>
                <label className="grid gap-1 text-sm font-semibold text-slate-700">
                  Effective to
                  <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3" type="date" value={form.effective_to || ""} onChange={(event) => setForm((prev) => ({ ...prev, effective_to: event.target.value }))} />
                </label>
              </div>

              <p className={`rounded px-3 py-2 text-sm font-semibold ${splitMatches(form) ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"}`}>
                Split preview: {money(form.facility_fee || "0")} + {money(form.state_fee || "0")} + {money(form.platform_fee || "0")} = {money(String(Number(form.facility_fee || 0) + Number(form.state_fee || 0) + Number(form.platform_fee || 0)))}
              </p>
              {saveMutation.isError ? <p className="rounded bg-red-50 px-3 py-2 text-sm font-semibold text-red-700">Could not save this fee. Check split totals and overlapping active periods.</p> : null}
              <div className="flex justify-end gap-3">
                <button className="h-10 rounded border border-slate-200 px-4 text-sm font-semibold text-slate-600 hover:bg-slate-50" onClick={() => setFormOpen(false)} type="button">Cancel</button>
                <button className="h-10 rounded bg-brand-green px-4 text-sm font-bold text-white hover:bg-brand-deep disabled:opacity-60" disabled={saveMutation.isPending || !splitMatches(form)} type="submit">Save fee</button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </PortalShell>
  );
}
