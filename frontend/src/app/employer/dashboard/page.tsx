"use client";

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { BadgeCheck, ClipboardList, FlaskConical, ShieldAlert, TriangleAlert } from "lucide-react";

import { OperationalSnapshot } from "@/components/dashboards/operational-snapshot";
import { PortalShell } from "@/components/layout/portal-shell";
import { AnalyticsWorkspaceHome } from "@/features/reports/analytics-workspace-home";
import { getApiErrorMessage } from "@/lib/api/client";
import { getEmployerDashboard } from "@/lib/api/reports";

export default function EmployerDashboardPage() {
  const snapshotQuery = useQuery({
    queryKey: ["employer-operational-dashboard"],
    queryFn: () => getEmployerDashboard(),
  });

  const cards = useMemo(
    () => [
      {
        label: "Pending declaration",
        value: snapshotQuery.data?.cards.staff_pending_declaration,
        icon: ClipboardList,
        detail: "Staff who still need to complete their health declaration.",
      },
      {
        label: "Pending test",
        value: snapshotQuery.data?.cards.staff_pending_test,
        icon: FlaskConical,
        detail: "Staff still moving through tests, exam review, or vaccination review.",
      },
      {
        label: "Certified staff",
        value: snapshotQuery.data?.cards.certified_staff,
        icon: BadgeCheck,
        detail: "Staff with an active certificate on file.",
      },
      {
        label: "Expired certificates",
        value: snapshotQuery.data?.cards.expired_certificate_staff,
        icon: TriangleAlert,
        detail: "Staff whose latest certificate has already expired.",
      },
      {
        label: "Temporarily unfit",
        value: snapshotQuery.data?.cards.temporarily_unfit_staff,
        icon: ShieldAlert,
        detail: "Staff currently marked temporarily not fit or excluded.",
      },
    ],
    [snapshotQuery.data],
  );

  return (
    <PortalShell
      role="employer"
      title="Dashboard Analytics"
      description="Create employer workbooks, compose canvases, and publish dashboards from your approved business datasets."
    >
      <div className="grid gap-6">
        <OperationalSnapshot
          title="Employer Snapshot"
          description="Keep staff declaration and certification readiness visible while building branch and compliance analytics."
          cards={cards}
          loading={snapshotQuery.isLoading}
          error={snapshotQuery.isError ? getApiErrorMessage(snapshotQuery.error, "Could not load employer dashboard snapshot.") : ""}
        />
        <AnalyticsWorkspaceHome
          role="employer"
          title="Dashboard Analytics"
          description="Analyze certificate status, branch performance, illness activity, and operational trends by choosing the dataset and chart logic you need."
          reportsHref="/employer/reports"
          templatesHref="/employer/dashboard/templates"
          worksheetBuilderHref="/employer/dashboard/worksheet-builder"
          dashboardBuilderHref="/employer/dashboard/dashboard-builder"
          canvasBuilderHref="/employer/dashboard/canvas-builder"
          publishedBaseHref="/employer/dashboard/published"
          datasetLibraryBaseHref="/employer/dashboard/datasets"
        />
      </div>
    </PortalShell>
  );
}
