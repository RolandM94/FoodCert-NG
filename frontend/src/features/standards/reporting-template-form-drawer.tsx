"use client";

import { useEffect, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { createReportingTemplate, updateReportingTemplate } from "@/lib/api/standards";
import { getApiErrorMessage } from "@/lib/api/client";
import type { ReportingFrequency, ReportingTemplate } from "@/types/standards";

interface Props {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  mode: "create" | "edit";
  policyVersionId: string;
  initial?: Partial<ReportingTemplate> | null;
}

const FREQUENCIES: ReportingFrequency[] = ["monthly", "quarterly", "biannual", "annual", "ad_hoc"];

function csv(value: unknown) {
  return Array.isArray(value) ? value.join(", ") : "";
}

function splitCsv(value: string) {
  return value.split(",").map((item) => item.trim()).filter(Boolean);
}

export function ReportingTemplateFormDrawer({ open, onClose, onSuccess, mode, policyVersionId, initial }: Props) {
  const queryClient = useQueryClient();
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    template_name: "",
    template_code: "",
    reporting_frequency: "monthly" as ReportingFrequency,
    deadline_day: "10",
    deadline_grace_days: "5",
    required_sections: "",
    required_indicators: "",
    required_uploads: "",
    minimum_score: "70",
    approval_required: true,
  });

  useEffect(() => {
    if (!open) return;
    setError("");
    if (initial) {
      const deadline = initial.deadline_rule ?? {};
      const scoring = initial.scoring_config ?? {};
      setForm({
        template_name: initial.template_name ?? "",
        template_code: initial.template_code ?? "",
        reporting_frequency: initial.reporting_frequency ?? "monthly",
        deadline_day: String(deadline.day_of_month ?? deadline.day ?? 10),
        deadline_grace_days: String(deadline.grace_days ?? 5),
        required_sections: csv(initial.required_sections),
        required_indicators: csv(initial.required_indicators),
        required_uploads: csv(initial.required_uploads),
        minimum_score: String(scoring.minimum_score ?? 70),
        approval_required: initial.approval_required ?? true,
      });
    } else {
      setForm({
        template_name: "",
        template_code: "",
        reporting_frequency: "monthly",
        deadline_day: "10",
        deadline_grace_days: "5",
        required_sections: "",
        required_indicators: "",
        required_uploads: "",
        minimum_score: "70",
        approval_required: true,
      });
    }
  }, [open, initial]);

  const mutation = useMutation({
    mutationFn: async (): Promise<ReportingTemplate> => {
      const payload: Partial<ReportingTemplate> = {
        policy_version: policyVersionId,
        template_name: form.template_name,
        template_code: form.template_code,
        reporting_frequency: form.reporting_frequency,
        deadline_rule: {
          day_of_month: Number(form.deadline_day) || 1,
          grace_days: Number(form.deadline_grace_days) || 0,
        },
        required_sections: splitCsv(form.required_sections),
        required_indicators: splitCsv(form.required_indicators),
        required_uploads: splitCsv(form.required_uploads),
        scoring_config: {
          minimum_score: Number(form.minimum_score) || 0,
        },
        approval_required: form.approval_required,
      };
      if (mode === "edit" && initial?.id) {
        return updateReportingTemplate(initial.id, payload);
      }
      return createReportingTemplate(payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["standards-reporting-templates"] });
      queryClient.invalidateQueries({ queryKey: ["standards-policy-versions"] });
      onSuccess();
      onClose();
    },
    onError: (err) => setError(getApiErrorMessage(err, "Failed to save reporting template.")),
  });

  function update(field: keyof typeof form, value: string | boolean) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    mutation.mutate();
  }

  if (!open) return null;

  return (
    <>
      <div className="fixed inset-0 z-40 bg-black/40" onClick={onClose} />
      <div className="fixed inset-y-0 right-0 z-50 w-full max-w-xl overflow-y-auto border-l border-neutral-200 bg-white shadow-2xl">
        <form onSubmit={handleSubmit} className="flex min-h-full flex-col">
          <div className="flex items-center justify-between border-b border-neutral-200 px-6 py-4">
            <h2 className="text-lg font-semibold text-neutral-900">{mode === "create" ? "Build Reporting Template" : "Edit Reporting Template"}</h2>
            <button type="button" onClick={onClose} className="text-sm font-semibold text-neutral-500 hover:text-neutral-900">Close</button>
          </div>

          <div className="flex-1 space-y-4 px-6 py-5">
            {error ? <div className="rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{error}</div> : null}

            <label className="block text-sm font-medium text-neutral-700">
              Template Name
              <input required className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" value={form.template_name} onChange={(event) => update("template_name", event.target.value)} />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Template Code
              <input required className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" value={form.template_code} onChange={(event) => update("template_code", event.target.value)} />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Reporting Frequency
              <select className="mt-1 h-11 w-full rounded border border-neutral-200 bg-white px-3 text-sm" value={form.reporting_frequency} onChange={(event) => update("reporting_frequency", event.target.value)}>
                {FREQUENCIES.map((frequency) => <option key={frequency} value={frequency}>{frequency.replace(/_/g, " ")}</option>)}
              </select>
            </label>

            <div className="grid gap-3 sm:grid-cols-2">
              <label className="block text-sm font-medium text-neutral-700">
                Deadline Day
                <input type="number" min="1" max="31" className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" value={form.deadline_day} onChange={(event) => update("deadline_day", event.target.value)} />
              </label>
              <label className="block text-sm font-medium text-neutral-700">
                Grace Days
                <input type="number" min="0" className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" value={form.deadline_grace_days} onChange={(event) => update("deadline_grace_days", event.target.value)} />
              </label>
            </div>

            <label className="block text-sm font-medium text-neutral-700">
              Required Sections
              <textarea className="mt-1 min-h-20 w-full rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm" value={form.required_sections} onChange={(event) => update("required_sections", event.target.value)} placeholder="coverage_summary, state_breakdown, compliance_notes" />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Required Indicator Codes
              <textarea className="mt-1 min-h-20 w-full rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm" value={form.required_indicators} onChange={(event) => update("required_indicators", event.target.value)} placeholder="CERT_COVERAGE, FACILITY_ACCREDITATION" />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Required Uploads
              <textarea className="mt-1 min-h-20 w-full rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm" value={form.required_uploads} onChange={(event) => update("required_uploads", event.target.value)} placeholder="signed_report, supporting_csv" />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Minimum Data Quality Score
              <input type="number" min="0" max="100" className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" value={form.minimum_score} onChange={(event) => update("minimum_score", event.target.value)} />
            </label>

            <label className="flex items-center gap-2 text-sm font-medium text-neutral-700">
              <input type="checkbox" className="h-4 w-4 rounded border-neutral-300" checked={form.approval_required} onChange={(event) => update("approval_required", event.target.checked)} />
              Federal approval required before submission is accepted
            </label>
          </div>

          <div className="flex justify-end gap-3 border-t border-neutral-200 px-6 py-4">
            <button type="button" onClick={onClose} className="rounded border border-neutral-200 px-4 py-2 text-sm font-semibold text-neutral-700 hover:bg-neutral-50">Cancel</button>
            <button disabled={mutation.isPending} type="submit" className="rounded bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-60">
              {mutation.isPending ? "Saving..." : "Save Template"}
            </button>
          </div>
        </form>
      </div>
    </>
  );
}
