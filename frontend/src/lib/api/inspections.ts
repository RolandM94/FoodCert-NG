import { apiClient, unwrap, type ApiEnvelope } from "@/lib/api/client";
import type {
  EmployerInspectionDetail,
  EmployerInspectionSummary,
  Inspection,
  InspectionCertificateScan,
  InspectionResponse,
  InspectionResponseType
} from "@/types/inspections";

export async function createInspection(payload: Record<string, unknown>): Promise<Inspection> {
  const response = await apiClient.post<ApiEnvelope<Inspection>>("/inspections/", payload);
  return unwrap(response.data);
}

export async function listInspections(): Promise<Inspection[]> {
  const response = await apiClient.get<ApiEnvelope<Inspection[]>>("/inspections/");
  return unwrap(response.data);
}

export async function getInspection(id: string): Promise<Inspection> {
  const response = await apiClient.get<ApiEnvelope<Inspection>>(`/inspections/${id}/`);
  return unwrap(response.data);
}

export async function updateInspection(id: string, payload: Record<string, unknown>): Promise<Inspection> {
  const response = await apiClient.patch<ApiEnvelope<Inspection>>(`/inspections/${id}/`, payload);
  return unwrap(response.data);
}

export async function submitInspection(id: string): Promise<Inspection> {
  const response = await apiClient.patch<ApiEnvelope<Inspection>>(`/inspections/${id}/submit/`);
  return unwrap(response.data);
}

export async function addInspectionEvidence(id: string, payload: Record<string, unknown>): Promise<Inspection> {
  const response = await apiClient.post<ApiEnvelope<Inspection>>(`/inspections/${id}/evidence/`, payload);
  return unwrap(response.data);
}

export async function scanInspectionCertificate(id: string, certificate_number: string): Promise<InspectionCertificateScan> {
  const response = await apiClient.post<ApiEnvelope<InspectionCertificateScan>>(`/inspections/${id}/scan-certificate/`, {
    certificate_number
  });
  return unwrap(response.data);
}

export type EmployerInspectionFilters = {
  branch?: string;
  status?: string;
  date_from?: string;
  date_to?: string;
};

export async function listEmployerInspections(
  employerId: string,
  filters: EmployerInspectionFilters = {}
): Promise<EmployerInspectionSummary[]> {
  const response = await apiClient.get<ApiEnvelope<EmployerInspectionSummary[]>>(`/employers/${employerId}/inspections/`, {
    params: filters
  });
  return unwrap(response.data);
}

export async function getEmployerInspection(employerId: string, inspectionId: string): Promise<EmployerInspectionDetail> {
  const response = await apiClient.get<ApiEnvelope<EmployerInspectionDetail>>(`/employers/${employerId}/inspections/${inspectionId}/`);
  return unwrap(response.data);
}

export async function submitEmployerInspectionResponse(
  employerId: string,
  inspectionId: string,
  payload: { response_type: InspectionResponseType; content?: string; evidence_file_url?: string }
): Promise<InspectionResponse> {
  const response = await apiClient.post<ApiEnvelope<InspectionResponse>>(
    `/employers/${employerId}/inspections/${inspectionId}/responses/`,
    payload
  );
  return unwrap(response.data);
}
