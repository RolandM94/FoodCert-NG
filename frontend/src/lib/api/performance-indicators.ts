import type {
  IndicatorAdoption,
  IndicatorAIExplanation,
  IndicatorAIFormula,
  IndicatorAISuggestion,
  IndicatorManualEntry,
  IndicatorTarget,
  IndicatorThreshold,
  MEIndicator,
  MEIndicatorValue,
  PIOverview,
} from "@/types/standards";

import { type ApiEnvelope, apiClient, unwrap } from "./client";

const BASE = "/federal/standards";

// --- Indicator library & lifecycle ---

export async function listPerformanceIndicators(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<MEIndicator[]>>(`${BASE}/me-indicators/`, { params });
  return unwrap(res.data);
}

export async function getPerformanceIndicator(id: string) {
  const res = await apiClient.get<ApiEnvelope<MEIndicator>>(`${BASE}/me-indicators/${id}/`);
  return unwrap(res.data);
}

export async function publishPerformanceIndicator(id: string) {
  const res = await apiClient.post<ApiEnvelope<MEIndicator>>(`${BASE}/me-indicators/${id}/publish/`);
  return unwrap(res.data);
}

export async function setIndicatorLifecycle(id: string, lifecycle_status: string) {
  const res = await apiClient.post<ApiEnvelope<MEIndicator>>(`${BASE}/me-indicators/${id}/set-lifecycle/`, { lifecycle_status });
  return unwrap(res.data);
}

export async function shareIndicatorToStates(id: string, stateIds?: string[]) {
  const res = await apiClient.post<ApiEnvelope<{ shared_with: number; new_adoption_records: number }>>(
    `${BASE}/me-indicators/${id}/share-to-states/`,
    stateIds ? { state_ids: stateIds } : {},
  );
  return unwrap(res.data);
}

export async function adoptFederalIndicator(id: string, stateId?: string) {
  const res = await apiClient.post<ApiEnvelope<IndicatorAdoption>>(
    `${BASE}/me-indicators/${id}/adopt/`,
    stateId ? { state_id: stateId } : {},
  );
  return unwrap(res.data);
}

export async function cloneFederalIndicator(id: string, stateId?: string) {
  const res = await apiClient.post<ApiEnvelope<MEIndicator>>(
    `${BASE}/me-indicators/${id}/clone/`,
    stateId ? { state_id: stateId } : {},
  );
  return unwrap(res.data);
}

export async function getIndicatorStateAdoption(id: string) {
  const res = await apiClient.get<ApiEnvelope<IndicatorAdoption[]>>(`${BASE}/me-indicators/${id}/state-adoption/`);
  return unwrap(res.data);
}

export async function calculateIndicatorNow(id: string) {
  const res = await apiClient.post<ApiEnvelope<Record<string, unknown>>>(`${BASE}/me-indicators/${id}/calculate/`, {});
  return unwrap(res.data);
}

// --- Overview ---

export async function getPIOverview() {
  const res = await apiClient.get<ApiEnvelope<PIOverview>>(`${BASE}/me-indicators/pi-overview/`);
  return unwrap(res.data);
}

// --- Targets ---

export async function listIndicatorTargets(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<IndicatorTarget[]>>(`${BASE}/indicator-targets/`, { params });
  return unwrap(res.data);
}

export async function createIndicatorTarget(data: Partial<IndicatorTarget>) {
  const res = await apiClient.post<ApiEnvelope<IndicatorTarget>>(`${BASE}/indicator-targets/`, data);
  return unwrap(res.data);
}

export async function updateIndicatorTarget(id: string, data: Partial<IndicatorTarget>) {
  const res = await apiClient.patch<ApiEnvelope<IndicatorTarget>>(`${BASE}/indicator-targets/${id}/`, data);
  return unwrap(res.data);
}

export async function deleteIndicatorTarget(id: string) {
  await apiClient.delete(`${BASE}/indicator-targets/${id}/`);
}

// --- Thresholds ---

export async function listIndicatorThresholds(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<IndicatorThreshold[]>>(`${BASE}/indicator-thresholds/`, { params });
  return unwrap(res.data);
}

export async function createIndicatorThreshold(data: Partial<IndicatorThreshold>) {
  const res = await apiClient.post<ApiEnvelope<IndicatorThreshold>>(`${BASE}/indicator-thresholds/`, data);
  return unwrap(res.data);
}

export async function updateIndicatorThreshold(id: string, data: Partial<IndicatorThreshold>) {
  const res = await apiClient.patch<ApiEnvelope<IndicatorThreshold>>(`${BASE}/indicator-thresholds/${id}/`, data);
  return unwrap(res.data);
}

export async function deleteIndicatorThreshold(id: string) {
  await apiClient.delete(`${BASE}/indicator-thresholds/${id}/`);
}

// --- Adoptions ---

export async function listIndicatorAdoptions(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<IndicatorAdoption[]>>(`${BASE}/indicator-adoptions/`, { params });
  return unwrap(res.data);
}

// --- Manual entries ---

export async function listIndicatorManualEntries(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<IndicatorManualEntry[]>>(`${BASE}/indicator-manual-entries/`, { params });
  return unwrap(res.data);
}

export async function createIndicatorManualEntry(data: Partial<IndicatorManualEntry>) {
  const res = await apiClient.post<ApiEnvelope<IndicatorManualEntry>>(`${BASE}/indicator-manual-entries/`, data);
  return unwrap(res.data);
}

export async function actionIndicatorManualEntry(id: string, action: "submit" | "approve" | "reject", comment = "") {
  const res = await apiClient.post<ApiEnvelope<IndicatorManualEntry>>(
    `${BASE}/indicator-manual-entries/${id}/${action}/`,
    { comment },
  );
  return unwrap(res.data);
}

// --- Results ---

export async function listIndicatorResults(indicatorId: string) {
  const res = await apiClient.get<ApiEnvelope<MEIndicatorValue[]>>(`${BASE}/me-indicators/${indicatorId}/values/`);
  return unwrap(res.data);
}

// --- AI ---

export async function aiSuggestIndicators(prompt: string) {
  const res = await apiClient.post<ApiEnvelope<{ suggestions: IndicatorAISuggestion[] }>>(
    `${BASE}/me-indicators/ai/suggest/`,
    { prompt },
  );
  return unwrap(res.data);
}

export async function aiGenerateIndicatorFormula(prompt: string) {
  const res = await apiClient.post<ApiEnvelope<{ formula: IndicatorAIFormula }>>(
    `${BASE}/me-indicators/ai/generate-formula/`,
    { prompt },
  );
  return unwrap(res.data);
}

export async function aiExplainIndicatorResult(id: string) {
  const res = await apiClient.post<ApiEnvelope<IndicatorAIExplanation>>(
    `${BASE}/me-indicators/${id}/ai/explain-result/`,
  );
  return unwrap(res.data);
}
