"use client";

import { PortalShell } from "@/components/layout/portal-shell";
import { NotificationPreferenceForm } from "@/components/ui/notification-preference-form";

export default function Page() {
  return (
    <PortalShell role="food_handler" title="Notification Preferences" description="Choose which notifications you receive and through which channels.">
      <NotificationPreferenceForm />
    </PortalShell>
  );
}
