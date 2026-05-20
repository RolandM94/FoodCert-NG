import { Search } from "lucide-react";

export function FilterBar({ label = "Search records" }: { label?: string }) {
  return (
    <div className="flex flex-col gap-3 rounded-lg border border-slate-200 bg-white p-3 shadow-sm sm:flex-row sm:items-center">
      <label className="relative flex-1">
        <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
        <input
          className="h-10 w-full rounded border border-slate-200 bg-slate-50 pl-9 pr-3 text-sm outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2"
          placeholder={label}
          type="search"
        />
      </label>
      <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm text-slate-700">
        <option>All statuses</option>
        <option>Pending</option>
        <option>Approved</option>
        <option>Expired</option>
      </select>
    </div>
  );
}
