import { apiClient, unwrap, type ApiEnvelope } from "@/lib/api/client";
import type { Certificate, CertificateRequest, PublicCertificateVerification } from "@/types/certificates";

export async function requestCertificate(assessmentId: string, request_notes = ""): Promise<CertificateRequest> {
  const response = await apiClient.post<ApiEnvelope<CertificateRequest>>(
    `/assessments/${assessmentId}/request-certificate/`,
    { request_notes }
  );
  return unwrap(response.data);
}

export async function listCertificateRequests(): Promise<CertificateRequest[]> {
  const response = await apiClient.get<ApiEnvelope<CertificateRequest[]>>("/certificate-requests/");
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

export async function listCertificates(): Promise<Certificate[]> {
  const response = await apiClient.get<ApiEnvelope<Certificate[]>>("/certificates/");
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
