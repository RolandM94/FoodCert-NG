export type PolicyVersionStatus =
  | "draft"
  | "under_review"
  | "returned"
  | "approved"
  | "scheduled"
  | "active"
  | "retired"
  | "archived";

export type PolicyVersionType = "major" | "minor" | "emergency";

export type RiskLevel = "low" | "medium" | "high";

export type StandardStatus = "draft" | "active" | "inactive" | "retired";

export type TestType = "laboratory" | "clinical" | "physical" | "other";

export type RuleType = "mandatory" | "conditional" | "optional" | "emergency";

export type ResultType =
  | "positive_negative"
  | "normal_abnormal"
  | "numeric"
  | "text"
  | "file";

export type Severity = "low" | "medium" | "high" | "critical";

export type TemplateStatus = "draft" | "active" | "retired";

export type ReportingFrequency =
  | "daily"
  | "weekly"
  | "monthly"
  | "quarterly"
  | "biannual"
  | "annual"
  | "ad_hoc"
  | "custom";

export type DataSource =
  | "manual"
  | "food_handler_registry"
  | "medical_test_records"
  | "test_results"
  | "certificate_records"
  | "facility_records"
  | "facility_handler_mapping"
  | "test_centers_labs"
  | "inspections"
  | "training_orientation"
  | "payments";

export type VisualizationType =
  | "card"
  | "line"
  | "bar"
  | "map"
  | "table"
  | "pie";

export type DocumentType =
  | "guideline"
  | "sop"
  | "circular"
  | "form_template"
  | "reporting_template"
  | "faq"
  | "training"
  | "awareness"
  | "memo";

export type DocumentStatus = "draft" | "published" | "retired" | "archived";

export type ApprovalStatus = "pending" | "returned" | "rejected" | "approved";

export type ImpactLevel = "low" | "medium" | "high" | "emergency";

export type AcknowledgementStatus = "pending" | "acknowledged" | "overdue";

export type FacilityRequirementCategory =
  | "documentation"
  | "staffing"
  | "equipment"
  | "digital_infrastructure"
  | "records"
  | "certification"
  | "reaccreditation";

export type EvidenceType = "text" | "file" | "checklist" | "url" | "inspection";

export interface PolicyVersion {
  id: string;
  version_code: string;
  title: string;
  description: string;
  version_type: PolicyVersionType;
  status: PolicyVersionStatus;
  effective_start_date: string | null;
  effective_end_date: string | null;
  requires_state_acknowledgement: boolean;
  change_summary: string;
  created_by: string | null;
  created_by_name: string;
  submitted_by: string | null;
  submitted_by_name: string;
  approved_by: string | null;
  approved_by_name: string;
  published_by: string | null;
  published_by_name: string;
  submitted_at: string | null;
  approved_at: string | null;
  published_at: string | null;
  retired_at: string | null;
  handler_category_count: number;
  medical_test_rule_count: number;
  vaccination_rule_count: number;
  acknowledgement_count: number;
  created_at: string;
  updated_at: string;
}

export interface PolicyVersionCompleteness {
  has_certificate_template: boolean;
  has_medical_test_rules: boolean;
  has_validity_rules: boolean;
  has_reporting_template: boolean;
  has_handler_categories: boolean;
  has_vaccination_rules: boolean;
}

export interface PolicyVersionDetail extends PolicyVersion {
  food_handler_categories: Array<{ id: string; name: string; code: string; status: string }>;
  establishment_categories: Array<{ id: string; name: string; code: string; status: string }>;
  medical_test_rules: Array<{ id: string; name: string; code: string; rule_type: string; test_type: string; blocks_certification: boolean; status: string }>;
  physical_examination_rules: Array<{ id: string; indicator_name: string; code: string; severity: string; blocks_certification: boolean; status: string }>;
  vaccination_rules: Array<{ id: string; vaccine_name: string; vaccine_code: string; required: boolean; validity_months: number | null; status: string }>;
  certificate_templates: Array<{ id: string; template_name: string; template_version: string; status: string }>;
  certificate_validity_rules: Array<{ id: string; certificate_validity_days: number; routine_assessment_interval_days: number; status: string }>;
  return_to_work_rules: Array<{ id: string; condition_name: string; condition_code: string; default_exclusion_hours: number; status: string }>;
  facility_requirement_rules: Array<{ id: string; requirement_name: string; requirement_code: string; category: string; mandatory: boolean; status: string }>;
  reporting_templates: Array<{ id: string; template_name: string; template_code: string; reporting_frequency: string; status: string }>;
  me_indicators: Array<{ id: string; indicator_name: string; indicator_code: string; data_source: string; mandatory: boolean; status: string }>;
  state_acknowledgements: Array<{ id: string; state__name: string; status: string; acknowledged_at: string | null }>;
  policy_documents: Array<{ id: string; title: string; document_type: string; version_label: string; status: string }>;
  completeness: PolicyVersionCompleteness;
}

