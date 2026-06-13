"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, ArrowLeft, BadgeCheck, ClipboardCheck, ExternalLink, Save, Send, ShieldAlert, Stethoscope } from "lucide-react";
import { useEffect, useState } from "react";

import { KoboFormRenderer, type KoboMediaUploadContext, type KoboMediaUploadStatus, type KoboQuestion, type KoboSchema } from "@/components/forms/kobo-form-renderer";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { saveFormResponseDraft, uploadFormResponseAttachment } from "@/lib/api/forms";
import {
  createFinding,
  fetchComplianceSummary,
  fetchFoodHandlers,
  fetchInspectionFormWorkspace,
  getFindings,
  getInspection,
  submitInspectionFormResponse,
  type FoodHandlerBrief
} from "@/lib/api/inspections";
import { validateKoboResponse, type KoboValidationError } from "@/lib/forms/kobo-validation";

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
  const [formValues, setFormValues] = useState<Record<string, unknown>>({});
  const [formErrors, setFormErrors] = useState<KoboValidationError[]>([]);
  const [mediaStatuses, setMediaStatuses] = useState<Record<string, KoboMediaUploadStatus>>({});

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

  const formWorkspaceQuery = useQuery({
    queryKey: ["inspection-form-workspace", inspectionId],
    queryFn: () => fetchInspectionFormWorkspace(inspectionId),
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
  const formResponse = formWorkspaceQuery.data?.response || null;
  const formAssignment = formWorkspaceQuery.data?.assignment || null;
  const formSchema = (formResponse?.template_schema || {}) as KoboSchema;
  const formLogic = formResponse?.template_logic;
  const formIsReadOnly = ["submitted", "reviewed", "approved"].includes(formResponse?.status || "");

  useEffect(() => {
    if (formResponse?.id) setFormValues(formResponse.response_json || {});
  }, [formResponse?.id, formResponse?.response_json]);

  const saveDraftMutation = useMutation({
    mutationFn: () => {
      if (!formResponse) throw new Error("No inspection form response exists.");
      return saveFormResponseDraft(formResponse.id, { response_json: formValues });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inspection-form-workspace", inspectionId] });
    },
  });

  const submitFormMutation = useMutation({
    mutationFn: () => {
      if (!formResponse) throw new Error("No inspection form response exists.");
      const errors = validateKoboResponse(formSchema, formValues, formLogic);
      setFormErrors(errors);
      if (errors.length) throw new Error("Resolve the highlighted form fields before submitting.");
      return submitInspectionFormResponse(inspectionId, formValues);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inspection", inspectionId] });
      queryClient.invalidateQueries({ queryKey: ["inspection-form-workspace", inspectionId] });
      queryClient.invalidateQueries({ queryKey: ["inspection-findings", inspectionId] });
    },
  });

  async function handleMediaUpload(question: KoboQuestion, file: File, context: KoboMediaUploadContext) {
    if (!formResponse) {
      return { file_name: file.name, file_size: file.size, mime_type: file.type, sync_status: "local_only" };
    }
    setMediaStatuses((current) => ({ ...current, [context.fieldKey]: { state: "uploading" } }));
    try {
      const attachment = await uploadFormResponseAttachment(formResponse.id, {
        question_key: context.questionKey || question.key,
        repeat_group_key: context.repeatGroupKey,
        repeat_item_id: context.repeatItemId,
        file,
      });
      setMediaStatuses((current) => ({ ...current, [context.fieldKey]: { state: "uploaded" } }));
      return attachment;
    } catch (error) {
      setMediaStatuses((current) => ({
        ...current,
        [context.fieldKey]: { state: "failed", message: error instanceof Error ? error.message : "Upload failed" },
      }));
      throw error;
    }
  }

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
          <div className="flex flex-col gap-3 border-b border-neutral-200 p-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 className="text-base font-bold text-neutral-900">Inspection Form</h2>
              <p className="mt-1 text-xs font-semibold text-neutral-500">
                {formAssignment ? `${formAssignment.template_title || "Assigned checklist"} · offline enabled` : "No dynamic checklist has been assigned to this inspection."}
              </p>
            </div>
            {formResponse ? (
              <div className="flex flex-wrap gap-2">
                <Link className="inline-flex h-9 items-center gap-2 rounded border border-neutral-200 px-3 text-xs font-bold text-neutral-700 hover:bg-neutral-50" href={`/forms/${formResponse.id}`}>
                  <ExternalLink size={14} />
                  Offline form
                </Link>
                <button
                  className="inline-flex h-9 items-center gap-2 rounded border border-brand-200 px-3 text-xs font-bold text-brand-700 disabled:opacity-50"
                  disabled={formIsReadOnly || saveDraftMutation.isPending}
                  onClick={() => saveDraftMutation.mutate()}
                  type="button"
                >
                  <Save size={14} />
                  {saveDraftMutation.isPending ? "Saving..." : "Save draft"}
                </button>
                <button
                  className="inline-flex h-9 items-center gap-2 rounded bg-brand-700 px-3 text-xs font-bold text-white disabled:bg-neutral-300"
                  disabled={formIsReadOnly || submitFormMutation.isPending}
                  onClick={() => submitFormMutation.mutate()}
                  type="button"
                >
                  <Send size={14} />
                  {submitFormMutation.isPending ? "Submitting..." : "Submit form"}
                </button>
              </div>
            ) : null}
          </div>
          {formWorkspaceQuery.isLoading ? (
            <p className="p-4 text-sm font-semibold text-neutral-500">Loading inspection form...</p>
          ) : formResponse && formSchema.sections?.length ? (
            <div className="grid gap-3 p-4">
              {saveDraftMutation.isSuccess ? <div className="rounded bg-brand-50 px-3 py-2 text-xs font-bold text-brand-700">Draft saved.</div> : null}
              {submitFormMutation.isError ? (
                <div className="rounded bg-danger-50 px-3 py-2 text-xs font-bold text-danger-700">
                  {submitFormMutation.error instanceof Error ? submitFormMutation.error.message : "Could not submit inspection form."}
                </div>
              ) : null}
              <KoboFormRenderer
                schema={formSchema}
                values={formValues}
                onChange={(values) => {
                  setFormValues(values);
                  if (formErrors.length) setFormErrors(validateKoboResponse(formSchema, values, formLogic));
                }}
                readOnly={formIsReadOnly}
                errors={formErrors}
                logic={formLogic}
                mediaUploadStatuses={mediaStatuses}
                onMediaUpload={handleMediaUpload}
              />
            </div>
          ) : (
            <p className="p-4 text-sm font-semibold text-neutral-500">Ask the State Ministry to assign an inspection checklist template for this inspection.</p>
          )}
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
