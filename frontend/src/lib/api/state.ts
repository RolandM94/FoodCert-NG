import { apiClient, unwrap, type ApiEnvelope } from "@/lib/api/client";
import type { MinistryStaffRole, UserRole } from "@/types/auth";
import type { CertificateRequestStatus, CertificateStatus } from "@/types/certificates";
import type { FacilityAccreditationApplication, MedicalFacility } from "@/types/facilities";
import type { EnforcementAction, Inspection, InspectionStatus } from "@/types/inspections";
import type { OrganizationUnit, UserInvite } from "@/types/organizations";
import type { DashboardPayload } from "@/types/reports";

export type StateDashboardParams = {
  state?: string;
  lga?: string;
  date_from?: string;
  date_to?: string;
  employer_category?: string;
  certificate_status?: string;
};

export async function getStateMinistryDashboard(params?: StateDashboardParams): Promise<DashboardPayload> {
  const response = await apiClient.get<ApiEnvelope<DashboardPayload>>("/state/dashboard/", { params });
  return unwrap(response.data);
}

export type StateMinistryUser = {
  id: string;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  role: UserRole;
  status: string;
  organization?: string | null;
  organization_name?: string | null;
  unit?: string | null;
  unit_name?: string | null;
  unit_restricted?: boolean;
  state?: string | null;
  state_name?: string | null;
  ministry_profile?: {
    id: string;
    ministry_type: "state" | "federal";
    sub_role: MinistryStaffRole;
    state?: string | null;
    state_name?: string | null;
    lga?: string | null;
    lga_name?: string | null;
    unit?: string | null;
    unit_name?: string | null;
    is_active: boolean;
  } | null;
};

export type StateInvitePayload = {
  email: string;
  role: Extract<UserRole, "state_admin" | "inspector">;
  ministry_staff_role?: MinistryStaffRole;
  unit?: string;
  phone?: string;
  message?: string;
  expires_at?: string;
};

export async function fetchStateUnits(): Promise<OrganizationUnit[]> {
  const response = await apiClient.get<ApiEnvelope<OrganizationUnit[]>>("/state/units/");
  return unwrap(response.data);
}

export async function createStateUnit(data: {
  name: string;
  unit_type: string;
  parent?: string | null;
  description?: string;
  state?: string | null;
  lga?: string | null;
  address?: string;
  phone?: string;
  email?: string;
}): Promise<OrganizationUnit> {
  const response = await apiClient.post<ApiEnvelope<OrganizationUnit>>("/state/units/", data);
  return unwrap(response.data);
}

export async function updateStateUnit(unitId: string, data: Partial<OrganizationUnit>): Promise<OrganizationUnit> {
  const response = await apiClient.patch<ApiEnvelope<OrganizationUnit>>(`/state/units/${unitId}/`, data);
  return unwrap(response.data);
}

export async function deleteStateUnit(unitId: string): Promise<void> {
  await apiClient.delete(`/state/units/${unitId}/`);
}

export async function fetchStateUsers(): Promise<StateMinistryUser[]> {
  const response = await apiClient.get<ApiEnvelope<StateMinistryUser[]>>("/state/users/");
  return unwrap(response.data);
}

export async function fetchStateInvites(): Promise<UserInvite[]> {
  const response = await apiClient.get<ApiEnvelope<UserInvite[]>>("/state/invites/");
  return unwrap(response.data);
}

export async function createStateInvite(data: StateInvitePayload): Promise<UserInvite> {
  const response = await apiClient.post<ApiEnvelope<UserInvite>>("/state/invites/", data);
  return unwrap(response.data);
}

export async function revokeStateInvite(inviteId: string): Promise<UserInvite> {
  const response = await apiClient.delete<ApiEnvelope<UserInvite>>(`/state/invites/${inviteId}/`);
  return unwrap(response.data);
}

export type StateLga = {
  id: string;
  name: string;
  state: string;
};

export async function fetchStateLgas(stateId: string): Promise<StateLga[]> {
  const response = await apiClient.get<ApiEnvelope<StateLga[]>>(`/states/${stateId}/lgas/`);
  return unwrap(response.data);
}

