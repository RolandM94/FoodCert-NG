"use client";

import { useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { NotificationProviderTable } from "@/components/ui/notification-provider-table";
import { ProviderConfigForm } from "@/components/ui/provider-config-form";
import type { NotificationProvider } from "@/types/notifications";

export default function Page() {
  const [editing, setEditing] = useState<NotificationProvider | "new" | null>(null);

  return (
    <PortalShell role="super_admin" title="Notification Providers" description="Configure email, SMS, and WhatsApp providers. Set defaults, test connections, and manage provider settings.">
      <div className="space-y-6">
        {editing === "new" || editing ? (
          <ProviderConfigForm
            provider={editing === "new" ? null : editing}
            onClose={() => setEditing(null)}
          />
        ) : null}
        <NotificationProviderTable
          onCreate={() => setEditing("new")}
          onEdit={(provider) => setEditing(provider)}
        />
      </div>
    </PortalShell>
  );
}
