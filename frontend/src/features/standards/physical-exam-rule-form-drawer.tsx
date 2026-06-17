"use client";

import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  createPhysicalExaminationRule,
  updatePhysicalExaminationRule,
} from "@/lib/api/standards";
import type { PhysicalExaminationRule } from "@/types/standards";
import { getApiErrorMessage } from "@/lib/api/client";

interface Props {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  mode: "create" | "edit";
  policyVersionId: string;
  initial?: Partial<PhysicalExaminationRule> | null;
}

export function PhysicalExamRuleFormDrawer({
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
    indicator_name: "",
    code: "",
    description: "",
    severity: "low" as "low" | "medium" | "high" | "critical",
    requires_doctor_notes: true,
    blocks_certification: false,
    requires_reexamination: false,
    requires_exclusion: false,
    public_health_escalation: false,
  });

  useEffect(() => {
    if (open && initial) {
      setForm({
        indicator_name: initial.indicator_name ?? "",
        code: initial.code ?? "",
        description: initial.description ?? "",
        severity: (initial.severity as "low" | "medium" | "high" | "critical") ?? "low",
        requires_doctor_notes: initial.requires_doctor_notes ?? true,
        blocks_certification: initial.blocks_certification ?? false,
        requires_reexamination: initial.requires_reexamination ?? false,
        requires_exclusion: initial.requires_exclusion ?? false,
        public_health_escalation: initial.public_health_escalation ?? false,
      });
      setError("");
    } else if (open && !initial) {
      setForm({
        indicator_name: "",
        code: "",
        description: "",
        severity: "low",
        requires_doctor_notes: true,
        blocks_certification: false,
        requires_reexamination: false,
        requires_exclusion: false,
        public_health_escalation: false,
      });
      setError("");
    }
  }, [open, initial]);

  const mutation = useMutation({
    mutationFn: async (): Promise<PhysicalExaminationRule> => {
      const payload = {
        policy_version: policyVersionId,
        indicator_name: form.indicator_name,
        code: form.code,
        description: form.description,
        severity: form.severity,
        requires_doctor_notes: form.requires_doctor_notes,
        blocks_certification: form.blocks_certification,
        requires_reexamination: form.requires_reexamination,
        requires_exclusion: form.requires_exclusion,
        public_health_escalation: form.public_health_escalation,
      };
      if (mode === "edit" && initial?.id) {
        return updatePhysicalExaminationRule(initial.id, payload);
      }
      return createPhysicalExaminationRule(payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["standards-physical-exam-rules"] });
      onSuccess();
      onClose();
    },
    onError: (err) => {
      setError(getApiErrorMessage(err, "Failed to save examination indicator."));
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

  const title = mode === "create" ? "Add Examination Indicator" : "Edit Examination Indicator";

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
              Indicator Name
              <input
                type="text"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                value={form.indicator_name}
                onChange={(e) => update("indicator_name", e.target.value)}
                required
              />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Code
              <input
                type="text"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                value={form.code}
                onChange={(e) => update("code", e.target.value)}
                required
              />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Description
              <textarea
                className="mt-1 min-h-[80px] w-full rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm"
                value={form.description}
                onChange={(e) => update("description", e.target.value)}
              />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Severity
              <select
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-white px-3 text-sm"
                value={form.severity}
                onChange={(e) => update("severity", e.target.value)}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </label>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-neutral-300"
                checked={form.requires_doctor_notes}
                onChange={(e) => update("requires_doctor_notes", e.target.checked)}
              />
              <span className="text-sm text-neutral-700">Requires Doctor Notes</span>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-neutral-300"
                checked={form.blocks_certification}
                onChange={(e) => update("blocks_certification", e.target.checked)}
              />
              <span className="text-sm text-neutral-700">Blocks Certification</span>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-neutral-300"
                checked={form.requires_reexamination}
                onChange={(e) => update("requires_reexamination", e.target.checked)}
              />
              <span className="text-sm text-neutral-700">Requires Re-examination</span>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-neutral-300"
                checked={form.requires_exclusion}
                onChange={(e) => update("requires_exclusion", e.target.checked)}
              />
              <span className="text-sm text-neutral-700">Requires Exclusion</span>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-neutral-300"
                checked={form.public_health_escalation}
                onChange={(e) => update("public_health_escalation", e.target.checked)}
              />
              <span className="text-sm text-neutral-700">Public Health Escalation</span>
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
