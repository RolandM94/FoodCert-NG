export type FacilityType =
  | "hospital"
  | "clinic"
  | "diagnostic_centre"
  | "primary_health_centre"
  | "mobile_health_unit";

export type OwnershipType = "public" | "private" | "mission" | "ngo";

export type AccreditationStatus =
  | "draft"
  | "submitted"
  | "under_review"
  | "more_information_required"
  | "approved"
  | "rejected"
  | "suspended"
  | "expired"
  | "reaccreditation_due";

export type MedicalFacility = {
  id: string;
  organization: string;
  facility_name: string;
  facility_type: FacilityType;
  ownership_type: OwnershipType;
  license_number: string;
  registration_number: string;
  address: string;
  state: string;
  state_name?: string;
  lga?: string;
  lga_name?: string;
  ward: string;
  contact_person: string;
  phone: string;
  email: string;
  operating_hours: string;
  service_capacity: number;
  accreditation_status: AccreditationStatus;
  accreditation_start_date?: string;
  accreditation_expiry_date?: string;
  approved_by?: string;
  approved_by_name?: string;
  standard_assessment_price: string;
  is_active: boolean;
  can_conduct_assessments: boolean;
  profile_complete: boolean;
  created_at: string;
  updated_at: string;
};

export type FacilityAccreditationApplication = {
  id: string;
  facility: string;
  facility_name: string;
  facility_state: string;
  application_status: AccreditationStatus;
  has_reporting_policy: boolean;
  has_medical_records_computers: boolean;
  has_computer_operators: boolean;
  has_standard_forms: boolean;
  has_laboratory_request_forms: boolean;
  has_patient_files: boolean;
  has_qr_certificate_capability: boolean;
  has_internet_access: boolean;
  has_trained_records_staff: boolean;
  has_trained_clinical_staff: boolean;
  has_trained_non_clinical_staff: boolean;
  has_valid_facility_license: boolean;
  has_laboratory_capacity: boolean;
  has_valid_doctor_credentials: boolean;
  has_valid_lab_staff_credentials: boolean;
  has_infection_prevention_readiness: boolean;
  has_confidentiality_policy: boolean;
  supporting_document?: string;
  is_renewal: boolean;
  renewal_of?: string;
  checklist_complete: boolean;
  reviewer?: string;
  reviewer_name?: string;
  review_comment: string;
  submitted_at?: string;
  reviewed_at?: string;
  created_at: string;
  updated_at: string;
};

export type FacilityDocument = {
  id: string;
  facility: string;
  facility_name: string;
  accreditation_application?: string;
  document_type: string;
  file?: string;
  file_url?: string;
  status: string;
  uploaded_by?: string;
  uploaded_by_name?: string;
  review_comment: string;
  created_at: string;
  updated_at: string;
};

export type FacilityStaffProfile = {
  id: string;
  user: string;
  user_email: string;
  user_name: string;
  user_role: string;
  user_status: string;
  facility: string;
  department?: string;
  department_name?: string;
  staff_type: string;
  professional_registration_number: string;
  digital_signature_url: string;
  is_active: boolean;
  last_login?: string;
  created_at: string;
  updated_at: string;
};

export type FacilityInvite = {
  id: string;
  organization: string;
  organization_name?: string;
  unit?: string;
  unit_name?: string;
  invited_by: string;
  invited_by_email?: string;
  email: string;
  phone: string;
  role: string;
  facility_staff_type: string;
  message: string;
  status: string;
  expires_at: string;
  created_at: string;
  updated_at: string;
};
