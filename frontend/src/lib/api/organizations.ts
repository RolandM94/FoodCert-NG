import { apiClient, unwrap, type ApiEnvelope } from "./client";
import type { Organization, OrganizationUnit, UserInvite } from "@/types/organizations";
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

export async function acceptInvite(token: string, data?: { password?: string; username?: string; first_name?: string; last_name?: string; phone?: string }) {
  const res = await apiClient.post<ApiEnvelope<{ user: Record<string, unknown>; invite: UserInvite }>>(
    `/invites/${token}/accept/`,
    data || {}
  );
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
