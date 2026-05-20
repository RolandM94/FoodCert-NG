"use client";

import { useQuery } from "@tanstack/react-query";
import { PortalShell } from "@/components/layout/portal-shell";
import { ComplianceReportBuilder } from "@/components/ui/compliance-report-builder";
import { listEmployers } from "@/lib/api/identity";

export default function Page() {
  const employersQuery = useQuery({
    queryKey: ["employers", "me"],
    queryFn: listEmployers,
  });
  const employer = employersQuery.data?.[0];

  return (
    <PortalShell
      role="employer"
      title="Reports"
      description="Generate compliance, certificate expiry, and vaccination reports with privacy-safe exports."
    >
      <ComplianceReportBuilder employerId={employer?.id} />
    </PortalShell>
  );
}