export type StateFacilityFilters = {
  status?: string;
  facility_type?: string;
  lga?: string;
  search?: string;
};

export async function fetchStateFacilities(params?: StateFacilityFilters): Promise<MedicalFacility[]> {
  const response = await apiClient.get<ApiEnvelope<MedicalFacility[]>>("/state/facilities/", { params });
  return unwrap(response.data);
}

export type StateFacilityApplicationFilters = {
  status?: string;
  queue?: "pending";
  lga?: string;
  search?: string;
};

export async function fetchStateFacilityApplications(
  params?: StateFacilityApplicationFilters
): Promise<FacilityAccreditationApplication[]> {
  const response = await apiClient.get<ApiEnvelope<FacilityAccreditationApplication[]>>(
    "/state/facilities/applications/",
    { params }
  );
  return unwrap(response.data);
}

async function patchStateFacilityApplication(
  applicationId: string,
  action: "approve" | "reject" | "suspend" | "reinstate",
  review_comment: string
): Promise<FacilityAccreditationApplication> {
  const response = await apiClient.patch<ApiEnvelope<FacilityAccreditationApplication>>(
    `/state/facilities/applications/${applicationId}/${action}/`,
    { review_comment }
  );
  return unwrap(response.data);
}

export function approveStateFacilityApplication(applicationId: string, review_comment = "") {
  return patchStateFacilityApplication(applicationId, "approve", review_comment);
}

export function rejectStateFacilityApplication(applicationId: string, review_comment: string) {
  return patchStateFacilityApplication(applicationId, "reject", review_comment);
}

export function suspendStateFacilityApplication(applicationId: string, review_comment: string) {
  return patchStateFacilityApplication(applicationId, "suspend", review_comment);
}

export function reinstateStateFacilityApplication(applicationId: string, review_comment = "") {
  return patchStateFacilityApplication(applicationId, "reinstate", review_comment);
}

export type AssessmentFee = {
  id: string;
  state: string;
  state_name?: string;
  facility_type: string;
  fee_name: string;
  amount: string;
  currency: string;
  state_fee: string;
  facility_fee: string;
  platform_fee: string;
  provider_fee_handling: string;
  effective_from: string;
  effective_to?: string | null;
  status: "draft" | "pending_approval" | "active" | "scheduled" | "expired" | "suspended" | "replaced" | "inactive";
  created_by?: string | null;
  approved_by?: string | null;
  approved_at?: string | null;
  notes?: string;
  created_at: string;
  updated_at: string;
};

export type StateAssessmentFeePayload = {
  facility_type: string;
  fee_name?: string;
  amount: string;
  state_fee: string;
  facility_fee: string;
  provider_fee_handling?: string;
  currency?: string;
  effective_from: string;
  effective_to?: string | null;
  status?: AssessmentFee["status"];
  notes?: string;
};

export async function fetchStateAssessmentFees(params?: {
  status?: string;
  facility_type?: string;
}): Promise<AssessmentFee[]> {
  const response = await apiClient.get<ApiEnvelope<AssessmentFee[]>>("/state/fee-schedules/", { params });
  return unwrap(response.data);
}

export async function createStateAssessmentFee(payload: StateAssessmentFeePayload): Promise<AssessmentFee> {
  const response = await apiClient.post<ApiEnvelope<AssessmentFee>>("/state/fee-schedules/", payload);
  return unwrap(response.data);
}

export async function updateStateAssessmentFee(id: string, payload: Partial<StateAssessmentFeePayload>): Promise<AssessmentFee> {
  const response = await apiClient.patch<ApiEnvelope<AssessmentFee>>(`/state/fee-schedules/${id}/`, payload);
  return unwrap(response.data);
}

export async function submitStateAssessmentFee(id: string): Promise<AssessmentFee> {
  const response = await apiClient.post<ApiEnvelope<AssessmentFee>>(`/state/fee-schedules/${id}/submit/`);
  return unwrap(response.data);
}

