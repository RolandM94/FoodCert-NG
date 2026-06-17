"use client";

import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  createVaccinationRule,
  updateVaccinationRule,
} from "@/lib/api/standards";
import type { VaccinationRule } from "@/types/standards";
import { getApiErrorMessage } from "@/lib/api/client";

interface Props {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  mode: "create" | "edit";
  policyVersionId: string;
  initial?: Partial<VaccinationRule> | null;
}

export function VaccinationRuleFormDrawer({
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
    vaccine_name: "",
    vaccine_code: "",
    required: false,
    validity_months: "",
    grace_period_days: "0",
    evidence_required: false,
    blocks_certification_if_missing: false,
    blocks_certification_if_expired: false,
    requires_doctor_prescription_if_missing: false,
  });
  const [doseSchedule, setDoseSchedule] = useState<Array<{ dose: number; interval_months: number }>>([]);
  const [evidenceStr, setEvidenceStr] = useState("");

  useEffect(() => {
    if (open && initial) {
      setForm({
        vaccine_name: initial.vaccine_name ?? "",
        vaccine_code: initial.vaccine_code ?? "",
        required: initial.required ?? false,
        validity_months: initial.validity_months != null ? String(initial.validity_months) : "",
        grace_period_days: String(initial.grace_period_days ?? 0),
        evidence_required: initial.evidence_required ?? false,
        blocks_certification_if_missing: initial.blocks_certification_if_missing ?? false,
        blocks_certification_if_expired: initial.blocks_certification_if_expired ?? false,
        requires_doctor_prescription_if_missing: initial.requires_doctor_prescription_if_missing ?? false,
      });
      setDoseSchedule(
        Array.isArray(initial.dose_schedule)
          ? initial.dose_schedule.map((d, i) => ({
              dose: (d as Record<string, unknown>).dose as number ?? i + 1,
              interval_months: (d as Record<string, unknown>).interval_months as number ?? 0,
            }))
          : []
      );
      setEvidenceStr(Array.isArray(initial.evidence_fields) ? initial.evidence_fields.join(", ") : "");
      setError("");
    } else if (open && !initial) {
      setForm({
        vaccine_name: "",
        vaccine_code: "",
        required: false,
        validity_months: "",
        grace_period_days: "0",
        evidence_required: false,
        blocks_certification_if_missing: false,
        blocks_certification_if_expired: false,
        requires_doctor_prescription_if_missing: false,
      });
      setDoseSchedule([]);
      setEvidenceStr("");
      setError("");
    }
  }, [open, initial]);

  const mutation = useMutation({
    mutationFn: async (): Promise<VaccinationRule> => {
      const payload = {
        policy_version: policyVersionId,
        vaccine_name: form.vaccine_name,
        vaccine_code: form.vaccine_code,
        required: form.required,
        dose_schedule: doseSchedule,
        validity_months: form.validity_months ? Number(form.validity_months) : null,
        grace_period_days: Number(form.grace_period_days) || 0,
        evidence_required: form.evidence_required,
        evidence_fields: evidenceStr
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
        blocks_certification_if_missing: form.blocks_certification_if_missing,
        blocks_certification_if_expired: form.blocks_certification_if_expired,
        requires_doctor_prescription_if_missing: form.requires_doctor_prescription_if_missing,
      };
      if (mode === "edit" && initial?.id) {
        return updateVaccinationRule(initial.id, payload);
      }
      return createVaccinationRule(payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["standards-vaccination-rules"] });
      onSuccess();
      onClose();
    },
    onError: (err) => {
      setError(getApiErrorMessage(err, "Failed to save vaccination rule."));
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

  const title = mode === "create" ? "Add Vaccine Rule" : "Edit Vaccine Rule";

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
              Vaccine Name
              <input
                type="text"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                value={form.vaccine_name}
                onChange={(e) => update("vaccine_name", e.target.value)}
                required
              />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Vaccine Code
              <input
                type="text"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                value={form.vaccine_code}
                onChange={(e) => update("vaccine_code", e.target.value)}
                required
              />
            </label>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-neutral-300"
                checked={form.required}
                onChange={(e) => update("required", e.target.checked)}
              />
              <span className="text-sm text-neutral-700">Required</span>
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700">Dose Schedule</label>
              <div className="mt-2 space-y-2">
                {doseSchedule.map((dose, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <span className="text-sm font-medium text-neutral-500 w-16">Dose {i + 1}</span>
                    <input
                      type="number"
                      value={dose.interval_months}
                      onChange={(e) => {
                        const next = [...doseSchedule];
                        next[i] = { ...next[i], interval_months: Number(e.target.value) };
                        setDoseSchedule(next);
                      }}
                      placeholder="Interval (months)"
                      className="h-9 w-40 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                    />
                    <span className="text-xs text-neutral-500">months after previous</span>
                    <button
                      type="button"
                      onClick={() => {
                        const next = doseSchedule.filter((_, idx) => idx !== i);
                        setDoseSchedule(next);
                      }}
                      className="text-sm text-danger-600 hover:text-danger-700"
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
              <button
                type="button"
                onClick={() =>
                  setDoseSchedule((prev) => [
                    ...prev,
                    { dose: prev.length + 1, interval_months: 0 },
                  ])
                }
                className="mt-2 inline-flex items-center rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-xs font-medium text-neutral-700 hover:bg-neutral-50"
              >
                Add Dose
              </button>
            </div>

            <label className="block text-sm font-medium text-neutral-700">
              Validity (months)
              <input
                type="number"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                value={form.validity_months}
                onChange={(e) => update("validity_months", e.target.value)}
              />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Grace Period (days)
              <input
                type="number"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                value={form.grace_period_days}
                onChange={(e) => update("grace_period_days", e.target.value)}
              />
            </label>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-neutral-300"
                checked={form.evidence_required}
                onChange={(e) => update("evidence_required", e.target.checked)}
              />
              <span className="text-sm text-neutral-700">Evidence Required</span>
            </div>

            <label className="block text-sm font-medium text-neutral-700">
              Evidence Fields
              <input
                type="text"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                value={evidenceStr}
                onChange={(e) => setEvidenceStr(e.target.value)}
                placeholder="field1, field2, field3"
              />
            </label>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-neutral-300"
                checked={form.blocks_certification_if_missing}
                onChange={(e) => update("blocks_certification_if_missing", e.target.checked)}
              />
              <span className="text-sm text-neutral-700">Blocks Certification if Missing</span>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-neutral-300"
                checked={form.blocks_certification_if_expired}
                onChange={(e) => update("blocks_certification_if_expired", e.target.checked)}
              />
              <span className="text-sm text-neutral-700">Blocks Certification if Expired</span>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-neutral-300"
                checked={form.requires_doctor_prescription_if_missing}
                onChange={(e) => update("requires_doctor_prescription_if_missing", e.target.checked)}
              />
              <span className="text-sm text-neutral-700">Requires Doctor Prescription if Missing</span>
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
