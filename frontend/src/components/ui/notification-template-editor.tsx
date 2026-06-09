"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Eye, Loader2, Save, X } from "lucide-react";
import { useState } from "react";
import {
  createTemplate,
  getTemplate,
  previewTemplate,
  updateTemplate,
} from "@/lib/api/notifications";
import type {
  NotificationCategory,
  NotificationChannel,
  NotificationTemplate,
  TemplateCreatePayload,
  TemplatePreview,
  TemplateScope,
} from "@/types/notifications";

const CATEGORIES: { value: NotificationCategory; label: string }[] = [
  { value: "account", label: "Account" },
  { value: "identity_verification", label: "Identity" },
  { value: "appointment", label: "Appointment" },
  { value: "assessment", label: "Assessment" },
  { value: "certificate", label: "Certificate" },
  { value: "enforcement", label: "Enforcement" },
  { value: "inspection", label: "Inspection" },
  { value: "payments", label: "Payments" },
  { value: "security", label: "Security" },
  { value: "subscriptions", label: "Subscriptions" },
  { value: "system", label: "System" },
  { value: "vaccination", label: "Vaccination" },
];

const CHANNELS: { value: NotificationChannel; label: string }[] = [
  { value: "email", label: "Email" },
  { value: "sms", label: "SMS" },
  { value: "in_app", label: "In-App" },
  { value: "whatsapp", label: "WhatsApp" },
];

const SCOPES: { value: TemplateScope; label: string }[] = [
  { value: "system", label: "System" },
  { value: "national", label: "National" },
  { value: "state", label: "State" },
];

