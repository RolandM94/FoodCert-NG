"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Banknote, Check, PauseCircle, Send, Plus } from "lucide-react";
import { useState } from "react";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import {
  approveStateAssessmentFee,
  createStateAssessmentFee,
  fetchStateAssessmentFees,
  submitStateAssessmentFee,
  suspendStateAssessmentFee,
  updateStateAssessmentFee,
  type AssessmentFee,
  type StateAssessmentFeePayload,
} from "@/lib/api/state";
import { redirect } from "next/navigation";

const FACILITY_TYPES = [
  ["clinic", "Clinic"],
  ["hospital", "Hospital"],
  ["diagnostic_centre", "Diagnostic centre"],
  ["primary_health_centre", "Primary health centre"],
  ["mobile_health_unit", "Mobile health unit"],
];

const blankForm: StateAssessmentFeePayload = {
  facility_type: "clinic",
  fee_name: "Assessment fee",
  amount: "",
  state_fee: "",
  facility_fee: "",
  provider_fee_handling: "deduct_from_platform",
  currency: "NGN",
  effective_from: new Date().toISOString().slice(0, 10),
  effective_to: "",
  status: "draft",
  notes: "",
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
  const split = Number(form.state_fee || 0) + Number(form.facility_fee || 0);
  return gross > 0 && gross === split;
}

