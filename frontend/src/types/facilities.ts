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
  contact_person: string;
  phone: string;
  email: string;
  accreditation_status: AccreditationStatus;
  accreditation_start_date?: string;
  accreditation_expiry_date?: string;
  approved_by?: string;
  approved_by_name?: string;
  standard_assessment_price: string;
  can_conduct_assessments: boolean;
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
  supporting_document?: string;
  checklist_complete: boolean;
  reviewer?: string;
  reviewer_name?: string;
  review_comment: string;
  submitted_at?: string;
  reviewed_at?: string;
  created_at: string;
  updated_at: string;
};
