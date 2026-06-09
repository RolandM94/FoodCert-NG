import { BadgeCheck, CalendarDays, ClipboardCheck, HeartPulse, SearchCheck, Settings2 } from "lucide-react";
import { CertificateScanPanel } from "@/components/ui/certificate-scan-panel";
import { PortalShell } from "@/components/layout/portal-shell";
import { DashboardCard } from "@/components/ui/dashboard-card";
import { FilterBar } from "@/components/ui/filter-bar";
import { Stepper } from "@/components/ui/stepper";
import { DashboardClient } from "@/features/dashboard/dashboard-client";
import type { UserRole } from "@/types/auth";

const certificationSteps = [
  "Profile",
  "NIN",
  "Facility",
  "Payment",
  "Appointment",
  "Declaration",
  "Assessment",
  "Lab",
  "Vaccination",
  "Certificate"
];

const doctorSteps = ["Declaration", "Exam", "Lab", "Vaccination", "Decision", "State"];

const dashboardByRole: Partial<Record<UserRole, "employer" | "facility" | "state" | "federal">> = {
  employer: "employer",
  facility_admin: "facility",
  state_admin: "state",
  federal_admin: "federal",
  super_admin: "federal"
};

function EmptyState({
  title,
  detail,
  icon: Icon = ClipboardCheck
}: {
  title: string;
  detail: string;
  icon?: typeof ClipboardCheck;
}) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-8 text-center shadow-sm">
      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-lg bg-brand-50 text-brand-700">
        <Icon size={22} />
      </div>
      <h3 className="mt-4 text-sm font-bold text-neutral-900">{title}</h3>
      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-neutral-500">{detail}</p>
    </div>
  );
}

export function PortalPage({
  role,
  title,
  description,
  mode = "records"
}: {
  role: UserRole;
  title: string;
  description: string;
  mode?: "dashboard" | "records" | "workflow" | "certificate" | "form" | "scanner";
}) {
  const dashboardKind = dashboardByRole[role];

  return (
    <PortalShell role={role} title={title} description={description}>
      {mode === "dashboard" && dashboardKind ? <DashboardClient kind={dashboardKind} /> : null}
      {mode === "dashboard" && !dashboardKind ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <DashboardCard label="Open tasks" value={0} icon={ClipboardCheck} />
          <DashboardCard label="Appointments" value={0} icon={CalendarDays} />
          <DashboardCard label="Certificates" value={0} icon={BadgeCheck} />
          <DashboardCard label="Alerts" value={0} icon={HeartPulse} />
        </div>
      ) : null}
      {mode === "workflow" ? (
        <div className="grid gap-6">
          <Stepper steps={role === "doctor" ? doctorSteps : certificationSteps} current={role === "doctor" ? 2 : 4} />
          <EmptyState
            title="Workflow queue is ready"
            detail="Live workflow records will appear here once assignments, appointments, assessments, or review tasks are created."
          />
        </div>
      ) : null}
      {mode === "certificate" ? (
        <div className="grid gap-6">
          <EmptyState
            title="No certificate records yet"
            detail="Certificates, validation requests, and verification records will appear here after medical assessment and State review workflows begin."
            icon={BadgeCheck}
          />
        </div>
      ) : null}
      {mode === "form" ? (
        <EmptyState
          title="Form workflow is ready"
          detail="This page is reserved for a configured workflow form. Fields and submit actions will appear here when the related API workflow is connected."
          icon={Settings2}
        />
      ) : null}
      {mode === "scanner" ? <CertificateScanPanel /> : null}
      {mode === "records" ? (
        <div className="grid gap-5">
          <FilterBar />
          <EmptyState
            title="No records found"
            detail="Records matching this page will appear here when connected workflow data is available."
            icon={SearchCheck}
          />
        </div>
      ) : null}
    </PortalShell>
  );
}
