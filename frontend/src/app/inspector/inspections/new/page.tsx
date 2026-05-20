"use client";

import { useQuery } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import { ClipboardCheck, MapPin } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { BranchSelector } from "@/components/ui/branch-selector";
import { fetchUnits } from "@/lib/api/organizations";
import { listInspections } from "@/lib/api/inspections";

export default function Page() {
  const [orgId, setOrgId] = useState<string | null>(null);
  const [branchId, setBranchId] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("foodcert_access_token");
    if (!token) return;
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      setOrgId(payload.organization_id || null);
    } catch { /* ignore */ }
  }, []);

  const { data: allUnits = [] } = useQuery({
    queryKey: ["all-units"],
    queryFn: async () => {
      // fetch units from the user's organization if known, else empty
      if (!orgId) return [];
      return fetchUnits(orgId);
    },
    enabled: !!orgId,
  });

  const branches = allUnits.filter((u) => u.unit_type === "branch");

  const { data: inspections = [] } = useQuery({
    queryKey: ["inspections", branchId],
    queryFn: listInspections,
  });

  return (
    <PortalShell role="inspector" title="New inspection" description="Start an inspection checklist, record GPS metadata, evidence, and findings.">
      <div className="grid gap-5">
        {branches.length > 0 && (
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <div className="flex flex-wrap items-center gap-4">
              <BranchSelector branches={branches} value={branchId ?? undefined} onChange={(id) => setBranchId(id)} />
              <span className="text-xs text-slate-400">
                {branchId ? "Inspection will target this specific branch." : "Inspection will target the entire business."}
              </span>
            </div>
          </div>
        )}

        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="grid gap-1 text-sm font-semibold text-slate-700">
              Employer / Business <span className="text-red-500">*</span>
              <input
                className="h-10 rounded border border-slate-200 bg-slate-50 px-3"
                placeholder="Search for employer..."
              />
            </label>
            {branchId && (
              <label className="grid gap-1 text-sm font-semibold text-slate-700">
                Branch <span className="text-xs text-slate-400">(pre-selected)</span>
                <div className="flex h-10 items-center gap-2 rounded border border-amber-100 bg-amber-50 px-3 text-sm font-semibold text-amber-800">
                  <MapPin size={14} />
                  {branches.find((b) => b.id === branchId)?.name ?? "Selected branch"}
                </div>
              </label>
            )}
            <label className="grid gap-1 text-sm font-semibold text-slate-700">
              Inspection type
              <select className="h-10 rounded border border-slate-200 bg-white px-3" defaultValue="routine">
                <option value="routine">Routine</option>
                <option value="follow_up">Follow-up</option>
                <option value="complaint">Complaint-driven</option>
                <option value="re_inspection">Re-inspection</option>
              </select>
            </label>
            <label className="grid gap-1 text-sm font-semibold text-slate-700">
              Date
              <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3" type="datetime-local" />
            </label>
          </div>

          <div className="mt-5 rounded bg-slate-50 p-4">
            <p className="text-sm font-bold text-slate-800 mb-3">Inspection Checklist</p>
            <div className="grid gap-2 text-sm">
              {[
                "Are all food handlers registered?",
                "Are certificates valid?",
                "Are certificates genuine?",
                "Are vaccination records current?",
                "Are sick handlers excluded?",
                "Are handwashing facilities available?",
                "Are PPEs available?",
                "Are hygiene practices enforced?",
                "Are employer records up to date?",
                "Are expired certificates being used?",
              ].map((item, i) => (
                <label key={i} className="flex items-center gap-3 rounded bg-white px-3 py-2 border border-slate-100">
                  <input type="checkbox" className="h-4 w-4 rounded border-slate-300 text-brand-green" />
                  <span className="text-slate-700">{item}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="mt-5 flex items-center gap-3">
            <button className="inline-flex h-10 items-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white hover:bg-brand-deep">
              <ClipboardCheck size={16} />
              Submit inspection
            </button>
            <button className="inline-flex h-10 items-center gap-2 rounded border border-slate-200 px-4 text-sm font-semibold text-slate-600 hover:bg-slate-50">
              Save draft
            </button>
          </div>
        </div>

        {inspections.length > 0 && (
          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="mb-3 text-sm font-bold text-slate-950">Recent inspections</h3>
            <div className="divide-y divide-slate-100">
              {inspections.slice(0, 5).map((insp) => (
                <div key={insp.id} className="flex items-center justify-between py-2 text-sm">
                  <span className="text-slate-700">{insp.employer_name ?? "Employer"}</span>
                  <span className="text-xs text-slate-400">{insp.status}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </PortalShell>
  );
}
