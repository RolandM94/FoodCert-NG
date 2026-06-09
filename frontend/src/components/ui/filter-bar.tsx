import { Search } from "lucide-react";

export function FilterBar({ label = "Search records" }: { label?: string }) {
  return (
    <div className="flex flex-col gap-3 rounded-lg border border-neutral-200 bg-white p-3 shadow-sm sm:flex-row sm:items-center">
      <label className="relative flex-1">
        <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400" size={16} />
        <input
          className="h-10 w-full rounded border border-neutral-200 bg-neutral-50 pl-9 pr-3 text-sm outline-none ring-brand-600/20 focus:border-brand-600 focus:ring-2"
          placeholder={label}
          type="search"
        />
      </label>
      <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm text-neutral-700">
        <option>All statuses</option>
        <option>Pending</option>
        <option>Approved</option>
        <option>Expired</option>
      </select>
    </div>
  );
}
