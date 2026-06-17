"use client";

import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createMedicalTestRule, updateMedicalTestRule } from "@/lib/api/standards";
import type { MedicalTestRule } from "@/types/standards";
import { getApiErrorMessage } from "@/lib/api/client";

interface Props {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  mode: "create" | "edit";
  policyVersionId: string;
  initial?: Partial<MedicalTestRule> | null;
}

export function MedicalTestRuleFormDrawer({
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
    name: "",
    code: "",
    test_type: "laboratory" as "laboratory" | "clinical" | "physical" | "other",
    rule_type: "mandatory" as "mandatory" | "conditional" | "optional" | "emergency",
    result_type: "" as "positive_negative" | "normal_abnormal" | "numeric" | "text" | "file" | "",
    blocks_certification: false,
    requires_attachment: false,
    requires_doctor_validation: true,
    requires_lab_validation: false,
    validity_days: "" as string,
  });
  const [acceptedStr, setAcceptedStr] = useState("");
  const [blockingStr, setBlockingStr] = useState("");
  const [categoriesStr, setCategoriesStr] = useState("");

  useEffect(() => {
    if (open && initial) {
      setForm({
        name: initial.name ?? "",
        code: initial.code ?? "",
        test_type: (initial.test_type as "laboratory" | "clinical" | "physical" | "other") ?? "laboratory",
        rule_type: (initial.rule_type as "mandatory" | "conditional" | "optional" | "emergency") ?? "mandatory",
        result_type: (initial.result_type as "positive_negative" | "normal_abnormal" | "numeric" | "text" | "file" | "") ?? "",
        blocks_certification: initial.blocks_certification ?? false,
        requires_attachment: initial.requires_attachment ?? false,
        requires_doctor_validation: initial.requires_doctor_validation ?? true,
        requires_lab_validation: initial.requires_lab_validation ?? false,
        validity_days: initial.validity_days != null ? String(initial.validity_days) : "",
      });
      setAcceptedStr(initial.accepted_values?.join(", ") ?? "");
      setBlockingStr(initial.blocking_values?.join(", ") ?? "");
      setCategoriesStr(initial.applicable_categories?.join(", ") ?? "");
      setError("");
    } else if (open && !initial) {
      setForm({
        name: "",
        code: "",
        test_type: "laboratory",
        rule_type: "mandatory",
        result_type: "",
        blocks_certification: false,
        requires_attachment: false,
        requires_doctor_validation: true,
        requires_lab_validation: false,
        validity_days: "",
      });
      setAcceptedStr("");
      setBlockingStr("");
      setCategoriesStr("");
      setError("");
    }
  }, [open, initial]);

  const mutation = useMutation({
    mutationFn: async (): Promise<MedicalTestRule> => {
      const payload: Partial<MedicalTestRule> = {
        policy_version: policyVersionId,
        name: form.name,
        code: form.code,
        test_type: form.test_type,
        rule_type: form.rule_type,
        result_type: form.result_type,
        accepted_values: acceptedStr.split(",").map((s) => s.trim()).filter(Boolean),
        blocking_values: blockingStr.split(",").map((s) => s.trim()).filter(Boolean),
        blocks_certification: form.blocks_certification,
        requires_attachment: form.requires_attachment,
        requires_doctor_validation: form.requires_doctor_validation,
        requires_lab_validation: form.requires_lab_validation,
        validity_days: form.validity_days ? Number(form.validity_days) : null,
        applicable_categories: categoriesStr.split(",").map((s) => s.trim()).filter(Boolean),
      };
      if (mode === "edit" && initial?.id) {
        return updateMedicalTestRule(initial.id, payload);
      }
      return createMedicalTestRule(payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["standards-medical-test-rules"] });
      onSuccess();
      onClose();
    },
    onError: (err) => {
      setError(getApiErrorMessage(err, "Failed to save medical test rule."));
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

  const title = mode === "create" ? "Add Test Rule" : "Edit Test Rule";

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
              Name
              <input
                type="text"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                value={form.name}
                onChange={(e) => update("name", e.target.value)}
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
              Test Type
              <select
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-white px-3 text-sm"
                value={form.test_type}
                onChange={(e) => update("test_type", e.target.value)}
              >
                <option value="laboratory">Laboratory</option>
                <option value="clinical">Clinical</option>
                <option value="physical">Physical</option>
                <option value="other">Other</option>
              </select>
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Rule Type
              <select
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-white px-3 text-sm"
                value={form.rule_type}
                onChange={(e) => update("rule_type", e.target.value)}
              >
                <option value="mandatory">Mandatory</option>
                <option value="conditional">Conditional</option>
                <option value="optional">Optional</option>
                <option value="emergency">Emergency</option>
              </select>
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Result Type
              <select
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-white px-3 text-sm"
                value={form.result_type}
                onChange={(e) => update("result_type", e.target.value)}
              >
                <option value="">--</option>
                <option value="positive_negative">Positive / Negative</option>
                <option value="normal_abnormal">Normal / Abnormal</option>
                <option value="numeric">Numeric</option>
                <option value="text">Text</option>
                <option value="file">File</option>
              </select>
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Accepted Values
              <input
                type="text"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                placeholder="Comma-separated"
                value={acceptedStr}
                onChange={(e) => setAcceptedStr(e.target.value)}
              />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Blocking Values
              <input
                type="text"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                placeholder="Comma-separated"
                value={blockingStr}
                onChange={(e) => setBlockingStr(e.target.value)}
              />
            </label>

            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-neutral-300"
                checked={form.blocks_certification}
                onChange={(e) => update("blocks_certification", e.target.checked)}
              />
              <span className="text-sm text-neutral-700">Blocks Certification</span>
            </label>

            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-neutral-300"
                checked={form.requires_attachment}
                onChange={(e) => update("requires_attachment", e.target.checked)}
              />
              <span className="text-sm text-neutral-700">Requires Attachment</span>
            </label>

            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-neutral-300"
                checked={form.requires_doctor_validation}
                onChange={(e) => update("requires_doctor_validation", e.target.checked)}
              />
              <span className="text-sm text-neutral-700">Requires Doctor Validation</span>
            </label>

            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-neutral-300"
                checked={form.requires_lab_validation}
                onChange={(e) => update("requires_lab_validation", e.target.checked)}
              />
              <span className="text-sm text-neutral-700">Requires Lab Validation</span>
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Validity Days
              <input
                type="number"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                value={form.validity_days}
                onChange={(e) => update("validity_days", e.target.value)}
              />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Applicable Categories
              <input
                type="text"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                placeholder="Comma-separated UUIDs"
                value={categoriesStr}
                onChange={(e) => setCategoriesStr(e.target.value)}
              />
            </label>
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
