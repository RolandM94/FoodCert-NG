"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";

import { getApiErrorMessage } from "@/lib/api/client";
import { aiGenerateIndicatorFormula, aiSuggestIndicators } from "@/lib/api/performance-indicators";
import type { IndicatorAIFormula, IndicatorAISuggestion } from "@/types/standards";

export function PIAiPanel() {
  const [prompt, setPrompt] = useState("");
  const [suggestions, setSuggestions] = useState<IndicatorAISuggestion[]>([]);
  const [formula, setFormula] = useState<IndicatorAIFormula | null>(null);
  const [error, setError] = useState<string | null>(null);

  const suggestMutation = useMutation({
    mutationFn: () => aiSuggestIndicators(prompt),
    onSuccess: (data) => { setSuggestions(data.suggestions); setFormula(null); setError(null); },
    onError: (err) => setError(getApiErrorMessage(err, "Could not suggest indicators.")),
  });
  const formulaMutation = useMutation({
    mutationFn: () => aiGenerateIndicatorFormula(prompt),
    onSuccess: (data) => { setFormula(data.formula); setSuggestions([]); setError(null); },
    onError: (err) => setError(getApiErrorMessage(err, "Could not draft a formula.")),
  });

  const busy = suggestMutation.isPending || formulaMutation.isPending;

  return (
    <section className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
      <h3 className="text-sm font-semibold text-neutral-900">AI assistant</h3>
      <p className="mt-1 text-sm text-neutral-500">
        Describe what you want to measure. Suggestions and formulas are drafts — review before saving. Sensitive or medical fields are blocked.
      </p>
      <div className="mt-3 flex flex-wrap gap-2">
        <input
          className="h-11 min-w-0 flex-1 rounded-md border border-neutral-200 bg-neutral-50 px-3 text-sm"
          placeholder="e.g. inspection completion rate by state"
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
        />
        <button
          className="inline-flex h-11 items-center rounded-md bg-brand-600 px-4 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-50"
          disabled={busy || !prompt.trim()}
          onClick={() => suggestMutation.mutate()}
          type="button"
        >
          Suggest indicators
        </button>
        <button
          className="inline-flex h-11 items-center rounded-md border border-neutral-200 bg-white px-4 text-sm font-semibold text-neutral-700 hover:bg-neutral-50 disabled:opacity-50"
          disabled={busy || !prompt.trim()}
          onClick={() => formulaMutation.mutate()}
          type="button"
        >
          Draft formula
        </button>
      </div>

      {error ? <p className="mt-3 rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{error}</p> : null}

      {suggestions.length > 0 ? (
        <div className="mt-4 grid gap-3 lg:grid-cols-3">
          {suggestions.map((suggestion) => (
            <article key={suggestion.code} className="rounded-lg border border-neutral-200 bg-neutral-50 p-3">
              <p className="text-sm font-bold text-neutral-900">{suggestion.name}</p>
              <p className="text-xs text-neutral-500">{suggestion.code} · {suggestion.category}</p>
              <p className="mt-1 text-sm text-neutral-700">{suggestion.description}</p>
              <p className="mt-2 text-xs text-neutral-500">
                {suggestion.formula_type} · {suggestion.unit_of_measurement} · {suggestion.target_direction.replace(/_/g, " ")}
              </p>
            </article>
          ))}
        </div>
      ) : null}

      {formula ? (
        <div className="mt-4 rounded-lg border border-neutral-200 bg-neutral-50 p-3 text-sm">
          <p className="font-bold text-neutral-900">Draft formula (review required)</p>
          <dl className="mt-2 grid gap-1 text-neutral-700">
            <div><dt className="inline font-semibold">Calculation:</dt> <dd className="inline">{formula.calculation_type}</dd></div>
            <div><dt className="inline font-semibold">Dataset:</dt> <dd className="inline">{formula.data_source}</dd></div>
            <div><dt className="inline font-semibold">Unit:</dt> <dd className="inline">{formula.unit_of_measurement}</dd></div>
            <div><dt className="inline font-semibold">Good direction:</dt> <dd className="inline">{formula.target_direction.replace(/_/g, " ")}</dd></div>
          </dl>
          <ul className="mt-2 list-disc pl-5 text-xs text-neutral-500">
            {formula.reasoning.map((reason) => <li key={reason}>{reason}</li>)}
          </ul>
        </div>
      ) : null}
    </section>
  );
}
