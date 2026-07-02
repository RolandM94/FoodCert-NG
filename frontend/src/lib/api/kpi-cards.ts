import type { KpiCard, KpiCardDraftConfig, KpiCardResolved } from "@/types/kpi-cards";

import { type ApiEnvelope, apiClient, unwrap } from "./client";

const BASE = "/analytics/kpi-cards";

export async function listKpiCards(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<KpiCard[]>>(`${BASE}/`, { params });
  return unwrap(res.data);
}

export async function createKpiCard(data: Partial<KpiCard>) {
  const res = await apiClient.post<ApiEnvelope<KpiCard>>(`${BASE}/`, data);
  return unwrap(res.data);
}

export async function updateKpiCard(id: string, data: Partial<KpiCard>) {
  const res = await apiClient.patch<ApiEnvelope<KpiCard>>(`${BASE}/${id}/`, data);
  return unwrap(res.data);
}

export async function resolveKpiCard(id: string) {
  const res = await apiClient.post<ApiEnvelope<KpiCardResolved & { code: string }>>(`${BASE}/${id}/resolve/`);
  return unwrap(res.data);
}

export async function resolveKpiCardConfig(config: KpiCardDraftConfig) {
  const res = await apiClient.post<ApiEnvelope<KpiCardResolved>>(`${BASE}/resolve-config/`, { config });
  return unwrap(res.data);
}

export async function instantiateKpiCard(id: string) {
  const res = await apiClient.post<ApiEnvelope<{ widget_id: string; worksheet_id: string; kpi_card_code: string }>>(
    `${BASE}/${id}/instantiate/`,
  );
  return unwrap(res.data);
}

export async function generateKpiCard(prompt: string, save = false) {
  const res = await apiClient.post<ApiEnvelope<{ config: KpiCardDraftConfig; saved: KpiCard | null }>>(
    `${BASE}/generate/`,
    { prompt, save },
  );
  return unwrap(res.data);
}
