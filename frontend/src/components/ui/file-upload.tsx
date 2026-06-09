import { Upload } from "lucide-react";

export function FileUpload({ label = "Upload evidence" }: { label?: string }) {
  return (
    <label className="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-neutral-300 bg-white p-6 text-center text-sm font-semibold text-neutral-600">
      <Upload aria-hidden="true" className="text-brand-700" size={22} />
      {label}
      <input className="sr-only" type="file" />
    </label>
  );
}
