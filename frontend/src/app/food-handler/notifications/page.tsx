"use client";

import { PortalShell } from "@/components/layout/portal-shell";
import { NotificationInbox } from "@/components/ui/notification-inbox";

export default function Page() {
  return (
    <PortalShell role="food_handler" title="Notifications" description="Review certification, vaccination, appointment, and account notifications.">
      <NotificationInbox />
    </PortalShell>
  );
}
