"use client";

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";

import { OperationalSnapshot } from "@/components/dashboards/operational-snapshot";
import { PortalShell } from "@/components/layout/portal-shell";
import { AnalyticsWorkspaceHome } from "@/features/reports/analytics-workspace-home";
import { getApiErrorMessage } from "@/lib/api/client";
import { listKpiCards } from "@/lib/api/kpi-cards";

/** Registry codes for the federal snapshot row (order matters). */
const FEDERAL_SNAPSHOT_CARD_CODES = [
  "states_adopted_declaration_template",
  "states_on_latest_template_version",
  "states_pending_template_adoption",
  "declarations_submitted_nationally",
  "declaration_risk_flags_total",
];

export default function FederalDashboardPage() {
  const libraryQuery = useQuery({
    queryKey: ["kpi-card-library"],
    queryFn: () => listKpiCards(),
    staleTime: 300_000,
  });

  const kpiConfigs = useMemo(() => {
    const byCode = new Map((libraryQuery.data ?? []).map((card) => [card.code, card]));
    return FEDERAL_SNAPSHOT_CARD_CODES.map((code) => byCode.get(code)).filter(
      (card): card is NonNullable<typeof card> => Boolean(card),
    );
  }, [libraryQuery.data]);

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
          kpiConfigs={kpiConfigs}
          loading={libraryQuery.isLoading}
          error={libraryQuery.isError ? getApiErrorMessage(libraryQuery.error, "Could not load federal dashboard snapshot.") : ""}
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