export function NotificationTemplateEditor({
  templateId,
  onClose,
}: {
  templateId?: string | null;
  onClose: () => void;
}) {
  const queryClient = useQueryClient();
  const isEdit = Boolean(templateId);

  const { data: existing, isLoading } = useQuery({
    queryKey: ["notification-template", templateId],
    queryFn: () => getTemplate(templateId!),
    enabled: isEdit,
  });

  const [form, setForm] = useState<TemplateCreatePayload>({
    template_key: "",
    name: "",
    category: "system",
    channel: "email",
    subject: "",
    body: "",
    allowed_variables: [],
    language: "en",
    scope: "system",
  });
  const [varInput, setVarInput] = useState("");
  const [previewCtx, setPreviewCtx] = useState<Record<string, string>>({});

  const [preview, setPreview] = useState<TemplatePreview | null>(null);
  const [previewError, setPreviewError] = useState("");
  const [previewLoading, setPreviewLoading] = useState(false);

  // Populate form when editing existing template
  if (existing && form.template_key === "" && isEdit) {
    setForm({
      template_key: existing.template_key,
      name: existing.name,
      category: existing.category,
      channel: existing.channel,
      subject: existing.subject,
      body: existing.body,
      allowed_variables: existing.allowed_variables,
      language: existing.language,
      scope: existing.scope,
      state: existing.state,
    });
  }

  const createMutation = useMutation({
    mutationFn: createTemplate,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notification-templates"] });
      onClose();
    },
  });

  const updateMutation = useMutation({
    mutationFn: (payload: Partial<TemplateCreatePayload>) => updateTemplate(templateId!, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notification-templates"] });
      onClose();
    },
  });

  function handleSave() {
    if (isEdit) {
      updateMutation.mutate({
        name: form.name,
        category: form.category,
        channel: form.channel,
        subject: form.subject,
        body: form.body,
        allowed_variables: form.allowed_variables,
        language: form.language,
        scope: form.scope,
        state: form.state,
      });
    } else {
      createMutation.mutate(form);
    }
  }

  function handleAddVariable() {
    const v = varInput.trim();
    if (!v || form.allowed_variables.includes(v)) return;
    setForm({ ...form, allowed_variables: [...form.allowed_variables, v] });
    setVarInput("");
  }

  function handleRemoveVariable(v: string) {
    setForm({ ...form, allowed_variables: form.allowed_variables.filter((x) => x !== v) });
  }

  async function handlePreview() {
    setPreviewLoading(true);
    setPreviewError("");
    try {
      // For new templates, just do a client-side preview
      if (!isEdit) {
        let subject = form.subject;
        let body = form.body;
        for (const v of form.allowed_variables) {
          const val = previewCtx[v] || `[${v}]`;
          subject = subject.replaceAll(`{{ ${v} }}`, val);
          body = body.replaceAll(`{{ ${v} }}`, val);
        }
        setPreview({ subject, body });
      } else {
        const result = await previewTemplate(templateId!, previewCtx);
        setPreview(result);
      }
    } catch (err) {
      setPreviewError(err instanceof Error ? err.message : "Preview failed");
    } finally {
      setPreviewLoading(false);
    }
  }

  const saving = createMutation.isPending || updateMutation.isPending;

  if (isEdit && isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-neutral-400" size={24} />
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-base font-bold text-neutral-900">
          {isEdit ? "Edit Template" : "New Template"}
        </h2>
        <button
          className="inline-flex h-8 w-8 items-center justify-center rounded text-neutral-400 hover:bg-neutral-100"
          onClick={onClose}
          type="button"
        >
          <X aria-hidden="true" size={18} />
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <label className="grid gap-1 text-sm font-semibold text-neutral-700">
          Template Key
          <input
            className="h-10 rounded border border-neutral-200 px-3 text-sm"
            disabled={isEdit}
            value={form.template_key}
            onChange={(e) => setForm({ ...form, template_key: e.target.value })}
          />
        </label>
        <label className="grid gap-1 text-sm font-semibold text-neutral-700">
          Name
          <input
            className="h-10 rounded border border-neutral-200 px-3 text-sm"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
          />
        </label>
        <label className="grid gap-1 text-sm font-semibold text-neutral-700">
          Category
          <select
            className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm"
            value={form.category}
            onChange={(e) => setForm({ ...form, category: e.target.value as NotificationCategory })}
          >
            {CATEGORIES.map((c) => (
              <option key={c.value} value={c.value}>{c.label}</option>
            ))}
          </select>
        </label>
        <label className="grid gap-1 text-sm font-semibold text-neutral-700">
          Channel
          <select
            className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm"
            value={form.channel}
            onChange={(e) => setForm({ ...form, channel: e.target.value as NotificationChannel })}
          >
            {CHANNELS.map((c) => (
              <option key={c.value} value={c.value}>{c.label}</option>
            ))}
          </select>
        </label>
        <label className="grid gap-1 text-sm font-semibold text-neutral-700">
          Scope
          <select
            className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm"
            value={form.scope}
            onChange={(e) => setForm({ ...form, scope: e.target.value as TemplateScope })}
          >
            {SCOPES.map((s) => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        </label>
        <label className="grid gap-1 text-sm font-semibold text-neutral-700">
          Language
          <input
            className="h-10 rounded border border-neutral-200 px-3 text-sm"
            value={form.language}
            onChange={(e) => setForm({ ...form, language: e.target.value })}
          />
        </label>
      </div>

      <label className="mt-4 grid gap-1 text-sm font-semibold text-neutral-700">
        Subject
        <textarea
          className="min-h-[60px] rounded border border-neutral-200 px-3 py-2 text-sm"
          rows={2}
          value={form.subject}
          onChange={(e) => setForm({ ...form, subject: e.target.value })}
        />
      </label>

      <label className="mt-4 grid gap-1 text-sm font-semibold text-neutral-700">
        Body
        <textarea
          className="min-h-[120px] rounded border border-neutral-200 px-3 py-2 text-sm font-mono"
          rows={6}
          value={form.body}
          onChange={(e) => setForm({ ...form, body: e.target.value })}
        />
      </label>

      <div className="mt-4">
        <p className="text-sm font-semibold text-neutral-700">Allowed Variables</p>
        <div className="mt-2 flex flex-wrap gap-2">
          {form.allowed_variables.map((v) => (
            <span
              key={v}
              className="inline-flex items-center gap-1 rounded-full bg-brand-50 px-2.5 py-1 text-xs font-semibold text-brand-700"
            >
              {`{{ ${v} }}`}
              <button
                className="ml-1 text-brand-600 hover:text-danger-500"
                onClick={() => handleRemoveVariable(v)}
                type="button"
              >
                <X size={12} />
              </button>
            </span>
          ))}
        </div>
        <div className="mt-2 flex gap-2">
          <input
            className="h-10 flex-1 rounded border border-neutral-200 px-3 text-sm"
            placeholder="Variable name (e.g. user_name)"
            value={varInput}
            onChange={(e) => setVarInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAddVariable()}
          />
          <button
            className="inline-flex h-10 items-center rounded border border-neutral-200 px-3 text-sm font-semibold text-neutral-700 hover:bg-neutral-50"
            onClick={handleAddVariable}
            type="button"
          >
            Add
          </button>
        </div>
      </div>

      <div className="mt-4">
        <p className="mb-2 text-sm font-semibold text-neutral-700">Preview Context</p>
        <div className="grid gap-2 md:grid-cols-3">
          {form.allowed_variables.map((v) => (
            <label key={v} className="grid gap-1 text-xs font-medium text-neutral-600">
              {v}
              <input
                className="h-8 rounded border border-neutral-200 px-2 text-sm"
                placeholder={`Value for ${v}`}
                value={previewCtx[v] || ""}
                onChange={(e) => setPreviewCtx({ ...previewCtx, [v]: e.target.value })}
              />
            </label>
          ))}
        </div>
      </div>

      <div className="mt-5 flex items-center justify-between">
        <button
          className="inline-flex h-10 items-center gap-1.5 rounded border border-neutral-200 px-4 text-sm font-semibold text-neutral-700 hover:bg-neutral-50"
          disabled={previewLoading}
          onClick={handlePreview}
          type="button"
        >
          {previewLoading ? <Loader2 className="animate-spin" size={16} /> : <Eye aria-hidden="true" size={16} />}
          Preview
        </button>
        <button
          className="inline-flex h-10 items-center gap-1.5 rounded bg-brand-600 px-4 text-sm font-bold text-white hover:bg-brand-700 disabled:opacity-60"
          disabled={saving || !form.template_key || !form.name}
          onClick={handleSave}
          type="button"
        >
          {saving ? <Loader2 className="animate-spin" size={16} /> : <Save aria-hidden="true" size={16} />}
          {saving ? "Saving..." : "Save"}
        </button>
      </div>

      {preview ? (
        <div className="mt-4 rounded border border-neutral-200 bg-neutral-50 p-4">
          <p className="text-xs font-bold uppercase tracking-wide text-neutral-500 mb-2">Preview</p>
          <p className="text-sm font-bold text-neutral-900">{preview.subject}</p>
          <p className="mt-1 whitespace-pre-wrap text-sm text-neutral-600">{preview.body}</p>
        </div>
      ) : null}
      {previewError ? (
        <p className="mt-4 rounded bg-danger-50 p-3 text-sm font-semibold text-danger-700">{previewError}</p>
      ) : null}
    </div>
  );
}
