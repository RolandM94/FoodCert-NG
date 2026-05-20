import { QrCode } from "lucide-react";

export function QRScanner() {
  return (
    <div className="flex aspect-video flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-slate-300 bg-slate-50 text-sm font-semibold text-slate-600">
      <QrCode aria-hidden="true" className="text-brand-deep" size={28} />
      Scanner ready
    </div>
  );
}
