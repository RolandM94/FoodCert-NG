"use client";

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, ClipboardCheck, Clock3, FileCheck2, RefreshCw } from "lucide-react";

import { OperationalSnapshot } from "@/components/dashboards/operational-snapshot";
import { PortalShell } from "@/components/layout/portal-shell";
import { AnalyticsWorkspaceHome } from "@/features/reports/analytics-workspace-home";
import { getApiErrorMessage } from "@/lib/api/client";
import { getFederalDashboard } from "@/lib/api/reports";

export default function FederalDashboardPage() {
  const snapshotQuery = useQuery({
    queryKey: ["federal-operational-dashboard"],
    queryFn: getFederalDashboard,
  });

  const cards = useMemo(
    () => {
      const riskRows = (snapshotQuery.data?.charts?.risk_flag_trends_by_state as Array<{ total?: number }> | undefined) ?? [];
      return [
      {
        label: "States adopted",
        value: snapshotQuery.data?.cards.states_adopted_federal_declaration_template,
        icon: ClipboardCheck,
        detail: "States with an adopted declaration template.",
      },
      {
        label: "Latest version",
        value: snapshotQuery.data?.cards.states_using_latest_federal_template_version,
        icon: RefreshCw,
        detail: "States currently aligned to the latest federal declaration version.",
      },
      {
        label: "Pending adoption",
        value: snapshotQuery.data?.cards.states_pending_federal_template_adoption,
        icon: Clock3,
        detail: "States still pending declaration template adoption.",
      },
      {
        label: "Declarations",
        value: snapshotQuery.data?.cards.declarations_submitted_nationally,
        icon: FileCheck2,
        detail: "Total health declarations submitted nationally.",
      },
      {
        label: "Risk flags",
        value: riskRows.reduce((sum, row) => sum + Number(row.total ?? 0), 0),
        icon: AlertTriangle,
        detail: "Total declaration risk flags across all reporting states.",
      },
    ];
    },
    [snapshotQuery.data],
  );

  return (
    <PortalShell
      role="federal_admin"
      title="Dashboard Analytics"
      description="Create national workbooks, compose canvases, and publish dashboards from approved federal datasets."
    >
      <div className="grid gap-6">
        <OperationalSnapshot
          title="Federal Snapshot"
          description="Track declaration rollout and adoption before moving into workbook design and dashboard publishing."
          cards={cards}
          loading={snapshotQuery.isLoading}
          error={snapshotQuery.isError ? getApiErrorMessage(snapshotQuery.error, "Could not load federal dashboard snapshot.") : ""}
        />
        <AnalyticsWorkspaceHome
          role="federal_admin"
          title="Dashboard Analytics"
          description="Build workbooks, create canvases, and publish dashboards for national oversight, standards tracking, and operational reporting."
          reportsHref="/federal/reports"
          templatesHref="/federal/dashboard/templates"
          worksheetBuilderHref="/federal/dashboard/worksheet-builder"
          dashboardBuilderHref="/federal/dashboard/dashboard-builder"
          canvasBuilderHref="/federal/dashboard/canvas-builder"
          publishedBaseHref="/federal/dashboard/published"
          datasetLibraryBaseHref="/federal/dashboard/datasets"
        />
      </div>
    </PortalShell>
  );
}
