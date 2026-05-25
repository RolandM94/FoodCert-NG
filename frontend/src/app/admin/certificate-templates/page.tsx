"use client";

import { PortalShell } from "@/components/layout/portal-shell";
import { CertificateTemplateEditor } from "@/components/certificates/certificate-template-editor";

export default function Page() {
  return (
    <PortalShell role="super_admin" title="Certificate templates" description="Manage national certificate templates and emergency defaults.">
      <CertificateTemplateEditor scope="national" />
    </PortalShell>
  );
}
