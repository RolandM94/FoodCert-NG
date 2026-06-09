export type OrganizationType =
  | "platform_operator"
  | "federal_ministry"
  | "state_ministry"
  | "medical_facility"
  | "employer";

export type OrganizationStatus =
  | "draft"
  | "active"
  | "pending-approval"
  | "suspended"
  | "inactive"
  | "archived";

export type Organization = {
  id: string;
  name: string;
  organization_type: OrganizationType;
  status: OrganizationStatus;
  parent?: string;
  parent_name?: string;
  state?: string;
  state_name?: string;
  lga?: string;
  lga_name?: string;
  address: string;
  contact_person_name?: string;
  phone: string;
  email: string;
  website?: string;
  created_by?: string;
  created_by_email?: string;
  children_count?: number;
  membership_count?: number;
  unit_count?: number;
  created_at: string;
  updated_at: string;
};

export type OrganizationUnitType =
  | "headquarters"
  | "directorate"
  | "department"
  | "unit"
  | "desk"
  | "office"
  | "branch"
  | "regional_office"
  | "site"
  | "outlet"
  | "store"
  | "lga_office"
  | "inspectorate"
  | "lab_department"
  | "clinical_department"
  | "medical_records_department"
  | "records_department"
  | "finance_unit"
  | "administration_unit"
  | "support_unit"
  | "technical_unit"
  | "other";

export type OrganizationUnitStatus =
  | "active"
  | "inactive"
  | "suspended"
  | "closed"
  | "archived";

export type OrganizationUnit = {
  id: string;
  organization: string;
  organization_name?: string;
  name: string;
  unit_type: OrganizationUnitType;
  parent?: string;
  parent_name?: string;
  manager?: string;
  manager_name?: string;
  description: string;
  state?: string;
  state_name?: string;
  lga?: string;
  lga_name?: string;
  address: string;
  phone: string;
  email: string;
  is_active: boolean;
  status?: OrganizationUnitStatus;
  member_count: number;
  open_assessment_count: number;
  pending_lab_test_count: number;
  records_ready_count: number;
  children?: OrganizationUnit[];
  created_by?: string;
  created_by_email?: string;
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

export type Permission = {
  id: string;
  code: string;
  name: string;
  module: string;
  description: string;
  is_sensitive: boolean;
  created_at: string;
  updated_at: string;
};

export type RoleStatus = "active" | "inactive" | "deprecated";

export type StakeholderRole = {
  id: string;
  name: string;
  code: string;
  organization_type: OrganizationType | "";
  description: string;
  is_system_role: boolean;
  is_custom_role: boolean;
  status: RoleStatus;
  permission_count: number;
  permissions?: Permission[];
  created_at: string;
  updated_at: string;
};

export type MembershipStatus =
  | "invited"
  | "active"
  | "suspended"
  | "removed"
  | "expired"
  | "pending-verification"
  | "pending_verification";

export type OrganizationMembership = {
  id: string;
  user: string;
  user_name?: string;
  user_email?: string;
  organization?: string;
  role: string;
  role_name?: string;
  role_code?: string;
  unit?: string;
  unit_name?: string;
  unit_restricted: boolean;
  status: MembershipStatus;
  invited_by?: string;
  invited_by_name?: string;
  joined_at?: string;
  last_active_at?: string;
  permissions?: string[];
  overrides?: PermissionOverrideSummary[];
  audit_log?: AuditEntry[];
  created_at: string;
  updated_at: string;
};

export type PermissionOverrideSummary = {
  id: string;
  permission: string;
  permission_code: string;
  permission_name: string;
  effect: "allow" | "deny";
  reason: string;
  expires_at?: string;
};

export type AuditEntry = {
  id: string;
  action: string;
  actor: string;
  actor_name: string;
  old_value?: string;
  new_value?: string;
  metadata?: Record<string, unknown>;
  created_at: string;
};
