"use client";

import Link from "next/link";
import { useMemo } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BellRing, Building2, Save, Settings, ShieldCheck } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { getEmployerSettings, updateEmployerSettings } from "@/lib/api/employer-management";
import { listEmployers } from "@/lib/api/identity";
import { NotificationPreferenceForm } from "@/components/ui/notification-preference-form";

function settingValue(settings: Record<string, unknown>, key: string, fallback: string | number | boolean) {
  const value = settings[key];
  return value === undefined || value === null ? fallback : value;
}

export default function Page() {
  const queryClient = useQueryClient();
  const employersQuery = useQuery({ queryKey: ["employers", "me"], queryFn: listEmployers });
  const employer = employersQuery.data?.[0];
  const settingsQuery = useQuery({
    queryKey: ["employer-settings", employer?.id],
    queryFn: () => getEmployerSettings(employer!.id),
    enabled: Boolean(employer?.id),
  });

  const settings = settingsQuery.data;
  const businessSettings = useMemo(() => settings?.business_settings || {}, [settings]);

  const mutation = useMutation({
    mutationFn: (payload: Parameters<typeof updateEmployerSettings>[1]) => updateEmployerSettings(employer!.id, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["employer-settings", employer?.id] }),
  });

  const updateBusinessSetting = (key: string, value: unknown) => {
    mutation.mutate({ business_settings: { ...businessSettings, [key]: value } });
  };

  return (
    <PortalShell role="employer" title="Employer Settings" description="Manage notification preferences, reminder cadence, and operational settings.">
      <div className="grid gap-6">
        {mutation.isError ? <p className="rounded-lg bg-danger-50 p-4 text-sm font-semibold text-danger-700">Could not save settings.</p> : null}
        {mutation.isSuccess ? <p className="rounded-lg bg-brand-50 p-4 text-sm font-semibold text-brand-700">Settings saved.</p> : null}

        <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <div className="mb-5 flex items-center gap-2">
            <BellRing className="text-brand-700" size={18} />
            <h2 className="text-base font-bold text-neutral-900">Notification Preferences</h2>
          </div>
          <NotificationPreferenceForm />
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
            <div className="mb-5 flex items-center gap-2">
              <Settings className="text-brand-700" size={18} />
              <h2 className="text-base font-bold text-neutral-900">Business Settings</h2>
            </div>
            <div className="grid gap-4">
              <label className="grid gap-2 text-sm font-semibold text-neutral-700">
                Renewal reminder days
                <input
                  className="h-10 rounded border border-neutral-200 px-3 text-sm"
                  min={1}
                  onBlur={(event) => updateBusinessSetting("renewal_reminder_days", Number(event.target.value))}
                  type="number"
                  defaultValue={String(settingValue(businessSettings, "renewal_reminder_days", 30))}
                />
              </label>
              <label className="grid gap-2 text-sm font-semibold text-neutral-700">
                Default escalation email
                <input
                  className="h-10 rounded border border-neutral-200 px-3 text-sm"
                  onBlur={(event) => updateBusinessSetting("escalation_email", event.target.value)}
                  type="email"
                  defaultValue={String(settingValue(businessSettings, "escalation_email", employer?.contact_person_email || ""))}
                />
              </label>
              <label className="flex items-center justify-between gap-4 rounded border border-neutral-100 p-3 text-sm font-semibold text-neutral-700">
                Auto-assign invited handlers to selected branch
                <input
                  checked={Boolean(settingValue(businessSettings, "auto_assign_branch", true))}
                  className="h-4 w-4 accent-brand-600"
                  onChange={(event) => updateBusinessSetting("auto_assign_branch", event.target.checked)}
                  type="checkbox"
                />
              </label>
            </div>
          </div>

          <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
            <div className="mb-5 flex items-center gap-2">
              <ShieldCheck className="text-brand-700" size={18} />
              <h2 className="text-base font-bold text-neutral-900">Account Shortcuts</h2>
            </div>
            <div className="grid gap-3">
              <Link className="flex items-center justify-between rounded border border-neutral-200 px-4 py-3 text-sm font-bold text-neutral-700 hover:bg-neutral-50" href="/employer/business-profile">
                <span className="inline-flex items-center gap-2"><Building2 size={16} />Business profile</span>
                <span>Open</span>
              </Link>
              <Link className="flex items-center justify-between rounded border border-neutral-200 px-4 py-3 text-sm font-bold text-neutral-700 hover:bg-neutral-50" href="/employer/subscription">
                <span className="inline-flex items-center gap-2"><Save size={16} />Subscription</span>
                <span className="capitalize">{settings?.subscription_status?.replaceAll("_", " ") || "Open"}</span>
              </Link>
            </div>
          </div>
        </section>
      </div>
    </PortalShell>
  );
}