export async function approveStateAssessmentFee(id: string): Promise<AssessmentFee> {
  const response = await apiClient.post<ApiEnvelope<AssessmentFee>>(`/state/fee-schedules/${id}/approve/`);
  return unwrap(response.data);
}

export async function suspendStateAssessmentFee(id: string): Promise<AssessmentFee> {
  const response = await apiClient.post<ApiEnvelope<AssessmentFee>>(`/state/fee-schedules/${id}/suspend/`);
  return unwrap(response.data);
}

export type StateCertificateValidationRequest = {
  id: string;
  assessment: string;
  food_handler_name?: string;
  food_handler_category?: string;
  employer_name?: string;
  facility_id?: string;
  facility_name?: string;
  issuing_state_name?: string;
  final_decision?: string;
  payment_status?: string;
  declaration_status?: string;
  physical_exam_status?: string;
  lab_status?: string;
  vaccination_status?: string;
  certificate_id?: string;
  certificate_number?: string;
  requested_by?: string;
  requested_by_name?: string;
  reviewed_by?: string;
  reviewed_by_name?: string;
  status: CertificateRequestStatus;
  request_notes: string;
  review_notes: string;
  reviewed_at?: string;
  facility_response?: string;
  facility_responded_at?: string;
  assessment_evidence_summary?: {
    fit_signed: boolean;
    payment_status: string;
    declaration_status: string;
    physical_exam_status: string;
    lab_status: string;
    vaccination_status: string;
    medical_report_generated: boolean;
  };
  created_at: string;
  updated_at: string;
};

export type StateCertificateValidationFilters = {
  status?: string;
  facility?: string;
  date_from?: string;
  date_to?: string;
};

export async function fetchStateCertificateValidationQueue(
  params?: StateCertificateValidationFilters
): Promise<StateCertificateValidationRequest[]> {
  const response = await apiClient.get<ApiEnvelope<StateCertificateValidationRequest[]>>(
    "/state/certificate-validation-queue/",
    { params }
  );
  return unwrap(response.data);
}

async function patchStateCertificateValidationRequest(
  id: string,
  action: "approve" | "reject" | "request-clarification",
  review_notes: string
): Promise<StateCertificateValidationRequest> {
  const response = await apiClient.patch<ApiEnvelope<StateCertificateValidationRequest>>(
    `/state/certificate-validation-queue/${id}/${action}/`,
    { review_notes }
  );
  return unwrap(response.data);
}

export function approveStateCertificateValidationRequest(id: string, review_notes = "") {
  return patchStateCertificateValidationRequest(id, "approve", review_notes);
}

export function rejectStateCertificateValidationRequest(id: string, review_notes: string) {
  return patchStateCertificateValidationRequest(id, "reject", review_notes);
}

export function requestStateCertificateValidationClarification(id: string, review_notes: string) {
  return patchStateCertificateValidationRequest(id, "request-clarification", review_notes);
}

export type StateCertificateRegistryItem = {
  id: string;
  certificate_number: string;
  food_handler: string;
  food_handler_name?: string;
  food_handler_category?: string;
  employer?: string;
  employer_name?: string;
  facility: string;
  facility_name?: string;
  issuing_state: string;
  issuing_state_name?: string;
  issue_date: string;
  expiry_date: string;
  status: CertificateStatus;
  effective_status: CertificateStatus;
  verification_url: string;
  suspended_by?: string;
  suspended_by_name?: string;
  suspended_at?: string;
  suspension_reason?: string;
  replaced_by?: string;
  replacement_reason?: string;
  revoked_by?: string;
  revoked_by_name?: string;
  revoked_at?: string;
  revocation_reason: string;
  created_at: string;
  updated_at: string;
};

export type UnifiedCertificateRegistryTab =
  | "pending_review"
  | "food_handler_certificates"
  | "employer_accreditation_certificates"
  | "facility_accreditation_certificates"
  | "all";

