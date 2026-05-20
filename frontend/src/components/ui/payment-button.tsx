import { CreditCard } from "lucide-react";

export function PaymentButton({ label = "Proceed to payment" }: { label?: string }) {
  return (
    <button className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white">
      <CreditCard aria-hidden="true" size={17} />
      {label}
    </button>
  );
}
