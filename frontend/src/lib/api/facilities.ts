import { apiClient, unwrap, type ApiEnvelope } from "@/lib/api/client";
import type { FacilityAccreditationApplication, MedicalFacility } from "@/types/facilities";

export async function listMedicalFacilities(): Promise<MedicalFacility[]> {
  const response = await apiClient.get<ApiEnvelope<MedicalFacility[]>>("/medical-facilities/");
  return unwrap(response.data);
}

export async function createMedicalFacility(payload: Record<string, unknown>): Promise<MedicalFacility> {
  const response = await apiClient.post<ApiEnvelope<MedicalFacility>>("/medical-facilities/", payload);
  return unwrap(response.data);
}

export async function updateMedicalFacility(id: string, payload: Record<string, unknown>): Promise<MedicalFacility> {
  const response = await apiClient.patch<ApiEnvelope<MedicalFacility>>(`/medical-facilities/${id}/`, payload);
  return unwrap(response.data);
}

export async function createFacilityAccreditation(
  payload: FormData | Record<string, unknown>
): Promise<FacilityAccreditationApplication> {
  const response = await apiClient.post<ApiEnvelope<FacilityAccreditationApplication>>("/facility-accreditation/", payload);
  return unwrap(response.data);
}

export async function submitFacilityAccreditation(id: string): Promise<FacilityAccreditationApplication> {
  const response = await apiClient.patch<ApiEnvelope<FacilityAccreditationApplication>>(`/facility-accreditation/${id}/submit/`);
  return unwrap(response.data);
}

export async function approveFacilityAccreditation(id: string, review_comment = "") {
  const response = await apiClient.patch<ApiEnvelope<FacilityAccreditationApplication>>(
    `/facility-accreditation/${id}/approve/`,
    { review_comment }
  );
  return unwrap(response.data);
}

export async function rejectFacilityAccreditation(id: string, review_comment = "") {
  const response = await apiClient.patch<ApiEnvelope<FacilityAccreditationApplication>>(
    `/facility-accreditation/${id}/reject/`,
    { review_comment }
  );
  return unwrap(response.data);
}

export async function suspendFacilityAccreditation(id: string, review_comment = "") {
  const response = await apiClient.patch<ApiEnvelope<FacilityAccreditationApplication>>(
    `/facility-accreditation/${id}/suspend/`,
    { review_comment }
  );
  return unwrap(response.data);
}

export async function reactivateFacilityAccreditation(id: string, review_comment = "") {
  const response = await apiClient.patch<ApiEnvelope<FacilityAccreditationApplication>>(
    `/facility-accreditation/${id}/reactivate/`,
    { review_comment }
  );
  return unwrap(response.data);
}
