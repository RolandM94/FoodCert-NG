"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Loader2, Save, X } from "lucide-react";
import { useState } from "react";
import { createProvider, updateProvider } from "@/lib/api/notifications";
import type { NotificationChannel, NotificationProvider, ProviderCreatePayload } from "@/types/notifications";

const CHANNELS: { value: NotificationChannel; label: string }[] = [
  { value: "email", label: "Email" },
  { value: "sms", label: "SMS" },
  { value: "whatsapp", label: "WhatsApp" },
  { value: "in_app", label: "In-App" },
];

export function ProviderConfigForm({
  provider,
  onClose,
}: {
  provider?: NotificationProvider | null;
  onClose: () => void;
}) {
  const queryClient = useQueryClient();
  const isEdit = Boolean(provider);

  const [form, setForm] = useState<ProviderCreatePayload>({
    name: provider?.name || "",
    channel: provider?.channel || "email",
    sender_id: provider?.sender_id || "",
    config: provider?.config || {},
    is_default: provider?.is_default || false,
    is_active: provider?.is_active ?? true,
    priority_order: provider?.priority_order || 1,
    rate_limit_per_minute: provider?.rate_limit_per_minute,
  });
  const [configKey, setConfigKey] = useState("");
  const [configValue, setConfigValue] = useState("");

  const createMutation = useMutation({
    mutationFn: createProvider,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notification-providers"] });
      onClose();
    },
  });

  const updateMutation = useMutation({
    mutationFn: (payload: Partial<ProviderCreatePayload>) => updateProvider(provider!.id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notification-providers"] });
      onClose();
    },
  });

  function handleSubmit() {
    if (isEdit) {
      updateMutation.mutate(form);
    } else {
      createMutation.mutate(form);
    }
  }

  function addConfigEntry() {
    const k = configKey.trim();
    if (!k) return;
    setForm({ ...form, config: { ...form.config, [k]: configValue } });
    setConfigKey("");
    setConfigValue("");
  }

  function removeConfigEntry(k: string) {
    const next = { ...form.config };
    delete next[k];
    setForm({ ...form, config: next });
  }

  const saving = createMutation.isPending || updateMutation.isPending;

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-base font-bold text-slate-950">
          {isEdit ? "Edit Provider" : "Add Provider"}
        </h2>
        <button
          className="inline-flex h-8 w-8 items-center justify-center rounded text-slate-400 hover:bg-slate-100"
          onClick={onClose}
          type="button"
        >
          <X aria-hidden="true" size={18} />
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <label className="grid gap-1 text-sm font-semibold text-slate-700">
          Name
          <input
            className="h-10 rounded border border-slate-200 px-3 text-sm"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
          />
        </label>
        <label className="grid gap-1 text-sm font-semibold text-slate-700">
          Channel
          <select
            className="h-10 rounded border border-slate-200 bg-white px-3 text-sm"
            disabled={isEdit}
            value={form.channel}
            onChange={(e) => setForm({ ...form, channel: e.target.value as NotificationChannel })}
          >
            {CHANNELS.map((c) => (
              <option key={c.value} value={c.value}>{c.label}</option>
            ))}
          </select>
        </label>
        <label className="grid gap-1 text-sm font-semibold text-slate-700">
          Sender ID
          <input
            className="h-10 rounded border border-slate-200 px-3 text-sm"
            placeholder="noreply@example.com or brand name"
            value={form.sender_id || ""}
            onChange={(e) => setForm({ ...form, sender_id: e.target.value })}
          />
        </label>
        <label className="grid gap-1 text-sm font-semibold text-slate-700">
          Priority Order
          <input
            className="h-10 rounded border border-slate-200 px-3 text-sm"
            min={1}
            type="number"
            value={form.priority_order || 1}
            onChange={(e) => setForm({ ...form, priority_order: Number(e.target.value) })}
          />
        </label>
        <label className="grid gap-1 text-sm font-semibold text-slate-700">
          Rate Limit (per minute)
          <input
            className="h-10 rounded border border-slate-200 px-3 text-sm"
            min={1}
            type="number"
            value={form.rate_limit_per_minute || ""}
            onChange={(e) => setForm({ ...form, rate_limit_per_minute: e.target.value ? Number(e.target.value) : null })}
          />
        </label>
      </div>

      <div className="mt-4 flex items-center gap-4">
        <label className="flex items-center gap-2 text-sm font-semibold text-slate-700">
          <input
            checked={form.is_active ?? true}
            className="h-4 w-4 accent-brand-green"
            type="checkbox"
            onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
          />
          Active
        </label>
        <label className="flex items-center gap-2 text-sm font-semibold text-slate-700">
          <input
            checked={form.is_default || false}
            className="h-4 w-4 accent-brand-green"
            type="checkbox"
            onChange={(e) => setForm({ ...form, is_default: e.target.checked })}
          />
          Default
        </label>
      </div>

      <div className="mt-4">
        <p className="text-sm font-semibold text-slate-700">Configuration (API keys, secrets, etc.)</p>
        <div className="mt-2 space-y-1">
          {Object.entries(form.config || {}).map(([k, v]) => (
            <div key={k} className="flex items-center gap-2 rounded border border-slate-100 px-3 py-1.5">
              <span className="text-sm font-mono font-semibold text-slate-700">{k}</span>
              <span className="text-sm text-slate-500">=</span>
              <span className="flex-1 text-sm text-slate-600">{String(v)}</span>
              <button
                className="text-slate-400 hover:text-rose-600"
                onClick={() => removeConfigEntry(k)}
                type="button"
              >
                <X size={14} />
              </button>
            </div>
          ))}
        </div>
        <div className="mt-2 flex gap-2">
          <input
            className="h-10 flex-1 rounded border border-slate-200 px-3 text-sm"
            placeholder="Key (e.g. api_key)"
            value={configKey}
            onChange={(e) => setConfigKey(e.target.value)}
          />
          <input
            className="h-10 flex-1 rounded border border-slate-200 px-3 text-sm"
            placeholder="Value"
            value={configValue}
            onChange={(e) => setConfigValue(e.target.value)}
          />
          <button
            className="inline-flex h-10 items-center rounded border border-slate-200 px-3 text-sm font-semibold text-slate-700 hover:bg-slate-50"
            onClick={addConfigEntry}
            type="button"
          >
            Add
          </button>
        </div>
      </div>

      <div className="mt-5">
        <button
          className="inline-flex h-10 items-center gap-1.5 rounded bg-brand-green px-4 text-sm font-bold text-white hover:bg-brand-deep disabled:opacity-60"
          disabled={saving || !form.name}
          onClick={handleSubmit}
          type="button"
        >
          {saving ? <Loader2 className="animate-spin" size={16} /> : <Save aria-hidden="true" size={16} />}
          {saving ? "Saving..." : "Save Provider"}
        </button>
      </div>
    </div>
  );
}
