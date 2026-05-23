import { apiClient, unwrap, type ApiEnvelope } from "@/lib/api/client";
import type { LabTest } from "@/types/assessments";

export async function listLabRequests(params?: Record<string, string>): Promise<LabTest[]> {
  const response = await apiClient.get<ApiEnvelope<LabTest[]>>("/lab/requests/", { params });
  return unwrap(response.data);
}

export async function getLabRequest(id: string): Promise<LabTest> {
  const response = await apiClient.get<ApiEnvelope<LabTest>>(`/lab/requests/${id}/`);
  return unwrap(response.data);
}

export async function markLabSampleCollected(id: string, payload: Record<string, unknown> = {}): Promise<LabTest> {
  const response = await apiClient.patch<ApiEnvelope<LabTest>>(`/lab/requests/${id}/sample-collected/`, payload);
  return unwrap(response.data);
}

export async function submitLabResult(id: string, payload: Record<string, unknown>): Promise<LabTest> {
  const response = await apiClient.patch<ApiEnvelope<LabTest>>(`/lab/requests/${id}/result/`, payload);
  return unwrap(response.data);
}

export async function uploadLabResultDocument(id: string, payload: FormData): Promise<LabTest> {
  const response = await apiClient.post<ApiEnvelope<LabTest>>(`/lab/requests/${id}/upload-result/`, payload, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return unwrap(response.data);
}

export async function submitLabResultToDoctor(id: string, payload: Record<string, unknown> = {}): Promise<LabTest> {
  const response = await apiClient.patch<ApiEnvelope<LabTest>>(`/lab/requests/${id}/submit-to-doctor/`, payload);
  return unwrap(response.data);
}

export async function reviewLabRequest(id: string, payload: Record<string, unknown> = {}): Promise<LabTest> {
  const response = await apiClient.post<ApiEnvelope<LabTest>>(`/lab/requests/${id}/review/`, payload);
  return unwrap(response.data);
}

export async function requestRepeatLabTest(id: string, payload: { reason: string; test_name?: string }): Promise<LabTest> {
  const response = await apiClient.post<ApiEnvelope<LabTest>>(`/lab-tests/${id}/request-repeat/`, payload);
  return unwrap(response.data);
}
