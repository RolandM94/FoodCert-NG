"use client";

import { useEffect, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { createPolicyDocument, updatePolicyDocument } from "@/lib/api/standards";
import { getApiErrorMessage } from "@/lib/api/client";
import type { DocumentType, PolicyDocument } from "@/types/standards";

interface Props {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  mode: "create" | "edit";
  policyVersionId: string;
  initial?: Partial<PolicyDocument> | null;
}

const DOCUMENT_TYPES: Array<{ value: DocumentType; label: string }> = [
  { value: "guideline", label: "National Guideline" },
  { value: "sop", label: "SOP" },
  { value: "circular", label: "Circular" },
  { value: "form_template", label: "Form Template" },
  { value: "reporting_template", label: "Reporting Template" },
  { value: "faq", label: "FAQ" },
  { value: "training", label: "Training Material" },
  { value: "awareness", label: "Public Awareness Material" },
  { value: "memo", label: "Technical Memo" },
];

const AUDIENCES = [
  "Federal users",
  "State users",
  "Medical facilities",
  "Food businesses",
  "Public",
];

function csv(value: unknown) {
  return Array.isArray(value) ? value.join(", ") : "";
}

function splitCsv(value: string) {
  return value.split(",").map((item) => item.trim()).filter(Boolean);
}

export function PolicyDocumentFormDrawer({ open, onClose, onSuccess, mode, policyVersionId, initial }: Props) {
  const queryClient = useQueryClient();
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    title: "",
    document_type: "guideline" as DocumentType,
    description: "",
    file_url: "",
    version_label: "v1.0",
    target_audience: "State users",
    requires_acknowledgement: true,
  });

  useEffect(() => {
    if (!open) return;
    setError("");
    if (initial) {
      setForm({
        title: initial.title ?? "",
        document_type: initial.document_type ?? "guideline",
        description: initial.description ?? "",
        file_url: initial.file_url ?? "",
        version_label: initial.version_label ?? "v1.0",
        target_audience: csv(initial.target_audience),
        requires_acknowledgement: initial.requires_acknowledgement ?? true,
      });
    } else {
      setForm({
        title: "",
        document_type: "guideline",
        description: "",
        file_url: "",
        version_label: "v1.0",
        target_audience: "State users",
        requires_acknowledgement: true,
      });
    }
  }, [open, initial]);

  const mutation = useMutation({
    mutationFn: async (): Promise<PolicyDocument> => {
      const payload: Partial<PolicyDocument> = {
        policy_version: policyVersionId || null,
        title: form.title,
        document_type: form.document_type,
        description: form.description,
        file_url: form.file_url,
        version_label: form.version_label,
        target_audience: splitCsv(form.target_audience),
        requires_acknowledgement: form.requires_acknowledgement,
      };
      if (mode === "edit" && initial?.id) {
        return updatePolicyDocument(initial.id, payload);
      }
      return createPolicyDocument(payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["standards-documents"] });
      queryClient.invalidateQueries({ queryKey: ["standards-policy-versions"] });
      onSuccess();
      onClose();
    },
    onError: (err) => setError(getApiErrorMessage(err, "Failed to save policy document.")),
  });

  function update(field: keyof typeof form, value: string | boolean) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    mutation.mutate();
  }

  if (!open) return null;

  return (
    <>
      <div className="fixed inset-0 z-40 bg-black/40" onClick={onClose} />
      <div className="fixed inset-y-0 right-0 z-50 w-full max-w-xl overflow-y-auto border-l border-neutral-200 bg-white shadow-2xl">
        <form onSubmit={handleSubmit} className="flex min-h-full flex-col">
          <div className="flex items-center justify-between border-b border-neutral-200 px-6 py-4">
            <h2 className="text-lg font-semibold text-neutral-900">{mode === "create" ? "Upload Document" : "Edit Document"}</h2>
            <button type="button" onClick={onClose} className="text-sm font-semibold text-neutral-500 hover:text-neutral-900">Close</button>
          </div>

          <div className="flex-1 space-y-4 px-6 py-5">
            {error ? <div className="rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{error}</div> : null}

            <label className="block text-sm font-medium text-neutral-700">
              Title
              <input required className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" value={form.title} onChange={(event) => update("title", event.target.value)} />
            </label>

            <div className="grid gap-3 sm:grid-cols-2">
              <label className="block text-sm font-medium text-neutral-700">
                Document Type
                <select className="mt-1 h-11 w-full rounded border border-neutral-200 bg-white px-3 text-sm" value={form.document_type} onChange={(event) => update("document_type", event.target.value as DocumentType)}>
                  {DOCUMENT_TYPES.map((type) => <option key={type.value} value={type.value}>{type.label}</option>)}
                </select>
              </label>
              <label className="block text-sm font-medium text-neutral-700">
                Version Label
                <input required className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" value={form.version_label} onChange={(event) => update("version_label", event.target.value)} />
              </label>
            </div>

            <label className="block text-sm font-medium text-neutral-700">
              Secure File URL
              <input required type="url" className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" value={form.file_url} onChange={(event) => update("file_url", event.target.value)} placeholder="https://..." />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Description
              <textarea className="mt-1 min-h-24 w-full rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm" value={form.description} onChange={(event) => update("description", event.target.value)} />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Target Audience
              <textarea className="mt-1 min-h-20 w-full rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm" value={form.target_audience} onChange={(event) => update("target_audience", event.target.value)} placeholder={AUDIENCES.join(", ")} />
            </label>

            <label className="flex items-center gap-2 text-sm font-medium text-neutral-700">
              <input type="checkbox" className="h-4 w-4 rounded border-neutral-300" checked={form.requires_acknowledgement} onChange={(event) => update("requires_acknowledgement", event.target.checked)} />
              Require state acknowledgement
            </label>
          </div>

          <div className="flex justify-end gap-3 border-t border-neutral-200 px-6 py-4">
            <button type="button" onClick={onClose} className="rounded border border-neutral-200 px-4 py-2 text-sm font-semibold text-neutral-700 hover:bg-neutral-50">Cancel</button>
            <button disabled={mutation.isPending} type="submit" className="rounded bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-60">
              {mutation.isPending ? "Saving..." : "Save Document"}
            </button>
          </div>
        </form>
      </div>
    </>
  );
}
