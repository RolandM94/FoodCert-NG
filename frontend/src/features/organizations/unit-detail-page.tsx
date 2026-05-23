"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, ClipboardCheck, FileText, ShieldCheck, UsersRound } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { OrganizationUnitDetail } from "@/components/ui/organization-unit-detail";
import { fetchUnit } from "@/lib/api/organizations";
import type { UserRole } from "@/types/auth";

function getOrganizationId() {
  const token = typeof window !== "undefined" ? localStorage.getItem("foodcert_access_token") : null;
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.organization_id || payload.organization || null;
  } catch {
    return null;
  }
}

const tabsByKind = {
  branch: ["Overview", "Food Handlers", "Certificates", "Illness Reports", "Inspections", "Compliance Reports", "Branch Users"],
  department: ["Overview", "Members", "Workload", "Reports"],
  state_unit: ["Overview", "Officers", "Assigned Queues", "Reports", "Audit"],
};

export function UnitDetailPage({
  role,
  unitId,
  kind,
  backHref,
}: {
  role: UserRole;
  unitId: string;
  kind: keyof typeof tabsByKind;
  backHref: string;
}) {
  const [orgId, setOrgId] = useState<string | null>(null);
  useEffect(() => setOrgId(getOrganizationId()), []);

  const unitQuery = useQuery({
    queryKey: ["organization-unit", orgId, unitId],
    queryFn: () => fetchUnit(orgId!, unitId),
    enabled: Boolean(orgId && unitId),
  });

  const unit = unitQuery.data;
  const tabs = useMemo(() => tabsByKind[kind], [kind]);
  const title = unit?.name || "Unit Detail";

  return (
    <PortalShell role={role} title={title} description="Review unit scope, linked workflows, members, and operational status.">
      <div className="grid gap-6">
        <Link className="inline-flex w-fit items-center gap-2 rounded border border-slate-200 px-3 py-2 text-sm font-bold text-slate-700 hover:bg-slate-50" href={backHref}>
          <ArrowLeft size={16} />
          Back
        </Link>

        {unitQuery.isError ? <p className="rounded-lg bg-rose-50 p-4 text-sm font-semibold text-rose-700">Could not load this unit.</p> : null}
        {unit ? <OrganizationUnitDetail unit={unit} memberCount={unit.member_count ?? 0} /> : null}

        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex flex-wrap gap-2">
            {tabs.map((tab) => (
              <button key={tab} className="rounded border border-slate-200 px-3 py-2 text-sm font-bold text-slate-700 hover:bg-slate-50" type="button">
                {tab}
              </button>
            ))}
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded border border-slate-100 p-4">
              <UsersRound className="text-brand-deep" size={18} />
              <p className="mt-2 text-sm font-bold text-slate-950">Members</p>
              <p className="mt-1 text-sm text-slate-500">Assigned users and scoped staff appear here.</p>
            </div>
            <div className="rounded border border-slate-100 p-4">
              <ClipboardCheck className="text-brand-deep" size={18} />
              <p className="mt-2 text-sm font-bold text-slate-950">Workload</p>
              <p className="mt-1 text-sm text-slate-500">Linked inspections, queues, and tasks are grouped by scope.</p>
            </div>
            <div className="rounded border border-slate-100 p-4">
              {kind === "branch" ? <ShieldCheck className="text-brand-deep" size={18} /> : <FileText className="text-brand-deep" size={18} />}
              <p className="mt-2 text-sm font-bold text-slate-950">Reports</p>
              <p className="mt-1 text-sm text-slate-500">Scope-specific compliance and activity reports stay privacy-filtered.</p>
            </div>
          </div>
        </section>
      </div>
    </PortalShell>
  );
}