export interface FoodHandlerCategory {
  id: string;
  policy_version: string;
  policy_version_code: string;
  name: string;
  code: string;
  description: string;
  risk_level: RiskLevel;
  certificate_required: boolean;
  medical_test_rule_group_id: string | null;
  vaccination_rule_group_id: string | null;
  nationally_locked: boolean;
  allow_state_subcategories: boolean;
  status: StandardStatus;
  created_by: string | null;
  created_by_name: string;
  created_at: string;
  updated_at: string;
}

export interface EstablishmentCategory {
  id: string;
  policy_version: string;
  policy_version_code: string;
  name: string;
  code: string;
  description: string;
  risk_level: RiskLevel;
  required_handler_categories: string[];
  compliance_requirements: string[];
  inspection_required: boolean;
  required_documents: string[];
  allow_state_subcategories: boolean;
  status: StandardStatus;
  created_by: string | null;
  created_by_name: string;
  created_at: string;
  updated_at: string;
}

export interface MedicalTestRule {
  id: string;
  policy_version: string;
  policy_version_code: string;
  name: string;
  code: string;
  test_type: TestType;
  rule_type: RuleType;
  result_type: ResultType | "";
  accepted_values: string[];
  blocking_values: string[];
  blocks_certification: boolean;
  requires_attachment: boolean;
  requires_doctor_validation: boolean;
  requires_lab_validation: boolean;
  validity_days: number | null;
  applicable_categories: string[];
  applicable_establishment_risk_levels: string[];
  emergency_activation_rule: Record<string, unknown> | null;
  status: StandardStatus;
  created_by: string | null;
  created_by_name: string;
  created_at: string;
  updated_at: string;
}

export interface PhysicalExaminationRule {
  id: string;
  policy_version: string;
  policy_version_code: string;
  indicator_name: string;
  code: string;
  description: string;
  severity: Severity;
  requires_doctor_notes: boolean;
  blocks_certification: boolean;
  requires_reexamination: boolean;
  requires_exclusion: boolean;
  return_to_work_rule: string | null;
  public_health_escalation: boolean;
  status: StandardStatus;
  created_by: string | null;
  created_by_name: string;
  created_at: string;
  updated_at: string;
}

export interface VaccinationRule {
  id: string;
  policy_version: string;
  policy_version_code: string;
  vaccine_name: string;
  vaccine_code: string;
  required: boolean;
  dose_schedule: Record<string, unknown>[];
  validity_months: number | null;
  grace_period_days: number;
  evidence_required: boolean;
  evidence_fields: string[];
  blocks_certification_if_missing: boolean;
  blocks_certification_if_expired: boolean;
  requires_doctor_prescription_if_missing: boolean;
  applicable_categories: string[];
  status: StandardStatus;
  created_by: string | null;
  created_by_name: string;
  created_at: string;
  updated_at: string;
}

export interface CertificateTemplate {
  id: string;
  policy_version: string;
  policy_version_code: string;
  template_name: string;
  template_version: string;
  layout_config: Record<string, unknown>;
  required_fields: string[];
  certificate_number_format: string;
  qr_payload_config: Record<string, unknown>;
  public_verification_fields: string[];
  status_rules: Record<string, unknown>;
  revocation_reasons: string[];
  digital_signature_config: Record<string, unknown>;
  status: TemplateStatus;
  created_by: string | null;
  created_by_name: string;
  created_at: string;
  updated_at: string;
}

export interface CertificateValidityRule {
  id: string;
  policy_version: string;
  policy_version_code: string;
  routine_assessment_interval_days: number;
  certificate_validity_days: number;
  renewal_window_days: number;
  grace_period_days: number;
  expiry_reminder_days: number[];
  illness_suspension_enabled: boolean;
  emergency_revalidation_enabled: boolean;
  status: TemplateStatus;
  created_by: string | null;
  created_by_name: string;
  created_at: string;
  updated_at: string;
}

