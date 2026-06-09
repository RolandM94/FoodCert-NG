"use client";

import { useState } from "react";
import { Save, X } from "lucide-react";
import type { OrganizationUnit } from "@/types/organizations";

const UNIT_TYPE_OPTIONS = [
  { value: "directorate", label: "Directorate" },
  { value: "department", label: "Department" },
  { value: "unit", label: "Unit" },
  { value: "branch", label: "Branch" },
  { value: "lab_department", label: "Lab Department" },
  { value: "clinical_department", label: "Clinical Department" },
  { value: "records_department", label: "Records Department" },
  { value: "lga_office", label: "LGA Office" },
  { value: "regional_office", label: "Regional Office" },
  { value: "headquarters", label: "Headquarters" },
  { value: "other", label: "Other" },
];

type UnitFormData = {
  name: string;
  unit_type: string;
  parent?: string;
  description: string;
  state?: string;
  lga?: string;
  address: string;
  phone: string;
  email: string;
};

export function OrganizationUnitForm({
  parentOptions,
  initial,
  onSubmit,
  onCancel,
  submitLabel = "Create Unit",
  error,
}: {
  parentOptions: { id: string; name: string }[];
  initial?: OrganizationUnit;
  onSubmit: (data: UnitFormData) => void;
  onCancel: () => void;
  submitLabel?: string;
  error?: string | null;
}) {
  const [form, setForm] = useState<UnitFormData>({
    name: initial?.name ?? "",
    unit_type: initial?.unit_type ?? "unit",
    parent: initial?.parent ?? undefined,
    description: initial?.description ?? "",
    state: initial?.state ?? undefined,
    lga: initial?.lga ?? undefined,
    address: initial?.address ?? "",
    phone: initial?.phone ?? "",
    email: initial?.email ?? "",
  });

  const set = (field: keyof UnitFormData, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <form
      className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(form);
      }}
    >
      <div className="grid gap-4 sm:grid-cols-2">
        <label className="grid gap-1 text-sm font-semibold text-neutral-700">
          Unit name <span className="text-danger-500">*</span>
          <input
            className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3"
            required
            value={form.name}
            onChange={(e) => set("name", e.target.value)}
          />
        </label>

        <label className="grid gap-1 text-sm font-semibold text-neutral-700">
          Unit type <span className="text-danger-500">*</span>
          <select
            className="h-10 rounded border border-neutral-200 bg-white px-3"
            value={form.unit_type}
            onChange={(e) => set("unit_type", e.target.value)}
          >
            {UNIT_TYPE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </label>

        {parentOptions.length > 0 && (
          <label className="grid gap-1 text-sm font-semibold text-neutral-700">
            Parent unit
            <select
              className="h-10 rounded border border-neutral-200 bg-white px-3"
              value={form.parent ?? ""}
              onChange={(e) => set("parent", e.target.value)}
            >
              <option value="">None (top level)</option>
              {parentOptions.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </label>
        )}

        <label className="grid gap-1 text-sm font-semibold text-neutral-700">
          Description
          <input
            className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3"
            value={form.description}
            onChange={(e) => set("description", e.target.value)}
          />
        </label>

        <label className="grid gap-1 text-sm font-semibold text-neutral-700">
          Address
          <input
            className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3"
            value={form.address}
            onChange={(e) => set("address", e.target.value)}
          />
        </label>

        <label className="grid gap-1 text-sm font-semibold text-neutral-700">
          Phone
          <input
            className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3"
            value={form.phone}
            onChange={(e) => set("phone", e.target.value)}
          />
        </label>

        <label className="grid gap-1 text-sm font-semibold text-neutral-700">
          Email
          <input
            className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3"
            type="email"
            value={form.email}
            onChange={(e) => set("email", e.target.value)}
          />
        </label>
      </div>

      {error && (
        <p className="mt-4 rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{error}</p>
      )}

      <div className="mt-5 flex items-center gap-3">
        <button
          type="submit"
          className="inline-flex h-10 items-center gap-2 rounded bg-brand-600 px-4 text-sm font-bold text-white hover:bg-brand-700"
        >
          <Save aria-hidden="true" size={16} />
          {submitLabel}
        </button>
        <button
          type="button"
          className="inline-flex h-10 items-center gap-2 rounded border border-neutral-200 px-4 text-sm font-semibold text-neutral-600 hover:bg-neutral-50"
          onClick={onCancel}
        >
          <X aria-hidden="true" size={16} />
          Cancel
        </button>
      </div>
    </form>
  );
}
