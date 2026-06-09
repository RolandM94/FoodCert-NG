import { apiClient, unwrap, type ApiEnvelope } from "./client";
import type { Organization, OrganizationType, OrganizationUnit, OrganizationMembership, Permission, RoleStatus, StakeholderRole, UserInvite } from "@/types/organizations";
import type { UserRole } from "@/types/auth";

// ── Organizations ──

export async function fetchOrganizations(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<Organization[]>>("/organizations/", { params });
  return unwrap(res.data);
}

export async function fetchOrganization(id: string) {
  const res = await apiClient.get<ApiEnvelope<Organization>>(`/organizations/${id}/`);
  return unwrap(res.data);
}

export async function updateOrganization(
  id: string,
  data: Partial<{
    name: string;
    organization_type: string;
    contact_person_name: string;
    address: string;
    phone: string;
    email: string;
    website: string;
  }>
) {
  const res = await apiClient.patch<ApiEnvelope<Organization>>(`/organizations/${id}/`, data);
  return unwrap(res.data);
}

export async function suspendOrganization(id: string) {
  const res = await apiClient.patch<ApiEnvelope<Organization>>(`/organizations/${id}/suspend/`);
  return unwrap(res.data);
}

export async function reactivateOrganization(id: string) {
  const res = await apiClient.patch<ApiEnvelope<Organization>>(`/organizations/${id}/reactivate/`);
  return unwrap(res.data);
}

// ── Organization Units ──

export async function fetchUnits(organizationId: string) {
  const res = await apiClient.get<ApiEnvelope<OrganizationUnit[]>>(
    `/organizations/${organizationId}/units/`
  );
  return unwrap(res.data);
}

export async function fetchUnit(organizationId: string, unitId: string) {
  const res = await apiClient.get<ApiEnvelope<OrganizationUnit>>(
    `/organizations/${organizationId}/units/${unitId}/`
  );
  return unwrap(res.data);
}

export async function createUnit(
  organizationId: string,
  data: {
    name: string;
    unit_type: string;
    parent?: string;
    description?: string;
    state?: string;
    lga?: string;
    address?: string;
    phone?: string;
    email?: string;
  }
) {
  const res = await apiClient.post<ApiEnvelope<OrganizationUnit>>(
    `/organizations/${organizationId}/units/`,
    data
  );
  return unwrap(res.data);
}

export async function updateUnit(
  organizationId: string,
  unitId: string,
  data: Partial<{
    name: string;
    unit_type: string;
    parent: string | null;
    description: string;
    state: string | null;
    lga: string | null;
    address: string;
    phone: string;
    email: string;
  }>
) {
  const res = await apiClient.patch<ApiEnvelope<OrganizationUnit>>(
    `/organizations/${organizationId}/units/${unitId}/`,
    data
  );
  return unwrap(res.data);
}

export async function deleteUnit(organizationId: string, unitId: string) {
  await apiClient.delete(`/organizations/${organizationId}/units/${unitId}/`);
}

// ── Invites ──

export async function fetchInvites(organizationId: string) {
  const res = await apiClient.get<ApiEnvelope<UserInvite[]>>(
    `/organizations/${organizationId}/invites/`
  );
  return unwrap(res.data);
}

export async function createInvite(
  organizationId: string,
  data: {
    email: string;
    role: UserRole;
    unit?: string;
    unit_restricted?: boolean;
    phone?: string;
    message?: string;
    expires_at?: string;
  }
) {
  const res = await apiClient.post<ApiEnvelope<UserInvite>>(
    `/organizations/${organizationId}/invites/`,
    data
  );
  return unwrap(res.data);
}

export async function revokeInvite(organizationId: string, inviteId: string) {
  const res = await apiClient.delete<ApiEnvelope<UserInvite>>(
    `/organizations/${organizationId}/invites/${inviteId}/`
  );
  return unwrap(res.data);
}

export async function resendInvite(organizationId: string, inviteId: string) {
  const res = await apiClient.post<ApiEnvelope<UserInvite>>(
    `/organizations/${organizationId}/invites/${inviteId}/resend/`
  );
  return unwrap(res.data);
}

export async function fetchInvitePreview(token: string) {
  const res = await apiClient.get<ApiEnvelope<UserInvite>>(`/invites/${token}/preview/`);
  return unwrap(res.data);
}

export async function acceptInvite(token: string, data?: { password?: string; username?: string; first_name?: string; last_name?: string; phone?: string }) {
  const res = await apiClient.post<ApiEnvelope<{ user: Record<string, unknown>; invite: UserInvite }>>(
    `/invites/${token}/accept/`,
    data || {}
  );
  return unwrap(res.data);
}

export async function declineInvite(token: string) {
  const res = await apiClient.post<ApiEnvelope<UserInvite>>(`/invites/${token}/decline/`);
  return unwrap(res.data);
}

// ── User Unit Assignment ──

export async function assignUserUnit(userId: string, unitId: string | null, unitRestricted?: boolean) {
  const res = await apiClient.patch(`/users/${userId}/unit/`, {
    unit: unitId,
    unit_restricted: unitRestricted ?? (unitId !== null),
  });
  return unwrap(res.data);
}

// ── Roles & Permissions ──

export async function fetchRoles(params?: { organization_type?: OrganizationType; status?: RoleStatus; search?: string }) {
  const res = await apiClient.get<ApiEnvelope<StakeholderRole[]>>("/roles/", { params });
  return unwrap(res.data);
}

export async function fetchRolesByOrganizationType(organizationType: OrganizationType) {
  const res = await apiClient.get<ApiEnvelope<StakeholderRole[]>>(
    `/organization-types/${organizationType}/roles/`
  );
  return unwrap(res.data);
}

