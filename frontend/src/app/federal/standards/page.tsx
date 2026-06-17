"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { StandardsPolicyWorkspaceShell } from "@/features/standards/standards-policy-workspaces";
import { listPolicyVersions } from "@/lib/api/standards";

export default function Page() {
  const versionsQuery = useQuery({
    queryKey: ["standards-policy-versions"],
    queryFn: () => listPolicyVersions(),
  });

  const versions = versionsQuery.data ?? [];
  const activeVersion = versions.find((v) => v.status === "active");
  const draftCount = versions.filter((v) => v.status === "draft").length;
  const pendingCount = versions.filter((v) => v.status === "under_review").length;

  return (
    <StandardsPolicyWorkspaceShell workspace="policy-governance"
      title="Standards & Policy Configuration"
      description="Configure and manage national food handler assessment standards."
    >
      <div className="grid gap-5">
        {versionsQuery.isLoading ? (
          <p className="text-sm text-neutral-500">Loading standards overview...</p>
        ) : null}

        {!versionsQuery.isLoading && !activeVersion ? (
          <div className="rounded border border-warning-100 bg-warning-50 p-4 text-sm text-warning-700">
            No active policy version found. Create and publish a policy version to activate national standards.
          </div>
        ) : null}

        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <p className="text-sm text-neutral-500">Active Policy Version</p>
            {activeVersion ? (
              <>
                <p className="mt-1 text-2xl font-bold text-neutral-900">{activeVersion.version_code}</p>
                <p className="mt-0.5 text-sm text-neutral-600">{activeVersion.title}</p>
                <span className="mt-2 inline-block rounded bg-brand-50 px-2 py-0.5 text-xs font-bold text-brand-700">
                  {activeVersion.status}
                </span>
              </>
            ) : (
              <p className="mt-1 text-2xl font-bold text-neutral-900">--</p>
            )}
          </div>

          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <p className="text-sm text-neutral-500">Draft Versions</p>
            <p className="mt-1 text-2xl font-bold text-neutral-900">{draftCount}</p>
          </div>

          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <p className="text-sm text-neutral-500">Pending Approval</p>
            <p className="mt-1 text-2xl font-bold text-neutral-900">{pendingCount}</p>
          </div>

          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <p className="text-sm text-neutral-500">Active Medical Test Rules</p>
            <p className="mt-1 text-2xl font-bold text-neutral-900">
              {activeVersion?.medical_test_rule_count ?? 0}
            </p>
          </div>

          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <p className="text-sm text-neutral-500">Active Vaccination Rules</p>
            <p className="mt-1 text-2xl font-bold text-neutral-900">
              {activeVersion?.vaccination_rule_count ?? 0}
            </p>
          </div>

          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <p className="text-sm text-neutral-500">States Acknowledged</p>
            <p className="mt-1 text-2xl font-bold text-neutral-900">
              {activeVersion?.acknowledgement_count ?? 0}
            </p>
          </div>
        </section>

        <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <h2 className="text-base font-bold text-neutral-900">Quick Actions</h2>
          <div className="mt-3 flex flex-wrap gap-3">
            <Link
              href="/federal/standards-policy/policy-governance/policy-versions"
              className="inline-flex items-center gap-2 rounded-md border border-neutral-200 bg-white px-4 py-2.5 text-sm font-medium text-neutral-700 hover:bg-neutral-50"
            >
              Create New Policy Version
            </Link>
            <Link
              href="/federal/standards-policy/assessment-standards/medical-test-rules"
              className="inline-flex items-center gap-2 rounded-md border border-neutral-200 bg-white px-4 py-2.5 text-sm font-medium text-neutral-700 hover:bg-neutral-50"
            >
              Add Medical Test Rule
            </Link>
            <Link
              href="/federal/standards-policy/assessment-standards/vaccination-rules"
              className="inline-flex items-center gap-2 rounded-md border border-neutral-200 bg-white px-4 py-2.5 text-sm font-medium text-neutral-700 hover:bg-neutral-50"
            >
              Add Vaccination Rule
            </Link>
            <Link
              href="/federal/standards-policy/policy-governance/documents"
              className="inline-flex items-center gap-2 rounded-md border border-neutral-200 bg-white px-4 py-2.5 text-sm font-medium text-neutral-700 hover:bg-neutral-50"
            >
              Upload Document
            </Link>
            <Link
              href="/federal/standards-policy/policy-governance/approval-queue"
              className="inline-flex items-center gap-2 rounded-md border border-neutral-200 bg-white px-4 py-2.5 text-sm font-medium text-neutral-700 hover:bg-neutral-50"
            >
              View Approval Queue
            </Link>
            <Link
              href="/federal/standards-policy/policy-governance/change-history"
              className="inline-flex items-center gap-2 rounded-md border border-neutral-200 bg-white px-4 py-2.5 text-sm font-medium text-neutral-700 hover:bg-neutral-50"
            >
              View Change History
            </Link>
          </div>
        </section>
      </div>
    </StandardsPolicyWorkspaceShell>
  );
}
