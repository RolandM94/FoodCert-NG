import type {
  Approval,
  CertificateTemplate,
  CertificateValidityRule,
  EstablishmentCategory,
  FacilityRequirementRule,
  FoodHandlerCategory,
  IndicatorEvidence,
  MEIndicator,
  MEIndicatorCalculationView,
  MEIndicatorDataSource,
  MEIndicatorSourceRecordsResponse,
  MEIndicatorValue,
  MedicalTestRule,
  PhysicalExaminationRule,
  PolicyDocument,
  PolicyVersion,
  ReportingTemplate,
  ReturnToWorkRule,
  StateAcknowledgement,
  StateConfigurationControl,
  StandardsAuditLog,
  VaccinationRule,
} from "@/types/standards";

import { type ApiEnvelope, apiClient, unwrap } from "./client";

const BASE = "/federal/standards";

export async function listPolicyVersions(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<PolicyVersion[]>>(`${BASE}/policy-versions/`, { params });
  return unwrap(res.data);
}

export async function getPolicyVersion(id: string) {
  const res = await apiClient.get<ApiEnvelope<PolicyVersion>>(`${BASE}/policy-versions/${id}/`);
  return unwrap(res.data);
}

export async function createPolicyVersion(data: Partial<PolicyVersion>) {
  const res = await apiClient.post<ApiEnvelope<PolicyVersion>>(`${BASE}/policy-versions/`, data);
  return unwrap(res.data);
}

export async function updatePolicyVersion(id: string, data: Partial<PolicyVersion>) {
  const res = await apiClient.patch<ApiEnvelope<PolicyVersion>>(`${BASE}/policy-versions/${id}/`, data);
  return unwrap(res.data);
}

export async function submitPolicyVersion(id: string) {
  const res = await apiClient.post<ApiEnvelope<PolicyVersion>>(`${BASE}/policy-versions/${id}/submit/`);
  return unwrap(res.data);
}

export async function approvePolicyVersion(id: string, comment?: string) {
  const res = await apiClient.post<ApiEnvelope<PolicyVersion>>(`${BASE}/policy-versions/${id}/approve/`, { comment });
  return unwrap(res.data);
}

export async function returnPolicyVersion(id: string, comment?: string) {
  const res = await apiClient.post<ApiEnvelope<PolicyVersion>>(`${BASE}/policy-versions/${id}/return/`, { comment });
  return unwrap(res.data);
}

export async function publishPolicyVersion(id: string, data?: { effective_date?: string; comment?: string }) {
  const res = await apiClient.post<ApiEnvelope<PolicyVersion>>(`${BASE}/policy-versions/${id}/publish/`, data);
  return unwrap(res.data);
}

export async function retirePolicyVersion(id: string) {
  const res = await apiClient.post<ApiEnvelope<PolicyVersion>>(`${BASE}/policy-versions/${id}/retire/`);
  return unwrap(res.data);
}

export async function archivePolicyVersion(id: string) {
  const res = await apiClient.post<ApiEnvelope<PolicyVersion>>(`${BASE}/policy-versions/${id}/archive/`);
  return unwrap(res.data);
}

export async function clonePolicyVersion(id: string, data: { version_code: string; title: string }) {
  const res = await apiClient.post<ApiEnvelope<PolicyVersion>>(`${BASE}/policy-versions/${id}/clone/`, data);
  return unwrap(res.data);
}

export async function comparePolicyVersions(id: string, otherId: string) {
  const res = await apiClient.get<ApiEnvelope<{ version_a: PolicyVersion; version_b: PolicyVersion }>>(
    `${BASE}/policy-versions/${id}/compare/${otherId}/`
  );
  return unwrap(res.data);
}

export async function listFoodHandlerCategories(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<FoodHandlerCategory[]>>(`${BASE}/food-handler-categories/`, { params });
  return unwrap(res.data);
}

export async function createFoodHandlerCategory(data: Partial<FoodHandlerCategory>) {
  const res = await apiClient.post<ApiEnvelope<FoodHandlerCategory>>(`${BASE}/food-handler-categories/`, data);
  return unwrap(res.data);
}

