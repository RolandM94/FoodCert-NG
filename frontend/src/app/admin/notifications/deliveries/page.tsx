"use client";

import { PortalShell } from "@/components/layout/portal-shell";
import { DeliveryLogTable } from "@/components/ui/delivery-log-table";

export default function Page() {
  return (
    <PortalShell role="super_admin" title="Delivery Logs" description="Track notification delivery status across all channels. Retry failed deliveries and monitor provider performance.">
      <DeliveryLogTable />
    </PortalShell>
  );
}
