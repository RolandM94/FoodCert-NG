"use client";

import { useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { NotificationTemplateTable } from "@/components/ui/notification-template-table";
import { NotificationTemplateEditor } from "@/components/ui/notification-template-editor";
import type { NotificationTemplate } from "@/types/notifications";

export default function Page() {
  const [editing, setEditing] = useState<NotificationTemplate | "new" | null>(null);

  return (
    <PortalShell role="super_admin" title="Notification Templates" description="Create, edit, approve, and manage notification templates across all channels.">
      <div className="space-y-6">
        {editing === "new" || editing ? (
          <NotificationTemplateEditor
            templateId={editing === "new" ? null : editing.id}
            onClose={() => setEditing(null)}
          />
        ) : null}
        <NotificationTemplateTable
          onCreate={() => setEditing("new")}
          onEdit={(template) => setEditing(template)}
        />
      </div>
    </PortalShell>
  );
}
