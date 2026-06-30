import { apiClient, unwrap, type ApiEnvelope } from "@/lib/api/client";
import type { UnifiedCertificateRegistryItem, UnifiedCertificateRegistryTab } from "@/lib/api/state";
import type { DashboardPayload } from "@/types/reports";

export async function getFederalMinistryDashboard(): Promise<DashboardPayload> {
  const response = await apiClient.get<ApiEnvelope<DashboardPayload>>("/federal/dashboard/");
  return unwrap(response.data);
}

export type FederalStatePerformanceRow = {
  state_id: string;
  state_name: string;
  state_code: string;
  is_fct: boolean;
  registered_handlers: number;
  certified_handlers: number;
  certification_coverage: number;
  registered_employers: number;
  approved_facilities: number;
  pending_facility_applications: number;
  pending_certificate_validations: number;
  inspection_count: number;
  illness_reports: number;
  latest_report_status: string;
  latest_report_period_end: string;
  data_quality_score: number;
};

export type FederalStatePerformancePayload = {
  totals: {
    states: number;
    registered_handlers: number;
    certified_handlers: number;
    certification_coverage: number;
    approved_facilities: number;
    pending_facility_applications: number;
    pending_certificate_validations: number;
    inspection_count: number;
    illness_reports: number;
  };
  states: FederalStatePerformanceRow[];
};

export type FederalStateSummaryPayload = {
  state: FederalStatePerformanceRow;
  reports: Array<{
    id: string;
    report_type: string;
    status: string;
    reporting_period_start: string;
    reporting_period_end: string;
    submitted_at?: string;
  }>;
};

export async function fetchFederalStatePerformance(): Promise<FederalStatePerformancePayload> {
  const response = await apiClient.get<ApiEnvelope<FederalStatePerformancePayload>>("/federal/states/performance/");
  return unwrap(response.data);
}

export async function fetchFederalStateSummary(stateId: string): Promise<FederalStateSummaryPayload> {
  const response = await apiClient.get<ApiEnvelope<FederalStateSummaryPayload>>(`/federal/states/${stateId}/summary/`);
  return unwrap(response.data);
}

export type FederalFinanceDashboard = {
  filters: { date_from: string; date_to: string };
  cards: Record<string, string | number>;
  charts: Record<string, Array<Record<string, string | number>>>;
};

export type FederalRevenueByStateRow = {
  state_id: string;
  state_name: string;
  settlement_count: number;
  gross_amount: string;
  facility_amount: string;
  state_amount: string;
  platform_amount: string;
};

