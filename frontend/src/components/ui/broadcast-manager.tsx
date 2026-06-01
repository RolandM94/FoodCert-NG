"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, Loader2, Plus, Send, Star, Users } from "lucide-react";
import { useState } from "react";
import {
  approveBroadcast,
  createBroadcast,
  estimateBroadcastAudience,
  listBroadcasts,
  sendBroadcast,
  submitBroadcastForApproval,
} from "@/lib/api/notifications";
import type { BroadcastMessage } from "@/types/notifications";

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-slate-100 text-slate-700",
  pending_approval: "bg-amber-100 text-amber-800",
  approved: "bg-blue-100 text-blue-800",
  sending: "bg-purple-100 text-purple-800",
  sent: "bg-emerald-100 text-emerald-800",
  failed: "bg-rose-100 text-rose-800",
  cancelled: "bg-slate-200 text-slate-500",
};

const AUDIENCE_LABELS: Record<string, string> = {
  all_users_in_state: "All Users (State)",
  all_employers_in_state: "All Employers (State)",
  all_facilities_in_state: "All Facilities (State)",
  all_inspectors_in_state: "All Inspectors (State)",
  all_state_ministry: "State Ministry",
  all_federal_ministry: "Federal Ministry",
  all_users_in_organization: "Organization",
  all_users_in_unit: "Unit",
  expiring_certs: "Expiring Certificates",
};

export function BroadcastManager() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: "", message: "", audience_type: "all_federal_ministry", category: "system", priority: "normal" });

  const { data: broadcasts = [], isLoading } = useQuery({
    queryKey: ["broadcasts"],
    queryFn: listBroadcasts,
  });

  const createMutation = useMutation({
    mutationFn: createBroadcast,
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["broadcasts"] }); setShowForm(false); },
  });

  const estimateMutation = useMutation({
    mutationFn: estimateBroadcastAudience,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["broadcasts"] }),
  });

  const submitMutation = useMutation({
    mutationFn: submitBroadcastForApproval,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["broadcasts"] }),
  });

  const approveMutation = useMutation({
    mutationFn: approveBroadcast,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["broadcasts"] }),
  });

  const sendMutation = useMutation({
    mutationFn: sendBroadcast,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["broadcasts"] }),
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-bold text-slate-950">Broadcasts</h3>
        <button className="inline-flex h-10 items-center gap-1.5 rounded bg-brand-green px-4 text-sm font-bold text-white hover:bg-brand-deep" onClick={() => setShowForm(true)} type="button">
          <Plus size={16} /> New Broadcast
        </button>
      </div>

      {showForm ? (
        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="grid gap-4 md:grid-cols-2">
            <label className="grid gap-1 text-sm font-semibold text-slate-700">Title
              <input className="h-10 rounded border border-slate-200 px-3 text-sm" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
            </label>
            <label className="grid gap-1 text-sm font-semibold text-slate-700">Audience
              <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={form.audience_type} onChange={(e) => setForm({ ...form, audience_type: e.target.value })}>
                {Object.entries(AUDIENCE_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </label>
            <label className="col-span-2 grid gap-1 text-sm font-semibold text-slate-700">Message
              <textarea className="min-h-[80px] rounded border border-slate-200 px-3 py-2 text-sm" value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })} />
            </label>
          </div>
          <div className="mt-4 flex gap-2">
            <button className="inline-flex h-10 items-center rounded bg-brand-green px-4 text-sm font-bold text-white hover:bg-brand-deep disabled:opacity-60" disabled={createMutation.isPending || !form.title} onClick={() => createMutation.mutate({ ...form, channels: ["in_app", "email"], audience_filters: {} })} type="button">
              {createMutation.isPending ? <Loader2 className="animate-spin" size={16} /> : "Create Draft"}
            </button>
            <button className="inline-flex h-10 items-center rounded border border-slate-200 px-4 text-sm font-semibold text-slate-700" onClick={() => setShowForm(false)} type="button">Cancel</button>
          </div>
        </div>
      ) : null}

      {isLoading ? <div className="flex justify-center py-12"><Loader2 className="animate-spin text-slate-400" size={24} /></div> : (
        <div className="space-y-3">
          {broadcasts.map((b) => (
            <div key={b.id} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <h4 className="font-bold text-slate-950">{b.title}</h4>
                  <p className="mt-1 text-sm text-slate-600 line-clamp-2">{b.message}</p>
                  <div className="mt-2 flex flex-wrap items-center gap-2">
                    <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${STATUS_COLORS[b.status] || ""}`}>{b.status_display}</span>
                    <span className="text-xs text-slate-500">{AUDIENCE_LABELS[b.audience_type] || b.audience_type}</span>
                    {b.estimated_recipient_count > 0 ? <span className="text-xs text-slate-400"><Users size={12} className="inline" /> ~{b.estimated_recipient_count}</span> : null}
                    {b.sent_count > 0 ? <span className="text-xs text-emerald-600">{b.sent_count} sent</span> : null}
                  </div>
                </div>
                <div className="flex items-center gap-1 shrink-0">
                  {b.status === "draft" ? (
                    <>
                      <button className="inline-flex h-8 items-center gap-1 rounded border border-slate-200 px-2 text-xs font-semibold text-slate-700 hover:bg-slate-50" onClick={() => estimateMutation.mutate(b.id)} title="Estimate audience" type="button"><Users size={14} /> Estimate</button>
                      <button className="inline-flex h-8 items-center gap-1 rounded border border-slate-200 px-2 text-xs font-semibold text-amber-700 hover:bg-amber-50" onClick={() => submitMutation.mutate(b.id)} type="button"><Send size={14} /> Submit</button>
                    </>
                  ) : null}
                  {b.status === "pending_approval" ? (
                    <button className="inline-flex h-8 items-center gap-1 rounded border border-slate-200 px-2 text-xs font-semibold text-emerald-700 hover:bg-emerald-50" onClick={() => approveMutation.mutate(b.id)} type="button"><Check size={14} /> Approve</button>
                  ) : null}
                  {b.status === "approved" ? (
                    <button className="inline-flex h-8 items-center gap-1 rounded bg-brand-green px-2 text-xs font-bold text-white hover:bg-brand-deep" onClick={() => sendMutation.mutate(b.id)} type="button"><Send size={14} /> Send</button>
                  ) : null}
                </div>
              </div>
            </div>
          ))}
          {!broadcasts.length ? <p className="py-8 text-center text-sm text-slate-500">No broadcasts yet.</p> : null}
        </div>
      )}
    </div>
  );
}
