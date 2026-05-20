import type { MinistryStaffRole, UserRole } from "@/types/auth";

export const ROLE_LABELS: Record<UserRole, string> = {
  super_admin: "Super Admin",
  federal_admin: "Federal Admin",
  state_admin: "State Ministry Admin",
  facility_admin: "Medical Facility Admin",
  doctor: "Doctor",
  lab_staff: "Lab Staff",
  employer: "Employer",
  food_handler: "Food Handler",
  inspector: "Inspector"
};

export const MINISTRY_STAFF_ROLE_LABELS: Record<MinistryStaffRole, string> = {
  state_super_admin: "State Ministry Super Admin",
  food_safety_officer: "Food Safety Directorate Officer",
  certificate_verification_officer: "Certificate Verification Officer",
  facility_accreditation_officer: "Facility Accreditation Officer",
  policy_finance_officer: "Policy and Finance Officer",
  inspectorate_coordinator: "Inspectorate Coordinator",
  lga_officer: "LGA Office Officer",
  federal_super_admin: "Federal Ministry Super Admin",
  national_food_safety_officer: "National Food Safety Programme Officer",
  national_me_officer: "National M&E Officer",
  national_policy_officer: "National Policy Officer",
  national_finance_officer: "National Finance/Oversight Officer",
  federal_viewer: "Federal Viewer"
};
