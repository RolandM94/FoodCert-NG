"use client";

import { PortalShell } from "@/components/layout/portal-shell";
import { NotificationDashboard } from "@/components/ui/notification-dashboard";

export default function Page() {
  return (
    <PortalShell role="super_admin" title="Notifications Dashboard" description="Monitor notification delivery across all channels. Track volumes, success rates, failures, and broadcast performance.">
      <NotificationDashboard />
    </PortalShell>
  );
}
