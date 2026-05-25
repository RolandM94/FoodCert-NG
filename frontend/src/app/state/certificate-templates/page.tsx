"use client";

import { PortalShell } from "@/components/layout/portal-shell";
import { CertificateTemplateEditor } from "@/components/certificates/certificate-template-editor";

export default function Page() {
  return (
    <PortalShell role="state_admin" title="Certificate templates" description="Manage state certificate branding and signatory defaults where national policy permits overrides.">
      <CertificateTemplateEditor scope="state" />
    </PortalShell>
  );
}
