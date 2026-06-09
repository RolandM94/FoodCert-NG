"use client";

import { useState } from "react";
import { Save, X } from "lucide-react";
import type { Organization, OrganizationType } from "@/types/organizations";

const ORG_TYPE_OPTIONS: { value: OrganizationType; label: string }[] = [
  { value: "platform_operator", label: "Platform Operator" },
  { value: "federal_ministry", label: "Federal Ministry" },
  { value: "state_ministry", label: "State Ministry" },
  { value: "medical_facility", label: "Medical Facility" },
  { value: "employer", label: "Employer" },
];

type ProfileFormData = {
  name: string;
  organization_type: OrganizationType;
  parent?: string;
  contact_person_name: string;
  address: string;
  phone: string;
  email: string;
  website: string;
};

export function OrganizationProfileForm({
  initial,
  onSubmit,
  onCancel,
  error,
  loading,
}: {
  initial: Organization;
  onSubmit: (data: ProfileFormData) => void;
  onCancel: () => void;
  error?: string | null;
  loading?: boolean;
}) {
  const [form, setForm] = useState<ProfileFormData>({
    name: initial.name ?? "",
    organization_type: initial.organization_type ?? "employer",
    parent: initial.parent ?? undefined,
    contact_person_name: initial.contact_person_name ?? "",
    address: initial.address ?? "",
    phone: initial.phone ?? "",
    email: initial.email ?? "",
    website: initial.website ?? "",
  });

  const set = (field: keyof ProfileFormData, value: string) => {
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
        <label className="grid gap-1 text-sm font-semibold text-neutral-700 sm:col-span-2">
          Organization name <span className="text-danger-500">*</span>
          <input
            className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3"
            required
            value={form.name}
            onChange={(e) => set("name", e.target.value)}
          />
        </label>

        <label className="grid gap-1 text-sm font-semibold text-neutral-700">
          Organization type <span className="text-danger-500">*</span>
          <select
            className="h-10 rounded border border-neutral-200 bg-white px-3"
            value={form.organization_type}
            onChange={(e) => set("organization_type", e.target.value as OrganizationType)}
          >
            {ORG_TYPE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </label>

        <label className="grid gap-1 text-sm font-semibold text-neutral-700">
          Contact person
          <input
            className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3"
            value={form.contact_person_name}
            onChange={(e) => set("contact_person_name", e.target.value)}
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

        <label className="grid gap-1 text-sm font-semibold text-neutral-700">
          Website
          <input
            className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3"
            type="url"
            value={form.website}
            onChange={(e) => set("website", e.target.value)}
            placeholder="https://"
          />
        </label>

        <label className="grid gap-1 text-sm font-semibold text-neutral-700 sm:col-span-2">
          Address
          <input
            className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3"
            value={form.address}
            onChange={(e) => set("address", e.target.value)}
          />
        </label>
      </div>

      {error && (
        <p className="mt-4 rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{error}</p>
      )}

      <div className="mt-5 flex items-center gap-3">
        <button
          type="submit"
          disabled={loading}
          className="inline-flex h-10 items-center gap-2 rounded bg-brand-600 px-4 text-sm font-bold text-white hover:bg-brand-700 disabled:opacity-60"
        >
          <Save aria-hidden="true" size={16} />
          {loading ? "Saving..." : "Save Changes"}
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
