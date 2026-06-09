export type OrganizationType =
  | "platform_operator"
  | "federal_ministry"
  | "state_ministry"
  | "medical_facility"
  | "employer";

export type OrganizationStatus = "active" | "inactive" | "suspended";

export type Organization = {
  id: string;
  name: string;
  organization_type: OrganizationType;
  status: OrganizationStatus;
  state?: string;
  state_name?: string;
  lga?: string;
  lga_name?: string;
  address: string;
  phone: string;
  email: string;
  created_at: string;
  updated_at: string;
};

export type OrganizationUnitType =
  | "headquarters"
  | "directorate"
  | "department"
  | "unit"
  | "branch"
  | "lab_department"
  | "clinical_department"
  | "records_department"
  | "lga_office"
  | "regional_office"
  | "other";

export type OrganizationUnit = {
  id: string;
  organization: string;
  organization_name?: string;
  name: string;
  unit_type: OrganizationUnitType;
  parent?: string;
  parent_name?: string;
  description: string;
  state?: string;
  state_name?: string;
  lga?: string;
  lga_name?: string;
  address: string;
  phone: string;
  email: string;
  is_active: boolean;
  member_count: number;
  open_assessment_count: number;
  pending_lab_test_count: number;
  records_ready_count: number;
  created_at: string;
  updated_at: string;
};

export type InviteStatus = "pending" | "accepted" | "expired" | "revoked" | "declined" | "failed";

export type UserInvite = {
  id: string;
  organization: string;
  organization_name?: string;
  organization_type?: OrganizationType;
  unit?: string;
  unit_name?: string;
  unit_restricted?: boolean;
  invited_by: string;
  invited_by_email?: string;
  invited_by_name?: string;
  email: string;
  phone: string;
  role: string;
  ministry_staff_role?: string;
  message: string;
  status: InviteStatus;
  token?: string;
  accepted_by?: string;
  accepted_by_name?: string;
  accepted_at?: string;
  expires_at: string;
  created_at: string;
  updated_at: string;
};
