"use client";

import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  createStateConfigControl,
  updateStateConfigControl,
} from "@/lib/api/standards";
import type { StateConfigurationControl } from "@/types/standards";
import { getApiErrorMessage } from "@/lib/api/client";

interface Props {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  mode: "create" | "edit";
  policyVersionId: string;
  initial?: Partial<StateConfigurationControl> | null;
}

export function StateConfigControlFormDrawer({
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
    config_domain: "",
    label: "",
    description: "",
    federal_locked: true,
    state_editable: false,
    requires_federal_approval: false,
  });

  useEffect(() => {
    if (open && initial) {
      setForm({
        config_domain: initial.config_domain ?? "",
        label: initial.label ?? "",
        description: initial.description ?? "",
        federal_locked: initial.federal_locked ?? true,
        state_editable: initial.state_editable ?? false,
        requires_federal_approval: initial.requires_federal_approval ?? false,
      });
      setError("");
    } else if (open && !initial) {
      setForm({
        config_domain: "",
        label: "",
        description: "",
        federal_locked: true,
        state_editable: false,
        requires_federal_approval: false,
      });
      setError("");
    }
  }, [open, initial]);

  const mutation = useMutation({
    mutationFn: async (): Promise<StateConfigurationControl> => {
      const payload = {
        policy_version: policyVersionId,
        config_domain: form.config_domain,
        label: form.label,
        description: form.description,
        federal_locked: form.federal_locked,
        state_editable: form.state_editable,
        requires_federal_approval: form.requires_federal_approval,
      };
      if (mode === "edit" && initial?.id) {
        return updateStateConfigControl(initial.id, payload);
      }
      return createStateConfigControl(payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["standards-state-config-controls"] });
      onSuccess();
      onClose();
    },
    onError: (err) => {
      setError(getApiErrorMessage(err, "Failed to save configuration control."));
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

  const title = mode === "create" ? "Add Configuration Control" : "Edit Configuration Control";

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

            <div>
              <label className="block text-sm font-medium text-neutral-700">
                Configuration Domain
                <input
                  type="text"
                  className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                  value={form.config_domain}
                  onChange={(e) => update("config_domain", e.target.value)}
                  required
                />
              </label>
              <p className="mt-1 text-xs text-neutral-500">
                e.g. medical_test_minimums, vaccination_minimums, handler_categories
              </p>
            </div>

            <label className="block text-sm font-medium text-neutral-700">
              Display Label
              <input
                type="text"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                value={form.label}
                onChange={(e) => update("label", e.target.value)}
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

            <div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-neutral-300"
                  checked={form.federal_locked}
                  onChange={(e) => update("federal_locked", e.target.checked)}
                />
                <span className="text-sm text-neutral-700">Federal Locked</span>
              </div>
              <p className="mt-1 text-xs text-neutral-500">
                When locked, States cannot modify this configuration.
              </p>
            </div>

            <div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-neutral-300"
                  checked={form.state_editable}
                  onChange={(e) => update("state_editable", e.target.checked)}
                />
                <span className="text-sm text-neutral-700">State Editable</span>
              </div>
              <p className="mt-1 text-xs text-neutral-500">
                Allow States to configure within their jurisdiction.
              </p>
            </div>

            <div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-neutral-300"
                  checked={form.requires_federal_approval}
                  onChange={(e) => update("requires_federal_approval", e.target.checked)}
                />
                <span className="text-sm text-neutral-700">Requires Federal Approval</span>
              </div>
              <p className="mt-1 text-xs text-neutral-500">
                State changes require Federal review before activation.
              </p>
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
