import { Clock3 } from "lucide-react";

export function AuditTimeline({ events }: { events: Array<{ label: string; time: string }> }) {
  return (
    <ol className="grid gap-3">
      {events.map((event) => (
        <li key={`${event.label}-${event.time}`} className="flex gap-3 rounded-lg border border-neutral-200 bg-white p-3">
          <Clock3 aria-hidden="true" className="mt-0.5 text-brand-700" size={17} />
          <div>
            <p className="text-sm font-semibold text-neutral-900">{event.label}</p>
            <p className="text-xs text-neutral-500">{event.time}</p>
          </div>
        </li>
      ))}
    </ol>
  );
}
