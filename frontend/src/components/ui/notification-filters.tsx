"use client";

import { Check, Search, X } from "lucide-react";
import type { NotificationCategory, NotificationPriority } from "@/types/notifications";

const CATEGORIES: { value: NotificationCategory; label: string }[] = [
  { value: "account", label: "Account" },
  { value: "identity_verification", label: "Identity" },
  { value: "employer_management", label: "Employer" },
  { value: "facility_accreditation", label: "Accreditation" },
  { value: "appointment", label: "Appointment" },
  { value: "assessment", label: "Assessment" },
  { value: "lab_workflow", label: "Lab" },
  { value: "vaccination", label: "Vaccination" },
  { value: "certificate", label: "Certificate" },
  { value: "renewal", label: "Renewal" },
  { value: "payments", label: "Payments" },
  { value: "subscriptions", label: "Subscriptions" },
  { value: "settlements", label: "Settlements" },
  { value: "inspection", label: "Inspection" },
  { value: "enforcement", label: "Enforcement" },
  { value: "reports", label: "Reports" },
  { value: "m_and_e", label: "M&E" },
  { value: "data_quality", label: "Data Quality" },
  { value: "security", label: "Security" },
  { value: "system", label: "System" },
];

const PRIORITIES: { value: NotificationPriority; label: string }[] = [
  { value: "low", label: "Low" },
  { value: "normal", label: "Normal" },
  { value: "high", label: "High" },
  { value: "critical", label: "Critical" },
];

type FilterState = {
  search: string;
  selectedCategories: NotificationCategory[];
  selectedPriorities: NotificationPriority[];
  readFilter: "all" | "unread" | "read";
  archivedFilter: "all" | "active" | "archived";
};

export function NotificationFilters({
  filters,
  onChange,
  onMarkAllRead,
  onClearFilters,
}: {
  filters: FilterState;
  onChange: (filters: FilterState) => void;
  onMarkAllRead?: () => void;
  onClearFilters?: () => void;
}) {
  function toggleCategory(cat: NotificationCategory) {
    const next = filters.selectedCategories.includes(cat)
      ? filters.selectedCategories.filter((c) => c !== cat)
      : [...filters.selectedCategories, cat];
    onChange({ ...filters, selectedCategories: next });
  }

  function togglePriority(pri: NotificationPriority) {
    const next = filters.selectedPriorities.includes(pri)
      ? filters.selectedPriorities.filter((p) => p !== pri)
      : [...filters.selectedPriorities, pri];
    onChange({ ...filters, selectedPriorities: next });
  }

  const hasFilters =
    filters.selectedCategories.length > 0 ||
    filters.selectedPriorities.length > 0 ||
    filters.readFilter !== "all" ||
    filters.archivedFilter !== "all" ||
    filters.search.length > 0;

  return (
    <div className="space-y-3">
      <div className="flex flex-col gap-3 rounded-lg border border-slate-200 bg-white p-3 shadow-sm sm:flex-row sm:items-center">
        <label className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
          <input
            className="h-10 w-full rounded border border-slate-200 bg-slate-50 pl-9 pr-3 text-sm outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2"
            placeholder="Search notifications..."
            type="search"
            value={filters.search}
            onChange={(e) => onChange({ ...filters, search: e.target.value })}
          />
        </label>
        <select
          className="h-10 rounded border border-slate-200 bg-white px-3 text-sm text-slate-700"
          value={filters.readFilter}
          onChange={(e) => onChange({ ...filters, readFilter: e.target.value as FilterState["readFilter"] })}
        >
          <option value="all">All</option>
          <option value="unread">Unread</option>
          <option value="read">Read</option>
        </select>
        <select
          className="h-10 rounded border border-slate-200 bg-white px-3 text-sm text-slate-700"
          value={filters.archivedFilter}
          onChange={(e) => onChange({ ...filters, archivedFilter: e.target.value as FilterState["archivedFilter"] })}
        >
          <option value="all">All</option>
          <option value="active">Active</option>
          <option value="archived">Archived</option>
        </select>
        {onMarkAllRead ? (
          <button
            className="inline-flex h-10 items-center gap-1.5 rounded border border-slate-200 px-3 text-sm font-semibold text-slate-700 hover:bg-emerald-50 hover:text-brand-green"
            onClick={onMarkAllRead}
            type="button"
          >
            <Check aria-hidden="true" size={16} />
            Mark all read
          </button>
        ) : null}
        {hasFilters && onClearFilters ? (
          <button
            className="inline-flex h-10 items-center gap-1.5 rounded border border-slate-200 px-3 text-sm font-semibold text-slate-700 hover:bg-rose-50 hover:text-rose-700"
            onClick={onClearFilters}
            type="button"
          >
            <X aria-hidden="true" size={16} />
            Clear
          </button>
        ) : null}
      </div>

      <div className="flex flex-wrap gap-2">
        <span className="text-xs font-bold uppercase tracking-wide text-slate-500 pt-1">Category:</span>
        {CATEGORIES.map((cat) => {
          const active = filters.selectedCategories.includes(cat.value);
          return (
            <button
              key={cat.value}
              className={`rounded-full px-2.5 py-1 text-xs font-semibold transition ${
                active
                  ? "bg-brand-green text-white"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
              onClick={() => toggleCategory(cat.value)}
              type="button"
            >
              {cat.label}
            </button>
          );
        })}
      </div>

      <div className="flex flex-wrap gap-2">
        <span className="text-xs font-bold uppercase tracking-wide text-slate-500 pt-1">Priority:</span>
        {PRIORITIES.map((pri) => {
          const active = filters.selectedPriorities.includes(pri.value);
          return (
            <button
              key={pri.value}
              className={`rounded-full px-2.5 py-1 text-xs font-semibold transition ${
                active
                  ? "bg-amber-600 text-white"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
              onClick={() => togglePriority(pri.value)}
              type="button"
            >
              {pri.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
