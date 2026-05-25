export type CertificateRequestStatus =
  | "pending_validation"
  | "approved"
  | "rejected"
  | "correction_requested"
  | "suspended";

export type CertificateStatus =
  | "active"
  | "expired"
  | "revoked"
  | "suspended"
  | "replaced"
  | "pending_validation"
  | "rejected";

export type CertificateRequest = {
  id: string;
  assessment: string;
  food_handler_name?: string;
  facility_name?: string;
  issuing_state_name?: string;
  requested_by?: string;
  requested_by_name?: string;
  reviewed_by?: string;
  reviewed_by_name?: string;
  status: CertificateRequestStatus;
  request_notes: string;
  review_notes: string;
  reviewed_at?: string;
  facility_response: string;
  facility_responded_by?: string;
  facility_responded_by_name?: string;
  facility_responded_at?: string;
  created_at: string;
  updated_at: string;
};

export type Certificate = {
  id: string;
  certificate_number: string;
  public_id?: string;
  verification_token?: string;
  food_handler: string;
  food_handler_name?: string;
  masked_nin?: string;
  assessment: string;
  employer?: string;
  employer_name?: string;
  business_branch?: string;
  facility: string;
  facility_name?: string;
  doctor: string;
  doctor_name?: string;
  issuing_state: string;
  issuing_state_name?: string;
  issued_by_state_user?: string;
  issue_date: string;
  expiry_date: string;
  status: CertificateStatus;
  effective_status: CertificateStatus;
  qr_code_url: string;
  verification_url: string;
  pdf_url: string;
  digital_signature_hash: string;
  replaced_by?: string;
  replacement_reason?: string;
  suspended_by?: string;
  suspended_at?: string;
  suspension_reason?: string;
  revoked_by?: string;
  revoked_at?: string;
  revocation_reason: string;
  renewal_status?: "not_started" | "renewal_due" | "assessment_pending" | "awaiting_state_validation" | "new_certificate_issued" | "renewal_overdue";
  created_at: string;
  updated_at: string;
};

export type PublicCertificateVerification = {
  certificate_validity: "valid" | "expired" | "revoked" | "suspended" | "replaced" | "invalid" | "not_found";
  certificate_number: string;
  food_handler_name?: string;
  passport_photo?: string;
  issuing_state_ministry?: string;
  approved_medical_facility?: string;
  issue_date?: string;
  expiry_date?: string;
  fitness_status?: string;
  last_verified_at?: string;
};