export interface ReturnToWorkRule {
  id: string;
  policy_version: string;
  policy_version_code: string;
  condition_name: string;
  condition_code: string;
  default_exclusion_hours: number;
  requires_medical_clearance: boolean;
  requires_lab_clearance: boolean;
  negative_samples_required: number | null;
  sample_interval_hours: number | null;
  requires_health_authority_approval: boolean;
  employer_acknowledgement_required: boolean;
  clearance_document_required: boolean;
  status: StandardStatus;
  created_by: string | null;
  created_by_name: string;
  created_at: string;
  updated_at: string;
}

export interface FacilityRequirementRule {
  id: string;
  policy_version: string;
  policy_version_code: string;
  requirement_name: string;
  requirement_code: string;
  category: FacilityRequirementCategory;
  mandatory: boolean;
  evidence_type: EvidenceType;
  renewal_required: boolean;
  renewal_interval_days: number | null;
  suspension_trigger: boolean;
  status: StandardStatus;
  created_by: string | null;
  created_by_name: string;
  created_at: string;
  updated_at: string;
}

export interface ReportingTemplate {
  id: string;
  policy_version: string;
  policy_version_code: string;
  template_name: string;
  template_code: string;
  reporting_frequency: ReportingFrequency;
  deadline_rule: Record<string, unknown>;
  required_sections: string[];
  required_indicators: string[];
  required_uploads: string[];
  scoring_config: Record<string, unknown>;
  approval_required: boolean;
  status: TemplateStatus;
  created_by: string | null;
  created_by_name: string;
  created_at: string;
  updated_at: string;
}

export interface MEIndicator {
  id: string;
  policy_version: string;
  policy_version_code: string;
  indicator_name: string;
  indicator_code: string;
  description: string;
  kpi_type: "quantitative" | "qualitative";
  unit_of_measurement: string;
  input_mode: "automatic" | "manual" | "imported" | "hybrid";
  record_input_type: "progress_only" | "cumulative_only" | "progress_or_cumulative";
  progress_cumulative_relationship: "dependent" | "same" | "independent";
  target_direction: "higher_better" | "lower_better" | "exact" | "range";
  calculation_type: "" | "percentage" | "count" | "unique_count" | "ratio" | "average" | "sum" | "score" | "formula";
  calculation_source: string;
  numerator_definition: Record<string, unknown>;
  denominator_definition: Record<string, unknown>;
  policy_standard_code: string;
  rule_parameter_key: string;
  allow_manual_override: boolean;
  override_requires_reason: boolean;
  last_calculated_at: string | null;
  latest_value: number | null;
  achievement_value: number | null;
  visibility_scope: Record<string, unknown>;
  formula_config: Record<string, unknown>;
  data_source: DataSource;
  reporting_frequency: ReportingFrequency;
  target_value: number | null;
  threshold_config: Record<string, unknown>;
  visualization_type: VisualizationType;
  federal_dashboard_visible: boolean;
  state_dashboard_visible: boolean;
  mandatory: boolean;
  status: StandardStatus;
  qualitative_config?: QualitativeIndicatorConfig | null;
  disaggregations?: IndicatorDisaggregation[];
  created_by: string | null;
  created_by_name: string;
  created_at: string;
  updated_at: string;
}

export interface IndicatorDisaggregation {
  id: string;
  indicator: string;
  source_type: IndicatorDataSourceType;
  field_id: string;
  field_label: string;
  level: number;
  created_at: string;
  updated_at: string;
}

export type QualitativeInputType = "text" | "likert_scale" | "category" | "rubric";

export interface QualitativeIndicatorConfig {
  id?: string;
  input_type: QualitativeInputType;
  scale_min: number | null;
  scale_max: number | null;
  scale_labels_json: Record<string, string>;
  category_options_json: string[];
  requires_narrative: boolean;
  created_at?: string;
  updated_at?: string;
}

export type IndicatorValueApprovalStatus = "draft" | "submitted" | "approved" | "rejected";
export type EvidenceApprovalStatus = "draft" | "submitted" | "approved" | "rejected";
export type IndicatorValueSource = "manual" | "automated" | "override" | "import";
export type IndicatorDataSourceType = DataSource | "kpi";
export type IndicatorCalculationMethod = "count" | "unique_count" | "sum" | "average" | "percentage" | "ratio" | "formula";
export type IndicatorPeriodFilterMode = "all_time" | "current_period" | "custom_period";

export interface MEIndicatorValueHistory {
  id: string;
  value: string;
  action: string;
  from_status: string;
  to_status: string;
  snapshot_json: Record<string, unknown>;
  comment: string;
  actor: string | null;
  actor_name: string;
  created_at: string;
  updated_at: string;
}

