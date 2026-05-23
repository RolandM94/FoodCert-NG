import { apiClient, unwrap, type ApiEnvelope } from "@/lib/api/client";
import type { FacilityAccreditationApplication, FacilityDocument, FacilityInvite, FacilityStaffProfile, MedicalFacility } from "@/types/facilities";

export async function listMedicalFacilities(): Promise<MedicalFacility[]> {
  const response = await apiClient.get<ApiEnvelope<MedicalFacility[]>>("/medical-facilities/");
  return unwrap(response.data);
}

export async function getCurrentMedicalFacility(): Promise<MedicalFacility> {
  const response = await apiClient.get<ApiEnvelope<MedicalFacility>>("/medical-facilities/me/");
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

export async function updateCurrentMedicalFacility(payload: Record<string, unknown>): Promise<MedicalFacility> {
  const response = await apiClient.patch<ApiEnvelope<MedicalFacility>>("/medical-facilities/me/", payload);
  return unwrap(response.data);
}

export async function startFacilityReAccreditation(id: string): Promise<FacilityAccreditationApplication> {
  const response = await apiClient.post<ApiEnvelope<FacilityAccreditationApplication>>(`/medical-facilities/${id}/re-accreditation/`);
  return unwrap(response.data);
}

export async function listFacilityAccreditations(): Promise<FacilityAccreditationApplication[]> {
  const response = await apiClient.get<ApiEnvelope<FacilityAccreditationApplication[]>>("/facility-accreditation/");
  return unwrap(response.data);
}

export async function createFacilityAccreditation(
  payload: FormData | Record<string, unknown>
): Promise<FacilityAccreditationApplication> {
  const response = await apiClient.post<ApiEnvelope<FacilityAccreditationApplication>>("/facility-accreditation/", payload);
  return unwrap(response.data);
}

export async function updateFacilityAccreditation(
  id: string,
  payload: Record<string, unknown>
): Promise<FacilityAccreditationApplication> {
  const response = await apiClient.patch<ApiEnvelope<FacilityAccreditationApplication>>(`/facility-accreditation/${id}/`, payload);
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

export async function listFacilityDocuments(params?: {
  facility?: string;
  accreditation_application?: string;
}): Promise<FacilityDocument[]> {
  const response = await apiClient.get<ApiEnvelope<FacilityDocument[]>>("/facility-documents/", { params });
  return unwrap(response.data);
}

export async function uploadFacilityDocument(payload: FormData): Promise<FacilityDocument> {
  const response = await apiClient.post<ApiEnvelope<FacilityDocument>>("/facility-documents/", payload, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return unwrap(response.data);
}

export async function listFacilityStaff(facilityId: string): Promise<FacilityStaffProfile[]> {
  const response = await apiClient.get<ApiEnvelope<FacilityStaffProfile[]>>(`/medical-facilities/${facilityId}/staff/`);
  return unwrap(response.data);
}

export async function updateFacilityStaff(
  facilityId: string,
  staffProfileId: string,
  payload: Record<string, unknown>
): Promise<FacilityStaffProfile> {
  const response = await apiClient.patch<ApiEnvelope<FacilityStaffProfile>>(
    `/medical-facilities/${facilityId}/staff/${staffProfileId}/`,
    payload
  );
  return unwrap(response.data);
}

export async function suspendFacilityStaff(facilityId: string, staffProfileId: string): Promise<FacilityStaffProfile> {
  const response = await apiClient.patch<ApiEnvelope<FacilityStaffProfile>>(
    `/medical-facilities/${facilityId}/staff/${staffProfileId}/suspend/`
  );
  return unwrap(response.data);
}

export async function reactivateFacilityStaff(facilityId: string, staffProfileId: string): Promise<FacilityStaffProfile> {
  const response = await apiClient.patch<ApiEnvelope<FacilityStaffProfile>>(
    `/medical-facilities/${facilityId}/staff/${staffProfileId}/reactivate/`
  );
  return unwrap(response.data);
}

export async function listFacilityInvites(facilityId: string): Promise<FacilityInvite[]> {
  const response = await apiClient.get<ApiEnvelope<FacilityInvite[]>>(`/medical-facilities/${facilityId}/invites/`);
  return unwrap(response.data);
}

export async function createFacilityInvite(facilityId: string, payload: Record<string, unknown>): Promise<FacilityInvite> {
  const response = await apiClient.post<ApiEnvelope<FacilityInvite>>(`/medical-facilities/${facilityId}/invites/`, payload);
  return unwrap(response.data);
}

export async function revokeFacilityInvite(facilityId: string, inviteId: string): Promise<FacilityInvite> {
  const response = await apiClient.delete<ApiEnvelope<FacilityInvite>>(`/medical-facilities/${facilityId}/invites/${inviteId}/`);
  return unwrap(response.data);
}
