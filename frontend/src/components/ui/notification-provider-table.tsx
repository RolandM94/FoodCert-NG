"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, Loader2, Play, Star, Plus } from "lucide-react";
import { useState } from "react";
import { listProviders, setDefaultProvider, testProvider } from "@/lib/api/notifications";
import type { NotificationProvider } from "@/types/notifications";

export function NotificationProviderTable({
  onEdit,
  onCreate,
}: {
  onEdit?: (provider: NotificationProvider) => void;
  onCreate?: () => void;
}) {
  const queryClient = useQueryClient();
  const [testing, setTesting] = useState<string | null>(null);
  const [testResults, setTestResults] = useState<Record<string, { ok: boolean; error?: string }>>({});

  const { data: providers = [], isLoading } = useQuery({
    queryKey: ["notification-providers"],
    queryFn: listProviders,
  });

  const setDefaultMutation = useMutation({
    mutationFn: setDefaultProvider,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notification-providers"] }),
  });

  async function handleTest(id: string) {
    setTesting(id);
    try {
      const result = await testProvider(id);
      setTestResults({ ...testResults, [id]: { ok: result.success, error: result.error } });
    } catch (err) {
      setTestResults({ ...testResults, [id]: { ok: false, error: err instanceof Error ? err.message : "Test failed" } });
    } finally {
      setTesting(null);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-bold text-neutral-900">Notification Providers</h3>
        {onCreate ? (
          <button
            className="inline-flex h-10 items-center gap-1.5 rounded bg-brand-600 px-4 text-sm font-bold text-white hover:bg-brand-700"
            onClick={onCreate}
            type="button"
          >
            <Plus aria-hidden="true" size={16} />
            Add Provider
          </button>
        ) : null}
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="animate-spin text-neutral-400" size={24} />
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {providers.map((p) => {
            const result = testResults[p.id];
            return (
              <div key={p.id} className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-bold text-neutral-900">{p.name}</h4>
                      {p.is_default ? (
                        <span className="inline-flex items-center gap-1 rounded bg-warning-100 px-1.5 py-0.5 text-xs font-bold text-warning-700">
                          <Star size={12} /> Default
                        </span>
                      ) : null}
                    </div>
                    <p className="mt-1 text-sm text-neutral-600 capitalize">{p.channel_display}</p>
                    {p.sender_id ? (
                      <p className="mt-0.5 text-xs text-neutral-400">Sender: {p.sender_id}</p>
                    ) : null}
                  </div>
                  <span
                    className={`inline-block rounded-full px-2 py-0.5 text-xs font-semibold ${
                      p.is_active ? "bg-brand-100 text-brand-800" : "bg-neutral-100 text-neutral-500"
                    }`}
                  >
                    {p.is_active ? "Active" : "Inactive"}
                  </span>
                </div>

                {result ? (
                  <p className={`mt-2 rounded p-2 text-xs font-semibold ${result.ok ? "bg-brand-50 text-brand-700" : "bg-danger-50 text-danger-700"}`}>
                    {result.ok ? "Connection OK" : result.error}
                  </p>
                ) : null}

                <div className="mt-3 flex items-center gap-2">
                  <button
                    className="inline-flex h-8 items-center gap-1 rounded border border-neutral-200 px-2.5 text-xs font-semibold text-neutral-700 hover:bg-neutral-50 disabled:opacity-50"
                    disabled={testing === p.id}
                    onClick={() => handleTest(p.id)}
                    type="button"
                  >
                    {testing === p.id ? <Loader2 className="animate-spin" size={14} /> : <Play size={14} />}
                    Test
                  </button>
                  {onEdit ? (
                    <button
                      className="inline-flex h-8 items-center gap-1 rounded border border-neutral-200 px-2.5 text-xs font-semibold text-neutral-700 hover:bg-neutral-50"
                      onClick={() => onEdit(p)}
                      type="button"
                    >
                      Edit
                    </button>
                  ) : null}
                  {!p.is_default ? (
                    <button
                      className="inline-flex h-8 items-center gap-1 rounded border border-neutral-200 px-2.5 text-xs font-semibold text-neutral-700 hover:bg-warning-50 hover:text-warning-700"
                      onClick={() => setDefaultMutation.mutate(p.id)}
                      type="button"
                    >
                      <Star size={14} />
                      Set Default
                    </button>
                  ) : null}
                </div>
              </div>
            );
          })}
          {!providers.length ? (
            <p className="col-span-2 py-8 text-center text-sm text-neutral-500">No providers configured.</p>
          ) : null}
        </div>
      )}
    </div>
  );
}