export interface MEIndicatorValue {
  id: string;
  indicator: string;
  indicator_name: string;
  indicator_code: string;
  period_start: string;
  period_end: string;
  progress_value_numeric: string | number | null;
  cumulative_value_numeric: string | number | null;
  qualitative_value_text: string;
  qualitative_rating: string | number | null;
  qualitative_category: string;
  value_source: IndicatorValueSource;
  source_reference_id: string;
  approval_status: IndicatorValueApprovalStatus;
  calculation_snapshot_json: Record<string, unknown>;
  evidence_json: Array<Record<string, unknown>>;
  notes: string;
  rejection_comment: string;
  created_by: string | null;
  created_by_name: string;
  submitted_by: string | null;
  submitted_by_name: string;
  submitted_at: string | null;
  approved_by: string | null;
  approved_by_name: string;
  approved_at: string | null;
  history: MEIndicatorValueHistory[];
  disaggregated_values: IndicatorDisaggregatedValue[];
  evidence_items: IndicatorEvidence[];
  created_at: string;
  updated_at: string;
}

export interface IndicatorDisaggregatedValue {
  id: string;
  indicator_value: string;
  indicator: string;
  period_start: string;
  period_end: string;
  dimension_values_json: Record<string, string>;
  value_numeric: string | number;
  created_at: string;
  updated_at: string;
}

export interface IndicatorEvidence {
  id: string;
  indicator: string;
  indicator_name: string;
  indicator_value: string | null;
  document_id: string;
  file_id: string;
  file_url: string;
  title: string;
  description: string;
  evidence_type: EvidenceType;
  approval_status: EvidenceApprovalStatus;
  uploaded_by: string | null;
  uploaded_by_name: string;
  approved_by: string | null;
  approved_by_name: string;
  approved_at: string | null;
  rejection_comment: string;
  created_at: string;
  updated_at: string;
}

export interface MEIndicatorDataSource {
  id: string;
  indicator: string;
  source_type: IndicatorDataSourceType;
  source_id: string;
  calculation_method: IndicatorCalculationMethod;
  value_field_id: string;
  numerator_config_json: Record<string, unknown>;
  denominator_config_json: Record<string, unknown>;
  filter_config_json: Record<string, unknown>;
  unicity_field_id: string;
  period_filter_mode: IndicatorPeriodFilterMode;
  created_at: string;
  updated_at: string;
}

export interface PolicyDocument {
  id: string;
  policy_version: string | null;
  policy_version_code: string;
  title: string;
  document_type: DocumentType;
  description: string;
  file_url: string;
  version_label: string;
  target_audience: string[];
  requires_acknowledgement: boolean;
  status: DocumentStatus;
  uploaded_by: string | null;
  uploaded_by_name: string;
  published_by: string | null;
  published_by_name: string;
  published_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Approval {
  id: string;
  entity_type: string;
  entity_id: string;
  requested_by: string | null;
  requested_by_name: string;
  reviewer: string | null;
  reviewer_name: string;
  approver: string | null;
  approver_name: string;
  status: ApprovalStatus;
  impact_level: ImpactLevel;
  request_comment: string;
  review_comment: string;
  approval_comment: string;
  entity_label: string;
  action_url: string;
  change_diff: {
    old_value: Record<string, unknown>;
    new_value: Record<string, unknown>;
    event: string;
  };
  reviewed_at: string | null;
  approved_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface StandardsAuditLog {
  id: string;
  actor: string | null;
  actor_name: string;
  actor_email: string;
  action: string;
  target_type: string;
  target_id: string;
  organization: string | null;
  organization_name: string;
  state: string | null;
  state_name: string;
  ip_address: string | null;
  user_agent: string;
  old_value: Record<string, unknown> | null;
  new_value: Record<string, unknown> | null;
  metadata: Record<string, unknown>;
  event: string;
  policy_version: string;
  created_at: string;
  updated_at: string;
}

export interface StateAcknowledgement {
  id: string;
  policy_version: string;
  policy_version_code: string;
  state: string;
  state_name: string;
  acknowledged_by: string | null;
  acknowledged_by_name: string;
  acknowledgement_comment: string;
  acknowledged_at: string | null;
  status: AcknowledgementStatus;
  created_at: string;
  updated_at: string;
}

export interface StateConfigurationControl {
  id: string;
  policy_version: string;
  policy_version_code: string;
  config_domain: string;
  label: string;
  description: string;
  federal_locked: boolean;
  state_editable: boolean;
  requires_federal_approval: boolean;
  created_by: string | null;
  created_by_name: string;
  created_at: string;
  updated_at: string;
}
