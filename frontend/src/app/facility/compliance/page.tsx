"use client";

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Activity, AlertTriangle, BadgeCheck, ClipboardList, Clock3, FlaskConical, ShieldCheck, UsersRound } from "lucide-react";

import { StatusBadge } from "@/components/status/status-badge";
import { DataTable } from "@/components/ui/data-table";
import { DashboardCard } from "@/components/ui/dashboard-card";
import { PortalShell } from "@/components/layout/portal-shell";
import { getApiErrorMessage } from "@/lib/api/client";
import { getCurrentMedicalFacility, getFacilityComplianceDashboard } from "@/lib/api/facilities";

function formatDateTime(value?: string | null) {
  if (!value) return "No activity";
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export default function FacilityCompliancePage() {
  const facilityQuery = useQuery({
    queryKey: ["facility-current-profile", "compliance"],
    queryFn: getCurrentMedicalFacility,
  });

  const complianceQuery = useQuery({
    queryKey: ["facility-compliance-dashboard", facilityQuery.data?.id],
    enabled: Boolean(facilityQuery.data?.id),
    queryFn: () => getFacilityComplianceDashboard(facilityQuery.data!.id),
  });

  const cards = useMemo(
    () => [
      { label: "Total assessments", value: complianceQuery.data?.cards.assessments_conducted, icon: Activity, detail: "All assessments recorded for the facility." },
      { label: "Certificates generated", value: complianceQuery.data?.cards.certificates_issued, icon: BadgeCheck, detail: "Certificates issued from this facility workflow." },
      { label: "Temporary unfit reports", value: complianceQuery.data?.cards.not_fit_reports, icon: AlertTriangle, detail: "Not fit and temporarily not fit outcomes requiring operational follow-up." },
      { label: "Pending lab results", value: complianceQuery.data?.cards.pending_lab_results, icon: FlaskConical, detail: "Samples or results still waiting to move forward." },
      { label: "Overdue doctor reviews", value: complianceQuery.data?.cards.pending_doctor_review, icon: Clock3, detail: "Assessments that still need doctor review or decision." },
      { label: "Pending declaration validations", value: complianceQuery.data?.cards.declarations_requiring_doctor_validation, icon: ClipboardList, detail: "Declarations submitted and waiting for clinical validation." },
      { label: "Accreditation countdown", value: complianceQuery.data?.cards.reaccreditation_countdown_days, icon: ShieldCheck, detail: "Days remaining before accreditation expiry." },
      { label: "Staff activity", value: complianceQuery.data?.sections?.staff_activity?.length ?? 0, icon: UsersRound, detail: "Team members with recent logged actions in the active range." },
    ],
    [complianceQuery.data],
  );

  const warnings = complianceQuery.data?.sections?.warnings ?? [];
  const staffActivity = complianceQuery.data?.sections?.staff_activity ?? [];
  const queueSummary = complianceQuery.data?.sections?.queue_summary ?? [];

  return (
    <PortalShell
      role="facility_admin"
      title="Compliance"
      description="Track operational readiness, pending workflow items, staff activity, and accreditation risk across the facility."
    >
      <div className="grid gap-6">
        {complianceQuery.isError ? (
          <div className="rounded-lg border border-danger-200 bg-danger-50 p-4 text-sm font-semibold text-danger-700">
            {getApiErrorMessage(complianceQuery.error, "Could not load the facility compliance dashboard.")}
          </div>
        ) : null}

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {cards.map((card) => (
            <DashboardCard key={card.label} label={card.label} value={card.value} icon={card.icon} detail={card.detail} />
          ))}
        </section>

        <section className="grid gap-4 xl:grid-cols-[1.4fr_0.9fr]">
          <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-xs font-bold uppercase tracking-wide text-brand-700">Accreditation Health</p>
                <h2 className="mt-2 text-lg font-bold text-neutral-900">
                  {facilityQuery.data?.facility_name || complianceQuery.data?.facility?.facility_name || "Facility"}
                </h2>
              </div>
              <StatusBadge status={String(complianceQuery.data?.cards.accreditation_status || "draft")} />
            </div>
            <div className="mt-4 space-y-3">
              {warnings.length ? warnings.map((warning) => (
                <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800" key={warning.code}>
                  {warning.message}
                </div>
              )) : (
                <div className="rounded-lg border border-brand-100 bg-brand-50 px-4 py-3 text-sm text-brand-800">
                  No accreditation or compliance warnings are active right now.
                </div>
              )}
            </div>
          </div>

          <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Queue Summary</p>
            <div className="mt-4 grid gap-3">
              {queueSummary.map((item, index) => (
                <div className="flex items-center justify-between rounded-lg border border-neutral-100 bg-neutral-50 px-4 py-3" key={`${item.name}-${index}`}>
                  <div>
                    <p className="text-sm font-semibold text-neutral-900">{String(item.name || "Queue item")}</p>
                    <p className="text-xs text-neutral-500">{String(item.href || "")}</p>
                  </div>
                  <span className="rounded-full bg-white px-3 py-1 text-sm font-bold text-neutral-900 shadow-sm">
                    {String(item.count ?? 0)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="grid gap-4 xl:grid-cols-[1.2fr_1fr]">
          <div>
            <DataTable
              columns={[
                {
                  key: "staff",
                  header: "Staff Member",
                  render: (row) => (
                    <div>
                      <p className="font-semibold text-neutral-900">
                        {[row.actor__first_name, row.actor__last_name].filter(Boolean).join(" ") || row.actor__email || "Unknown"}
                      </p>
                      <p className="text-xs text-neutral-500">{row.actor__email || "No email"}</p>
                    </div>
                  ),
                },
                {
                  key: "role",
                  header: "Role",
                  render: (row) => row.actor__facility_staff_profile__role__name || "Facility user",
                },
                {
                  key: "actions",
                  header: "Actions",
                  render: (row) => row.total_actions ?? 0,
                },
                {
                  key: "last",
                  header: "Last Activity",
                  render: (row) => formatDateTime(row.last_activity),
                },
              ]}
              rows={staffActivity}
              empty={complianceQuery.isLoading ? "Loading staff activity..." : "No recent staff activity found for this facility."}
            />
          </div>

          <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Operational Highlights</p>
            <div className="mt-4 grid gap-3">
              <div className="rounded-lg border border-neutral-100 bg-neutral-50 px-4 py-3">
                <p className="text-xs font-bold uppercase text-neutral-500">Pending declarations</p>
                <p className="mt-2 text-2xl font-bold text-neutral-900">{String(complianceQuery.data?.cards.pending_declarations ?? 0)}</p>
              </div>
              <div className="rounded-lg border border-neutral-100 bg-neutral-50 px-4 py-3">
                <p className="text-xs font-bold uppercase text-neutral-500">Lab review backlog</p>
                <p className="mt-2 text-2xl font-bold text-neutral-900">{String(complianceQuery.data?.cards.lab_results_pending_doctor_review ?? 0)}</p>
              </div>
              <div className="rounded-lg border border-neutral-100 bg-neutral-50 px-4 py-3">
                <p className="text-xs font-bold uppercase text-neutral-500">Appointments blocked by declaration</p>
                <p className="mt-2 text-2xl font-bold text-neutral-900">{String(complianceQuery.data?.cards.appointments_blocked_missing_declaration ?? 0)}</p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </PortalShell>
  );
}