export async function updateFoodHandlerCategory(id: string, data: Partial<FoodHandlerCategory>) {
  const res = await apiClient.patch<ApiEnvelope<FoodHandlerCategory>>(`${BASE}/food-handler-categories/${id}/`, data);
  return unwrap(res.data);
}

export async function deleteFoodHandlerCategory(id: string) {
  await apiClient.delete(`${BASE}/food-handler-categories/${id}/`);
}

export async function listEstablishmentCategories(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<EstablishmentCategory[]>>(`${BASE}/establishment-categories/`, { params });
  return unwrap(res.data);
}

export async function createEstablishmentCategory(data: Partial<EstablishmentCategory>) {
  const res = await apiClient.post<ApiEnvelope<EstablishmentCategory>>(`${BASE}/establishment-categories/`, data);
  return unwrap(res.data);
}

export async function updateEstablishmentCategory(id: string, data: Partial<EstablishmentCategory>) {
  const res = await apiClient.patch<ApiEnvelope<EstablishmentCategory>>(`${BASE}/establishment-categories/${id}/`, data);
  return unwrap(res.data);
}

export async function deleteEstablishmentCategory(id: string) {
  await apiClient.delete(`${BASE}/establishment-categories/${id}/`);
}

export async function listMedicalTestRules(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<MedicalTestRule[]>>(`${BASE}/medical-test-rules/`, { params });
  return unwrap(res.data);
}

export async function createMedicalTestRule(data: Partial<MedicalTestRule>) {
  const res = await apiClient.post<ApiEnvelope<MedicalTestRule>>(`${BASE}/medical-test-rules/`, data);
  return unwrap(res.data);
}

export async function updateMedicalTestRule(id: string, data: Partial<MedicalTestRule>) {
  const res = await apiClient.patch<ApiEnvelope<MedicalTestRule>>(`${BASE}/medical-test-rules/${id}/`, data);
  return unwrap(res.data);
}

export async function deleteMedicalTestRule(id: string) {
  await apiClient.delete(`${BASE}/medical-test-rules/${id}/`);
}

export async function listPhysicalExaminationRules(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<PhysicalExaminationRule[]>>(`${BASE}/physical-examination-rules/`, { params });
  return unwrap(res.data);
}

export async function createPhysicalExaminationRule(data: Partial<PhysicalExaminationRule>) {
  const res = await apiClient.post<ApiEnvelope<PhysicalExaminationRule>>(`${BASE}/physical-examination-rules/`, data);
  return unwrap(res.data);
}

export async function updatePhysicalExaminationRule(id: string, data: Partial<PhysicalExaminationRule>) {
  const res = await apiClient.patch<ApiEnvelope<PhysicalExaminationRule>>(`${BASE}/physical-examination-rules/${id}/`, data);
  return unwrap(res.data);
}

export async function deletePhysicalExaminationRule(id: string) {
  await apiClient.delete(`${BASE}/physical-examination-rules/${id}/`);
}

export async function listVaccinationRules(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<VaccinationRule[]>>(`${BASE}/vaccination-rules/`, { params });
  return unwrap(res.data);
}

export async function createVaccinationRule(data: Partial<VaccinationRule>) {
  const res = await apiClient.post<ApiEnvelope<VaccinationRule>>(`${BASE}/vaccination-rules/`, data);
  return unwrap(res.data);
}

export async function updateVaccinationRule(id: string, data: Partial<VaccinationRule>) {
  const res = await apiClient.patch<ApiEnvelope<VaccinationRule>>(`${BASE}/vaccination-rules/${id}/`, data);
  return unwrap(res.data);
}

export async function deleteVaccinationRule(id: string) {
  await apiClient.delete(`${BASE}/vaccination-rules/${id}/`);
}

export async function listCertificateTemplates(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<CertificateTemplate[]>>(`${BASE}/certificate-templates/`, { params });
  return unwrap(res.data);
}

