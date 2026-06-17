"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createPolicyVersion, clonePolicyVersion, listPolicyVersions } from "@/lib/api/standards";
import { getApiErrorMessage } from "@/lib/api/client";

interface Props {
  onClose: () => void;
  onSuccess: () => void;
}

const STEP_TITLES = ["Basic Information", "Effective Dates", "Clone Existing", "Review"];

export function CreatePolicyVersionForm({ onClose, onSuccess }: Props) {
  const queryClient = useQueryClient();
  const [step, setStep] = useState(1);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [cloneMode, setCloneMode] = useState<"blank" | "clone">("blank");
  const [form, setForm] = useState({
    version_code: "",
    title: "",
    version_type: "major" as "major" | "minor" | "emergency",
    description: "",
    change_summary: "",
    effective_start_date: "",
    effective_end_date: "",
    requires_state_acknowledgement: false,
  });

  const { data: activeVersion } = useQuery({
    queryKey: ["standards-policy-versions", "active"],
    queryFn: () => listPolicyVersions({ status: "active" }),
    select: (versions) => versions[0] ?? null,
  });

  const createMutation = useMutation({
    mutationFn: () => createPolicyVersion(form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["standards-policy-versions"] });
      setSuccess(true);
      onSuccess();
    },
    onError: (err) => {
      setError(getApiErrorMessage(err, "Failed to create policy version."));
    },
  });

  const cloneMutation = useMutation({
    mutationFn: () =>
      clonePolicyVersion(activeVersion!.id, {
        version_code: form.version_code,
        title: form.title,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["standards-policy-versions"] });
      setSuccess(true);
      onSuccess();
    },
    onError: (err) => {
      setError(getApiErrorMessage(err, "Failed to clone policy version."));
    },
  });

  function update(field: string, value: string | boolean) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function handleNext() {
    setError("");
    if (step < 4) {
      setStep(step + 1);
    } else {
      if (cloneMode === "clone" && activeVersion) {
        cloneMutation.mutate();
      } else {
        createMutation.mutate();
      }
    }
  }

  function handleBack() {
    setError("");
    if (step > 1) setStep(step - 1);
  }

  if (success) {
    return (
      <div className="rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
        <p className="text-sm font-medium text-neutral-700">Policy version created successfully</p>
        <div className="mt-4 flex gap-2">
          <button
            type="button"
            className="inline-flex h-10 items-center gap-2 rounded-md px-4 text-sm font-medium border border-neutral-200 bg-white text-neutral-700 hover:bg-neutral-50"
            onClick={onClose}
          >
            Close
          </button>
        </div>
      </div>
    );
  }

  const isSubmitting = createMutation.isPending || cloneMutation.isPending;

  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
      <div className="mb-4 text-sm font-medium text-neutral-700">
        Step {step} of 4 — {STEP_TITLES[step - 1]}
      </div>

      {error && (
        <div className="mb-4 rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">
          {error}
        </div>
      )}

      {step === 1 && (
        <div className="grid gap-4">
          <label className="block text-sm font-medium text-neutral-700">
            Version Code
            <input
              type="text"
              className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
              value={form.version_code}
              onChange={(e) => update("version_code", e.target.value)}
            />
          </label>
          <label className="block text-sm font-medium text-neutral-700">
            Title
            <input
              type="text"
              className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
              value={form.title}
              onChange={(e) => update("title", e.target.value)}
            />
          </label>
          <label className="block text-sm font-medium text-neutral-700">
            Version Type
            <select
              className="mt-1 h-11 w-full rounded border border-neutral-200 bg-white px-3 text-sm"
              value={form.version_type}
              onChange={(e) => update("version_type", e.target.value)}
            >
              <option value="major">Major</option>
              <option value="minor">Minor</option>
              <option value="emergency">Emergency</option>
            </select>
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
            Change Summary
            <textarea
              className="mt-1 min-h-[80px] w-full rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm"
              value={form.change_summary}
              onChange={(e) => update("change_summary", e.target.value)}
            />
          </label>
        </div>
      )}

      {step === 2 && (
        <div className="grid gap-4">
          <label className="block text-sm font-medium text-neutral-700">
            Effective Start Date
            <input
              type="date"
              className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
              value={form.effective_start_date}
              onChange={(e) => update("effective_start_date", e.target.value)}
            />
          </label>
          <label className="block text-sm font-medium text-neutral-700">
            Effective End Date (optional)
            <input
              type="date"
              className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
              value={form.effective_end_date}
              onChange={(e) => update("effective_end_date", e.target.value)}
            />
          </label>
          <label className="flex items-center gap-2 text-sm font-medium text-neutral-700">
            <input
              type="checkbox"
              checked={form.requires_state_acknowledgement}
              onChange={(e) => update("requires_state_acknowledgement", e.target.checked)}
            />
            Requires State Acknowledgement
          </label>
        </div>
      )}

      {step === 3 && (
        <div className="grid gap-3">
          <button
            type="button"
            className={`inline-flex h-10 items-center gap-2 rounded-md px-4 text-sm font-medium ${
              cloneMode === "blank"
                ? "bg-brand-600 text-white hover:bg-brand-700"
                : "border border-neutral-200 bg-white text-neutral-700 hover:bg-neutral-50"
            }`}
            onClick={() => setCloneMode("blank")}
          >
            Start blank
          </button>
          <button
            type="button"
            className={`inline-flex h-10 items-center gap-2 rounded-md px-4 text-sm font-medium ${
              cloneMode === "clone"
                ? "bg-brand-600 text-white hover:bg-brand-700"
                : "border border-neutral-200 bg-white text-neutral-700 hover:bg-neutral-50"
            }`}
            onClick={() => setCloneMode("clone")}
          >
            Clone active policy
          </button>
          {cloneMode === "clone" && (
            <p className="rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm text-neutral-600">
              Rules from the active policy version will be copied into this draft.
            </p>
          )}
        </div>
      )}

      {step === 4 && (
        <div className="grid gap-2 text-sm text-neutral-700">
          <div><span className="font-medium">Version Code:</span> {form.version_code}</div>
          <div><span className="font-medium">Title:</span> {form.title}</div>
          <div><span className="font-medium">Version Type:</span> {form.version_type}</div>
          <div><span className="font-medium">Description:</span> {form.description || "—"}</div>
          <div><span className="font-medium">Change Summary:</span> {form.change_summary || "—"}</div>
          <div><span className="font-medium">Effective Start:</span> {form.effective_start_date || "—"}</div>
          <div><span className="font-medium">Effective End:</span> {form.effective_end_date || "—"}</div>
          <div><span className="font-medium">State Acknowledgement:</span> {form.requires_state_acknowledgement ? "Yes" : "No"}</div>
          <div><span className="font-medium">Mode:</span> {cloneMode === "clone" ? "Clone active policy" : "Start blank"}</div>
        </div>
      )}

      <div className="mt-6 flex items-center justify-between">
        <div className="flex gap-2">
          {step > 1 && (
            <button
              type="button"
              className="inline-flex h-10 items-center gap-2 rounded-md px-4 text-sm font-medium border border-neutral-200 bg-white text-neutral-700 hover:bg-neutral-50"
              onClick={handleBack}
            >
              Back
            </button>
          )}
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            className="inline-flex h-10 items-center gap-2 rounded-md px-4 text-sm font-medium border border-neutral-200 bg-white text-neutral-700 hover:bg-neutral-50"
            onClick={onClose}
          >
            Cancel
          </button>
          <button
            type="button"
            className="inline-flex h-10 items-center gap-2 rounded-md px-4 text-sm font-medium bg-brand-600 text-white hover:bg-brand-700"
            disabled={isSubmitting}
            onClick={handleNext}
          >
            {step < 4 ? "Next" : isSubmitting ? "Creating..." : "Create Draft"}
          </button>
        </div>
      </div>
    </div>
  );
}
