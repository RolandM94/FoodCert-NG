export type AppointmentStatus = "pending" | "confirmed" | "rescheduled" | "cancelled" | "completed" | "no_show";
export type StepStatus = "pending" | "submitted" | "validated" | "completed" | "reviewed";
export type IdentityVerificationStatus = "pending" | "verified" | "mismatch";
export type FitnessDecision =
  | "pending"
  | "fit"
  | "temporarily_not_fit"
  | "not_fit"
  | "requires_vaccination"
  | "requires_lab_test"
  | "requires_recheck"
  | "requires_treatment"
  | "requires_public_health_clearance"
  | "return_to_work_on_date";

export type AssessmentFormScope = "system" | "national" | "state" | "facility";
export type AssessmentFormStatus =
  | "draft"
  | "pending_approval"
  | "approved"
  | "published"
  | "active"
  | "retired"
  | "rejected"
  | "changes_requested"
  | "archived";
export type AssessmentFormType =
  | "health_declaration"
  | "facility_intake"
  | "doctor_clinical_review"
  | "lab_result"
  | "vaccination_review"
  | "return_to_work"
  | "illness_report"
  | "state_validation_checklist"
  | "inspection_support";
export type AssessmentQuestionType =
  | "short_text"
  | "long_text"
  | "number"
  | "date"
  | "time"
  | "datetime"
  | "yes_no"
  | "single_choice"
  | "multiple_choice"
  | "checkbox"
  | "dropdown"
  | "phone"
  | "email"
  | "file_upload"
  | "temperature"
  | "weight"
  | "height"
  | "blood_pressure"
  | "pulse_rate"
  | "symptom_checklist"
  | "exposure_history"
  | "vaccination_date"
  | "vaccine_dose"
  | "lab_result_status"
  | "clinical_note"
  | "doctor_only_note"
  | "lab_only_note";
export type AssessmentPrivacyClassification =
  | "public_safe"
  | "employer_safe_summary"
  | "inspector_safe_summary"
  | "medical_sensitive"
  | "restricted_medical"
  | "internal_administrative"
  | "regulatory_restricted";
export type AssessmentRespondentRole = "food_handler" | "doctor" | "lab_staff" | "facility_staff" | "state_user" | "inspector";
export type AssessmentFormResponseStatus =
  | "not_started"
  | "draft"
  | "submitted"
  | "under_review"
  | "clarification_requested"
  | "reopened"
  | "resubmitted"
  | "validated"
  | "locked"
  | "superseded"
  | "archived";

