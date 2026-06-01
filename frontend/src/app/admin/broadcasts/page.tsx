"use client";

import { PortalShell } from "@/components/layout/portal-shell";
import { BroadcastManager } from "@/components/ui/broadcast-manager";

export default function Page() {
  return (
    <PortalShell role="super_admin" title="Broadcast Messaging" description="Create and send broadcast messages to user groups across the platform. Estimate audiences, submit for approval, and track delivery.">
      <BroadcastManager />
    </PortalShell>
  );
}
