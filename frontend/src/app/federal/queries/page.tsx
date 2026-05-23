"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { MessageSquarePlus } from "lucide-react";
import { useMemo, useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import {
  closeFederalQuery,
  createFederalQuery,
  fetchFederalQueries,
  fetchFederalStatePerformance,
  respondFederalQuery,
  type FederalStateQueryItem,
} from "@/lib/api/federal";

export default function Page() {
  const queryClient = useQueryClient();
  const [status, setStatus] = useState("");
  const [stateId, setStateId] = useState("");
  const [subject, setSubject] = useState("");
  const [category, setCategory] = useState("data_quality");
  const [priority, setPriority] = useState("medium");
  const [description, setDescription] = useState("");
  const [responseText, setResponseText] = useState("");
  const queriesQuery = useQuery({ queryKey: ["federal-queries", status], queryFn: () => fetchFederalQueries({ status }) });
  const statesQuery = useQuery({ queryKey: ["federal-state-performance"], queryFn: fetchFederalStatePerformance });
  const rows = useMemo(() => queriesQuery.data || [], [queriesQuery.data]);
  const selectedQuery = useMemo(() => rows.find((row) => row.status !== "closed") || rows[0], [rows]);

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["federal-queries"] });
  const createMutation = useMutation({
    mutationFn: () => createFederalQuery({ state: stateId, subject, description, category, priority }),
    onSuccess: () => {
      setSubject("");
      setDescription("");
      invalidate();
    },
  });
  const respondMutation = useMutation({
    mutationFn: () => respondFederalQuery(selectedQuery?.id || "", responseText),
    onSuccess: () => {
      setResponseText("");
      invalidate();
    },
  });
  const closeMutation = useMutation({ mutationFn: closeFederalQuery, onSuccess: invalidate });

  return (
    <PortalShell role="federal_admin" title="State queries" description="Create, respond to, and close official federal queries to state ministries.">
      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_380px]">
        <section className="grid gap-4">
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={status} onChange={(event) => setStatus(event.target.value)}>
              <option value="">All statuses</option>
              <option value="open">Open</option>
              <option value="responded">Responded</option>
              <option value="closed">Closed</option>
            </select>
          </div>
          <DataTable<FederalStateQueryItem>
            columns={[
              { key: "subject", header: "Subject", render: (row) => <div><p className="font-bold text-slate-950">{row.subject}</p><p className="text-xs text-slate-500">{row.category.replaceAll("_", " ")}</p></div> },
              { key: "state", header: "State", render: (row) => row.state_name },
              { key: "priority", header: "Priority", render: (row) => <StatusCell status={row.priority} /> },
              { key: "status", header: "Status", render: (row) => <StatusCell status={row.status} /> },
              { key: "response", header: "Response", render: (row) => row.response ? "Received" : "Pending" },
            ]}
            rows={rows}
            empty={queriesQuery.isLoading ? "Loading queries..." : "No federal queries yet."}
          />
        </section>

        <aside className="grid gap-4">
          <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <div className="mb-3 flex items-center gap-2"><MessageSquarePlus className="text-brand-deep" size={18} /><h2 className="text-sm font-bold text-slate-950">Create Query</h2></div>
            <div className="grid gap-3">
              <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={stateId} onChange={(event) => setStateId(event.target.value)}>
                <option value="">Select state</option>
                {(statesQuery.data?.states || []).map((state) => <option key={state.state_id} value={state.state_id}>{state.state_name}</option>)}
              </select>
              <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" value={subject} onChange={(event) => setSubject(event.target.value)} placeholder="Subject" />
              <div className="grid grid-cols-2 gap-3">
                <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={category} onChange={(event) => setCategory(event.target.value)}>
                  <option value="data_quality">Data quality</option>
                  <option value="reporting">Reporting</option>
                  <option value="policy">Policy</option>
                  <option value="compliance">Compliance</option>
                </select>
                <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={priority} onChange={(event) => setPriority(event.target.value)}>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
              <textarea className="min-h-24 rounded border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Description" />
              <button className="h-10 rounded bg-brand-deep px-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-300" disabled={!stateId || !subject || createMutation.isPending} onClick={() => createMutation.mutate()} type="button">
                {createMutation.isPending ? "Creating..." : "Create query"}
              </button>
            </div>
          </section>

          <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <h2 className="mb-3 text-sm font-bold text-slate-950">Response / Closure</h2>
            {selectedQuery ? (
              <div className="grid gap-3">
                <p className="text-sm font-semibold text-slate-900">{selectedQuery.subject}</p>
                <textarea className="min-h-24 rounded border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={responseText} onChange={(event) => setResponseText(event.target.value)} placeholder="Response note" />
                <button className="h-10 rounded border border-brand-deep px-3 text-sm font-semibold text-brand-deep disabled:cursor-not-allowed disabled:border-slate-300 disabled:text-slate-400" disabled={!responseText || respondMutation.isPending || selectedQuery.status === "closed"} onClick={() => respondMutation.mutate()} type="button">
                  {respondMutation.isPending ? "Saving..." : "Save response"}
                </button>
                <button className="h-10 rounded bg-slate-950 px-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-300" disabled={closeMutation.isPending || selectedQuery.status === "closed"} onClick={() => closeMutation.mutate(selectedQuery.id)} type="button">
                  {closeMutation.isPending ? "Closing..." : "Close query"}
                </button>
              </div>
            ) : <p className="text-sm text-slate-600">No query selected.</p>}
          </section>
        </aside>
      </div>
    </PortalShell>
  );
}
