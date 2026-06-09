"use client";

import { Plus, Send, X } from "lucide-react";

const ADDITIONAL_TEST_OPTIONS = [
  ["typhoid", "Typhoid"],
  ["cholera", "Cholera"],
  ["other", "Other"],
] as const;

export type LabTestRequestItem = {
  test_type: string;
  test_name?: string;
};

export function LabTestRequestForm({
  additionalTests,
  includeRequired,
  busy,
  onAdditionalTestsChange,
  onIncludeRequiredChange,
  onSubmit,
}: {
  additionalTests: LabTestRequestItem[];
  includeRequired: boolean;
  busy?: boolean;
  onAdditionalTestsChange: (tests: LabTestRequestItem[]) => void;
  onIncludeRequiredChange: (value: boolean) => void;
  onSubmit: () => void;
}) {
  function updateTest(index: number, patch: Partial<LabTestRequestItem>) {
    onAdditionalTestsChange(additionalTests.map((test, currentIndex) => currentIndex === index ? { ...test, ...patch } : test));
  }

  function removeTest(index: number) {
    onAdditionalTestsChange(additionalTests.filter((_, currentIndex) => currentIndex !== index));
  }

  return (
    <div className="grid gap-3">
      <label className="flex items-start gap-3 rounded border border-brand-200 bg-brand-50 p-3 text-sm font-semibold text-brand-900">
        <input checked={includeRequired} className="mt-1" disabled={busy} type="checkbox" onChange={(event) => onIncludeRequiredChange(event.target.checked)} />
        Include required FoodCert tests: stool microscopy, stool culture and sensitivity, Hepatitis A antigen.
      </label>
      {additionalTests.map((test, index) => (
        <div className="grid gap-2 rounded border border-neutral-200 bg-neutral-50 p-3 sm:grid-cols-[0.8fr_1fr_auto]" key={`${test.test_type}-${index}`}>
          <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" disabled={busy} value={test.test_type} onChange={(event) => updateTest(index, { test_type: event.target.value })}>
            {ADDITIONAL_TEST_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>
          <input className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" disabled={busy} placeholder="Test name or note" value={test.test_name || ""} onChange={(event) => updateTest(index, { test_name: event.target.value })} />
          <button aria-label="Remove test" className="inline-flex h-10 w-10 items-center justify-center rounded border border-neutral-200 text-neutral-700" disabled={busy} type="button" onClick={() => removeTest(index)}>
            <X size={16} />
          </button>
        </div>
      ))}
      <div className="flex flex-wrap gap-2">
        <button className="inline-flex h-10 items-center gap-2 rounded border border-neutral-200 px-4 text-sm font-bold text-neutral-700 disabled:opacity-60" disabled={busy} type="button" onClick={() => onAdditionalTestsChange([...additionalTests, { test_type: "other", test_name: "" }])}>
          <Plus size={16} /> Add test
        </button>
        <button className="inline-flex h-10 items-center gap-2 rounded bg-brand-600 px-4 text-sm font-bold text-white disabled:opacity-60" disabled={busy || (!includeRequired && additionalTests.length === 0)} type="button" onClick={onSubmit}>
          <Send size={16} /> Request tests
        </button>
      </div>
    </div>
  );
}
