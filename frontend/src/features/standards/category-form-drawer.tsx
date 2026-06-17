"use client";

import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  createFoodHandlerCategory,
  updateFoodHandlerCategory,
  createEstablishmentCategory,
  updateEstablishmentCategory,
} from "@/lib/api/standards";
import type { FoodHandlerCategory, EstablishmentCategory } from "@/types/standards";
import { getApiErrorMessage } from "@/lib/api/client";

interface Props {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  mode: "create" | "edit";
  entityType: "handler" | "establishment";
  policyVersionId: string;
  initial?: Partial<FoodHandlerCategory | EstablishmentCategory> | null;
}

export function CategoryFormDrawer({
  open,
  onClose,
  onSuccess,
  mode,
  entityType,
  policyVersionId,
  initial,
}: Props) {
  const queryClient = useQueryClient();
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    name: "",
    code: "",
    description: "",
    risk_level: "low" as "low" | "medium" | "high",
    certificate_required: false,
    nationally_locked: false,
    allow_state_subcategories: false,
    inspection_required: false,
  });

  useEffect(() => {
    if (open && initial) {
      setForm({
        name: initial.name ?? "",
        code: initial.code ?? "",
        description: initial.description ?? "",
        risk_level: (initial.risk_level as "low" | "medium" | "high") ?? "low",
        certificate_required: (initial as Partial<FoodHandlerCategory>).certificate_required ?? false,
        nationally_locked: (initial as Partial<FoodHandlerCategory>).nationally_locked ?? false,
        allow_state_subcategories: initial.allow_state_subcategories ?? false,
        inspection_required: (initial as Partial<EstablishmentCategory>).inspection_required ?? false,
      });
      setError("");
    } else if (open && !initial) {
      setForm({
        name: "",
        code: "",
        description: "",
        risk_level: "low",
        certificate_required: false,
        nationally_locked: false,
        allow_state_subcategories: false,
        inspection_required: false,
      });
      setError("");
    }
  }, [open, initial]);

  const queryKey =
    entityType === "handler"
      ? ["standards-food-handler-categories"]
      : ["standards-establishment-categories"];

  const mutation = useMutation({
    mutationFn: async (): Promise<FoodHandlerCategory | EstablishmentCategory> => {
      if (entityType === "handler") {
        const payload = {
          policy_version: policyVersionId,
          name: form.name,
          code: form.code,
          description: form.description,
          risk_level: form.risk_level,
          certificate_required: form.certificate_required,
          nationally_locked: form.nationally_locked,
          allow_state_subcategories: form.allow_state_subcategories,
        };
        if (mode === "edit" && initial?.id) {
          return updateFoodHandlerCategory(initial.id, payload);
        }
        return createFoodHandlerCategory(payload);
      }
      const payload = {
        policy_version: policyVersionId,
        name: form.name,
        code: form.code,
        description: form.description,
        risk_level: form.risk_level,
        inspection_required: form.inspection_required,
        allow_state_subcategories: form.allow_state_subcategories,
      };
      if (mode === "edit" && initial?.id) {
        return updateEstablishmentCategory(initial.id, payload);
      }
      return createEstablishmentCategory(payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey });
      onSuccess();
      onClose();
    },
    onError: (err) => {
      setError(getApiErrorMessage(err, "Failed to save category."));
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

  const categoryLabel = entityType === "handler" ? "Food Handler Category" : "Establishment Category";
  const title = mode === "create" ? `Create ${categoryLabel}` : `Edit ${form.name || categoryLabel}`;

  return (
    <>
      <div className="fixed inset-0 z-40 bg-black/40" onClick={onClose} />
      <div className="fixed inset-y-0 right-0 z-50 w-full max-w-lg overflow-y-auto border-l border-neutral-200 bg-white shadow-2xl">
        <form onSubmit={handleSubmit} className="flex h-full flex-col">
          <div className="border-b border-neutral-200 px-6 py-4">
            <h2 className="text-lg font-semibold text-neutral-900">{title}</h2>
          </div>

          <div className="flex-1 space-y-4 px-6 py-4">
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
              Description
              <textarea
                className="mt-1 min-h-[80px] w-full rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm"
                value={form.description}
                onChange={(e) => update("description", e.target.value)}
              />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Risk Level
              <select
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-white px-3 text-sm"
                value={form.risk_level}
                onChange={(e) => update("risk_level", e.target.value)}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </label>

            {entityType === "handler" && (
              <>
                <label className="flex items-center gap-2 text-sm font-medium text-neutral-700">
                  <input
                    type="checkbox"
                    checked={form.certificate_required}
                    onChange={(e) => update("certificate_required", e.target.checked)}
                  />
                  Certificate Required
                </label>
                <label className="flex items-center gap-2 text-sm font-medium text-neutral-700">
                  <input
                    type="checkbox"
                    checked={form.nationally_locked}
                    onChange={(e) => update("nationally_locked", e.target.checked)}
                  />
                  Nationally Locked
                </label>
              </>
            )}

            {entityType === "establishment" && (
              <label className="flex items-center gap-2 text-sm font-medium text-neutral-700">
                <input
                  type="checkbox"
                  checked={form.inspection_required}
                  onChange={(e) => update("inspection_required", e.target.checked)}
                />
                Inspection Required
              </label>
            )}

            <label className="flex items-center gap-2 text-sm font-medium text-neutral-700">
              <input
                type="checkbox"
                checked={form.allow_state_subcategories}
                onChange={(e) => update("allow_state_subcategories", e.target.checked)}
              />
              Allow State Subcategories
            </label>
          </div>

          <div className="flex items-center justify-end gap-2 border-t border-neutral-200 px-6 py-4">
            <button
              type="button"
              className="inline-flex h-10 items-center gap-2 rounded-md px-4 text-sm font-medium border border-neutral-200 bg-white text-neutral-700 hover:bg-neutral-50"
              onClick={onClose}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="inline-flex h-10 items-center gap-2 rounded-md px-4 text-sm font-medium bg-brand-600 text-white hover:bg-brand-700"
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
