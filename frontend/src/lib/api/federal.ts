import { apiClient, unwrap, type ApiEnvelope } from "@/lib/api/client";
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

export async function fetchFederalEmployers(params?: Record<string, string>): Promise<FederalEmployerRegistryItem[]> {
  const response = await apiClient.get<ApiEnvelope<FederalEmployerRegistryItem[]>>("/federal/employers/", { params });
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