export type AssessmentFormQuestion = {
  id: string;
  section: string;
  key: string;
  label: string;
  help_text: string;
  placeholder: string;
  owner_level?: "federal" | "state" | "facility";
  owner_id?: string | null;
  locked?: boolean;
  inherited_from_question?: string | null;
  editable_by_child?: boolean;
  deletable_by_child?: boolean;
  question_type: AssessmentQuestionType;
  required: boolean;
  options: string[];
  validation_rules: Record<string, unknown>;
  conditional_logic: Record<string, unknown>;
  risk_flag_rules: Record<string, unknown> | Array<Record<string, unknown>>;
  privacy_classification: AssessmentPrivacyClassification;
  respondent_role: AssessmentRespondentRole;
  sort_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type AssessmentFormSection = {
  id: string;
  template: string;
  key: string;
  title: string;
  description: string;
  owner_level?: "federal" | "state" | "facility";
  owner_id?: string | null;
  locked?: boolean;
  inherited_from_section?: string | null;
  editable_by_child?: boolean;
  deletable_by_child?: boolean;
  sort_order: number;
  visibility_rules: Record<string, unknown>;
  required_completion: boolean;
  questions: AssessmentFormQuestion[];
  created_at: string;
  updated_at: string;
};

export type AssessmentFormTemplate = {
  id: string;
  name: string;
  description: string;
  form_type: AssessmentFormType;
  scope: AssessmentFormScope;
  state?: string | null;
  state_name?: string;
  facility?: string | null;
  facility_name?: string;
  owner_organization?: string | null;
  owner_level?: "federal" | "state" | "facility";
  owner_id?: string | null;
  base_template?: string | null;
  superseded_by?: string | null;
  version: number;
  status: AssessmentFormStatus;
  is_mandatory: boolean;
  requires_approval: boolean;
  approved_by?: string | null;
  approved_at?: string | null;
  review_requested_at?: string | null;
  reviewed_by?: string | null;
  reviewed_at?: string | null;
  review_comment: string;
  published_at?: string | null;
  effective_from?: string | null;
  effective_to?: string | null;
  created_by?: string | null;
  parent_template?: string | null;
  sections: AssessmentFormSection[];
  created_at: string;
  updated_at: string;
};

export type AssessmentRequirementResolution = {
  assessment_id: string;
  assessment_type: string;
  applied_requirement_sets: Array<{ id: string; name: string; scope: AssessmentFormScope; version: number }>;
  required_forms: Array<{ id: string; name: string; form_type: AssessmentFormType; scope: AssessmentFormScope; version: number; mandatory: boolean }>;
  required_documents: string[];
  required_lab_tests: string[];
  required_vaccinations: string[];
  required_approvals: string[];
  blocking_requirements: string[];
  advisory_requirements: string[];
};

export type AssessmentFormResponse = {
  id: string;
  assessment: string;
  template: string;
  template_name?: string;
  form_type?: AssessmentFormType;
  template_version: number;
  respondent?: string | null;
  respondent_role: AssessmentRespondentRole;
  status: AssessmentFormResponseStatus;
  response_data: Record<string, unknown>;
  question_snapshot: Omit<AssessmentFormTemplate, "id" | "status" | "scope" | "state" | "facility" | "owner_organization" | "is_mandatory" | "requires_approval" | "approved_by" | "approved_at" | "review_requested_at" | "reviewed_by" | "reviewed_at" | "review_comment" | "published_at" | "effective_from" | "effective_to" | "created_by" | "parent_template" | "created_at" | "updated_at"> & {
    template_id: string;
    template_version: number;
    sections: Array<Omit<AssessmentFormSection, "template" | "created_at" | "updated_at" | "questions"> & { questions: Array<Omit<AssessmentFormQuestion, "section" | "created_at" | "updated_at" | "is_active">> }>;
  };
  risk_flags: string[];
  is_required: boolean;
  is_locked: boolean;
  version: number;
  previous_response?: string | null;
  submitted_at?: string | null;
  validated_by?: string | null;
  validated_at?: string | null;
  created_at: string;
  updated_at: string;
};

export type AssessmentFormSnapshot = AssessmentFormResponse["question_snapshot"];

export type Appointment = {
  id: string;
  food_handler: string;
  food_handler_name?: string;
  food_handler_nin?: string;
  food_handler_date_of_birth?: string;
  food_handler_passport_photo?: string | null;
  facility: string;
  facility_name?: string;
  doctor?: string;
  doctor_name?: string;
  employer_name?: string;
  appointment_date: string;
  status: AppointmentStatus;
  payment_status?: string;
  payment_transaction_id?: string | null;
  payment_receipt_number?: string;
  pay_at_facility_allowed?: boolean;
  can_confirm_payment_at_facility?: boolean;
  assessment_id?: string | null;
  assessment_status?: string | null;
  declaration_status?: StepStatus | null;
  checked_in_at?: string | null;
  checked_in_by_name?: string;
  identity_verification_status?: IdentityVerificationStatus | null;
  identity_verified_at?: string | null;
  identity_verified_by_name?: string;
  identity_mismatch_reason?: string;
  reason: string;
  notes: string;
  created_at: string;
  updated_at: string;
};

export type MedicalAssessment = {
  id: string;
  food_handler: string;
  assessment_type?: string;
  food_handler_name?: string;
  food_handler_identifier?: string;
  employer?: string;
  employer_name?: string;
  branch?: string;
  branch_name?: string;
  facility: string;
  facility_name?: string;
  doctor?: string;
  doctor_name?: string;
  assigned_lab_staff?: string | null;
  assigned_lab_staff_name?: string;
  assigned_lab_unit?: string | null;
  assigned_lab_unit_name?: string;
  appointment?: string;
  appointment_status?: string;
  appointment_date?: string;
  assessment_date?: string;
  checked_in_at?: string | null;
  checked_in_by_name?: string;
  payment_transaction?: string;
  payment_status?: string;
  status: string;
  identity_verification_status?: IdentityVerificationStatus | null;
  identity_verified_at?: string | null;
  identity_verified_by_name?: string;
  identity_mismatch_reason?: string;
  declaration_status: StepStatus;
  physical_exam_status: StepStatus;
  lab_status: StepStatus;
  vaccination_status: StepStatus;
  final_decision: FitnessDecision;
  certificate_submission_status?: string;
  return_to_work_date?: string;
  doctor_notes?: string;
  decision_draft?: FitnessDecision;
  decision_draft_return_to_work_date?: string;
  decision_draft_notes?: string;
  decision_draft_saved_at?: string;
  signed_at?: string;
  signed_by?: string;
  digital_signature_hash?: string;
  can_request_certificate: boolean;
  can_view_clinical?: boolean;
  workflow_recommendation?: AssessmentWorkflowRecommendation | null;
  health_declaration?: HealthDeclaration | null;
  physical_examination?: PhysicalExamination | null;
  lab_tests?: LabTest[];
  vaccinations?: VaccinationRecord[];
  created_at: string;
  updated_at: string;
};

export type AssessmentWorkflowRecommendation = {
  status: "ready" | "warning" | "blocked" | string;
  suggested_decision: FitnessDecision;
  rationale: string;
  reasons: string[];
  signals: {
    declaration_risk: boolean;
    physical_exam_risk: boolean;
    flagged_lab_results: number;
    repeat_required_tests: number;
    highest_lab_recommendation: string;
    vaccination_concerns: string[];
    declaration_status: StepStatus;
    physical_exam_status: StepStatus;
    lab_status: StepStatus;
    vaccination_status: StepStatus;
  };
};

export type AssessmentWorkflowItem = {
  code: string;
  label: string;
  detail?: string;
  blocking?: boolean;
  status?: "pending" | "complete" | "blocked" | "warning" | string;
};

export type AssessmentNextAction = {
  code: string;
  label: string;
};

export type AssessmentStatusSnapshot = {
  assessment: string;
  current_status: string;
  current_status_label: string;
  stage: string;
  stage_label: string;
  next_action: AssessmentNextAction;
  blockers: AssessmentWorkflowItem[];
  warnings: AssessmentWorkflowItem[];
  steps: AssessmentWorkflowItem[];
  can_cancel: boolean;
  can_close: boolean;
  can_proceed: boolean;
  updated_at: string;
};

export type AssessmentAuditTimelineItem = {
  id: string;
  action: string;
  event: string;
  label: string;
  actor_name: string;
  actor_role: string;
  target_type: string;
  target_id: string;
  metadata: Record<string, unknown>;
  created_at: string;
};

export type HealthDeclaration = {
  id: string;
  assessment: string;
  assessment_status?: string;
  template_snapshot?: string | null;
  merged_schema?: AssessmentFormSnapshot | Record<string, unknown>;
  form_response_id?: string | null;
  form_response_status?: AssessmentFormResponseStatus | "";
  response_data?: Record<string, unknown>;
  diarrhoea_vomiting_last_7_days: boolean;
  fever_more_than_one_week: boolean;
  skin_trouble: boolean;
  boils_styes_sepsis: boolean;
  discharge_eye_ear_nose_mouth: boolean;
  recurring_skin_or_ear_infection: boolean;
  recurring_bowel_disorder: boolean;
  cholera_contact_last_5_days: boolean;
  diarrhoea_vomiting_contact_last_7_days: boolean;
  typhoid_paratyphoid_jaundice_contact_last_21_days: boolean;
  typhoid_or_paratyphoid_carrier: boolean;
  previous_or_current_typhoid: boolean;
  certified_true: boolean;
  risk_flag: boolean;
  version: number;
  is_locked: boolean;
  reopened_by?: string;
  reopened_at?: string;
  reopen_reason?: string;
  submitted_at?: string;
  validated_by_doctor?: string;
  validated_at?: string;
  clarification_requested_by?: string;
  clarification_requested_at?: string;
  clarification_reason?: string;
  created_at: string;
  updated_at: string;
};

export type PhysicalExamination = {
  id: string;
  assessment: string;
  fever: boolean;
  jaundice: boolean;
  skin_infection: boolean;
  boils_styes_sepsis: boolean;
  discharge: boolean;
  diarrhoea: boolean;
  vomiting: boolean;
  sore_throat_with_fever: boolean;
  cough_or_flu: boolean;
  known_typhoid_carrier_history: boolean;
  other_notes: string;
  risk_flag: boolean;
  is_completed: boolean;
  completed_at?: string;
  examined_by: string;
  examined_by_name?: string;
  examined_at: string;
  created_at: string;
  updated_at: string;
};

export type LabTest = {
  id: string;
  assessment: string;
  parent_lab_test?: string;
  assessment_status?: string;
  food_handler_name?: string;
  facility_name?: string;
  test_type: string;
  test_name: string;
  status: string;
  repeat_required: boolean;
  repeat_reason: string;
  is_flagged: boolean;
  result_value: string;
  result_notes: string;
  lab_staff_notes?: string;
  doctor_review_notes?: string;
  doctor_recommendation?: string;
  result_document?: string;
  result_document_url?: string;
  assigned_lab_staff?: string | null;
  assigned_lab_staff_name?: string;
  assigned_lab_unit?: string | null;
  assigned_lab_unit_name?: string;
  requested_by: string;
  resulted_by?: string;
  reviewed_by?: string;
  requested_at: string;
  sample_collected_at?: string;
  resulted_at?: string;
  submitted_to_doctor_at?: string;
  reviewed_at?: string;
  created_at: string;
  updated_at: string;
};

export type VaccinationRecord = {
  id: string;
  food_handler: string;
  food_handler_name?: string;
  assessment?: string;
  vaccine_type: string;
  vaccine_name: string;
  brand_name?: string;
  batch_number?: string;
  vaccinator_name?: string;
  vaccination_facility_name?: string;
  vaccination_facility_address?: string;
  certificate_upload?: string;
  certificate_upload_url?: string;
  dose_number: number;
  date_administered?: string;
  expiry_date?: string;
  status: string;
  compliance_status?: string;
  doctor_clearance: boolean;
  next_dose_date?: string;
  reminder_date?: string;
  notes: string;
  recorded_by: string;
  recorded_by_name?: string;
  reviewed_at: string;
  created_at: string;
  updated_at: string;
};
