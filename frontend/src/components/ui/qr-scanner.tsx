import { QrCode } from "lucide-react";

export function QRScanner() {
  return (
    <div className="flex aspect-video flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-neutral-300 bg-neutral-50 text-sm font-semibold text-neutral-600">
      <QrCode aria-hidden="true" className="text-brand-700" size={28} />
      Scanner ready
    </div>
  );
}