export async function createCertificateTemplate(data: Partial<CertificateTemplate>) {
  const res = await apiClient.post<ApiEnvelope<CertificateTemplate>>(`${BASE}/certificate-templates/`, data);
  return unwrap(res.data);
}

export async function updateCertificateTemplate(id: string, data: Partial<CertificateTemplate>) {
  const res = await apiClient.patch<ApiEnvelope<CertificateTemplate>>(`${BASE}/certificate-templates/${id}/`, data);
  return unwrap(res.data);
}

export async function listCertificateValidityRules(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<CertificateValidityRule[]>>(`${BASE}/certificate-validity-rules/`, { params });
  return unwrap(res.data);
}

export async function createCertificateValidityRule(data: Partial<CertificateValidityRule>) {
  const res = await apiClient.post<ApiEnvelope<CertificateValidityRule>>(`${BASE}/certificate-validity-rules/`, data);
  return unwrap(res.data);
}

export async function updateCertificateValidityRule(id: string, data: Partial<CertificateValidityRule>) {
  const res = await apiClient.patch<ApiEnvelope<CertificateValidityRule>>(`${BASE}/certificate-validity-rules/${id}/`, data);
  return unwrap(res.data);
}

export async function listReturnToWorkRules(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<ReturnToWorkRule[]>>(`${BASE}/return-to-work-rules/`, { params });
  return unwrap(res.data);
}

export async function createReturnToWorkRule(data: Partial<ReturnToWorkRule>) {
  const res = await apiClient.post<ApiEnvelope<ReturnToWorkRule>>(`${BASE}/return-to-work-rules/`, data);
  return unwrap(res.data);
}

export async function updateReturnToWorkRule(id: string, data: Partial<ReturnToWorkRule>) {
  const res = await apiClient.patch<ApiEnvelope<ReturnToWorkRule>>(`${BASE}/return-to-work-rules/${id}/`, data);
  return unwrap(res.data);
}

export async function deleteReturnToWorkRule(id: string) {
  await apiClient.delete(`${BASE}/return-to-work-rules/${id}/`);
}

export async function listFacilityRequirements(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<FacilityRequirementRule[]>>(`${BASE}/facility-requirements/`, { params });
  return unwrap(res.data);
}

export async function createFacilityRequirement(data: Partial<FacilityRequirementRule>) {
  const res = await apiClient.post<ApiEnvelope<FacilityRequirementRule>>(`${BASE}/facility-requirements/`, data);
  return unwrap(res.data);
}

export async function updateFacilityRequirement(id: string, data: Partial<FacilityRequirementRule>) {
  const res = await apiClient.patch<ApiEnvelope<FacilityRequirementRule>>(`${BASE}/facility-requirements/${id}/`, data);
  return unwrap(res.data);
}

export async function listReportingTemplates(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<ReportingTemplate[]>>(`${BASE}/reporting-templates/`, { params });
  return unwrap(res.data);
}

export async function createReportingTemplate(data: Partial<ReportingTemplate>) {
  const res = await apiClient.post<ApiEnvelope<ReportingTemplate>>(`${BASE}/reporting-templates/`, data);
  return unwrap(res.data);
}

export async function updateReportingTemplate(id: string, data: Partial<ReportingTemplate>) {
  const res = await apiClient.patch<ApiEnvelope<ReportingTemplate>>(`${BASE}/reporting-templates/${id}/`, data);
  return unwrap(res.data);
}

export async function activateReportingTemplate(id: string) {
  const res = await apiClient.post<ApiEnvelope<ReportingTemplate>>(`${BASE}/reporting-templates/${id}/submit/`);
  return unwrap(res.data);
}

export async function listMEIndicators(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<MEIndicator[]>>(`${BASE}/me-indicators/`, { params });
  return unwrap(res.data);
}

export async function getMEIndicator(id: string) {
  const res = await apiClient.get<ApiEnvelope<MEIndicator>>(`${BASE}/me-indicators/${id}/`);
  return unwrap(res.data);
}

