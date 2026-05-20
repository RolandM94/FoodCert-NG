export type ClearanceStatus = "pending" | "under_review" | "cleared" | "rejected" | "clearance_required";

export type IllnessReport = {
  id: string;
  food_handler: string;
  food_handler_name?: string;
  employer?: string;
  employer_name?: string;
  reported_by: string;
  reported_by_name?: string;
  symptoms: Record<string, boolean | string>;
  suspected_condition: string;
  symptom_start_date?: string;
  symptom_end_date?: string;
  exclusion_start_date: string;
  earliest_return_date?: string;
  clearance_required: boolean;
  clearance_status: ClearanceStatus;
  reviewed_by_doctor?: string;
  reviewed_by_doctor_name?: string;
  reviewed_at?: string;
  cleared_at?: string;
  return_to_work_certificate_number: string;
  notes: string;
  created_at: string;
  updated_at: string;
};
