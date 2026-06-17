import Link from "next/link";

import { PortalShell } from "@/components/layout/portal-shell";

const GROUPS = [
  {
    title: "Overview",
    description: "Review active policy version status, draft activity, approvals, and quick actions.",
    href: "/federal/standards-policy/overview",
  },
  {
    title: "Policy Governance",
    description: "Manage policy versions, approval workflows, change history, and governance documents.",
    href: "/federal/standards-policy/policy-governance/overview",
  },
  {
    title: "Assessment Standards",
    description: "Configure handler categories, establishments, tests, examinations, vaccination, and return-to-work rules.",
    href: "/federal/standards-policy/assessment-standards/handler-categories",
  },
  {
    title: "Certification & Facilities",
    description: "Configure certificate standards, facility requirements, QR verification, and validity rules.",
    href: "/federal/standards-policy/certification-facilities/certificate-standards",
  },
  {
    title: "Reporting & M&E Standards",
    description: "Build reporting forms, maintain reporting templates, and configure national monitoring indicators.",
    href: "/federal/standards-policy/reporting-me/reporting-templates",
  },
  {
    title: "Documents & Circulars",
    description: "Upload and publish national guidelines, SOPs, circulars, FAQs, and technical memos.",
    href: "/federal/standards-policy/policy-governance/documents",
  },
];

export default function StandardsPolicyLandingPage() {
  return (
    <PortalShell
      role="federal_admin"
      title="Standards & Policy"
      description="Choose a policy administration workspace to configure national standards."
    >
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {GROUPS.map((group) => (
          <article key={group.href} className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
            <h2 className="text-base font-bold text-neutral-900">{group.title}</h2>
            <p className="mt-2 min-h-16 text-sm leading-6 text-neutral-600">{group.description}</p>
            <Link
              href={group.href}
              className="mt-4 inline-flex h-10 items-center rounded-md bg-brand-600 px-4 text-sm font-semibold text-white hover:bg-brand-700"
            >
              Open
            </Link>
          </article>
        ))}
      </section>
    </PortalShell>
  );
}
