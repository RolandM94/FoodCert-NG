import { PortalShell } from "@/components/layout/portal-shell";
import { AnalyticsDatasetLibrary } from "@/features/reports/analytics-dataset-library";

export default async function StateDatasetLibraryPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <PortalShell
      role="state_admin"
      title="Dataset Library"
      description="Inspect approved state datasets in table form, then move into workbook and dashboard creation."
    >
      <AnalyticsDatasetLibrary
        datasetId={id}
        homeHref="/state/dashboard"
        worksheetBuilderHref="/state/dashboard/worksheet-builder"
      />
    </PortalShell>
  );
}
