import { PortalShell } from "@/components/layout/portal-shell";
import { AnalyticsDatasetLibrary } from "@/features/reports/analytics-dataset-library";

export default async function FederalDashboardDatasetLibraryPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <PortalShell
      role="federal_admin"
      title="Dataset Library"
      description="Inspect approved federal datasets in table form, then move into workbook and dashboard creation."
    >
      <AnalyticsDatasetLibrary
        datasetId={id}
        homeHref="/federal/dashboard"
        worksheetBuilderHref="/federal/dashboard/worksheet-builder"
      />
    </PortalShell>
  );
}