export async function createMEIndicator(data: Partial<MEIndicator>) {
  const res = await apiClient.post<ApiEnvelope<MEIndicator>>(`${BASE}/me-indicators/`, data);
  return unwrap(res.data);
}

export async function updateMEIndicator(id: string, data: Partial<MEIndicator>) {
  const res = await apiClient.patch<ApiEnvelope<MEIndicator>>(`${BASE}/me-indicators/${id}/`, data);
  return unwrap(res.data);
}

export async function activateMEIndicator(id: string) {
  const res = await apiClient.post<ApiEnvelope<MEIndicator>>(`${BASE}/me-indicators/${id}/submit/`);
  return unwrap(res.data);
}

export type MEIndicatorDashboardSummary = {
  summary_cards: Array<{ key: string; label: string; value: number; suffix?: string; helper: string }>;
  status_breakdown: Record<string, number>;
  input_mode_breakdown: Record<string, number>;
  source_breakdown: Record<string, number>;
  rankings: Array<{
    id: string;
    name: string;
    code: string;
    status: string;
    input_mode: string;
    data_source: string;
    latest_value: string | null;
    target: string | null;
    achievement: number | null;
    last_updated: string;
  }>;
  trends: Array<{ period: string; value: number; count: number }>;
  alerts: Array<{ severity: "info" | "warning" | "critical"; title: string; detail: string; indicator_id?: string }>;
  state_comparison: Array<{ state: string; kpi_count: number; total_value: number; achievement: number | null }>;
  filters: Record<string, string>;
};

export async function getMEIndicatorDashboardSummary(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<MEIndicatorDashboardSummary>>(`${BASE}/me-indicators/dashboard-summary/`, { params });
  return unwrap(res.data);
}

export async function downloadMEIndicatorImportTemplate(id: string) {
  const res = await apiClient.get<Blob>(`${BASE}/me-indicators/${id}/import-template/`, { responseType: "blob" });
  return res.data;
}

export type MEIndicatorImportPreviewRow = {
  row: number;
  data: Record<string, unknown>;
  errors: string[];
  valid: boolean;
};

export type MEIndicatorImportPreview = {
  valid_rows: MEIndicatorImportPreviewRow[];
  invalid_rows: MEIndicatorImportPreviewRow[];
  errors: Array<{ row: number; errors: string[] }>;
  summary: { total: number; valid: number; invalid: number };
};

export async function previewMEIndicatorImport(id: string, data: { csv_text: string }) {
  const res = await apiClient.post<ApiEnvelope<MEIndicatorImportPreview>>(`${BASE}/me-indicators/${id}/import-preview/`, data);
  return unwrap(res.data);
}

export async function confirmMEIndicatorImport(id: string, data: { csv_text: string; submit?: boolean }) {
  const res = await apiClient.post<ApiEnvelope<{ summary: { imported: number; submitted: boolean }; values: MEIndicatorValue[] }>>(`${BASE}/me-indicators/${id}/import-confirm/`, data);
  return unwrap(res.data);
}

export async function listMEIndicatorDataSources(indicatorId: string) {
  const res = await apiClient.get<ApiEnvelope<MEIndicatorDataSource[]>>(`${BASE}/me-indicators/${indicatorId}/data-sources/`);
  return unwrap(res.data);
}

export async function createMEIndicatorDataSource(indicatorId: string, data: Partial<MEIndicatorDataSource>) {
  const res = await apiClient.post<ApiEnvelope<MEIndicatorDataSource>>(`${BASE}/me-indicators/${indicatorId}/data-sources/`, data);
  return unwrap(res.data);
}

export async function createMEIndicatorKpiSource(indicatorId: string, data: {
  source_kpi_ids: string[];
  calculation_method: "sum" | "average" | "ratio" | "formula";
  period_filter_mode?: MEIndicatorDataSource["period_filter_mode"];
}) {
  const res = await apiClient.post<ApiEnvelope<MEIndicatorDataSource>>(`${BASE}/me-indicators/${indicatorId}/data-sources/indicators/`, data);
  return unwrap(res.data);
}

