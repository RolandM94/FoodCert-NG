"use client";

import { PortalShell } from "@/components/layout/portal-shell";
import { ReconciliationWorkspace } from "@/components/payments/reconciliation-workspace";

export default function Page() {
  return (
    <PortalShell role="federal_admin" title="Federal reconciliation" description="Monitor provider performance and national reconciliation issues without exposing clinical payment context.">
      <ReconciliationWorkspace scope="federal" />
    </PortalShell>
  );
}
