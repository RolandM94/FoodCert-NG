"use client";

import { usePathname } from "next/navigation";

import {
  StandardsPolicyWorkspaceLayout,
  type StandardsPolicySidebarItem,
} from "@/features/standards/standards-policy-workspace-layout";

type StandardsPolicyWorkspace = "policy-governance" | "assessment-standards" | "certification-facilities" | "reporting-me";

const BASE = "/federal/standards-policy";

const WORKSPACES: Record<
  StandardsPolicyWorkspace,
  {
    title: string;
    description: string;
    items: StandardsPolicySidebarItem[];
  }
> = {
  "policy-governance": {
    title: "Policy Governance",
    description: "Manage national policy versions, approvals, documents, and lifecycle governance.",
    items: [
      { label: "Overview", href: `${BASE}/policy-governance/overview` },
      { label: "Policy Versions", href: `${BASE}/policy-governance/policy-versions` },
      { label: "Approval Queue", href: `${BASE}/policy-governance/approval-queue` },
      { label: "Change History", href: `${BASE}/policy-governance/change-history` },
      { label: "Documents", href: `${BASE}/policy-governance/documents` },
    ],
  },
  "assessment-standards": {
    title: "Assessment Standards",
    description: "Configure categories, medical tests, examinations, vaccinations, and return-to-work rules.",
    items: [
      { label: "Handler Categories", href: `${BASE}/assessment-standards/handler-categories` },
      { label: "Establishment Categories", href: `${BASE}/assessment-standards/establishment-categories` },
      { label: "Medical Test Rules", href: `${BASE}/assessment-standards/medical-test-rules` },
      { label: "Physical Examination", href: `${BASE}/assessment-standards/physical-examination` },
      { label: "Vaccination Rules", href: `${BASE}/assessment-standards/vaccination-rules` },
      { label: "Return-to-Work Rules", href: `${BASE}/assessment-standards/return-to-work-rules` },
    ],
  },
  "certification-facilities": {
    title: "Certification & Facilities",
    description: "Configure certificate standards, facility rules, QR verification, and validity policies.",
    items: [
      { label: "Certificate Standards", href: `${BASE}/certification-facilities/certificate-standards` },
      { label: "Facility Requirements", href: `${BASE}/certification-facilities/facility-requirements` },
      { label: "Medical Facility Criteria", href: `${BASE}/certification-facilities/medical-facility-criteria` },
      { label: "QR Verification Rules", href: `${BASE}/certification-facilities/qr-verification-rules` },
      { label: "Certificate Validity Rules", href: `${BASE}/certification-facilities/certificate-validity-rules` },
    ],
  },
  "reporting-me": {
    title: "Reporting & M&E Standards",
    description: "Configure reporting templates and monitoring indicators for national oversight.",
    items: [
      { label: "Reporting Templates", href: `${BASE}/reporting-me/reporting-templates` },
      { label: "M&E Indicators", href: `${BASE}/reporting-me/me-indicators` },
    ],
  },
};

const LEGACY_ROUTE_MAP: Record<string, string> = {
  "/federal/standards": `${BASE}/policy-governance/overview`,
  "/federal/standards/policy-versions": `${BASE}/policy-governance/policy-versions`,
  "/federal/standards/approval-queue": `${BASE}/policy-governance/approval-queue`,
  "/federal/standards/change-history": `${BASE}/policy-governance/change-history`,
  "/federal/standards/documents": `${BASE}/policy-governance/documents`,
  "/federal/standards/food-handler-categories": `${BASE}/assessment-standards/handler-categories`,
  "/federal/standards/establishment-categories": `${BASE}/assessment-standards/establishment-categories`,
  "/federal/standards/medical-test-rules": `${BASE}/assessment-standards/medical-test-rules`,
  "/federal/standards/physical-examination-rules": `${BASE}/assessment-standards/physical-examination`,
  "/federal/standards/vaccination-rules": `${BASE}/assessment-standards/vaccination-rules`,
  "/federal/standards/return-to-work": `${BASE}/assessment-standards/return-to-work-rules`,
  "/federal/standards/certificate-standards": `${BASE}/certification-facilities/certificate-standards`,
  "/federal/standards/facility-requirements": `${BASE}/certification-facilities/facility-requirements`,
  "/federal/standards/state-config-controls": `${BASE}/certification-facilities/medical-facility-criteria`,
  "/federal/standards/certificate-validity": `${BASE}/certification-facilities/certificate-validity-rules`,
  "/federal/standards/reporting-templates": `${BASE}/reporting-me/reporting-templates`,
  "/federal/forms": `${BASE}/reporting-me/form-builder`,
  "/federal/standards/me-indicators": `${BASE}/reporting-me/me-indicators`,
};

function mappedActiveItem(pathname: string, items: StandardsPolicySidebarItem[]) {
  const direct = items.find((item) => pathname === item.href || pathname.startsWith(`${item.href}/`));
  if (direct) return direct.href;

  const legacyPath = Object.keys(LEGACY_ROUTE_MAP)
    .sort((a, b) => b.length - a.length)
    .find((legacy) => pathname === legacy || pathname.startsWith(`${legacy}/`));

  return legacyPath ? LEGACY_ROUTE_MAP[legacyPath] : items[0]?.href;
}

export function StandardsPolicyWorkspaceShell({
  workspace,
  title,
  description,
  children,
}: {
  workspace: StandardsPolicyWorkspace;
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const config = WORKSPACES[workspace];
  const activeHref = mappedActiveItem(pathname, config.items);
  const sidebarItems = config.items.map((item) => ({ ...item, href: item.href }));

  if (activeHref && !sidebarItems.some((item) => item.href === activeHref)) {
    sidebarItems.unshift({ label: "Current Page", href: activeHref });
  }

  return (
    <StandardsPolicyWorkspaceLayout
      title={title}
      description={description}
      breadcrumb={[
        { label: "Standards & Policy", href: BASE },
        { label: config.title, href: config.items[0]?.href ?? BASE },
      ]}
      sidebarItems={sidebarItems}
    >
      {children}
    </StandardsPolicyWorkspaceLayout>
  );
}

export { BASE as STANDARDS_POLICY_BASE, WORKSPACES as STANDARDS_POLICY_WORKSPACES };
