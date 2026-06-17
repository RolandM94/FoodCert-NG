"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_GROUPS = [
  {
    label: "Overview",
    items: [{ label: "Overview", href: "/federal/standards" }],
  },
  {
    label: "Policy Governance",
    items: [
      { label: "Policy Versions", href: "/federal/standards/policy-versions" },
      { label: "Approval Queue", href: "/federal/standards/approval-queue" },
      { label: "Change History", href: "/federal/standards/change-history" },
      { label: "Documents", href: "/federal/standards/documents" },
    ],
  },
  {
    label: "Assessment Standards",
    items: [
      { label: "Handler Categories", href: "/federal/standards/food-handler-categories" },
      { label: "Establishment Categories", href: "/federal/standards/establishment-categories" },
      { label: "Medical Test Rules", href: "/federal/standards/medical-test-rules" },
      { label: "Physical Examination", href: "/federal/standards/physical-examination-rules" },
      { label: "Vaccination Rules", href: "/federal/standards/vaccination-rules" },
      { label: "Return-to-Work", href: "/federal/standards/return-to-work" },
    ],
  },
  {
    label: "Certification & Facility Rules",
    items: [
      { label: "Certificate Standards", href: "/federal/standards/certificate-standards" },
      { label: "Validity & Expiry", href: "/federal/standards/certificate-validity" },
      { label: "Facility Requirements", href: "/federal/standards/facility-requirements" },
      { label: "State Controls", href: "/federal/standards/state-config-controls" },
    ],
  },
  {
    label: "Reporting & M&E",
    items: [
      { label: "Reporting Templates", href: "/federal/standards/reporting-templates" },
      { label: "M&E Indicators", href: "/federal/standards/me-indicators" },
    ],
  },
];

export function StandardsNav() {
  const pathname = usePathname();

  return (
    <nav className="overflow-x-auto rounded-lg border border-neutral-200 bg-white shadow-sm" aria-label="Standards sections">
      <div className="flex min-w-max items-stretch gap-2 p-2">
        {NAV_GROUPS.map((group) => {
          const isGroupActive = group.items.some((item) => pathname === item.href);
          return (
            <section
              key={group.label}
              className={`rounded-md border p-1.5 transition-colors ${
                isGroupActive ? "border-brand-100 bg-brand-50/60" : "border-neutral-100 bg-neutral-50/70"
              }`}
              aria-label={group.label}
            >
              <p className={`px-2 pb-1 text-[11px] font-bold uppercase ${isGroupActive ? "text-brand-700" : "text-neutral-500"}`}>
                {group.label}
              </p>
              <div className="flex gap-0.5">
                {group.items.map((item) => {
                  const isActive = pathname === item.href;
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={`whitespace-nowrap rounded px-2.5 py-1.5 text-xs font-medium transition-colors ${
                        isActive
                          ? "bg-white text-brand-700 shadow-sm ring-1 ring-brand-100"
                          : "text-neutral-600 hover:bg-white hover:text-neutral-900"
                      }`}
                    >
                      {item.label}
                    </Link>
                  );
                })}
              </div>
            </section>
          );
        })}
      </div>
    </nav>
  );
}
