import { apiClient, unwrap, type ApiEnvelope } from "@/lib/api/client";
import type { Certificate, CertificateRequest, PublicCertificateVerification } from "@/types/certificates";

export type CertificateTemplate = {
  id: string;
  name: string;
  scope: "national" | "state";
  state?: string | null;
  state_name?: string;
  ministry_name: string;
  subtitle: string;
  logo_url: string;
  accent_color: string;
  signatory_name: string;
  signatory_title: string;
  footer_note: string;
  is_active: boolean;
  is_default: boolean;
  created_by?: string | null;
  created_by_name?: string;
  created_at: string;
  updated_at: string;
};

export type CertificateTemplatePayload = Partial<Omit<CertificateTemplate, "id" | "state_name" | "created_by" | "created_by_name" | "created_at" | "updated_at">>;

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

export async function listCertificateTemplates(params?: Record<string, string>): Promise<CertificateTemplate[]> {
  const response = await apiClient.get<ApiEnvelope<CertificateTemplate[]>>("/certificate-templates/", { params });
  return unwrap(response.data);
}

export async function createCertificateTemplate(payload: CertificateTemplatePayload): Promise<CertificateTemplate> {
  const response = await apiClient.post<ApiEnvelope<CertificateTemplate>>("/certificate-templates/", payload);
  return unwrap(response.data);
}

export async function updateCertificateTemplate(id: string, payload: CertificateTemplatePayload): Promise<CertificateTemplate> {
  const response = await apiClient.patch<ApiEnvelope<CertificateTemplate>>(`/certificate-templates/${id}/`, payload);
  return unwrap(response.data);
}

export async function setDefaultCertificateTemplate(id: string): Promise<CertificateTemplate> {
  const response = await apiClient.post<ApiEnvelope<CertificateTemplate>>(`/certificate-templates/${id}/set-default/`);
  return unwrap(response.data);
}

export async function getCertificate(id: string): Promise<Certificate> {
  const response = await apiClient.get<ApiEnvelope<Certificate>>(`/certificates/${id}/`);
  return unwrap(response.data);
}

export async function startCertificateRenewal(id: string): Promise<Certificate> {
  const response = await apiClient.post<ApiEnvelope<Certificate>>(`/certificates/${id}/start-renewal/`);
  return unwrap(response.data);
}

export async function downloadCertificatePdf(id: string, certificateNumber: string): Promise<void> {
  const response = await apiClient.get(`/certificates/${id}/download/`, { responseType: "blob" });
  const url = window.URL.createObjectURL(response.data as Blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${certificateNumber}.pdf`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
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

export async function publicVerifyCertificateByNumber(certificateNumber: string): Promise<PublicCertificateVerification> {
  const response = await apiClient.post<ApiEnvelope<PublicCertificateVerification>>(
    "/public/certificates/verify-by-number/",
    { certificate_number: certificateNumber }
  );
  return unwrap(response.data);
}

export async function reportSuspiciousCertificate(payload: {
  certificate_number?: string;
  verification_token?: string;
  reporter_name?: string;
  reporter_contact?: string;
  reason: string;
  details?: string;
}): Promise<{ id: string }> {
  const response = await apiClient.post<ApiEnvelope<{ id: string }>>(
    "/public/certificates/report-suspicious/",
    payload
  );
  return unwrap(response.data);
}
