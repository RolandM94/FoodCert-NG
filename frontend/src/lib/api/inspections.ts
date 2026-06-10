import { apiClient, unwrap, type ApiEnvelope } from "@/lib/api/client";
import type {
  EmployerInspectionDetail,
  EmployerInspectionSummary,
  Inspection,
  InspectionCertificateScan,
  InspectorCertificateVerification,
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

export async function inspectorVerifyCertificateByNumber(certificate_number: string): Promise<InspectorCertificateVerification> {
  const response = await apiClient.post<ApiEnvelope<InspectorCertificateVerification>>("/inspector/certificates/verify-by-number/", {
    certificate_number
  });
  return unwrap(response.data);
}

export async function inspectorSaveCertificateToInspection(certificateId: string, inspection: string): Promise<InspectionCertificateScan> {
  const response = await apiClient.post<ApiEnvelope<InspectionCertificateScan>>(`/inspector/certificates/${certificateId}/save-to-inspection/`, {
    inspection
  });
  return unwrap(response.data);
}

export async function inspectorFlagCertificate(certificateId: string, payload: { reason: string; details?: string }): Promise<{ status: string; report_id: string }> {
  const response = await apiClient.post<ApiEnvelope<{ status: string; report_id: string }>>(`/inspector/certificates/${certificateId}/flag/`, payload);
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

export type InspectorDashboardCards = {
  assigned_inspections: number;
  due_today: number;
  overdue: number;
  in_progress: number;
  submitted: number;
  notices_issued: number;
  corrective_actions_pending: number;
  follow_ups: number;
  high_priority: number;
  closed_this_month: number;
};

export type InspectorDashboard = {
  cards: InspectorDashboardCards;
  filters: { user_id: string };
};

export async function fetchInspectorDashboard(): Promise<InspectorDashboard> {
  const response = await apiClient.get<ApiEnvelope<InspectorDashboard>>("/inspector/dashboard/");
  return unwrap(response.data);
}

export async function fetchInspectorTasks(params?: Record<string, string>): Promise<ApiEnvelope<Inspection[]>> {
  const response = await apiClient.get<ApiEnvelope<Inspection[]>>("/inspector/tasks/", { params });
  return response.data;
}

export async function acceptInspection(id: string): Promise<Inspection> {
  const response = await apiClient.post<ApiEnvelope<Inspection>>(`/inspections/${id}/accept/`);
  return unwrap(response.data);
}

export async function startInspection(id: string): Promise<Inspection> {
  const response = await apiClient.post<ApiEnvelope<Inspection>>(`/inspections/${id}/start/`);
  return unwrap(response.data);
}

export async function rescheduleInspection(id: string, reason: string): Promise<Inspection> {
  const response = await apiClient.post<ApiEnvelope<Inspection>>(`/inspections/${id}/reschedule-request/`, { reason });
  return unwrap(response.data);
}

export async function escalateInspection(id: string, payload: { severity?: string; summary?: string }): Promise<Record<string, unknown>> {
  const response = await apiClient.post<ApiEnvelope<Record<string, unknown>>>(`/inspections/${id}/escalate/`, payload);
  return unwrap(response.data);
}

export async function createFollowUp(id: string, payload: { inspector_id?: string; scheduled_at?: string; reason?: string }): Promise<Inspection> {
  const response = await apiClient.post<ApiEnvelope<Inspection>>(`/inspections/${id}/create-follow-up/`, payload);
  return unwrap(response.data);
}

export type EmployerContext = {
  employer: { id: string; name: string; establishment_category: string; lga: string | null; state: string | null };
  branch: { id: string; name: string } | null;
};

export async function fetchEmployerContext(inspectionId: string): Promise<EmployerContext> {
  const response = await apiClient.get<ApiEnvelope<EmployerContext>>(`/inspections/${inspectionId}/employer-context/`);
  return unwrap(response.data);
}

export type ComplianceSummary = Record<string, number | string>;

export async function fetchComplianceSummary(inspectionId: string): Promise<ComplianceSummary> {
  const response = await apiClient.get<ApiEnvelope<ComplianceSummary>>(`/inspections/${inspectionId}/compliance-summary/`);
  return unwrap(response.data);
}

export type FoodHandlerBrief = {
  id: string;
  name: string;
  system_identifier?: string;
  branch_name?: string | null;
  photo_url: string | null;
  certificate_status: string | null;
  fitness_status: string;
  certificate_id?: string | null;
  certificate_number: string | null;
  certificate_expiry_date?: string | null;
  active_illness_status?: string;
  return_to_work_status?: string;
  exclusion_start_date?: string | null;
  earliest_return_date?: string | null;
  operational_instruction?: string;
};

export async function fetchFoodHandlers(inspectionId: string): Promise<FoodHandlerBrief[]> {
  const response = await apiClient.get<ApiEnvelope<FoodHandlerBrief[]>>(`/inspections/${inspectionId}/food-handlers/`);
  return unwrap(response.data);
}

export async function listChecklistItems(): Promise<Record<string, unknown>[]> {
  const response = await apiClient.get<ApiEnvelope<Record<string, unknown>[]>>("/inspection-checklist-items/");
  return unwrap(response.data);
}

export async function upsertChecklistResponse(inspectionId: string, payload: Record<string, unknown>): Promise<Record<string, unknown>> {
  const response = await apiClient.post<ApiEnvelope<Record<string, unknown>>>(`/inspections/${inspectionId}/checklist-responses/`, payload);
  return unwrap(response.data);
}

export async function getChecklistResponses(inspectionId: string): Promise<Record<string, unknown>[]> {
  const response = await apiClient.get<ApiEnvelope<Record<string, unknown>[]>>(`/inspections/${inspectionId}/checklist-responses/`);
  return unwrap(response.data);
}

export async function createFinding(inspectionId: string, payload: Record<string, unknown>): Promise<Record<string, unknown>> {
  const response = await apiClient.post<ApiEnvelope<Record<string, unknown>>>(`/inspections/${inspectionId}/findings/`, payload);
  return unwrap(response.data);
}

export async function getFindings(inspectionId: string): Promise<Record<string, unknown>[]> {
  const response = await apiClient.get<ApiEnvelope<Record<string, unknown>[]>>(`/inspections/${inspectionId}/findings/`);
  return unwrap(response.data);
}

export async function uploadEvidence(inspectionId: string, payload: Record<string, unknown>): Promise<Record<string, unknown>> {
  const response = await apiClient.post<ApiEnvelope<Record<string, unknown>>>(`/inspections/${inspectionId}/evidence-upload/`, payload);
  return unwrap(response.data);
}

export async function getEvidence(inspectionId: string): Promise<Record<string, unknown>[]> {
  const response = await apiClient.get<ApiEnvelope<Record<string, unknown>[]>>(`/inspections/${inspectionId}/evidence-entries/`);
  return unwrap(response.data);
}

export async function deleteEvidence(inspectionId: string, evidenceId: string): Promise<void> {
  await apiClient.delete(`/inspections/${inspectionId}/evidence-entries/${evidenceId}/`);
}

export async function listEnforcementNotices(params?: Record<string, string>): Promise<ApiEnvelope<Record<string, unknown>[]>> {
  const response = await apiClient.get<ApiEnvelope<Record<string, unknown>[]>>("/enforcement-notices/", { params });
  return response.data;
}

export async function getEnforcementNotice(id: string): Promise<Record<string, unknown>> {
  const response = await apiClient.get<ApiEnvelope<Record<string, unknown>>>(`/enforcement-notices/${id}/`);
  return unwrap(response.data);
}

export async function submitNoticeForApproval(id: string): Promise<Record<string, unknown>> {
  const response = await apiClient.post<ApiEnvelope<Record<string, unknown>>>(`/enforcement-notices/${id}/submit-for-approval/`);
  return unwrap(response.data);
}

export async function approveNotice(id: string): Promise<Record<string, unknown>> {
  const response = await apiClient.post<ApiEnvelope<Record<string, unknown>>>(`/enforcement-notices/${id}/approve/`);
  return unwrap(response.data);
}

export async function acknowledgeNotice(id: string): Promise<Record<string, unknown>> {
  const response = await apiClient.post<ApiEnvelope<Record<string, unknown>>>(`/enforcement-notices/${id}/acknowledge/`);
  return unwrap(response.data);
}

export async function closeNotice(id: string, closure_note?: string): Promise<Record<string, unknown>> {
  const response = await apiClient.post<ApiEnvelope<Record<string, unknown>>>(`/enforcement-notices/${id}/close/`, { closure_note });
  return unwrap(response.data);
}

export async function submitCorrectiveAction(noticeId: string, payload: { response_note: string; action_taken: string }): Promise<Record<string, unknown>> {
  const response = await apiClient.post<ApiEnvelope<Record<string, unknown>>>(`/enforcement-notices/${noticeId}/corrective-actions/`, payload);
  return unwrap(response.data);
}

export async function getCorrectiveActions(noticeId: string): Promise<Record<string, unknown>[]> {
  const response = await apiClient.get<ApiEnvelope<Record<string, unknown>[]>>(`/enforcement-notices/${noticeId}/corrective-actions/`);
  return unwrap(response.data);
}

export async function listEnforcementCases(params?: Record<string, string>): Promise<ApiEnvelope<Record<string, unknown>[]>> {
  const response = await apiClient.get<ApiEnvelope<Record<string, unknown>[]>>("/enforcement-cases/", { params });
  return response.data;
}

export async function getEnforcementCase(id: string): Promise<Record<string, unknown>> {
  const response = await apiClient.get<ApiEnvelope<Record<string, unknown>>>(`/enforcement-cases/${id}/`);
  return unwrap(response.data);
}

export async function escalateCase(id: string, reason?: string): Promise<Record<string, unknown>> {
  const response = await apiClient.post<ApiEnvelope<Record<string, unknown>>>(`/enforcement-cases/${id}/escalate/`, { reason });
  return unwrap(response.data);
}

export async function closeCase(id: string, closure_note?: string): Promise<Record<string, unknown>> {
  const response = await apiClient.post<ApiEnvelope<Record<string, unknown>>>(`/enforcement-cases/${id}/close/`, { closure_note });
  return unwrap(response.data);
}

export type StateEnforcementDashboard = {
  cards: Record<string, unknown>;
  charts: Record<string, unknown>;
  filters: Record<string, unknown>;
};

export async function fetchStateEnforcementDashboard(params?: Record<string, string>): Promise<StateEnforcementDashboard> {
  const response = await apiClient.get<ApiEnvelope<StateEnforcementDashboard>>("/state/enforcement/dashboard/", { params });
  return unwrap(response.data);
}

export type FederalEnforcementDashboard = {
  cards: Record<string, unknown>;
  charts: Record<string, unknown>;
};

export async function fetchFederalEnforcementDashboard(): Promise<FederalEnforcementDashboard> {
  const response = await apiClient.get<ApiEnvelope<FederalEnforcementDashboard>>("/federal/enforcement/dashboard/");
  return unwrap(response.data);
}
