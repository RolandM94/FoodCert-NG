import { apiClient, unwrap, type ApiEnvelope } from "@/lib/api/client";
import type { IllnessReport } from "@/types/illness";

export async function createIllnessReport(payload: Record<string, unknown>): Promise<IllnessReport> {
  const response = await apiClient.post<ApiEnvelope<IllnessReport>>("/illness-reports/", payload);
  return unwrap(response.data);
}

export async function listIllnessReports(): Promise<IllnessReport[]> {
  const response = await apiClient.get<ApiEnvelope<IllnessReport[]>>("/illness-reports/");
  return unwrap(response.data);
}

export async function getIllnessReport(id: string): Promise<IllnessReport> {
  const response = await apiClient.get<ApiEnvelope<IllnessReport>>(`/illness-reports/${id}/`);
  return unwrap(response.data);
}

export async function reviewIllnessReport(id: string, payload: Record<string, unknown>): Promise<IllnessReport> {
  const response = await apiClient.patch<ApiEnvelope<IllnessReport>>(`/illness-reports/${id}/review/`, payload);
  return unwrap(response.data);
}

export async function clearIllnessReport(id: string, payload: { cleared: boolean; notes?: string }): Promise<IllnessReport> {
  const response = await apiClient.patch<ApiEnvelope<IllnessReport>>(`/illness-reports/${id}/clearance/`, payload);
  return unwrap(response.data);
}