export async function createMEIndicatorDisaggregation(indicatorId: string, data: {
  source_type: MEIndicatorDataSource["source_type"];
  field_id: string;
  field_label: string;
  level: number;
}) {
  const res = await apiClient.post<ApiEnvelope<NonNullable<MEIndicator["disaggregations"]>[number]>>(`${BASE}/me-indicators/${indicatorId}/disaggregations/`, data);
  return unwrap(res.data);
}

export async function updateMEIndicatorDataSource(id: string, data: Partial<MEIndicatorDataSource>) {
  const res = await apiClient.patch<ApiEnvelope<MEIndicatorDataSource>>(`${BASE}/indicator-data-sources/${id}/`, data);
  return unwrap(res.data);
}

export async function deleteMEIndicatorDataSource(id: string) {
  await apiClient.delete(`${BASE}/indicator-data-sources/${id}/`);
}

export async function calculateMEIndicator(id: string, data: {
  data_source_id?: string;
  source_type?: string;
  source_id?: string;
  calculation_method?: MEIndicatorDataSource["calculation_method"];
  value_field_id?: string;
  numerator_config_json?: Record<string, unknown>;
  denominator_config_json?: Record<string, unknown>;
  filter_config_json?: Record<string, unknown>;
  unicity_field_id?: string;
  period_filter_mode?: MEIndicatorDataSource["period_filter_mode"];
  period_start: string;
  period_end: string;
  records?: Array<Record<string, unknown>>;
}) {
  const res = await apiClient.post<ApiEnvelope<MEIndicatorValue>>(`${BASE}/me-indicators/${id}/calculate/`, data);
  return unwrap(res.data);
}

export async function recalculateMEIndicator(id: string, data: { period_start: string; period_end: string }) {
  const res = await apiClient.post<ApiEnvelope<MEIndicatorValue>>(`${BASE}/me-indicators/${id}/recalculate/`, data);
  return unwrap(res.data);
}

export async function overrideMEIndicator(id: string, data: {
  period_start: string;
  period_end: string;
  override_value: string;
  reason: string;
}) {
  const res = await apiClient.post<ApiEnvelope<MEIndicatorValue>>(`${BASE}/me-indicators/${id}/override/`, data);
  return unwrap(res.data);
}

export async function getMEIndicatorCalculation(id: string) {
  const res = await apiClient.get<ApiEnvelope<MEIndicatorCalculationView>>(`${BASE}/me-indicators/${id}/calculation/`);
  return unwrap(res.data);
}

export async function getMEIndicatorSourceRecords(id: string, params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<MEIndicatorSourceRecordsResponse>>(`${BASE}/me-indicators/${id}/source-records/`, { params });
  return unwrap(res.data);
}

export async function listMEIndicatorValues(indicatorId: string, params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<MEIndicatorValue[]>>(`${BASE}/me-indicators/${indicatorId}/values/`, { params });
  return unwrap(res.data);
}

export async function listAllMEIndicatorValues(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<MEIndicatorValue[]>>(`${BASE}/indicator-values/`, { params });
  return unwrap(res.data);
}

export async function createMEIndicatorValue(indicatorId: string, data: Partial<MEIndicatorValue>) {
  const res = await apiClient.post<ApiEnvelope<MEIndicatorValue>>(`${BASE}/me-indicators/${indicatorId}/values/`, data);
  return unwrap(res.data);
}

export async function listIndicatorValueEvidence(valueId: string, params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<IndicatorEvidence[]>>(`${BASE}/indicator-values/${valueId}/evidence/`, { params });
  return unwrap(res.data);
}

export async function createIndicatorValueEvidence(valueId: string, data: Partial<IndicatorEvidence>) {
  const res = await apiClient.post<ApiEnvelope<IndicatorEvidence>>(`${BASE}/indicator-values/${valueId}/evidence/`, data);
  return unwrap(res.data);
}

export async function submitIndicatorEvidence(id: string) {
  const res = await apiClient.post<ApiEnvelope<IndicatorEvidence>>(`${BASE}/indicator-evidence/${id}/submit/`);
  return unwrap(res.data);
}

