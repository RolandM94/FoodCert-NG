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
  created_at: string;
  updated_at: string;
};

export type Certificate = {
  id: string;
  certificate_number: string;
  food_handler: string;
  food_handler_name?: string;
  masked_nin?: string;
  assessment: string;
  employer?: string;
  employer_name?: string;
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
  revoked_by?: string;
  revoked_at?: string;
  revocation_reason: string;
  created_at: string;
  updated_at: string;
};

export type PublicCertificateVerification = {
  certificate_validity: "valid" | "expired" | "revoked" | "suspended" | "invalid" | "not_found";
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
