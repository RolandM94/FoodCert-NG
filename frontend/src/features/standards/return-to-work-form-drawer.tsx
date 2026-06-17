"use client";

import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  createReturnToWorkRule,
  updateReturnToWorkRule,
} from "@/lib/api/standards";
import type { ReturnToWorkRule } from "@/types/standards";
import { getApiErrorMessage } from "@/lib/api/client";

interface Props {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  mode: "create" | "edit";
  policyVersionId: string;
  initial?: Partial<ReturnToWorkRule> | null;
}

export function ReturnToWorkFormDrawer({
  open,
  onClose,
  onSuccess,
  mode,
  policyVersionId,
  initial,
}: Props) {
  const queryClient = useQueryClient();
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    condition_name: "",
    condition_code: "",
    default_exclusion_hours: "48",
    requires_medical_clearance: false,
    requires_lab_clearance: false,
    negative_samples_required: "",
    sample_interval_hours: "",
    requires_health_authority_approval: false,
    employer_acknowledgement_required: false,
    clearance_document_required: false,
  });

  useEffect(() => {
    if (open && initial) {
      setForm({
        condition_name: initial.condition_name ?? "",
        condition_code: initial.condition_code ?? "",
        default_exclusion_hours: String(initial.default_exclusion_hours ?? 48),
        requires_medical_clearance: initial.requires_medical_clearance ?? false,
        requires_lab_clearance: initial.requires_lab_clearance ?? false,
        negative_samples_required: initial.negative_samples_required != null ? String(initial.negative_samples_required) : "",
        sample_interval_hours: initial.sample_interval_hours != null ? String(initial.sample_interval_hours) : "",
        requires_health_authority_approval: initial.requires_health_authority_approval ?? false,
        employer_acknowledgement_required: initial.employer_acknowledgement_required ?? false,
        clearance_document_required: initial.clearance_document_required ?? false,
      });
      setError("");
    } else if (open && !initial) {
      setForm({
        condition_name: "",
        condition_code: "",
        default_exclusion_hours: "48",
        requires_medical_clearance: false,
        requires_lab_clearance: false,
        negative_samples_required: "",
        sample_interval_hours: "",
        requires_health_authority_approval: false,
        employer_acknowledgement_required: false,
        clearance_document_required: false,
      });
      setError("");
    }
  }, [open, initial]);

  const mutation = useMutation({
    mutationFn: async (): Promise<ReturnToWorkRule> => {
      const payload: Partial<ReturnToWorkRule> = {
        policy_version: policyVersionId,
        condition_name: form.condition_name,
        condition_code: form.condition_code,
        default_exclusion_hours: Number(form.default_exclusion_hours) || 48,
        requires_medical_clearance: form.requires_medical_clearance,
        requires_lab_clearance: form.requires_lab_clearance,
        negative_samples_required: form.negative_samples_required ? Number(form.negative_samples_required) : null,
        sample_interval_hours: form.sample_interval_hours ? Number(form.sample_interval_hours) : null,
        requires_health_authority_approval: form.requires_health_authority_approval,
        employer_acknowledgement_required: form.employer_acknowledgement_required,
        clearance_document_required: form.clearance_document_required,
      };
      if (mode === "edit" && initial?.id) {
        return updateReturnToWorkRule(initial.id, payload);
      }
      return createReturnToWorkRule(payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["standards-return-to-work"] });
      onSuccess();
      onClose();
    },
    onError: (err) => {
      setError(getApiErrorMessage(err, "Failed to save return-to-work rule."));
    },
  });

  function update(field: string, value: string | boolean) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    mutation.mutate();
  }

  if (!open) return null;

  const title = mode === "create" ? "Add Condition Rule" : "Edit Condition Rule";

  return (
    <>
      <div className="fixed inset-0 z-40 bg-black/40" onClick={onClose} />
      <div className="fixed inset-y-0 right-0 z-50 w-full max-w-lg overflow-y-auto border-l border-neutral-200 bg-white shadow-2xl">
        <form onSubmit={handleSubmit} className="flex h-full flex-col">
          <div className="flex items-center justify-between border-b border-neutral-200 px-6 py-4">
            <h2 className="text-lg font-semibold text-neutral-900">{title}</h2>
            <button
              type="button"
              className="text-neutral-400 hover:text-neutral-600"
              onClick={onClose}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>

          <div className="flex-1 space-y-4 px-6 py-5">
            {error && (
              <div className="rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">
                {error}
              </div>
            )}

            <label className="block text-sm font-medium text-neutral-700">
              Condition Name
              <input
                type="text"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                value={form.condition_name}
                onChange={(e) => update("condition_name", e.target.value)}
                required
              />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Condition Code
              <input
                type="text"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                value={form.condition_code}
                onChange={(e) => update("condition_code", e.target.value)}
                required
              />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Default Exclusion Period (hours)
              <input
                type="number"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                value={form.default_exclusion_hours}
                onChange={(e) => update("default_exclusion_hours", e.target.value)}
              />
            </label>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-neutral-300"
                checked={form.requires_medical_clearance}
                onChange={(e) => update("requires_medical_clearance", e.target.checked)}
              />
              <span className="text-sm text-neutral-700">Requires Medical Clearance</span>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-neutral-300"
                checked={form.requires_lab_clearance}
                onChange={(e) => update("requires_lab_clearance", e.target.checked)}
              />
              <span className="text-sm text-neutral-700">Requires Lab Clearance</span>
            </div>

            <label className="block text-sm font-medium text-neutral-700">
              Negative Samples Required
              <input
                type="number"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                value={form.negative_samples_required}
                onChange={(e) => update("negative_samples_required", e.target.value)}
              />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Sample Interval (hours)
              <input
                type="number"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                value={form.sample_interval_hours}
                onChange={(e) => update("sample_interval_hours", e.target.value)}
              />
            </label>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-neutral-300"
                checked={form.requires_health_authority_approval}
                onChange={(e) => update("requires_health_authority_approval", e.target.checked)}
              />
              <span className="text-sm text-neutral-700">Requires Health Authority Approval</span>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-neutral-300"
                checked={form.employer_acknowledgement_required}
                onChange={(e) => update("employer_acknowledgement_required", e.target.checked)}
              />
              <span className="text-sm text-neutral-700">Employer Acknowledgement Required</span>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-neutral-300"
                checked={form.clearance_document_required}
                onChange={(e) => update("clearance_document_required", e.target.checked)}
              />
              <span className="text-sm text-neutral-700">Clearance Document Required</span>
            </div>
          </div>

          <div className="flex justify-end gap-3 border-t border-neutral-200 px-6 py-4">
            <button
              type="button"
              className="inline-flex h-10 items-center rounded-md border border-neutral-200 bg-white px-4 text-sm font-medium text-neutral-700 hover:bg-neutral-50"
              onClick={onClose}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="inline-flex h-10 items-center rounded-md bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
              disabled={mutation.isPending}
            >
              {mutation.isPending ? "Saving..." : "Save"}
            </button>
          </div>
        </form>
      </div>
    </>
  );
}
