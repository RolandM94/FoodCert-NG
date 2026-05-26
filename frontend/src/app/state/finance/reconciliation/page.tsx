"use client";

import { PortalShell } from "@/components/layout/portal-shell";
import { ReconciliationWorkspace } from "@/components/payments/reconciliation-workspace";

export default function Page() {
  return (
    <PortalShell role="state_admin" title="State reconciliation" description="Review provider reconciliation issues scoped to your state and export finance-safe records.">
      <ReconciliationWorkspace scope="state" />
    </PortalShell>
  );
}
