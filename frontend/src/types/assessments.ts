export type AppointmentStatus = "pending" | "confirmed" | "rescheduled" | "cancelled" | "completed" | "no_show";
export type StepStatus = "pending" | "submitted" | "validated" | "completed" | "reviewed";
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

export type Appointment = {
  id: string;
  food_handler: string;
  food_handler_name?: string;
  facility: string;
  facility_name?: string;
  doctor?: string;
  doctor_name?: string;
  employer_name?: string;
  appointment_date: string;
  status: AppointmentStatus;
  payment_status?: string;
  reason: string;
  notes: string;
  created_at: string;
  updated_at: string;
};

export type MedicalAssessment = {
  id: string;
  food_handler: string;
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
  appointment?: string;
  appointment_status?: string;
  appointment_date?: string;
  assessment_date?: string;
  payment_transaction?: string;
  payment_status?: string;
  status: string;
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
  health_declaration?: HealthDeclaration | null;
  physical_examination?: PhysicalExamination | null;
  lab_tests?: LabTest[];
  vaccinations?: VaccinationRecord[];
  created_at: string;
  updated_at: string;
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
