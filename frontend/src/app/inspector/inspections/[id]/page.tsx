"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, ArrowLeft, BadgeCheck, ClipboardCheck, ShieldAlert, Stethoscope } from "lucide-react";

import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import {
  createFinding,
  fetchComplianceSummary,
  fetchFoodHandlers,
  getFindings,
  getInspection,
  type FoodHandlerBrief
} from "@/lib/api/inspections";

function formatDate(value?: string | null) {
  if (!value) return "Not set";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

function isExcluded(handler: FoodHandlerBrief) {
  return handler.active_illness_status === "excluded" || ["excluded", "temporarily_excluded"].includes(handler.fitness_status);
}

function findingForHandler(findings: Record<string, unknown>[] | undefined, handlerId: string) {
  return findings?.find((finding) => {
    const foodHandler = finding.food_handler;
    const severity = finding.severity;
    const description = String(finding.description || "").toLowerCase();
    return foodHandler === handlerId && severity === "critical" && description.includes("excluded food handler");
  });
}

export default function Page() {
  const params = useParams<{ id: string }>();
  const inspectionId = params.id;
  const queryClient = useQueryClient();

  const inspectionQuery = useQuery({
    queryKey: ["inspection", inspectionId],
    queryFn: () => getInspection(inspectionId),
    enabled: Boolean(inspectionId),
  });

  const summaryQuery = useQuery({
    queryKey: ["inspection-compliance-summary", inspectionId],
    queryFn: () => fetchComplianceSummary(inspectionId),
    enabled: Boolean(inspectionId),
  });

  const handlersQuery = useQuery({
    queryKey: ["inspection-food-handlers", inspectionId],
    queryFn: () => fetchFoodHandlers(inspectionId),
    enabled: Boolean(inspectionId),
  });

  const findingsQuery = useQuery({
    queryKey: ["inspection-findings", inspectionId],
    queryFn: () => getFindings(inspectionId),
    enabled: Boolean(inspectionId),
  });

  const findingMutation = useMutation({
    mutationFn: (handler: FoodHandlerBrief) =>
      createFinding(inspectionId, {
        category: "fitness_exclusion_compliance",
        finding_type: "critical_non_compliance",
        severity: "critical",
        description: "Excluded food handler found handling food.",
        recommended_action:
          "Immediate removal from food handling duties, compliance notice, follow-up inspection, and State escalation if repeated or serious.",
        food_handler: handler.id,
        certificate: handler.certificate_id || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inspection-findings", inspectionId] });
    },
  });

  const inspection = inspectionQuery.data;
  const handlers = handlersQuery.data || [];
  const findings = findingsQuery.data || [];
  const excludedHandlers = handlers.filter(isExcluded);

  return (
    <PortalShell
      role="inspector"
      title="Inspection Detail"
      description="Complete privacy-safe compliance checks, review handler operational flags, record findings, and submit evidence."
    >
      <div className="grid gap-6">
        <Link className="inline-flex w-fit items-center gap-2 text-sm font-bold text-brand-700 hover:text-brand-600" href="/inspector/dashboard">
          <ArrowLeft size={16} />
          Back to dashboard
        </Link>

        {inspectionQuery.isError || handlersQuery.isError ? (
          <div className="rounded-lg bg-danger-50 p-4 text-sm font-semibold text-danger-700">Could not load this inspection workspace.</div>
        ) : null}

        <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div>
              <p className="text-xs font-bold uppercase tracking-wide text-brand-700">Inspection Workspace</p>
              <h2 className="mt-2 text-xl font-bold text-neutral-900">{inspection?.employer_name || "Inspection"}</h2>
              <p className="mt-2 text-sm leading-6 text-neutral-600">
                {inspection?.branch_name || "All branches"} · {formatDate(inspection?.inspection_date)}
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <StatusBadge status={inspection?.status || "draft"} />
              <StatusBadge status={inspection?.enforcement_action || "none"} />
            </div>
          </div>

          <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-lg border border-neutral-100 bg-neutral-50 p-4">
              <div className="flex items-center gap-2 text-brand-700">
                <BadgeCheck size={16} />
                <p className="text-xs font-bold uppercase">Active certificates</p>
              </div>
              <p className="mt-2 text-2xl font-bold text-neutral-900">{Number(summaryQuery.data?.active_certificates || 0)}</p>
            </div>
            <div className="rounded-lg border border-neutral-100 bg-neutral-50 p-4">
              <div className="flex items-center gap-2 text-warning-700">
                <Stethoscope size={16} />
                <p className="text-xs font-bold uppercase">RTW pending</p>
              </div>
              <p className="mt-2 text-2xl font-bold text-neutral-900">{Number(summaryQuery.data?.return_to_work_pending || 0)}</p>
            </div>
            <div className="rounded-lg border border-neutral-100 bg-neutral-50 p-4">
              <div className="flex items-center gap-2 text-danger-700">
                <ShieldAlert size={16} />
                <p className="text-xs font-bold uppercase">Excluded on roster</p>
              </div>
              <p className="mt-2 text-2xl font-bold text-neutral-900">{excludedHandlers.length}</p>
            </div>
            <div className="rounded-lg border border-neutral-100 bg-neutral-50 p-4">
              <div className="flex items-center gap-2 text-neutral-700">
                <ClipboardCheck size={16} />
                <p className="text-xs font-bold uppercase">Findings</p>
              </div>
              <p className="mt-2 text-2xl font-bold text-neutral-900">{findings.length}</p>
            </div>
          </div>
        </section>

        <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
          <div className="flex flex-col gap-2 border-b border-neutral-200 p-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 className="text-base font-bold text-neutral-900">Food Handler Operational Flags</h2>
              <p className="mt-1 text-xs font-semibold text-neutral-500">Inspectors see status signals only. Symptoms and clinical notes stay hidden.</p>
            </div>
            {findingMutation.isError ? (
              <span className="rounded bg-danger-50 px-3 py-2 text-xs font-bold text-danger-700">Could not create finding</span>
            ) : null}
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-neutral-200 text-sm">
              <thead className="bg-neutral-50 text-left text-xs font-bold uppercase tracking-wide text-neutral-500">
                <tr>
                  <th className="px-4 py-3">Food Handler</th>
                  <th className="px-4 py-3">Certificate</th>
                  <th className="px-4 py-3">Fitness</th>
                  <th className="px-4 py-3">Illness Exclusion</th>
                  <th className="px-4 py-3">Return-to-Work</th>
                  <th className="px-4 py-3">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-100">
                {handlers.map((handler) => {
                  const existingFinding = findingForHandler(findings, handler.id);
                  const excluded = isExcluded(handler);
                  return (
                    <tr className={excluded ? "bg-danger-50/40" : "bg-white"} key={handler.id}>
                      <td className="px-4 py-3">
                        <p className="font-bold text-neutral-900">{handler.name}</p>
                        <p className="mt-1 text-xs text-neutral-500">{handler.system_identifier || "No ID"} · {handler.branch_name || "No branch"}</p>
                      </td>
                      <td className="px-4 py-3">
                        <StatusBadge status={handler.certificate_status || "not_issued"} />
                        <p className="mt-1 text-xs text-neutral-500">{handler.certificate_number || "No certificate"} · expires {formatDate(handler.certificate_expiry_date)}</p>
                      </td>
                      <td className="px-4 py-3"><StatusBadge status={handler.fitness_status} /></td>
                      <td className="px-4 py-3">
                        <StatusBadge status={handler.active_illness_status || "none"} />
                        {handler.exclusion_start_date ? <p className="mt-1 text-xs text-neutral-500">Since {formatDate(handler.exclusion_start_date)}</p> : null}
                      </td>
                      <td className="px-4 py-3">
                        <StatusBadge status={handler.return_to_work_status || "not_applicable"} />
                        <p className="mt-1 text-xs text-neutral-500">Earliest {formatDate(handler.earliest_return_date)}</p>
                      </td>
                      <td className="px-4 py-3">
                        {excluded ? (
                          existingFinding ? (
                            <span className="inline-flex items-center gap-1 rounded bg-brand-50 px-2 py-1 text-xs font-bold text-brand-700">
                              <ClipboardCheck size={13} />
                              Finding recorded
                            </span>
                          ) : (
                            <button
                              className="inline-flex min-h-9 items-center gap-2 rounded bg-danger-600 px-3 py-2 text-xs font-bold text-white hover:bg-danger-700 disabled:opacity-60"
                              disabled={findingMutation.isPending}
                              onClick={() => findingMutation.mutate(handler)}
                              type="button"
                            >
                              <AlertTriangle size={14} />
                              Flag critical
                            </button>
                          )
                        ) : (
                          <span className="text-xs font-semibold text-neutral-500">{handler.operational_instruction || "No action required"}</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
                {!handlers.length ? (
                  <tr>
                    <td className="px-4 py-6 text-sm font-semibold text-neutral-500" colSpan={6}>
                      No food handlers are linked to this inspection scope yet.
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </section>

        <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <h2 className="text-base font-bold text-neutral-900">Structured Findings</h2>
          <div className="mt-4 grid gap-3">
            {findings.map((finding) => (
              <div className="rounded border border-neutral-100 bg-neutral-50 p-3" key={String(finding.id)}>
                <div className="flex flex-wrap items-center gap-2">
                  <StatusBadge status={String(finding.severity || "open")} />
                  <StatusBadge status={String(finding.status || "open")} />
                </div>
                <p className="mt-2 text-sm font-bold text-neutral-900">{String(finding.description || "Finding")}</p>
                <p className="mt-1 text-sm leading-6 text-neutral-600">{String(finding.recommended_action || "No recommended action recorded.")}</p>
              </div>
            ))}
            {!findings.length ? <p className="text-sm font-semibold text-neutral-500">No structured findings have been recorded yet.</p> : null}
          </div>
        </section>
      </div>
    </PortalShell>
  );
}
