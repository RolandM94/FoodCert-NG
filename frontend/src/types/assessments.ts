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
  appointment_date: string;
  status: AppointmentStatus;
  reason: string;
  notes: string;
  created_at: string;
  updated_at: string;
};

export type MedicalAssessment = {
  id: string;
  food_handler: string;
  food_handler_name?: string;
  employer?: string;
  employer_name?: string;
  facility: string;
  facility_name?: string;
  doctor?: string;
  doctor_name?: string;
  appointment?: string;
  assessment_date?: string;
  payment_transaction?: string;
  status: string;
  declaration_status: StepStatus;
  physical_exam_status: StepStatus;
  lab_status: StepStatus;
  vaccination_status: StepStatus;
  final_decision: FitnessDecision;
  return_to_work_date?: string;
  signed_at?: string;
  can_request_certificate: boolean;
  created_at: string;
  updated_at: string;
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
  submitted_at?: string;
  validated_by_doctor?: string;
  validated_at?: string;
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
  examined_by: string;
  examined_by_name?: string;
  examined_at: string;
  created_at: string;
  updated_at: string;
};

export type LabTest = {
  id: string;
  assessment: string;
  test_type: string;
  test_name: string;
  status: string;
  result_value: string;
  result_notes: string;
  requested_by: string;
  resulted_by?: string;
  reviewed_by?: string;
  requested_at: string;
  resulted_at?: string;
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
  dose_number: number;
  date_administered?: string;
  expiry_date?: string;
  status: string;
  doctor_clearance: boolean;
  reminder_date?: string;
  notes: string;
  recorded_by: string;
  recorded_by_name?: string;
  reviewed_at: string;
  created_at: string;
  updated_at: string;
};
