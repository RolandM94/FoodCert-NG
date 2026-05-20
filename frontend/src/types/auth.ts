export type UserRole =
  | "super_admin"
  | "federal_admin"
  | "state_admin"
  | "facility_admin"
  | "doctor"
  | "lab_staff"
  | "employer"
  | "food_handler"
  | "inspector";

export type UserStatus = "active" | "inactive" | "suspended";

export type MinistryType = "state" | "federal";

export type MinistryStaffRole =
  | "state_super_admin"
  | "food_safety_officer"
  | "certificate_verification_officer"
  | "facility_accreditation_officer"
  | "policy_finance_officer"
  | "inspectorate_coordinator"
  | "lga_officer"
  | "federal_super_admin"
  | "national_food_safety_officer"
  | "national_me_officer"
  | "national_policy_officer"
  | "national_finance_officer"
  | "federal_viewer";

export type MinistryStaffProfile = {
  id: string;
  ministry_type: MinistryType;
  sub_role: MinistryStaffRole;
  state?: string | null;
  state_name?: string | null;
  lga?: string | null;
  lga_name?: string | null;
  unit?: string | null;
  unit_name?: string | null;
  is_active: boolean;
};

export type AuthenticatedUser = {
  id: string;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  role: UserRole;
  status: UserStatus;
  email_verified: boolean;
  phone_verified: boolean;
  organization?: string;
  organization_name?: string;
  unit?: string;
  unit_name?: string;
  unit_restricted?: boolean;
  employer_staff_role?: string;
  ministry_profile?: MinistryStaffProfile | null;
  state?: string;
  state_name?: string;
};

export type AuthTokens = {
  access: string;
  refresh: string;
  user: AuthenticatedUser;
};