export type UnifiedCertificateRegistryItem = {
  id: string;
  record_type: string;
  owner_type: "food_handler" | "employer" | "facility";
  owner_id: string;
  owner_name: string;
  certificate_number: string;
  status: string;
  issue_date?: string | null;
  expiry_date?: string | null;
  issuing_state_name: string;
  action_status: string;
  source_id: string;
  metadata: Record<string, string>;
};

export async function fetchStateUnifiedCertificateRegistry(params?: {
  tab?: UnifiedCertificateRegistryTab;
  search?: string;
}): Promise<UnifiedCertificateRegistryItem[]> {
  const response = await apiClient.get<ApiEnvelope<UnifiedCertificateRegistryItem[]>>("/state/certificates/registry/", { params });
  return unwrap(response.data);
}

export type StateCertificateFilters = {
  search?: string;
  status?: string;
  facility?: string;
  employer?: string;
  expiry_window?: string;
};

export async function fetchStateCertificates(params?: StateCertificateFilters): Promise<StateCertificateRegistryItem[]> {
  const response = await apiClient.get<ApiEnvelope<StateCertificateRegistryItem[]>>("/state/certificates/", { params });
  return unwrap(response.data);
}

async function patchStateCertificateLifecycle(
  id: string,
  action: "suspend" | "revoke" | "reinstate",
  reason: string
): Promise<StateCertificateRegistryItem> {
  const response = await apiClient.patch<ApiEnvelope<StateCertificateRegistryItem>>(
    `/state/certificates/${id}/${action}/`,
    { reason }
  );
  return unwrap(response.data);
}

export function suspendStateCertificate(id: string, reason: string) {
  return patchStateCertificateLifecycle(id, "suspend", reason);
}

export function revokeStateCertificate(id: string, reason: string) {
  return patchStateCertificateLifecycle(id, "revoke", reason);
}

export function reinstateStateCertificate(id: string, reason: string) {
  return patchStateCertificateLifecycle(id, "reinstate", reason);
}

export function replaceStateCertificate(id: string, reason: string): Promise<StateCertificateRegistryItem> {
  return apiClient.post<ApiEnvelope<StateCertificateRegistryItem>>(`/state/certificates/${id}/replace/`, { reason }).then((response) => unwrap(response.data));
}

export type StateCertificateAuditItem = {
  id: string;
  action: string;
  actor_name?: string;
  metadata: Record<string, unknown>;
  created_at: string;
};

export async function fetchStateCertificateAudit(id: string): Promise<StateCertificateAuditItem[]> {
  const response = await apiClient.get<ApiEnvelope<StateCertificateAuditItem[]>>(`/state/certificates/${id}/audit/`);
  return unwrap(response.data);
}

