"use client";

import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  createFacilityRequirement,
  updateFacilityRequirement,
} from "@/lib/api/standards";
import type { FacilityRequirementRule } from "@/types/standards";
import { getApiErrorMessage } from "@/lib/api/client";

interface Props {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  mode: "create" | "edit";
  policyVersionId: string;
  initial?: Partial<FacilityRequirementRule> | null;
}

export function FacilityRequirementFormDrawer({
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
    requirement_name: "",
    requirement_code: "",
    category: "documentation",
    mandatory: true,
    evidence_type: "text",
    renewal_required: false,
    renewal_interval_days: "",
    suspension_trigger: false,
  });

  useEffect(() => {
    if (open && initial) {
      setForm({
        requirement_name: initial.requirement_name ?? "",
        requirement_code: initial.requirement_code ?? "",
        category: initial.category ?? "documentation",
        mandatory: initial.mandatory ?? true,
        evidence_type: initial.evidence_type ?? "text",
        renewal_required: initial.renewal_required ?? false,
        renewal_interval_days:
          initial.renewal_interval_days != null
            ? String(initial.renewal_interval_days)
            : "",
        suspension_trigger: initial.suspension_trigger ?? false,
      });
      setError("");
    } else if (open && !initial) {
      setForm({
        requirement_name: "",
        requirement_code: "",
        category: "documentation",
        mandatory: true,
        evidence_type: "text",
        renewal_required: false,
        renewal_interval_days: "",
        suspension_trigger: false,
      });
      setError("");
    }
  }, [open, initial]);

  const mutation = useMutation({
    mutationFn: async (): Promise<FacilityRequirementRule> => {
      const payload: Partial<FacilityRequirementRule> = {
        policy_version: policyVersionId,
        requirement_name: form.requirement_name,
        requirement_code: form.requirement_code,
        category: form.category as FacilityRequirementRule["category"],
        mandatory: form.mandatory,
        evidence_type: form.evidence_type as FacilityRequirementRule["evidence_type"],
        renewal_required: form.renewal_required,
        renewal_interval_days: form.renewal_required && form.renewal_interval_days
          ? Number(form.renewal_interval_days)
          : null,
        suspension_trigger: form.suspension_trigger,
      };
      if (mode === "edit" && initial?.id) {
        return updateFacilityRequirement(initial.id, payload);
      }
      return createFacilityRequirement(payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["standards-facility-requirements"] });
      onSuccess();
      onClose();
    },
    onError: (err) => {
      setError(getApiErrorMessage(err, "Failed to save facility requirement."));
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

  const title = mode === "create" ? "Add Facility Requirement" : "Edit Facility Requirement";

  return (
    <>
      <div className="fixed inset-0 z-40 bg-black/40" onClick={onClose} />
      <div className="fixed inset-y-0 right-0 z-50 w-full max-w-lg overflow-y-auto border-l border-neutral-200 bg-white shadow-2xl">
        <form onSubmit={handleSubmit} className="flex h-full flex-col">
          <div className="flex items-center justify-between border-b border-neutral-200 px-6 py-4">
            <h2 className="text-lg font-semibold text-neutral-900">{title}</h2>
          </div>

          <div className="flex-1 space-y-4 px-6 py-5">
            {error && (
              <div className="rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">
                {error}
              </div>
            )}

            <label className="block text-sm font-medium text-neutral-700">
              Requirement Name
              <input
                type="text"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                value={form.requirement_name}
                onChange={(e) => update("requirement_name", e.target.value)}
                required
              />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Requirement Code
              <input
                type="text"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                value={form.requirement_code}
                onChange={(e) => update("requirement_code", e.target.value)}
                required
              />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Category
              <select
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-white px-3 text-sm"
                value={form.category}
                onChange={(e) => update("category", e.target.value)}
              >
                <option value="documentation">Documentation</option>
                <option value="staffing">Staffing</option>
                <option value="equipment">Equipment</option>
                <option value="digital_infrastructure">Digital Infrastructure</option>
                <option value="records">Records Management</option>
                <option value="certification">Certificate Capability</option>
                <option value="reaccreditation">Re-accreditation</option>
              </select>
            </label>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-neutral-300"
                checked={form.mandatory}
                onChange={(e) => update("mandatory", e.target.checked)}
              />
              <span className="text-sm text-neutral-700">Mandatory</span>
            </div>

            <label className="block text-sm font-medium text-neutral-700">
              Evidence Type
              <select
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-white px-3 text-sm"
                value={form.evidence_type}
                onChange={(e) => update("evidence_type", e.target.value)}
              >
                <option value="text">Text</option>
                <option value="file">File Upload</option>
                <option value="checklist">Checklist</option>
                <option value="url">URL</option>
                <option value="inspection">Inspection</option>
              </select>
            </label>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-neutral-300"
                checked={form.renewal_required}
                onChange={(e) => update("renewal_required", e.target.checked)}
              />
              <span className="text-sm text-neutral-700">Renewal Required</span>
            </div>

            {form.renewal_required && (
              <label className="block text-sm font-medium text-neutral-700">
                Renewal Interval (days)
                <input
                  type="number"
                  className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                  value={form.renewal_interval_days}
                  onChange={(e) => update("renewal_interval_days", e.target.value)}
                />
              </label>
            )}

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-neutral-300"
                checked={form.suspension_trigger}
                onChange={(e) => update("suspension_trigger", e.target.checked)}
              />
              <span className="text-sm text-neutral-700">Suspension Trigger</span>
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