export type FederalFinanceSettlementItem = {
  id: string;
  facility: string;
  facility_name?: string;
  state: string;
  state_name?: string;
  payment_transaction: string;
  payment_reference?: string;
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

export type FederalSubscriptionFinance = {
  cards: Record<string, string | number>;
  status: Array<{ status: string; total: number }>;
  invoices: Array<{ status: string; total: number; amount_due?: string; amount_paid?: string }>;
};

export async function fetchFederalFinanceDashboard(params?: { date_from?: string; date_to?: string }): Promise<FederalFinanceDashboard> {
  const response = await apiClient.get<ApiEnvelope<FederalFinanceDashboard>>("/federal/finance/dashboard/", { params });
  return unwrap(response.data);
}

export async function fetchFederalRevenueByState(params?: { date_from?: string; date_to?: string }): Promise<FederalRevenueByStateRow[]> {
  const response = await apiClient.get<ApiEnvelope<FederalRevenueByStateRow[]>>("/federal/finance/revenue-by-state/", { params });
  return unwrap(response.data);
}

export async function fetchFederalFinanceSettlements(params?: { status?: string; state?: string }): Promise<FederalFinanceSettlementItem[]> {
  const response = await apiClient.get<ApiEnvelope<FederalFinanceSettlementItem[]>>("/federal/finance/settlements/", { params });
  return unwrap(response.data);
}

export async function fetchFederalFinanceSubscriptions(): Promise<FederalSubscriptionFinance> {
  const response = await apiClient.get<ApiEnvelope<FederalSubscriptionFinance>>("/federal/finance/subscriptions/");
  return unwrap(response.data);
}

export type FederalCertificateRegistryItem = {
  id: string;
  certificate_number: string;
  food_handler_name?: string;
  employer_name?: string;
  facility_name?: string;
  issuing_state: string;
  issuing_state_name?: string;
  issue_date: string;
  expiry_date: string;
  status: string;
  effective_status: string;
  suspicious_report_count: number;
  verification_url: string;
  created_at: string;
  updated_at: string;
};

export type FederalFacilityRegistryItem = {
  id: string;
  facility_name: string;
  facility_type: string;
  ownership_type: string;
  license_number: string;
  registration_number: string;
  state: string;
  state_name?: string;
  lga?: string | null;
  lga_name?: string | null;
  accreditation_status: string;
  accreditation_start_date?: string | null;
  accreditation_expiry_date?: string | null;
  can_conduct_assessments: boolean;
  assessments_count: number;
  certificates_count: number;
  temporary_unfit_count: number;
  created_at: string;
  updated_at: string;
};

export type FederalEmployerRegistryItem = {
  id: string;
  business_name: string;
  establishment_category: string;
  business_registration_number?: string;
  state: string;
  state_name?: string;
  lga?: string | null;
  lga_name?: string | null;
  compliance_status: string;
  subscription_status: string;
  is_active: boolean;
  food_handler_count: number;
  created_at: string;
  updated_at: string;
};

export type FederalPolicyConfig = {
  id: string;
  certificate_validity_months: number;
  renewal_reminder_days: number[];
  typhoid_validity_years: number;
  hepatitis_a_second_dose_months: number;
  nin_required: boolean;
  payment_before_assessment_required: boolean;
  state_validation_before_certificate_required: boolean;
  public_qr_verification_enabled: boolean;
  state_certificate_template_overrides_enabled: boolean;
  updated_by?: string | null;
  updated_by_name?: string;
  created_at: string;
  updated_at: string;
};

export type FederalStateOverrideItem = {
  id: string;
  state: string;
  state_name?: string;
  requires_state_certificate_validation: boolean;
  certificate_validity_months: number;
  typhoid_validity_years: number;
  hepatitis_a_second_dose_months: number;
  auto_renewal_reminder_days: number[];
  updated_by?: string | null;
  created_at: string;
  updated_at: string;
};

export async function fetchFederalCertificates(params?: Record<string, string>): Promise<FederalCertificateRegistryItem[]> {
  const response = await apiClient.get<ApiEnvelope<FederalCertificateRegistryItem[]>>("/federal/certificates/", { params });
  return unwrap(response.data);
}

export async function fetchFederalUnifiedCertificateRegistry(params?: {
  tab?: UnifiedCertificateRegistryTab;
  state?: string;
  search?: string;
}): Promise<UnifiedCertificateRegistryItem[]> {
  const response = await apiClient.get<ApiEnvelope<UnifiedCertificateRegistryItem[]>>("/federal/certificates/registry/", { params });
  return unwrap(response.data);
}

export type FederalCertificateAnalytics = {
  cards: {
    total: number;
    active: number;
    expired: number;
    expiring_30_days: number;
    suspended: number;
    revoked: number;
    flagged: number;
    invalid_verification_attempts: number;
  };
  by_state: Array<{
    state_name: string;
    total: number;
    active: number;
    expired: number;
    suspended: number;
    revoked: number;
  }>;
  status_distribution: Array<{ status: string; total: number }>;
  invalid_verification_trends: Array<{ day: string; total: number }>;
  high_risk_facilities: Array<{
    facility_id?: string | null;
    facility_name: string;
    state_name: string;
    total: number;
    suspended: number;
    revoked: number;
    flagged: number;
  }>;
};

export async function fetchFederalCertificateAnalytics(): Promise<FederalCertificateAnalytics> {
  const response = await apiClient.get<ApiEnvelope<FederalCertificateAnalytics>>("/federal/certificates/analytics/");
  return unwrap(response.data);
}

export async function fetchFederalCertificate(id: string): Promise<FederalCertificateRegistryItem> {
  const response = await apiClient.get<ApiEnvelope<FederalCertificateRegistryItem>>(`/federal/certificates/${id}/`);
  return unwrap(response.data);
}

export async function flagFederalCertificate(id: string, reason: string, details = ""): Promise<{ status: string; report_id: string }> {
  const response = await apiClient.post<ApiEnvelope<{ status: string; report_id: string }>>(`/federal/certificates/${id}/flag/`, { reason, details });
  return unwrap(response.data);
}

export async function fetchFederalFacilities(params?: Record<string, string>): Promise<FederalFacilityRegistryItem[]> {
  const response = await apiClient.get<ApiEnvelope<FederalFacilityRegistryItem[]>>("/federal/facilities/", { params });
  return unwrap(response.data);
}

export async function flagFederalFacility(id: string, payload: { subject?: string; description?: string; priority?: string }): Promise<FederalStateQueryItem> {
  const response = await apiClient.post<ApiEnvelope<FederalStateQueryItem>>(`/federal/facilities/${id}/flag/`, payload);
  return unwrap(response.data);
}

export async function fetchFederalEmployers(params?: Record<string, string>): Promise<FederalEmployerRegistryItem[]> {
  const response = await apiClient.get<ApiEnvelope<FederalEmployerRegistryItem[]>>("/federal/employers/", { params });
  return unwrap(response.data);
}

export type FederalProfile = {
  id: string;
  ministry_name: string;
  department_name: string;
  programme_name: string;
  national_coordinator: string;
  official_email: string;
  official_phone: string;
  logo_url: string;
  active_guideline_version: string;
  reporting_cycle: "monthly" | "quarterly" | "annual";
  central_portal_status: "active" | "inactive";
  updated_by?: string | null;
  updated_by_name?: string;
  created_at: string;
  updated_at: string;
};

export async function fetchFederalProfile(): Promise<FederalProfile> {
  const response = await apiClient.get<ApiEnvelope<FederalProfile>>("/federal/profile/");
  return unwrap(response.data);
}

export async function updateFederalProfile(payload: Partial<FederalProfile>): Promise<FederalProfile> {
  const response = await apiClient.patch<ApiEnvelope<FederalProfile>>("/federal/profile/", payload);
  return unwrap(response.data);
}

export async function fetchFederalPolicy(): Promise<FederalPolicyConfig> {
  const response = await apiClient.get<ApiEnvelope<FederalPolicyConfig>>("/federal/policy/");
  return unwrap(response.data);
}

export async function updateFederalPolicy(payload: Partial<FederalPolicyConfig>): Promise<FederalPolicyConfig> {
  const response = await apiClient.patch<ApiEnvelope<FederalPolicyConfig>>("/federal/policy/", payload);
  return unwrap(response.data);
}

export async function fetchFederalStateOverrides(): Promise<FederalStateOverrideItem[]> {
  const response = await apiClient.get<ApiEnvelope<FederalStateOverrideItem[]>>("/federal/state-overrides/");
  return unwrap(response.data);
}

export type FederalIndicatorsPayload = {
  cards: Record<string, number | string>;
  sections: Record<string, FederalStatePerformanceRow[]>;
};

export type FederalDataQualityRisk = {
  state_id: string;
  state_name: string;
  risk: string;
  severity: string;
  detail: string;
};

export type FederalDataQualityPayload = {
  cards: { risk_count: number };
  risks: FederalDataQualityRisk[];
};

export type FederalAuditLogItem = {
  id: string;
  actor_name?: string;
  actor_email?: string;
  action: string;
  target_type: string;
  target_id: string;
  state_name?: string;
  metadata: Record<string, unknown>;
  risk_level: string;
  created_at: string;
};

export type FederalStateQueryItem = {
  id: string;
  state: string;
  state_name?: string;
  subject: string;
  description: string;
  category: string;
  priority: string;
  status: string;
  raised_by?: string | null;
  raised_by_name?: string;
  assigned_to?: string | null;
  assigned_to_name?: string;
  response: string;
  responded_by?: string | null;
  responded_by_name?: string;
  responded_at?: string | null;
  closed_at?: string | null;
  created_at: string;
  updated_at: string;
};

export async function fetchFederalIndicators(): Promise<FederalIndicatorsPayload> {
  const response = await apiClient.get<ApiEnvelope<FederalIndicatorsPayload>>("/federal/m-and-e/indicators/");
  return unwrap(response.data);
}

export async function fetchFederalDataQuality(): Promise<FederalDataQualityPayload> {
  const response = await apiClient.get<ApiEnvelope<FederalDataQualityPayload>>("/federal/data-quality/");
  return unwrap(response.data);
}

export async function fetchFederalAuditLogs(params?: Record<string, string>): Promise<FederalAuditLogItem[]> {
  const response = await apiClient.get<ApiEnvelope<FederalAuditLogItem[]>>("/federal/audit-logs/", { params });
  return unwrap(response.data);
}

export type FederalDashboardWidgets = {
  states_onboarded: number;
  states_using_latest_policy: number;
  approved_facilities: number;
  registered_food_handlers: number;
  assessments_completed: number;
  certificates_issued: number;
  active_certificates: number;
  expired_certificates: number;
  temporary_unfit_reports: number;
  state_report_submissions: { submitted: number; accepted: number; returned: number };
  compliance_alerts: number;
  qr_verification_activity: number;
  public_awareness_campaigns: number;
};

export async function fetchFederalDashboardWidgets(): Promise<FederalDashboardWidgets> {
  const response = await apiClient.get<ApiEnvelope<FederalDashboardWidgets>>("/federal/dashboard/widgets/");
  return unwrap(response.data);
}

export async function fetchFederalAccountAuditLogs(params?: Record<string, string>): Promise<FederalAuditLogItem[]> {
  const response = await apiClient.get<ApiEnvelope<FederalAuditLogItem[]>>("/federal/account-audit-logs/", { params });
  return unwrap(response.data);
}

export type PublicNoticeAudience = "states" | "medical_facilities" | "food_businesses" | "food_handlers" | "inspectors" | "general_public";

export type PublicNotice = {
  id: string;
  title: string;
  body: string;
  audiences: PublicNoticeAudience[];
  attachments: { name: string; url: string }[];
  effective_date?: string | null;
  expiry_date?: string | null;
  status: "draft" | "submitted" | "approved" | "published" | "archived";
  created_by_name?: string;
  published_by_name?: string;
  submitted_at?: string | null;
  approved_at?: string | null;
  published_at?: string | null;
  created_at: string;
  updated_at: string;
};

export async function fetchPublicNotices(params?: { status?: string }): Promise<PublicNotice[]> {
  const response = await apiClient.get<ApiEnvelope<PublicNotice[]>>("/federal/notices/", { params });
  return unwrap(response.data);
}

export async function createPublicNotice(payload: Partial<PublicNotice>): Promise<PublicNotice> {
  const response = await apiClient.post<ApiEnvelope<PublicNotice>>("/federal/notices/", payload);
  return unwrap(response.data);
}

export async function updatePublicNotice(id: string, payload: Partial<PublicNotice>): Promise<PublicNotice> {
  const response = await apiClient.patch<ApiEnvelope<PublicNotice>>(`/federal/notices/${id}/`, payload);
  return unwrap(response.data);
}

export async function actionPublicNotice(id: string, action: "submit" | "approve" | "publish" | "archive", comment = ""): Promise<PublicNotice> {
  const response = await apiClient.patch<ApiEnvelope<PublicNotice>>(`/federal/notices/${id}/${action}/`, { comment });
  return unwrap(response.data);
}

export type ComplianceAlert = {
  id: string;
  alert_type: string;
  alert_type_display: string;
  severity: "low" | "medium" | "high" | "critical";
  status: "open" | "acknowledged" | "in_review" | "resolved" | "dismissed";
  title: string;
  description: string;
  state?: string | null;
  state_name?: string;
  entity_type: string;
  entity_id: string;
  metric_value?: number | null;
  threshold_value?: number | null;
  auto_generated: boolean;
  metadata: Record<string, unknown>;
  created_by_name?: string;
  resolved_by_name?: string;
  resolved_at?: string | null;
  resolution_note: string;
  last_detected_at?: string | null;
  created_at: string;
  updated_at: string;
};

export async function fetchComplianceAlerts(params?: { status?: string; alert_type?: string; severity?: string; state?: string; auto_generated?: string }): Promise<ComplianceAlert[]> {
  const response = await apiClient.get<ApiEnvelope<ComplianceAlert[]>>("/federal/compliance/alerts/", { params });
  return unwrap(response.data);
}

export async function createComplianceAlert(payload: {
  alert_type: string;
  severity?: string;
  title: string;
  description?: string;
  state?: string;
  entity_type?: string;
  entity_id?: string;
}): Promise<ComplianceAlert> {
  const response = await apiClient.post<ApiEnvelope<ComplianceAlert>>("/federal/compliance/alerts/", payload);
  return unwrap(response.data);
}

export async function runComplianceScan(): Promise<{ created: number; updated: number; open_alerts: number }> {
  const response = await apiClient.post<ApiEnvelope<{ created: number; updated: number; open_alerts: number }>>("/federal/compliance/scan/");
  return unwrap(response.data);
}

export async function actionComplianceAlert(
  id: string,
  action: "acknowledge" | "in-review" | "resolve" | "dismiss",
  note = "",
): Promise<ComplianceAlert> {
  const response = await apiClient.patch<ApiEnvelope<ComplianceAlert>>(`/federal/compliance/alerts/${id}/${action}/`, { note });
  return unwrap(response.data);
}

export type FederalStateReportItem = {
  id: string;
  state: string;
  state_name?: string;
  report_type: string;
  reporting_period_start: string;
  reporting_period_end: string;
  status: "draft" | "generated" | "submitted" | "returned" | "accepted" | "escalated";
  submitted_by_name?: string;
  submitted_at?: string | null;
  reviewed_by_name?: string;
  reviewed_at?: string | null;
  review_comment: string;
  data_snapshot: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export async function fetchFederalReports(params?: { status?: string; state?: string }): Promise<FederalStateReportItem[]> {
  const response = await apiClient.get<ApiEnvelope<FederalStateReportItem[]>>("/federal/reports/", { params });
  return unwrap(response.data);
}

export async function reviewFederalReport(
  id: string,
  action: "accept" | "return" | "escalate",
  comment = "",
): Promise<FederalStateReportItem> {
  const response = await apiClient.patch<ApiEnvelope<FederalStateReportItem>>(`/federal/reports/${id}/${action}/`, { comment });
  return unwrap(response.data);
}

export async function sendStateAdoptionReminder(stateId: string): Promise<{
  state_id: string;
  state_name: string;
  policy_version_id: string;
  policy_version_code: string;
  acknowledgement_status: string;
}> {
  const response = await apiClient.post<ApiEnvelope<{ state_id: string; state_name: string; policy_version_id: string; policy_version_code: string; acknowledgement_status: string }>>(
    `/federal/states/${stateId}/send-adoption-reminder/`,
  );
  return unwrap(response.data);
}

export async function fetchFederalQueries(params?: { status?: string; state?: string }): Promise<FederalStateQueryItem[]> {
  const response = await apiClient.get<ApiEnvelope<FederalStateQueryItem[]>>("/federal/queries/", { params });
  return unwrap(response.data);
}

export async function createFederalQuery(payload: {
  state: string;
  subject: string;
  description?: string;
  category: string;
  priority?: string;
  assigned_to?: string;
}): Promise<FederalStateQueryItem> {
  const response = await apiClient.post<ApiEnvelope<FederalStateQueryItem>>("/federal/queries/", payload);
  return unwrap(response.data);
}

export async function respondFederalQuery(id: string, responseText: string): Promise<FederalStateQueryItem> {
  const response = await apiClient.patch<ApiEnvelope<FederalStateQueryItem>>(`/federal/queries/${id}/respond/`, { response: responseText });
  return unwrap(response.data);
}

export async function closeFederalQuery(id: string): Promise<FederalStateQueryItem> {
  const response = await apiClient.patch<ApiEnvelope<FederalStateQueryItem>>(`/federal/queries/${id}/close/`);
  return unwrap(response.data);
}
