import { apiClient, unwrap, type ApiEnvelope } from "@/lib/api/client";
import type { Certificate, CertificateRequest, PublicCertificateVerification } from "@/types/certificates";

export async function requestCertificate(assessmentId: string, request_notes = ""): Promise<CertificateRequest> {
  const response = await apiClient.post<ApiEnvelope<CertificateRequest>>(
    `/assessments/${assessmentId}/request-certificate/`,
    { request_notes }
  );
  return unwrap(response.data);
}

export async function submitFacilityAssessmentToState(facilityId: string, assessmentId: string, request_notes = ""): Promise<CertificateRequest> {
  const response = await apiClient.post<ApiEnvelope<CertificateRequest>>(
    `/facilities/${facilityId}/assessments/${assessmentId}/submit-to-state/`,
    { request_notes }
  );
  return unwrap(response.data);
}

export async function submitAssessmentToState(assessmentId: string, request_notes = ""): Promise<CertificateRequest> {
  const response = await apiClient.post<ApiEnvelope<CertificateRequest>>(
    `/assessments/${assessmentId}/submit-to-state/`,
    { request_notes }
  );
  return unwrap(response.data);
}

export async function respondFacilityCertificateClarification(facilityId: string, assessmentId: string, responseText: string): Promise<CertificateRequest> {
  const response = await apiClient.post<ApiEnvelope<CertificateRequest>>(
    `/facilities/${facilityId}/assessments/${assessmentId}/respond-to-clarification/`,
    { response: responseText }
  );
  return unwrap(response.data);
}

export async function listCertificateRequests(params?: Record<string, string>): Promise<CertificateRequest[]> {
  const response = await apiClient.get<ApiEnvelope<CertificateRequest[]>>("/certificate-requests/", { params });
  return unwrap(response.data);
}

export async function approveCertificateRequest(id: string, review_notes = ""): Promise<CertificateRequest> {
  const response = await apiClient.patch<ApiEnvelope<CertificateRequest>>(`/certificate-requests/${id}/approve/`, {
    review_notes
  });
  return unwrap(response.data);
}

export async function rejectCertificateRequest(id: string, review_notes = ""): Promise<CertificateRequest> {
  const response = await apiClient.patch<ApiEnvelope<CertificateRequest>>(`/certificate-requests/${id}/reject/`, {
    review_notes
  });
  return unwrap(response.data);
}

export async function generateCertificate(payload: {
  assessment?: string;
  certificate_request?: string;
}): Promise<Certificate> {
  const response = await apiClient.post<ApiEnvelope<Certificate>>("/certificates/generate/", payload);
  return unwrap(response.data);
}

export async function listCertificates(params?: Record<string, string>): Promise<Certificate[]> {
  const response = await apiClient.get<ApiEnvelope<Certificate[]>>("/certificates/", { params });
  return unwrap(response.data);
}

export async function getCertificate(id: string): Promise<Certificate> {
  const response = await apiClient.get<ApiEnvelope<Certificate>>(`/certificates/${id}/`);
  return unwrap(response.data);
}

export async function revokeCertificate(id: string, reason = ""): Promise<Certificate> {
  const response = await apiClient.patch<ApiEnvelope<Certificate>>(`/certificates/${id}/revoke/`, { reason });
  return unwrap(response.data);
}

export async function suspendCertificate(id: string, reason = ""): Promise<Certificate> {
  const response = await apiClient.patch<ApiEnvelope<Certificate>>(`/certificates/${id}/suspend/`, { reason });
  return unwrap(response.data);
}

export async function publicVerifyCertificate(certificateNumber: string): Promise<PublicCertificateVerification> {
  const response = await apiClient.get<ApiEnvelope<PublicCertificateVerification>>(
    `/public/certificates/verify/${certificateNumber}/`
  );
  return unwrap(response.data);
}
