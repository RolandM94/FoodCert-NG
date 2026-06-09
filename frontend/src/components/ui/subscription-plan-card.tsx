import { CheckCircle2 } from "lucide-react";

export function SubscriptionPlanCard({
  name,
  price,
  description,
  features,
  selected = false,
  current = false,
  actionLabel,
  onAction,
  disabled = false
}: {
  name: string;
  price: string;
  description?: string;
  features: string[];
  selected?: boolean;
  current?: boolean;
  actionLabel?: string;
  onAction?: () => void;
  disabled?: boolean;
}) {
  return (
    <div className={`rounded-lg border bg-white p-5 shadow-sm ${selected ? "border-brand-600 ring-2 ring-brand-100" : "border-neutral-200"}`}>
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-base font-bold text-neutral-900">{name}</h3>
        {current ? (
          <span className="rounded bg-brand-50 px-2 py-1 text-xs font-bold uppercase tracking-wide text-brand-700">
            Current
          </span>
        ) : null}
      </div>
      <p className="mt-2 text-2xl font-bold text-brand-700">{price}</p>
      {description ? <p className="mt-2 text-sm leading-5 text-neutral-600">{description}</p> : null}
      <ul className="mt-4 grid gap-2 text-sm text-neutral-600">
        {features.map((feature) => (
          <li key={feature} className="flex items-center gap-2">
            <CheckCircle2 aria-hidden="true" className="text-brand-700" size={16} />
            {feature}
          </li>
        ))}
      </ul>
      {actionLabel && onAction ? (
        <button
          className="mt-5 w-full rounded bg-brand-600 px-4 py-2 text-sm font-bold text-white disabled:cursor-not-allowed disabled:bg-neutral-300"
          disabled={disabled || current}
          onClick={onAction}
          type="button"
        >
          {current ? "Current Plan" : actionLabel}
        </button>
      ) : null}
    </div>
  );
}
