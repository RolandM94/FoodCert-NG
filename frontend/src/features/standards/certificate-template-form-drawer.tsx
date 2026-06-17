"use client";

import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  createCertificateTemplate,
  updateCertificateTemplate,
} from "@/lib/api/standards";
import type { CertificateTemplate } from "@/types/standards";
import { getApiErrorMessage } from "@/lib/api/client";

interface Props {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  mode: "create" | "edit";
  policyVersionId: string;
  initial?: Partial<CertificateTemplate> | null;
}

export function CertificateTemplateFormDrawer({
  open,
  onClose,
  onSuccess,
  mode,
  policyVersionId,
  initial,
}: Props) {
  const queryClient = useQueryClient();
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    template_name: "",
    template_version: "",
    certificate_number_format: "FHMT-{STATE}-{YYYY}-{SEQ}",
  });
  const [requiredFieldsStr, setRequiredFieldsStr] = useState("");
  const [qrFieldsStr, setQrFieldsStr] = useState("");
  const [verificationFieldsStr, setVerificationFieldsStr] = useState("");
  const [revocationStr, setRevocationStr] = useState("");

  useEffect(() => {
    if (open && initial) {
      setForm({
        template_name: initial.template_name ?? "",
        template_version: initial.template_version ?? "",
        certificate_number_format: initial.certificate_number_format ?? "FHMT-{STATE}-{YYYY}-{SEQ}",
      });
      setRequiredFieldsStr(initial.required_fields?.join(", ") ?? "");
      setQrFieldsStr(
        Array.isArray((initial.qr_payload_config as Record<string, unknown>)?.fields)
          ? ((initial.qr_payload_config as Record<string, unknown>).fields as string[]).join(", ")
          : ""
      );
      setVerificationFieldsStr(initial.public_verification_fields?.join(", ") ?? "");
      setRevocationStr(initial.revocation_reasons?.join(", ") ?? "");
      setError("");
    } else if (open && !initial) {
      setForm({
        template_name: "",
        template_version: "",
        certificate_number_format: "FHMT-{STATE}-{YYYY}-{SEQ}",
      });
      setRequiredFieldsStr("");
      setQrFieldsStr("");
      setVerificationFieldsStr("");
      setRevocationStr("");
      setError("");
    }
  }, [open, initial]);

  const mutation = useMutation({
    mutationFn: async (): Promise<CertificateTemplate> => {
      const payload: Partial<CertificateTemplate> = {
        policy_version: policyVersionId,
        template_name: form.template_name,
        template_version: form.template_version,
        certificate_number_format: form.certificate_number_format,
        required_fields: requiredFieldsStr.split(",").map((s) => s.trim()).filter(Boolean),
        qr_payload_config: {
          fields: qrFieldsStr.split(",").map((s) => s.trim()).filter(Boolean),
        },
        public_verification_fields: verificationFieldsStr.split(",").map((s) => s.trim()).filter(Boolean),
        revocation_reasons: revocationStr.split(",").map((s) => s.trim()).filter(Boolean),
      };
      if (mode === "edit" && initial?.id) {
        return updateCertificateTemplate(initial.id, payload);
      }
      return createCertificateTemplate(payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["standards-certificate-templates"] });
      onSuccess();
      onClose();
    },
    onError: (err) => {
      setError(getApiErrorMessage(err, "Failed to save certificate template."));
    },
  });

  function update(field: string, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    mutation.mutate();
  }

  if (!open) return null;

  const title = mode === "create" ? "Create Certificate Template" : "Edit Certificate Template";

  return (
    <>
      <div className="fixed inset-0 z-40 bg-black/40" onClick={onClose} />
      <div className="fixed inset-y-0 right-0 z-50 w-full max-w-lg overflow-y-auto border-l border-neutral-200 bg-white shadow-2xl">
        <form onSubmit={handleSubmit} className="flex h-full flex-col">
          <div className="flex items-center justify-between border-b border-neutral-200 px-6 py-4">
            <h2 className="text-lg font-semibold text-neutral-900">{title}</h2>
            <button
              type="button"
              className="text-neutral-400 hover:text-neutral-600"
              onClick={onClose}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>

          <div className="flex-1 space-y-4 px-6 py-5">
            {error && (
              <div className="rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">
                {error}
              </div>
            )}

            <label className="block text-sm font-medium text-neutral-700">
              Template Name
              <input
                type="text"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                value={form.template_name}
                onChange={(e) => update("template_name", e.target.value)}
                required
              />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Template Version
              <input
                type="text"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                value={form.template_version}
                onChange={(e) => update("template_version", e.target.value)}
                placeholder="1.0"
                required
              />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Certificate Number Format
              <input
                type="text"
                className="mt-1 h-11 w-full rounded border border-neutral-200 bg-neutral-50 px-3 text-sm"
                value={form.certificate_number_format}
                onChange={(e) => update("certificate_number_format", e.target.value)}
              />
            </label>

            <div>
              <label className="block text-sm font-medium text-neutral-700">
                Required Fields
                <textarea
                  className="mt-1 min-h-[80px] w-full rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm"
                  value={requiredFieldsStr}
                  onChange={(e) => setRequiredFieldsStr(e.target.value)}
                />
              </label>
              <p className="text-xs text-neutral-500">Enter field names separated by commas</p>
            </div>

            <label className="block text-sm font-medium text-neutral-700">
              QR Payload Fields
              <textarea
                className="mt-1 min-h-[80px] w-full rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm"
                value={qrFieldsStr}
                onChange={(e) => setQrFieldsStr(e.target.value)}
              />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Public Verification Fields
              <textarea
                className="mt-1 min-h-[80px] w-full rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm"
                value={verificationFieldsStr}
                onChange={(e) => setVerificationFieldsStr(e.target.value)}
              />
            </label>

            <label className="block text-sm font-medium text-neutral-700">
              Revocation Reasons
              <textarea
                className="mt-1 min-h-[80px] w-full rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm"
                value={revocationStr}
                onChange={(e) => setRevocationStr(e.target.value)}
              />
            </label>
          </div>

          <div className="flex justify-end gap-3 border-t border-neutral-200 px-6 py-4">
            <button
              type="button"
              className="inline-flex h-10 items-center rounded-md border border-neutral-200 bg-white px-4 text-sm font-medium text-neutral-700 hover:bg-neutral-50"
              onClick={onClose}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="inline-flex h-10 items-center rounded-md bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
              disabled={mutation.isPending}
            >
              {mutation.isPending ? "Saving..." : "Save"}
            </button>
          </div>
        </form>
      </div>
    </>
  );
}
