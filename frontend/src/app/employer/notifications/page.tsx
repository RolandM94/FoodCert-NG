"use client";

import { PortalShell } from "@/components/layout/portal-shell";
import { NotificationInbox } from "@/components/ui/notification-inbox";

export default function Page() {
  return (
    <PortalShell role="employer" title="Notifications" description="Review invite, certification, illness, inspection, compliance, and subscription notices.">
      <NotificationInbox />
    </PortalShell>
  );
}