export async function fetchRole(roleId: string) {
  const res = await apiClient.get<ApiEnvelope<StakeholderRole>>(`/roles/${roleId}/`);
  return unwrap(res.data);
}

export async function createRole(data: {
  name: string;
  code: string;
  organization_type: OrganizationType;
  description?: string;
  status?: RoleStatus;
}) {
  const res = await apiClient.post<ApiEnvelope<StakeholderRole>>("/roles/", data);
  return unwrap(res.data);
}

export async function updateRole(roleId: string, data: Partial<{ name: string; description: string; status: RoleStatus }>) {
  const res = await apiClient.patch<ApiEnvelope<StakeholderRole>>(`/roles/${roleId}/`, data);
  return unwrap(res.data);
}

export async function fetchPermissions(params?: { module?: string; search?: string }) {
  const res = await apiClient.get<ApiEnvelope<Permission[]>>("/permissions/", { params });
  return unwrap(res.data);
}

export async function fetchRolePermissions(roleId: string) {
  const res = await apiClient.get<ApiEnvelope<Permission[]>>(`/roles/${roleId}/permissions/`);
  return unwrap(res.data);
}

export async function addRolePermission(roleId: string, permissionId: string) {
  const res = await apiClient.post<ApiEnvelope<StakeholderRole>>(`/roles/${roleId}/permissions/`, {
    permission: permissionId,
  });
  return unwrap(res.data);
}

export async function removeRolePermission(roleId: string, permissionId: string) {
  await apiClient.delete(`/roles/${roleId}/permissions/${permissionId}/`);
}

// ── Memberships ──

export async function fetchMemberships(organizationId: string, params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<OrganizationMembership[]>>(
    `/organizations/${organizationId}/memberships/`,
    { params }
  );
  return unwrap(res.data);
}

export async function fetchMembership(organizationId: string, membershipId: string) {
  const res = await apiClient.get<ApiEnvelope<OrganizationMembership>>(
    `/organizations/${organizationId}/memberships/${membershipId}/`
  );
  return unwrap(res.data);
}

export async function updateMembership(
  organizationId: string,
  membershipId: string,
  data: { role?: string; unit?: string | null; unit_restricted?: boolean }
) {
  const res = await apiClient.patch<ApiEnvelope<OrganizationMembership>>(
    `/organizations/${organizationId}/memberships/${membershipId}/`,
    data
  );
  return unwrap(res.data);
}

export async function suspendMembership(organizationId: string, membershipId: string) {
  const res = await apiClient.patch<ApiEnvelope<OrganizationMembership>>(
    `/organizations/${organizationId}/memberships/${membershipId}/suspend/`
  );
  return unwrap(res.data);
}

export async function reactivateMembership(organizationId: string, membershipId: string) {
  const res = await apiClient.patch<ApiEnvelope<OrganizationMembership>>(
    `/organizations/${organizationId}/memberships/${membershipId}/reactivate/`
  );
  return unwrap(res.data);
}

export async function removeMembership(organizationId: string, membershipId: string) {
  const res = await apiClient.patch<ApiEnvelope<OrganizationMembership>>(
    `/organizations/${organizationId}/memberships/${membershipId}/remove/`
  );
  return unwrap(res.data);
}

export async function changeMembershipRole(organizationId: string, membershipId: string, role: string) {
  const res = await apiClient.patch<ApiEnvelope<OrganizationMembership>>(
    `/organizations/${organizationId}/memberships/${membershipId}/change-role/`,
    { role }
  );
  return unwrap(res.data);
}

export async function changeMembershipUnit(
  organizationId: string,
  membershipId: string,
  unit: string | null,
  unit_restricted?: boolean
) {
  const res = await apiClient.patch<ApiEnvelope<OrganizationMembership>>(
    `/organizations/${organizationId}/memberships/${membershipId}/change-unit/`,
    { unit, unit_restricted }
  );
  return unwrap(res.data);
}

export async function toggleMembershipUnitRestriction(organizationId: string, membershipId: string) {
  const res = await apiClient.patch<ApiEnvelope<OrganizationMembership>>(
    `/organizations/${organizationId}/memberships/${membershipId}/toggle-unit-restriction/`
  );
  return unwrap(res.data);
}

// ── Stakeholder Management Context ──

export type StakeholderContext = {
  organization: {
    id: string;
    name: string;
    organization_type: string;
    status: string;
    state?: string;
    state_name?: string;
    lga_name?: string;
  };
  membership: {
    id: string;
    role?: string;
    role_name?: string;
    unit?: string;
    unit_name?: string;
    unit_restricted: boolean;
    status: string;
  };
  labels: {
    module_title: string;
    stakeholders: string;
    units: string;
    unit: string;
    invite_button: string;
  };
  permissions: {
    can_view_users: boolean;
    can_invite_users: boolean;
    can_view_roles: boolean;
    can_view_units: boolean;
    can_view_invites: boolean;
    can_view_audit_logs: boolean;
  };
};

export async function fetchStakeholderContext() {
  const res = await apiClient.get<ApiEnvelope<StakeholderContext>>("/stakeholder-management/context/");
  return unwrap(res.data);
}

export type StakeholderSummary = {
  summary: {
    total_users: number;
    active_users: number;
    pending_invites: number;
    suspended_users: number;
    total_units: number;
    active_units: number;
    roles_in_use: number;
    users_without_unit: number;
    users_with_unit_restriction: number;
  };
  recent_activity: {
    id: string;
    user_name: string;
    role_name?: string;
    unit_name?: string;
    status: string;
    updated_at: string;
  }[];
};

export async function fetchStakeholderSummary() {
  const res = await apiClient.get<ApiEnvelope<StakeholderSummary>>("/stakeholder-management/summary/");
  return unwrap(res.data);
}