export async function approveIndicatorEvidence(id: string) {
  const res = await apiClient.post<ApiEnvelope<IndicatorEvidence>>(`${BASE}/indicator-evidence/${id}/approve/`);
  return unwrap(res.data);
}

export async function rejectIndicatorEvidence(id: string, comment: string) {
  const res = await apiClient.post<ApiEnvelope<IndicatorEvidence>>(`${BASE}/indicator-evidence/${id}/reject/`, { comment });
  return unwrap(res.data);
}

export async function updateMEIndicatorValue(id: string, data: Partial<MEIndicatorValue>) {
  const res = await apiClient.patch<ApiEnvelope<MEIndicatorValue>>(`${BASE}/indicator-values/${id}/`, data);
  return unwrap(res.data);
}

export async function submitMEIndicatorValue(id: string) {
  const res = await apiClient.post<ApiEnvelope<MEIndicatorValue>>(`${BASE}/indicator-values/${id}/submit/`);
  return unwrap(res.data);
}

export async function approveMEIndicatorValue(id: string, comment?: string) {
  const res = await apiClient.post<ApiEnvelope<MEIndicatorValue>>(`${BASE}/indicator-values/${id}/approve/`, { comment });
  return unwrap(res.data);
}

export async function rejectMEIndicatorValue(id: string, comment: string) {
  const res = await apiClient.post<ApiEnvelope<MEIndicatorValue>>(`${BASE}/indicator-values/${id}/reject/`, { comment });
  return unwrap(res.data);
}

export async function listPolicyDocuments(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<PolicyDocument[]>>(`${BASE}/documents/`, { params });
  return unwrap(res.data);
}

export async function createPolicyDocument(data: Partial<PolicyDocument>) {
  const res = await apiClient.post<ApiEnvelope<PolicyDocument>>(`${BASE}/documents/`, data);
  return unwrap(res.data);
}

export async function updatePolicyDocument(id: string, data: Partial<PolicyDocument>) {
  const res = await apiClient.patch<ApiEnvelope<PolicyDocument>>(`${BASE}/documents/${id}/`, data);
  return unwrap(res.data);
}

export async function publishPolicyDocument(id: string) {
  const res = await apiClient.post<ApiEnvelope<PolicyDocument>>(`${BASE}/documents/${id}/publish/`);
  return unwrap(res.data);
}

export async function retirePolicyDocument(id: string) {
  const res = await apiClient.post<ApiEnvelope<PolicyDocument>>(`${BASE}/documents/${id}/retire/`);
  return unwrap(res.data);
}

export async function archivePolicyDocument(id: string) {
  const res = await apiClient.post<ApiEnvelope<PolicyDocument>>(`${BASE}/documents/${id}/archive/`);
  return unwrap(res.data);
}

export async function listStateConfigControls(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<StateConfigurationControl[]>>(`${BASE}/state-config-controls/`, { params });
  return unwrap(res.data);
}

export async function createStateConfigControl(data: Partial<StateConfigurationControl>) {
  const res = await apiClient.post<ApiEnvelope<StateConfigurationControl>>(`${BASE}/state-config-controls/`, data);
  return unwrap(res.data);
}

export async function updateStateConfigControl(id: string, data: Partial<StateConfigurationControl>) {
  const res = await apiClient.patch<ApiEnvelope<StateConfigurationControl>>(`${BASE}/state-config-controls/${id}/`, data);
  return unwrap(res.data);
}

export async function listApprovalQueue(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<Approval[]>>(`${BASE}/approval-queue/`, { params });
  return unwrap(res.data);
}

export async function approveApproval(id: string, comment?: string) {
  const res = await apiClient.post<ApiEnvelope<Approval>>(`${BASE}/approval-queue/${id}/approve/`, { comment });
  return unwrap(res.data);
}

export async function returnApproval(id: string, comment: string) {
  const res = await apiClient.post<ApiEnvelope<Approval>>(`${BASE}/approval-queue/${id}/return/`, { comment });
  return unwrap(res.data);
}