export function StateFeesSettingsPanel() {
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

  const actionMutation = useMutation({
    mutationFn: ({ id, action }: { id: string; action: "submit" | "approve" | "suspend" }) => {
      if (action === "submit") return submitStateAssessmentFee(id);
      if (action === "approve") return approveStateAssessmentFee(id);
      return suspendStateAssessmentFee(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["state-fees"] });
    },
  });

  const fees = feesQuery.data || [];

  return (
    <>
      <div className="grid gap-5">
        <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div className="grid gap-3 md:grid-cols-[220px_220px_1fr_auto] md:items-end">
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-neutral-500">
              Status
              <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm normal-case tracking-normal text-neutral-700" value={status} onChange={(event) => setStatus(event.target.value)}>
                <option value="">All statuses</option>
                <option value="draft">Draft</option>
                <option value="pending_approval">Pending approval</option>
                <option value="active">Active</option>
                <option value="scheduled">Scheduled</option>
                <option value="suspended">Suspended</option>
                <option value="inactive">Inactive</option>
              </select>
            </label>
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-neutral-500">
              Facility type
              <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm normal-case tracking-normal text-neutral-700" value={facilityType} onChange={(event) => setFacilityType(event.target.value)}>
                <option value="">All facility types</option>
                {FACILITY_TYPES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </label>
            <div />
            <button
              className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-600 px-4 text-sm font-bold text-white hover:bg-brand-700"
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
            <Banknote className="text-brand-700" size={18} />
            <h2 className="text-base font-bold text-neutral-900">State Fee Rules</h2>
          </div>
          <DataTable<AssessmentFee>
            columns={[
              { key: "facility_type", header: "Facility type", render: (row) => row.facility_type.replaceAll("_", " ") },
              { key: "fee_name", header: "Fee name", render: (row) => row.fee_name },
              { key: "amount", header: "State assessment fee", render: (row) => money(row.amount) },
              { key: "split", header: "State split", render: (row) => `${money(row.facility_fee)} facility / ${money(row.state_fee)} state` },
              { key: "platform_fee", header: "Platform fee", render: (row) => `${money(row.platform_fee)} auto-added` },
              { key: "effective", header: "Effective period", render: (row) => `${dateLabel(row.effective_from)} - ${dateLabel(row.effective_to)}` },
              { key: "status", header: "Status", render: (row) => <StatusCell status={row.status} /> },
              {
                key: "action",
                header: "Action",
                render: (row) => (
                  <div>
                    <button
                      className="h-8 rounded border border-neutral-200 px-3 text-xs font-bold text-neutral-700 hover:bg-neutral-50"
                      onClick={() => {
                        setEditing(row);
                        setForm({
                          facility_type: row.facility_type,
                          fee_name: row.fee_name,
                          amount: row.amount,
                          state_fee: row.state_fee,
                          facility_fee: row.facility_fee,
                          provider_fee_handling: row.provider_fee_handling,
                          currency: row.currency,
                          effective_from: row.effective_from,
                          effective_to: row.effective_to || "",
                          status: row.status,
                          notes: row.notes || "",
                        });
                        setFormOpen(true);
                      }}
                      type="button"
                    >
                      Edit
                    </button>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {row.status === "draft" || row.status === "inactive" ? (
                        <button className="inline-flex h-8 items-center gap-1 rounded border border-neutral-200 px-2 text-xs font-bold text-neutral-700 hover:bg-neutral-50" disabled={actionMutation.isPending} onClick={() => actionMutation.mutate({ id: row.id, action: "submit" })} type="button"><Send size={13} /> Submit</button>
                      ) : null}
                      {row.status === "pending_approval" ? (
                        <button className="inline-flex h-8 items-center gap-1 rounded bg-brand-600 px-2 text-xs font-bold text-white hover:bg-brand-700" disabled={actionMutation.isPending} onClick={() => actionMutation.mutate({ id: row.id, action: "approve" })} type="button"><Check size={13} /> Approve</button>
                      ) : null}
                      {row.status === "active" || row.status === "scheduled" ? (
                        <button className="inline-flex h-8 items-center gap-1 rounded border border-warning-100 px-2 text-xs font-bold text-warning-700 hover:bg-warning-50" disabled={actionMutation.isPending} onClick={() => actionMutation.mutate({ id: row.id, action: "suspend" })} type="button"><PauseCircle size={13} /> Suspend</button>
                      ) : null}
                    </div>
                  </div>
                ),
              },
            ]}
            rows={fees}
            empty={feesQuery.isLoading ? "Loading assessment fees..." : "No assessment fees match the current filters."}
          />
        </section>
      </div>

      {formOpen ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-neutral-900/50 p-4">
          <div className="w-full max-w-2xl rounded-lg border border-neutral-200 bg-white shadow-xl">
            <div className="border-b border-neutral-100 px-6 py-4">
              <h2 className="text-lg font-bold text-neutral-900">{editing ? "Edit assessment fee" : "New assessment fee"}</h2>
              <p className="mt-1 text-sm text-neutral-500">State assessment amount must equal facility and state shares. FoodCert platform fee is configured by the platform owner and added automatically at checkout.</p>
            </div>
            <form
              className="grid gap-4 p-6"
              onSubmit={(event) => {
                event.preventDefault();
                saveMutation.mutate();
              }}
            >
              <div className="grid gap-3 md:grid-cols-2">
                <label className="grid gap-1 text-sm font-semibold text-neutral-700">
                  Fee name
                  <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3" required value={form.fee_name || ""} onChange={(event) => setForm((prev) => ({ ...prev, fee_name: event.target.value }))} />
                </label>
                <label className="grid gap-1 text-sm font-semibold text-neutral-700">
                  Facility type
                  <select className="h-10 rounded border border-neutral-200 bg-white px-3" value={form.facility_type} onChange={(event) => setForm((prev) => ({ ...prev, facility_type: event.target.value }))}>
                    {FACILITY_TYPES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                  </select>
                </label>
                <label className="grid gap-1 text-sm font-semibold text-neutral-700">
                  State assessment amount
                  <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3" required type="number" min="0" step="0.01" value={form.amount} onChange={(event) => setForm((prev) => ({ ...prev, amount: event.target.value }))} />
                </label>
                <label className="grid gap-1 text-sm font-semibold text-neutral-700">
                  Facility amount
                  <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3" required type="number" min="0" step="0.01" value={form.facility_fee} onChange={(event) => setForm((prev) => ({ ...prev, facility_fee: event.target.value }))} />
                </label>
                <label className="grid gap-1 text-sm font-semibold text-neutral-700">
                  State amount
                  <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3" required type="number" min="0" step="0.01" value={form.state_fee} onChange={(event) => setForm((prev) => ({ ...prev, state_fee: event.target.value }))} />
                </label>
                <label className="grid gap-1 text-sm font-semibold text-neutral-700">
                  Status
                  <select className="h-10 rounded border border-neutral-200 bg-white px-3" value={form.status} onChange={(event) => setForm((prev) => ({ ...prev, status: event.target.value as AssessmentFee["status"] }))}>
                    <option value="draft">Draft</option>
                    <option value="pending_approval">Pending approval</option>
                    <option value="active">Active</option>
                    <option value="scheduled">Scheduled</option>
                    <option value="suspended">Suspended</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </label>
                <label className="grid gap-1 text-sm font-semibold text-neutral-700">
                  Effective from
                  <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3" required type="date" value={form.effective_from} onChange={(event) => setForm((prev) => ({ ...prev, effective_from: event.target.value }))} />
                </label>
                <label className="grid gap-1 text-sm font-semibold text-neutral-700">
                  Effective to
                  <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3" type="date" value={form.effective_to || ""} onChange={(event) => setForm((prev) => ({ ...prev, effective_to: event.target.value }))} />
                </label>
                <label className="grid gap-1 text-sm font-semibold text-neutral-700 md:col-span-2">
                  Notes
                  <textarea className="min-h-20 rounded border border-neutral-200 bg-neutral-50 px-3 py-2" value={form.notes || ""} onChange={(event) => setForm((prev) => ({ ...prev, notes: event.target.value }))} />
                </label>
              </div>

              <p className={`rounded px-3 py-2 text-sm font-semibold ${splitMatches(form) ? "bg-brand-50 text-brand-700" : "bg-warning-50 text-warning-700"}`}>
                State split preview: {money(form.facility_fee || "0")} facility + {money(form.state_fee || "0")} state = {money(String(Number(form.facility_fee || 0) + Number(form.state_fee || 0)))}
              </p>
              {saveMutation.isError ? <p className="rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">Could not save this fee. Check split totals and overlapping active periods.</p> : null}
              <div className="flex justify-end gap-3">
                <button className="h-10 rounded border border-neutral-200 px-4 text-sm font-semibold text-neutral-600 hover:bg-neutral-50" onClick={() => setFormOpen(false)} type="button">Cancel</button>
                <button className="h-10 rounded bg-brand-600 px-4 text-sm font-bold text-white hover:bg-brand-700 disabled:opacity-60" disabled={saveMutation.isPending || !splitMatches(form)} type="submit">Save fee</button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </>
  );
}

export default function Page() {
  redirect("/state/account-settings?tab=fees-payments");
}
