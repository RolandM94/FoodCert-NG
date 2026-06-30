"use client";

import { Suspense } from "react";
import { FormBuilderContent } from "@/features/organizations/forms-tool-layout";
import { EmbeddedAnalyticsActions } from "@/features/reports/embedded-analytics-actions";
import { StandardsPolicyWorkspaceShell } from "@/features/standards/standards-policy-workspaces";

const FEDERAL_FORMS_TABS = ["overview", "templates", "assignments", "responses", "reports", "settings"] as const;

function ReportingMEFormBuilderContent() {
  return (
    <StandardsPolicyWorkspaceShell
      workspace="reporting-me"
      title="Form Builder"
      description="Build Federal reporting forms and state reporting templates used by Reporting & M&E standards."
    >
      <EmbeddedAnalyticsActions
        moduleSource="reports"
        addToDashboardHref="/federal/dashboard/worksheet-builder?module=reports"
        openInDashboardBuilderHref="/federal/dashboard/canvas-builder?module=reports"
      />
      <section className="mb-5 rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
        <p className="text-xs font-bold uppercase tracking-wide text-brand-700">Reporting & M&E Standards</p>
        <h2 className="mt-2 text-lg font-bold text-neutral-950">Federal reporting template builder</h2>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-neutral-600">
          Use the Forms Tool to design state reporting templates, Federal M&E data collection forms, policy compliance surveys, and cross-state monitoring forms.
        </p>
      </section>
      <FormBuilderContent
        accountScope="federal"
        basePath="/federal/standards-policy/reporting-me/form-builder"
        visibleTabs={[...FEDERAL_FORMS_TABS]}
      />
    </StandardsPolicyWorkspaceShell>
  );
}

export default function ReportingMEFormBuilderPage() {
  return (
    <Suspense fallback={null}>
      <ReportingMEFormBuilderContent />
    </Suspense>
  );
}
