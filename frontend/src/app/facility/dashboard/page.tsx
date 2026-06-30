"use client";

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Activity, CalendarClock, ClipboardList, FileCheck2, FlaskConical, Stethoscope } from "lucide-react";

import { OperationalSnapshot } from "@/components/dashboards/operational-snapshot";
import { PortalShell } from "@/components/layout/portal-shell";
import { getApiErrorMessage } from "@/lib/api/client";
import { getFacilityDashboard } from "@/lib/api/reports";

export default function FacilityDashboardPage() {
  const snapshotQuery = useQuery({
    queryKey: ["facility-operational-dashboard"],
    queryFn: () => getFacilityDashboard(),
  });

  const cards = useMemo(
    () => [
      {
        label: "Today's appointments",
        value: snapshotQuery.data?.cards.appointments_today,
        icon: CalendarClock,
        detail: "Bookings scheduled for today across the facility assessment queue.",
      },
      {
        label: "Pending declarations",
        value: snapshotQuery.data?.cards.pending_declarations,
        icon: ClipboardList,
        detail: "Assessment records still waiting on declaration completion.",
      },
      {
        label: "Assessments in progress",
        value: snapshotQuery.data?.cards.assessments_in_progress,
        icon: Activity,
        detail: "Handlers already in workflow and still moving through clinical steps.",
      },
      {
        label: "Awaiting lab results",
        value: snapshotQuery.data?.cards.lab_requests_pending,
        icon: FlaskConical,
        detail: "Assessments with lab work still pending collection, processing, or submission.",
      },
      {
        label: "Doctor review pending",
        value: snapshotQuery.data?.cards.doctor_decisions_pending,
        icon: Stethoscope,
        detail: "Cases waiting for final doctor decision after supporting steps are complete.",
      },
      {
        label: "Completed assessments",
        value: snapshotQuery.data?.cards.assessments_conducted,
        icon: FileCheck2,
        detail: "Total assessments recorded for the active reporting range.",
      },
    ],
    [snapshotQuery.data],
  );

  return (
    <PortalShell
      role="facility_admin"
      title="Dashboard"
      description="Monitor live facility operations across appointments, assessments, lab workflow, and completed reviews."
    >
      <div className="grid gap-6">
        <OperationalSnapshot
          title="Facility Snapshot"
          description="Review the live appointment and assessment workload across reception, clinical review, and lab processing."
          cards={cards}
          loading={snapshotQuery.isLoading}
          error={snapshotQuery.isError ? getApiErrorMessage(snapshotQuery.error, "Could not load facility dashboard snapshot.") : ""}
        />
      </div>
    </PortalShell>
  );
}