export async function rejectApproval(id: string, comment: string) {
  const res = await apiClient.post<ApiEnvelope<Approval>>(`${BASE}/approval-queue/${id}/reject/`, { comment });
  return unwrap(res.data);
}

export async function listStandardsAuditLogs(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<StandardsAuditLog[]>>(`${BASE}/change-history/`, { params });
  return unwrap(res.data);
}

export async function exportStandardsAuditLogs(params?: Record<string, string>) {
  const res = await apiClient.get(`${BASE}/change-history/export/`, {
    params,
    responseType: "blob",
  });
  const url = URL.createObjectURL(res.data);
  const link = document.createElement("a");
  link.href = url;
  link.download = "standards-change-history.csv";
  link.click();
  URL.revokeObjectURL(url);
}

export async function listStateAcknowledgements(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<StateAcknowledgement[]>>(`${BASE}/state-acknowledgements/`, { params });
  return unwrap(res.data);
}

export async function acknowledgePolicy(id: string, comment?: string) {
  const res = await apiClient.post<ApiEnvelope<StateAcknowledgement>>(
    `${BASE}/state-acknowledgements/${id}/acknowledge/`,
    { comment }
  );
  return unwrap(res.data);
}

export async function getActivePolicy() {
  const res = await apiClient.get<ApiEnvelope<PolicyVersion>>("/standards/active/");
  return unwrap(res.data);
}

export async function getActiveHandlerCategories() {
  const res = await apiClient.get<ApiEnvelope<FoodHandlerCategory[]>>("/standards/active/handler-categories/");
  return unwrap(res.data);
}

export async function getActiveEstablishmentCategories() {
  const res = await apiClient.get<ApiEnvelope<EstablishmentCategory[]>>("/standards/active/establishment-categories/");
  return unwrap(res.data);
}

export async function getActiveMedicalTests(categoryId?: string) {
  const params = categoryId ? { category_id: categoryId } : undefined;
  const res = await apiClient.get<ApiEnvelope<MedicalTestRule[]>>("/standards/active/medical-tests/", { params });
  return unwrap(res.data);
}

export async function getActivePhysicalExaminationRules() {
  const res = await apiClient.get<ApiEnvelope<PhysicalExaminationRule[]>>("/standards/active/physical-examination-rules/");
  return unwrap(res.data);
}

export async function getActiveVaccinationRules(categoryId?: string) {
  const params = categoryId ? { category_id: categoryId } : undefined;
  const res = await apiClient.get<ApiEnvelope<VaccinationRule[]>>("/standards/active/vaccination-rules/", { params });
  return unwrap(res.data);
}

export async function getActiveCertificateTemplate() {
  const res = await apiClient.get<ApiEnvelope<CertificateTemplate>>("/standards/active/certificate-template/");
  return unwrap(res.data);
}

export async function getActiveCertificateValidityRules() {
  const res = await apiClient.get<ApiEnvelope<CertificateValidityRule[]>>("/standards/active/certificate-validity-rules/");
  return unwrap(res.data);
}

export async function getActiveReturnToWorkRules() {
  const res = await apiClient.get<ApiEnvelope<ReturnToWorkRule[]>>("/standards/active/return-to-work-rules/");
  return unwrap(res.data);
}

export async function getActiveFacilityRequirements() {
  const res = await apiClient.get<ApiEnvelope<FacilityRequirementRule[]>>("/standards/active/facility-requirements/");
  return unwrap(res.data);
}

export async function getActiveReportingTemplate() {
  const res = await apiClient.get<ApiEnvelope<ReportingTemplate>>("/standards/active/reporting-template/");
  return unwrap(res.data);
}

export async function getActiveMEIndicators() {
  const res = await apiClient.get<ApiEnvelope<MEIndicator[]>>("/standards/active/me-indicators/");
  return unwrap(res.data);
}

export async function getActiveStateConfigurationControls() {
  const res = await apiClient.get<ApiEnvelope<StateConfigurationControl[]>>("/standards/active/state-configuration-controls/");
  return unwrap(res.data);
}
