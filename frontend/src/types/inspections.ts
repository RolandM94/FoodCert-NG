export type EnforcementAction =
  | "none"
  | "advisory"
  | "warning"
  | "compliance_notice"
  | "follow_up_required"
  | "sanction_recommended"
  | "escalated_to_state";

export type InspectionStatus =
  | "draft"
  | "assigned"
  | "accepted"
  | "scheduled"
  | "in_progress"
  | "submitted"
  | "under_review"
  | "returned_for_correction"
  | "notice_issued"
  | "corrective_action_pending"
  | "corrective_action_submitted"
  | "follow_up_required"
  | "follow_up_scheduled"
  | "resolved"
  | "employer_response_submitted"
  | "escalated"
  | "closed"
  | "cancelled";

export type InspectionResponseType = "acknowledge" | "corrective_action" | "evidence" | "comment";

export type Inspection = {
  id: string;
  inspector: string;
  inspector_name?: string;
  employer: string;
  employer_name?: string;
  branch?: string;
  branch_name?: string;
  inspection_date: string;
  gps_latitude?: string;
  gps_longitude?: string;
  checklist_responses: Record<string, boolean | string | number>;
  compliance_score?: string;
  enforcement_action: EnforcementAction;
  findings: string;
  evidence_files: Array<Record<string, unknown>>;
  status: InspectionStatus;
  submitted_at?: string;
  created_at: string;
  updated_at: string;
};

export type InspectionResponse = {
  id: string;
  inspection: string;
  submitted_by: string;
  submitted_by_name?: string;
  response_type: InspectionResponseType;
  content: string;
  evidence_file_url?: string;
  submitted_at: string;
  created_at: string;
  updated_at: string;
};

export type EmployerInspectionSummary = {
  id: string;
  inspection_date: string;
  inspector_name?: string;
  branch?: string | null;
  branch_name?: string | null;
  compliance_score?: string | null;
  findings_summary: string;
  findings: string;
  enforcement_action: EnforcementAction;
  status: InspectionStatus;
  follow_up_date?: string | null;
  response_count: number;
  submitted_at?: string | null;
  created_at: string;
  updated_at: string;
};

export type EmployerInspectionDetail = EmployerInspectionSummary & {
  checklist_responses: Record<string, boolean | string | number>;
  evidence_files: Array<Record<string, unknown>>;
  gps_latitude?: string | null;
  gps_longitude?: string | null;
  responses: InspectionResponse[];
};

export type InspectionCertificateScan = {
  id: string;
  inspection: string;
  certificate_number: string;
  certificate?: string;
  certificate_status?: string;
  result: string;
  scanned_at: string;
  created_at: string;
  updated_at: string;
};

export type InspectorCertificateVerification = {
  id?: string;
  certificate_number: string;
  certificate_validity: "valid" | "expired" | "revoked" | "suspended" | "invalid" | "not_found" | "replaced";
  verification_result?: string;
  food_handler_name?: string;
  passport_photo?: string;
  issuing_state_ministry?: string;
  approved_medical_facility?: string;
  issue_date?: string;
  expiry_date?: string;
  fitness_status?: string;
};
