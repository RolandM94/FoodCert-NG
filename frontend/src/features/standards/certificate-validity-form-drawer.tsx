"use client";

import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  createCertificateValidityRule,
  updateCertificateValidityRule,
} from "@/lib/api/standards";
import type { CertificateValidityRule } from "@/types/standards";
import { getApiErrorMessage } from "@/lib/api/client";

interface Props {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  mode: "create" | "edit";
  policyVersionId: string;
  initial?: Partial<CertificateValidityRule> | null;
}

export function CertificateValidityFormDrawer({
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
    certificate_validity_days: "365",
    routine_assessment_interval_days: "180",
    renewal_window_days: "30",
    grace_period_days: "0",
    illness_suspension_enabled: true,
    emergency_revalidation_enabled: false,
  });
  const [reminderStr, setReminderStr] = useState("");

  useEffect(() => {
    if (open && initial) {
      setForm({
        certificate_validity_days: String(initial.certificate_validity_days ?? 365),
        routine_assessment_interval_days: String(initial.routine_assessment_interval_days ?? 180),
        renewal_window_days: String(initial.renewal_window_days ?? 30),
        grace_period_days: String(initial.grace_period_days ?? 0),
        illness_suspension_enabled: initial.illness_suspension_enabled ?? true,
        emergency_revalidation_enabled: initial.emergency_revalidation_enabled ?? false,
      });
      setReminderStr(
        Array.isArray(initial.expiry_reminder_days)
          ? initial.expiry_reminder_days.join(", ")
          : ""
      );
      setError("");
    } else if (open && !initial) {
      setForm({
        certificate_validity_days: "365",
        routine_assessment_interval_days: "180",
        renewal_window_days: "30",
        grace_period_days: "0",
        illness_suspension_enabled: true,
        emergency_revalidation_enabled: false,
      });
      setReminderStr("");
      setError("");
    }
  }, [open, initial]);

  const mutation = useMutation({
    mutationFn: async (): Promise<CertificateValidityRule> => {
      const payload: Partial<CertificateValidityRule> = {
        policy_version: policyVersionId,
        certificate_validity_days: Number(form.certificate_validity_days) || 365,
        routine_assessment_interval_days: Number(form.routine_assessment_interval_days) || 180,
        renewal_window_days: Number(form.renewal_window_days) || 30,
        grace_period_days: Number(form.grace_period_days) || 0,
        expiry_reminder_days: reminderStr
          .split(",")
          .map((s) => parseInt(s.trim()))
          .filter((n) => !isNaN(n)),
        illness_suspension_enabled: form.illness_suspension_enabled,
        emergency_revalidation_enabled: form.emergency_revalidation_enabled,
      };
      if (mode === "edit" && initial?.id) {
        return updateCertificateValidityRule(initial.id, payload);
      }
      return createCertificateValidityRule(payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["standards-validity-rules"] });
      onSuccess();
      onClose();
    },
    onError: (err) => {
      setError(getApiErrorMessage(err, "Failed to save validity rules."));
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

  const title = mode === "create" ? "Configure Validity Rules" : "Edit Validity Rules";

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
              Certificate Validity (days)
              <input
                type="number"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                value={form.certificate_validity_days}
                onChange={(e) => update("certificate_validity_days", e.target.value)}
              />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Routine Assessment Interval (days)
              <input
                type="number"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                value={form.routine_assessment_interval_days}
                onChange={(e) => update("routine_assessment_interval_days", e.target.value)}
              />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Renewal Window (days)
              <input
                type="number"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                value={form.renewal_window_days}
                onChange={(e) => update("renewal_window_days", e.target.value)}
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

            <label className="block text-sm font-medium text-neutral-700">
              Expiry Reminder Days
              <input
                type="text"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                value={reminderStr}
                onChange={(e) => setReminderStr(e.target.value)}
                placeholder="30, 14, 7"
              />
            </label>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-neutral-300"
                checked={form.illness_suspension_enabled}
                onChange={(e) => update("illness_suspension_enabled", e.target.checked)}
              />
              <span className="text-sm text-neutral-700">Enable Illness Suspension</span>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-neutral-300"
                checked={form.emergency_revalidation_enabled}
                onChange={(e) => update("emergency_revalidation_enabled", e.target.checked)}
              />
              <span className="text-sm text-neutral-700">Enable Emergency Revalidation</span>
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