export async function downloadStateCertificateExport(): Promise<void> {
  const response = await apiClient.get("/state/certificates/export/", { responseType: "blob" });
  const url = window.URL.createObjectURL(response.data as Blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "state-certificates.csv";
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

export type StateEmployerMonitoringItem = {
  id: string;
  business_name: string;
  establishment_category: string;
  business_registration_number?: string;
  lga?: string | null;
  lga_name?: string | null;
  compliance_status: string;
  subscription_status: string;
  is_active: boolean;
  food_handler_count: number;
  active_certificate_count: number;
  active_illness_exclusion_count: number;
  created_at: string;
  updated_at: string;
};

export type StateFoodHandlerMonitoringItem = {
  id: string;
  full_name: string;
  system_identifier: string;
  lga?: string | null;
  lga_name?: string | null;
  employer?: string | null;
  employer_name?: string | null;
  branch_name?: string | null;
  food_handler_category: string;
  current_status: string;
  certificate_status: string;
  certificate_number?: string;
  certificate_expiry_date?: string | null;
  active_illness_status?: string;
  created_at: string;
  updated_at: string;
};

export type StateIllnessMonitoringItem = {
  id: string;
  food_handler: string;
  food_handler_name?: string;
  food_handler_category?: string;
  employer?: string | null;
  employer_name?: string | null;
  lga_name?: string | null;
  suspected_condition?: string;
  exclusion_start_date?: string;
  earliest_return_date?: string | null;
  clearance_required: boolean;
  clearance_status: string;
  cleared_at?: string | null;
  return_to_work_certificate_number?: string;
  created_at: string;
  updated_at: string;
};

export async function fetchStateEmployers(params?: Record<string, string>): Promise<StateEmployerMonitoringItem[]> {
  const response = await apiClient.get<ApiEnvelope<StateEmployerMonitoringItem[]>>("/state/employers/", { params });
  return unwrap(response.data);
}

export async function fetchStateFoodHandlers(params?: Record<string, string>): Promise<StateFoodHandlerMonitoringItem[]> {
  const response = await apiClient.get<ApiEnvelope<StateFoodHandlerMonitoringItem[]>>("/state/food-handlers/", { params });
  return unwrap(response.data);
}

export async function fetchStateIllnessReports(params?: Record<string, string>): Promise<StateIllnessMonitoringItem[]> {
  const response = await apiClient.get<ApiEnvelope<StateIllnessMonitoringItem[]>>("/state/illness-reports/", { params });
  return unwrap(response.data);
}

export type StateInspectionAuditLog = {
  id: string;
  action: string;
  actor_name?: string;
  metadata: Record<string, unknown>;
  created_at: string;
};

export type StateInspectionItem = Inspection & {
  state_name?: string;
  lga_name?: string;
  responses?: Array<{
    id: string;
    response_type: string;
    content: string;
    evidence_file_url?: string;
    submitted_by_name?: string;
    submitted_at: string;
  }>;
  audit_history?: StateInspectionAuditLog[];
};

export type StateInspectionFilters = {
  search?: string;
  status?: InspectionStatus | "";
  enforcement_action?: EnforcementAction | "";
  inspector?: string;
  employer?: string;
  lga?: string;
  queue?: "active" | "submitted" | "enforcement" | "";
};

export type StateInspectionAssignmentPayload = {
  inspector: string;
  employer: string;
  branch?: string;
  form_template?: string;
  inspection_date?: string;
  checklist_responses?: Record<string, boolean | string | number>;
  enforcement_action?: EnforcementAction;
  findings?: string;
};

export async function fetchStateInspections(params?: StateInspectionFilters): Promise<StateInspectionItem[]> {
  const response = await apiClient.get<ApiEnvelope<StateInspectionItem[]>>("/state/inspections/", { params });
  return unwrap(response.data);
}

export async function fetchStateInspection(id: string): Promise<StateInspectionItem> {
  const response = await apiClient.get<ApiEnvelope<StateInspectionItem>>(`/state/inspections/${id}/`);
  return unwrap(response.data);
}

export async function assignStateInspection(payload: StateInspectionAssignmentPayload): Promise<StateInspectionItem> {
  const response = await apiClient.post<ApiEnvelope<StateInspectionItem>>("/state/inspections/", payload);
  return unwrap(response.data);
}

export async function reviewStateInspection(
  id: string,
  payload: Partial<Pick<StateInspectionItem, "checklist_responses" | "enforcement_action" | "findings" | "evidence_files">>
): Promise<StateInspectionItem> {
  const response = await apiClient.patch<ApiEnvelope<StateInspectionItem>>(`/state/inspections/${id}/review/`, payload);
  return unwrap(response.data);
}

export async function closeStateInspection(id: string, closure_notes: string): Promise<StateInspectionItem> {
  const response = await apiClient.patch<ApiEnvelope<StateInspectionItem>>(`/state/inspections/${id}/close/`, { closure_notes });
  return unwrap(response.data);
}

export type StateReportStatus = "draft" | "generated" | "submitted" | "returned" | "accepted";

export type StateReportItem = {
  id: string;
  state: string;
  state_name?: string;
  report_type: string;
  reporting_period_start: string;
  reporting_period_end: string;
  status: StateReportStatus;
  generated_by?: string | null;
  generated_by_name?: string;
  submitted_by?: string | null;
  submitted_by_name?: string;
  submitted_at?: string | null;
  reviewed_by?: string | null;
  reviewed_by_name?: string;
  reviewed_at?: string | null;
  file_url?: string;
  data_snapshot: Record<string, unknown>;
  review_comment: string;
  created_at: string;
  updated_at: string;
};

export type StateRevenueSnapshot = {
  state: { id: string; name: string };
  filters: Record<string, string>;
  cards: {
    settlement_count: number;
    paid_settlement_count: number;
    pending_settlement_count: number;
    gross_amount: string;
    facility_amount: string;
    state_amount: string;
    platform_amount: string;
    payment_count?: number;
    successful_payment_count?: number;
    payment_amount?: string;
    refund_count?: number;
    refund_amount?: string;
    open_refund_count?: number;
    reconciliation_issue_count?: number;
  };
  charts: Record<string, Array<Record<string, string | number>>>;
  sections: {
    recent_settlements: StateSettlementItem[];
  };
};

export type StateSettlementItem = {
  id: string;
  facility: string;
  facility_name?: string;
  state: string;
  state_name?: string;
  payment_transaction: string;
  assessment?: string | null;
  gross_amount: string;
  facility_amount: string;
  state_amount: string;
  platform_amount: string;
  settlement_status: string;
  settlement_reference: string;
  settled_at?: string | null;
  created_at: string;
  updated_at: string;
};

export async function fetchStateReports(params?: { status?: string; report_type?: string }): Promise<StateReportItem[]> {
  const response = await apiClient.get<ApiEnvelope<StateReportItem[]>>("/state/reports/", { params });
  return unwrap(response.data);
}

export async function generateStateReport(payload: {
  report_type: string;
  reporting_period_start: string;
  reporting_period_end: string;
}): Promise<StateReportItem> {
  const response = await apiClient.post<ApiEnvelope<StateReportItem>>("/state/reports/generate/", payload);
  return unwrap(response.data);
}

export async function submitStateReport(id: string): Promise<StateReportItem> {
  const response = await apiClient.patch<ApiEnvelope<StateReportItem>>(`/state/reports/${id}/submit/`);
  return unwrap(response.data);
}

export async function fetchStateRevenue(params?: { date_from?: string; date_to?: string }): Promise<StateRevenueSnapshot> {
  const response = await apiClient.get<ApiEnvelope<StateRevenueSnapshot>>("/state/revenue/", { params });
  return unwrap(response.data);
}

export async function fetchStateFinanceDashboard(params?: { date_from?: string; date_to?: string }): Promise<StateRevenueSnapshot> {
  const response = await apiClient.get<ApiEnvelope<StateRevenueSnapshot>>("/state/finance/dashboard/", { params });
  return unwrap(response.data);
}

export async function fetchStateSettlements(params?: {
  status?: string;
  facility?: string;
  date_from?: string;
  date_to?: string;
}): Promise<StateSettlementItem[]> {
  const response = await apiClient.get<ApiEnvelope<StateSettlementItem[]>>("/state/settlements/", { params });
  return unwrap(response.data);
}

export async function fetchStateFinanceSettlements(params?: {
  status?: string;
  facility?: string;
  date_from?: string;
  date_to?: string;
}): Promise<StateSettlementItem[]> {
  const response = await apiClient.get<ApiEnvelope<StateSettlementItem[]>>("/state/finance/settlements/", { params });
  return unwrap(response.data);
}

export type StateRefundItem = {
  id: string;
  payment_transaction: string;
  payment_reference?: string;
  requested_by?: string | null;
  requested_by_email?: string;
  approved_by?: string | null;
  amount: string;
  reason: string;
  review_notes?: string;
  status: string;
  provider_refund_reference?: string;
  approved_at?: string | null;
  processed_at?: string | null;
  created_at: string;
  updated_at: string;
};

export async function fetchStateFinanceRefunds(params?: { status?: string }): Promise<StateRefundItem[]> {
  const response = await apiClient.get<ApiEnvelope<StateRefundItem[]>>("/state/finance/refunds/", { params });
  return unwrap(response.data);
}
