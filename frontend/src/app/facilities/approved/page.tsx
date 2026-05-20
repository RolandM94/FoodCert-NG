import { PublicShell } from "@/components/layout/public-shell";
import { ApprovedFacilitiesClient } from "@/features/facilities/approved-facilities-client";

export default function ApprovedFacilitiesPage() {
  return (
    <PublicShell title="Approved medical facilities" description="Find facilities accredited to conduct FoodCert NG medical assessments.">
      <ApprovedFacilitiesClient />
    </PublicShell>
  );
}
