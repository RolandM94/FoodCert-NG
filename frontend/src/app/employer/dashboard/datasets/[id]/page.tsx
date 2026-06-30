import { PortalShell } from "@/components/layout/portal-shell";
import { AnalyticsDatasetLibrary } from "@/features/reports/analytics-dataset-library";

export default async function EmployerDashboardDatasetLibraryPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <PortalShell
      role="employer"
      title="Dataset Library"
      description="Inspect approved business datasets in table form, then move into workbook and dashboard creation."
    >
      <AnalyticsDatasetLibrary
        datasetId={id}
        homeHref="/employer/dashboard"
        worksheetBuilderHref="/employer/dashboard/worksheet-builder"
      />
    </PortalShell>
  );
}
