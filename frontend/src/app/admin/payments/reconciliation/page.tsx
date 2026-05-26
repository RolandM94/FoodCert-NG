"use client";

import { PortalShell } from "@/components/layout/portal-shell";
import { ReconciliationWorkspace } from "@/components/payments/reconciliation-workspace";

export default function Page() {
  return (
    <PortalShell role="super_admin" title="Payment reconciliation" description="Compare provider records with internal payments, review mismatches, and export finance-safe evidence.">
      <ReconciliationWorkspace scope="admin" />
    </PortalShell>
  );
}
