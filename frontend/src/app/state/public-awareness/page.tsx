"use client";

import { PortalShell } from "@/components/layout/portal-shell";
import { StatePublicAwarenessManager } from "@/components/ui/state-public-awareness-manager";

export default function StatePublicAwarenessPage() {
  return (
    <PortalShell
      role="state_admin"
      title="Public Awareness"
      description="Create, approve, publish, and archive state public notices and awareness campaigns for regulated audiences."
    >
      <StatePublicAwarenessManager />
    </PortalShell>
  );
}
