"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Loader2, Save } from "lucide-react";
import { useState, useEffect } from "react";
import { bulkUpdatePreferences, listPreferences } from "@/lib/api/notifications";
import { ChannelPreferenceToggle } from "@/components/ui/channel-preference-toggle";
import type {
  NotificationCategory,
  NotificationChannel,
  NotificationPreference,
} from "@/types/notifications";

const CATEGORIES: { value: NotificationCategory; label: string }[] = [
  { value: "account", label: "Account" },
  { value: "identity_verification", label: "Identity Verification" },
  { value: "employer_management", label: "Employer Management" },
  { value: "facility_accreditation", label: "Facility Accreditation" },
  { value: "appointment", label: "Appointments" },
  { value: "assessment", label: "Assessments" },
  { value: "lab_workflow", label: "Lab Workflow" },
  { value: "vaccination", label: "Vaccination" },
  { value: "certificate", label: "Certificates" },
  { value: "renewal", label: "Renewals" },
  { value: "payments", label: "Payments" },
  { value: "subscriptions", label: "Subscriptions" },
  { value: "settlements", label: "Settlements" },
  { value: "inspection", label: "Inspections" },
  { value: "enforcement", label: "Enforcement" },
  { value: "reports", label: "Reports" },
  { value: "m_and_e", label: "M&E" },
  { value: "data_quality", label: "Data Quality" },
  { value: "security", label: "Security" },
  { value: "system", label: "System" },
];

const CHANNELS: { value: NotificationChannel; label: string }[] = [
  { value: "in_app", label: "In-App" },
  { value: "email", label: "Email" },
  { value: "sms", label: "SMS" },
  { value: "whatsapp", label: "WhatsApp" },
];

type PrefMap = Record<string, NotificationPreference>;

function buildKey(category: string, channel: string) {
  return `${category}::${channel}`;
}

export function NotificationPreferenceForm() {
  const queryClient = useQueryClient();
  const [dirty, setDirty] = useState(false);
  const [error, setError] = useState("");

  const { data: preferences = [], isLoading } = useQuery({
    queryKey: ["notification-preferences"],
    queryFn: listPreferences,
  });

  const prefMap: PrefMap = {};
  for (const p of preferences) {
    prefMap[buildKey(p.category, p.channel)] = p;
  }

  const bulkMutation = useMutation({
    mutationFn: bulkUpdatePreferences,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notification-preferences"] });
      setDirty(false);
      setError("");
    },
    onError: (err) => {
      setError(err instanceof Error ? err.message : "Failed to save preferences.");
    },
  });

  function handleToggle(category: NotificationCategory, channel: NotificationChannel, enabled: boolean) {
    setDirty(true);
    setError("");

    const payload = CATEGORIES.map((cat) =>
      CHANNELS.map((ch) => {
        const isThis = cat.value === category && ch.value === channel;
        const key = buildKey(cat.value, ch.value);
        const existing = prefMap[key];
        return {
          category: cat.value,
          channel: ch.value,
          is_enabled: isThis ? enabled : existing?.is_enabled ?? true,
          digest_enabled: existing?.digest_enabled ?? false,
          quiet_hours_start: existing?.quiet_hours_start ?? null,
          quiet_hours_end: existing?.quiet_hours_end ?? null,
        };
      })
    ).flat();

    bulkMutation.mutate(payload);
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-neutral-400" size={24} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {error ? (
        <div className="rounded bg-danger-50 p-3 text-sm font-semibold text-danger-700">{error}</div>
      ) : null}

      <div className="grid gap-6 md:grid-cols-2">
        {CATEGORIES.map((cat) => (
          <div key={cat.value} className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <h3 className="mb-3 text-sm font-bold text-neutral-900">{cat.label}</h3>
            <div className="space-y-2">
              {CHANNELS.map((ch) => {
                const key = buildKey(cat.value, ch.value);
                const pref = prefMap[key];
                return (
                  <ChannelPreferenceToggle
                    key={key}
                    category={cat.value}
                    channel={ch.value}
                    channelLabel={ch.label}
                    enabled={pref?.is_enabled ?? true}
                    onChange={handleToggle}
                  />
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {dirty ? (
        <div className="flex items-center gap-2 text-sm text-neutral-500">
          <Loader2 className="animate-spin" size={14} />
          Saving preferences...
        </div>
      ) : null}
    </div>
  );
}
