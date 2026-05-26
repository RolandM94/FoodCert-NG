"use client";

import { PortalShell } from "@/components/layout/portal-shell";
import { ReconciliationWorkspace } from "@/components/payments/reconciliation-workspace";

export default function Page() {
  return (
    <PortalShell role="federal_admin" title="Provider performance" description="Monitor payment provider reconciliation quality and unresolved mismatch volumes.">
      <ReconciliationWorkspace scope="federal" />
    </PortalShell>
  );
}
