"use client";

import { useQuery } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import { AlertCircle, BadgeCheck, Building2, ClipboardCheck, HeartPulse, Landmark, ShieldCheck, Syringe, UsersRound } from "lucide-react";
import { DashboardCard } from "@/components/ui/dashboard-card";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import { FilterBar } from "@/components/ui/filter-bar";
import { OrganizationScopeSwitcher } from "@/components/ui/organization-scope-switcher";
import { fetchUnits } from "@/lib/api/organizations";
import {
  getEmployerDashboard,
  getFacilityDashboard,
  getFederalDashboard,
  getStateDashboard
} from "@/lib/api/reports";
import type { DashboardPayload } from "@/types/reports";
import type { OrganizationUnit } from "@/types/organizations";

const dashboardConfig = {
  employer: {
    queryKey: ["dashboard", "employer"],
    queryFn: getEmployerDashboard,
    cards: [
      ["total_food_handlers", "Food handlers", UsersRound],
      ["valid_certificates", "Valid certificates", BadgeCheck],
      ["expired_certificates", "Expired certificates", AlertCircle],
      ["temporarily_not_fit", "Excluded/not fit", HeartPulse],
      ["typhoid_vaccination_valid", "Typhoid valid", Syringe],
      ["compliance_percentage", "Compliance %", ShieldCheck]
    ]
  },
  facility: {
    queryKey: ["dashboard", "facility"],
    queryFn: getFacilityDashboard,
    cards: [
      ["assessments_conducted", "Assessments", ClipboardCheck],
      ["certificates_issued", "Certificates", BadgeCheck],
      ["pending_lab_results", "Pending lab", AlertCircle],
      ["pending_settlements", "Pending settlements", Landmark],
      ["settled_amount", "Settled amount", ShieldCheck],
      ["reaccreditation_countdown_days", "Accreditation days", Building2]
    ]
  },
  state: {
    queryKey: ["dashboard", "state"],
    queryFn: getStateDashboard,
    cards: [
      ["registered_food_handlers", "Food handlers", UsersRound],
      ["certified_food_handlers", "Certified", BadgeCheck],
      ["food_businesses_registered", "Businesses", Building2],
      ["approved_facilities", "Approved facilities", ShieldCheck],
      ["illness_reports", "Illness reports", HeartPulse],
      ["inspections_conducted", "Inspections", ClipboardCheck]
    ]
  },
  federal: {
    queryKey: ["dashboard", "federal"],
    queryFn: getFederalDashboard,
    cards: [
      ["national_certification_coverage", "Coverage %", ShieldCheck],
      ["registered_food_handlers", "Food handlers", UsersRound],
      ["certified_food_handlers", "Certified", BadgeCheck],
      ["approved_facilities", "Facilities", Building2],
      ["illness_reports", "Illness reports", HeartPulse],
      ["inspections", "Inspections", ClipboardCheck]
    ]
  }
} as const;

type DashboardKind = keyof typeof dashboardConfig;

export function DashboardClient({ kind }: { kind: DashboardKind }) {
  const config = dashboardConfig[kind];
  const [branchId, setBranchId] = useState<string | null>(null);
  const [deptId, setDeptId] = useState<string | null>(null);
  const [orgId, setOrgId] = useState<string | null>(null);
  const [unitRestricted, setUnitRestricted] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("foodcert_access_token");
    if (!token) return;
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      setOrgId(payload.organization_id || null);
      setUnitRestricted(payload.unit_restricted === true);
      if (payload.unit_id) {
        if (kind === "employer") setBranchId(payload.unit_id);
        if (kind === "facility") setDeptId(payload.unit_id);
      }
    } catch { /* ignore */ }
  }, [kind]);

  // Fetch units for scope switcher
  const { data: units = [] } = useQuery<OrganizationUnit[]>({
    queryKey: ["units", orgId],
    queryFn: () => fetchUnits(orgId!),
    enabled: !!orgId && (kind === "employer" || kind === "facility"),
  });

  const branches = kind === "employer" ? units.filter((u) => u.unit_type === "branch") : undefined;
  const departments = kind === "facility" ? units.filter((u) => ["lab_department", "clinical_department", "records_department"].includes(u.unit_type)) : undefined;

  const params: Record<string, string> = {};
  if (branchId) params.branch = branchId;
  if (deptId) params.department = deptId;

  const query = useQuery<DashboardPayload>({
    queryKey: [...config.queryKey, branchId, deptId],
    queryFn: () => config.queryFn(params)
  });

  if (query.isLoading) {
    return <div className="rounded-lg border border-slate-200 bg-white p-6 text-sm text-slate-600">Loading dashboard...</div>;
  }

  if (query.isError) {
    return (
      <div className="rounded-lg border border-rose-200 bg-rose-50 p-6 text-sm font-semibold text-rose-800">
        Dashboard data needs a signed-in user with the right role.
      </div>
    );
  }

  const payload = query.data;
  const cards = payload?.cards ?? {};
  const chartRows = Object.entries(payload?.charts ?? {}).map(([name, value]) => ({
    name,
    status: Array.isArray(value) ? `${value.length} rows` : "summary"
  }));

  return (
    <div className="grid gap-6">
      {(branches || departments) && (
        <OrganizationScopeSwitcher
          branches={branches}
          departments={departments}
          currentBranchId={branchId ?? undefined}
          currentDeptId={deptId ?? undefined}
          onBranchChange={(id) => setBranchId(id)}
          onDeptChange={(id) => setDeptId(id)}
          restricted={unitRestricted}
          restrictedLabel={unitRestricted && branchId ? branches?.find((b) => b.id === branchId)?.name : undefined}
        />
      )}
      {payload?.branch && (
        <div className="rounded-lg border border-amber-100 bg-amber-50 px-4 py-2 text-sm font-semibold text-amber-800">
          Viewing branch: {payload.branch.name}
        </div>
      )}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {config.cards.map(([key, label, Icon]) => (
          <DashboardCard key={key} label={label} value={cards[key]} icon={Icon} />
        ))}
      </div>
      <FilterBar label="Filter dashboard records" />
      <DataTable
        columns={[
          { key: "name", header: "Dataset", render: (row) => row.name },
          { key: "status", header: "Status", render: (row) => <StatusCell status={row.status} /> }
        ]}
        rows={chartRows}
        empty="Charts and breakdowns will appear after records are available."
      />
    </div>
  );
}
