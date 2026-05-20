import { Upload } from "lucide-react";

export function FileUpload({ label = "Upload evidence" }: { label?: string }) {
  return (
    <label className="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-slate-300 bg-white p-6 text-center text-sm font-semibold text-slate-600">
      <Upload aria-hidden="true" className="text-brand-deep" size={22} />
      {label}
      <input className="sr-only" type="file" />
    </label>
  );
}
