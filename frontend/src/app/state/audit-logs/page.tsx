import { PortalShell } from "@/components/layout/portal-shell";
import { StateAuditLogsPanel } from "@/components/ui/state-audit-logs-panel";

export default function StateAuditLogsPage() {
  return (
    <PortalShell
      role="state_admin"
      title="Audit Logs"
      description="Review state-scoped governance, compliance, reporting, public awareness, and account activity."
    >
      <StateAuditLogsPanel />
    </PortalShell>
  );
}
