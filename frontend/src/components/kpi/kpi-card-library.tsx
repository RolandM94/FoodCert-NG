"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Sparkles, X } from "lucide-react";

import { KpiCard } from "@/components/kpi/kpi-card";
import { getApiErrorMessage } from "@/lib/api/client";
import { generateKpiCard, instantiateKpiCard, listKpiCards } from "@/lib/api/kpi-cards";
import type { KpiCard as KpiCardConfig, KpiCardDraftConfig } from "@/types/kpi-cards";

export function KpiCardLibrary({
  onAddToSurface,
  addLabel = "Add to canvas",
  showInstantiate = true,
  onClose,
}: {
  /** Called with the chosen card when the user adds it to the current surface. */
  onAddToSurface?: (card: KpiCardConfig) => void;
  addLabel?: string;
  /** Show the "Add as widget" action (creates worksheet + widget from the registry). */
  showInstantiate?: boolean;
  onClose?: () => void;
}) {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [prompt, setPrompt] = useState("");
  const [draft, setDraft] = useState<KpiCardDraftConfig | null>(null);
  const [feedback, setFeedback] = useState<{ tone: "ok" | "error"; text: string } | null>(null);

  const libraryQuery = useQuery({ queryKey: ["kpi-card-library"], queryFn: () => listKpiCards(), staleTime: 300_000 });
  const cards = useMemo(() => (Array.isArray(libraryQuery.data) ? libraryQuery.data : []), [libraryQuery.data]);

  const categories = useMemo(
    () => Array.from(new Set(cards.map((card) => card.category))).sort(),
    [cards],
  );

  const visible = useMemo(() => {
    const needle = search.trim().toLowerCase();
    return cards.filter((card) => {
      if (category && card.category !== category) return false;
      if (!needle) return true;
      return (
        card.title.toLowerCase().includes(needle)
        || card.code.toLowerCase().includes(needle)
        || card.description.toLowerCase().includes(needle)
      );
    });
  }, [cards, search, category]);

  const grouped = useMemo(() => {
    const groups = new Map<string, KpiCardConfig[]>();
    for (const card of visible) {
      const list = groups.get(card.category) ?? [];
      list.push(card);
      groups.set(card.category, list);
    }
    return Array.from(groups.entries()).sort(([a], [b]) => a.localeCompare(b));
  }, [visible]);

  const instantiate = useMutation({
    mutationFn: (id: string) => instantiateKpiCard(id),
    onSuccess: (data) => setFeedback({ tone: "ok", text: `Widget created from “${data.kpi_card_code}” — available in your widget list.` }),
    onError: (error) => setFeedback({ tone: "error", text: getApiErrorMessage(error, "Could not create a widget from this card.") }),
  });

  const generate = useMutation({
    mutationFn: (save: boolean) => generateKpiCard(prompt, save),
    onSuccess: (data, save) => {
      setDraft(data.config);
      if (save && data.saved) {
        setFeedback({ tone: "ok", text: `Saved “${data.saved.title}” to the library.` });
        queryClient.invalidateQueries({ queryKey: ["kpi-card-library"] });
        setDraft(null);
        setPrompt("");
      }
    },
    onError: (error) => setFeedback({ tone: "error", text: getApiErrorMessage(error, "Could not generate a KPI card.") }),
  });

  return (
    <section className="grid gap-4 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
      <div className="flex flex-wrap items-center gap-3">
        <h3 className="text-sm font-bold text-neutral-900">KPI card library</h3>
        <span className="text-xs text-neutral-500">{cards.length} cards</span>
        {onClose ? (
          <button className="ml-auto text-neutral-400 hover:text-neutral-700" onClick={onClose} type="button" aria-label="Close library">
            <X size={16} />
          </button>
        ) : null}
      </div>

      <div className="flex flex-wrap gap-2">
        <input
          className="h-10 min-w-56 flex-1 rounded-md border border-neutral-200 bg-neutral-50 px-3 text-sm"
          placeholder="Search cards…"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
        <select
          className="h-10 rounded-md border border-neutral-200 bg-white px-3 text-sm"
          value={category}
          onChange={(event) => setCategory(event.target.value)}
        >
          <option value="">All categories</option>
          {categories.map((item) => <option key={item} value={item}>{item}</option>)}
        </select>
      </div>

      {feedback ? (
        <p className={`rounded px-3 py-2 text-sm font-semibold ${feedback.tone === "ok" ? "bg-brand-50 text-brand-700" : "bg-danger-50 text-danger-700"}`}>
          {feedback.text}
        </p>
      ) : null}

      <div className="grid max-h-[28rem] gap-4 overflow-y-auto pr-1">
        {libraryQuery.isLoading ? <p className="text-sm text-neutral-500">Loading library…</p> : null}
        {grouped.map(([groupName, groupCards]) => (
          <div key={groupName} className="grid gap-2">
            <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">{groupName}</p>
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {groupCards.map((card) => (
                <div key={card.code} className="grid gap-2">
                  <KpiCard config={card} />
                  <div className="flex gap-1.5">
                    {onAddToSurface ? (
                      <button
                        className="inline-flex h-8 items-center rounded-md bg-brand-600 px-2.5 text-xs font-semibold text-white hover:bg-brand-700"
                        onClick={() => onAddToSurface(card)}
                        type="button"
                      >
                        {addLabel}
                      </button>
                    ) : null}
                    {showInstantiate && card.source_type === "dataset" ? (
                      <button
                        className="inline-flex h-8 items-center rounded-md border border-neutral-200 bg-white px-2.5 text-xs font-semibold text-neutral-700 hover:bg-neutral-50 disabled:opacity-50"
                        disabled={instantiate.isPending}
                        onClick={() => instantiate.mutate(card.id)}
                        type="button"
                      >
                        Add as widget
                      </button>
                    ) : null}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
        {!libraryQuery.isLoading && visible.length === 0 ? (
          <p className="text-sm text-neutral-500">No cards match this search.</p>
        ) : null}
      </div>

      <div className="grid gap-2 rounded-lg border border-neutral-200 bg-neutral-50 p-3">
        <p className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wide text-neutral-600">
          <Sparkles size={13} /> Ask AI for a new card
        </p>
        <div className="flex flex-wrap gap-2">
          <input
            className="h-10 min-w-56 flex-1 rounded-md border border-neutral-200 bg-white px-3 text-sm"
            placeholder="e.g. average inspection compliance score"
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
          />
          <button
            className="inline-flex h-10 items-center rounded-md border border-neutral-200 bg-white px-3 text-sm font-semibold text-neutral-700 hover:bg-neutral-100 disabled:opacity-50"
            disabled={generate.isPending || !prompt.trim()}
            onClick={() => generate.mutate(false)}
            type="button"
          >
            Draft
          </button>
          <button
            className="inline-flex h-10 items-center rounded-md bg-brand-600 px-3 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-50"
            disabled={generate.isPending || !prompt.trim()}
            onClick={() => generate.mutate(true)}
            type="button"
          >
            Draft &amp; save to library
          </button>
        </div>
        {draft ? (
          <div className="rounded-md border border-neutral-200 bg-white p-3 text-sm text-neutral-700">
            <p className="font-semibold text-neutral-900">{draft.title}</p>
            <p className="text-xs text-neutral-500">
              {draft.dataset_code} · {draft.aggregation}{draft.metric ? ` of ${draft.metric}` : ""} · {draft.format}
            </p>
            <p className="mt-1 text-xs text-warning-700">AI draft — review before saving to the library.</p>
          </div>
        ) : null}
      </div>
    </section>
  );
}
