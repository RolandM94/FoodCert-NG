"use client";

import { ToggleLeft, ToggleRight } from "lucide-react";
import type { NotificationCategory, NotificationChannel } from "@/types/notifications";

type MandatoryMap = Record<string, boolean>;

const MANDATORY_CATEGORIES: MandatoryMap = {
  security: true,
  enforcement: true,
};

export function ChannelPreferenceToggle({
  category,
  channel,
  channelLabel,
  enabled,
  onChange,
  disabled = false,
}: {
  category: NotificationCategory;
  channel: NotificationChannel;
  channelLabel: string;
  enabled: boolean;
  onChange: (category: NotificationCategory, channel: NotificationChannel, enabled: boolean) => void;
  disabled?: boolean;
}) {
  const isMandatory = MANDATORY_CATEGORIES[category] === true;
  const locked = disabled || isMandatory;

  return (
    <div className="flex items-center justify-between gap-3 rounded border border-neutral-200 bg-white px-3 py-2">
      <span className="text-sm font-medium text-neutral-700">{channelLabel}</span>
      <button
        className={`inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-semibold transition ${
          enabled
            ? "bg-brand-50 text-brand-700"
            : "bg-neutral-100 text-neutral-400"
        } ${locked ? "cursor-not-allowed opacity-60" : "hover:bg-brand-100"}`}
        disabled={locked}
        onClick={() => onChange(category, channel, !enabled)}
        title={isMandatory ? "This notification category is mandatory" : enabled ? "Click to disable" : "Click to enable"}
        type="button"
      >
        {enabled ? (
          <ToggleRight aria-hidden="true" size={16} />
        ) : (
          <ToggleLeft aria-hidden="true" size={16} />
        )}
        {enabled ? "On" : "Off"}
      </button>
    </div>
  );
}
