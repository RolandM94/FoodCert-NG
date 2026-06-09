"use client";

import { useState } from "react";
import { MessageSquarePlus, Send } from "lucide-react";
import type { InspectionResponseType } from "@/types/inspections";

const responseTypes: Array<{ value: InspectionResponseType; label: string }> = [
  { value: "acknowledge", label: "Acknowledge notice" },
  { value: "corrective_action", label: "Corrective action" },
  { value: "evidence", label: "Evidence update" },
  { value: "comment", label: "Comment" },
];

export function InspectionResponseForm({
  disabled,
  onSubmit,
}: {
  disabled?: boolean;
  onSubmit: (payload: { response_type: InspectionResponseType; content: string; evidence_file_url?: string }) => Promise<void>;
}) {
  const [responseType, setResponseType] = useState<InspectionResponseType>("acknowledge");
  const [content, setContent] = useState("");
  const [evidenceUrl, setEvidenceUrl] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!content.trim() && !evidenceUrl.trim()) {
      setError("Add a response note or evidence link before submitting.");
      return;
    }
    setError("");
    await onSubmit({
      response_type: responseType,
      content: content.trim(),
      evidence_file_url: evidenceUrl.trim() || undefined,
    });
    setResponseType("acknowledge");
    setContent("");
    setEvidenceUrl("");
  }

  return (
    <form className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm" onSubmit={handleSubmit}>
      <div className="mb-4 flex items-center gap-2">
        <MessageSquarePlus className="text-brand-700" size={18} />
        <h2 className="text-base font-bold text-neutral-900">Submit Response</h2>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
          Response type
          <select
            className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm"
            value={responseType}
            onChange={(event) => setResponseType(event.target.value as InspectionResponseType)}
          >
            {responseTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </label>
        <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
          Evidence link
          <input
            className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3 text-sm"
            placeholder="https://..."
            type="url"
            value={evidenceUrl}
            onChange={(event) => setEvidenceUrl(event.target.value)}
          />
        </label>
      </div>
      <label className="mt-4 grid gap-1.5 text-sm font-semibold text-neutral-700">
        Response note
        <textarea
          className="min-h-28 rounded-lg border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm leading-6"
          placeholder="Describe the acknowledgement, corrective action, or evidence submitted."
          value={content}
          onChange={(event) => setContent(event.target.value)}
        />
      </label>
      {error ? <p className="mt-3 text-sm font-semibold text-danger-500">{error}</p> : null}
      <button
        className="mt-5 inline-flex h-11 items-center gap-2 rounded-lg bg-brand-600 px-5 text-sm font-bold text-white hover:bg-brand-700 disabled:opacity-60"
        disabled={disabled}
        type="submit"
      >
        <Send size={16} />
        {disabled ? "Submitting..." : "Submit Response"}
      </button>
    </form>
  );
}
