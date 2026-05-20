import { apiClient, unwrap, type ApiEnvelope } from "@/lib/api/client";
import type {
  EmployerComplianceSummary,
  EmployerDashboard,
  EmployerInvite,
  EmployerNotificationsPayload,
  EmployerSettings,
  EmployerStaffRole,
  EmployerUser,
} from "@/types/employer-management";
import type { UserStatus } from "@/types/auth";

export async function listEmployerUsers(employerId: string, params?: Record<string, string>): Promise<EmployerUser[]> {
  const response = await apiClient.get<ApiEnvelope<EmployerUser[]>>(`/employers/${employerId}/users/`, { params });
  return unwrap(response.data);
}

export async function updateEmployerUser(
  employerId: string,
  userId: string,
  payload: { employer_staff_role?: EmployerStaffRole; unit?: string | null; status?: UserStatus }
): Promise<EmployerUser> {
  const response = await apiClient.patch<ApiEnvelope<EmployerUser>>(`/employers/${employerId}/users/${userId}/`, payload);
  return unwrap(response.data);
}

export async function listEmployerInvites(employerId: string, params?: Record<string, string>): Promise<EmployerInvite[]> {
  const response = await apiClient.get<ApiEnvelope<EmployerInvite[]>>(`/employers/${employerId}/invites/`, { params });
  return unwrap(response.data);
}

export async function createEmployerInvite(
  employerId: string,
  payload: { email: string; phone?: string; employer_staff_role: EmployerStaffRole; unit?: string; message?: string; expires_at?: string }
): Promise<EmployerInvite> {
  const response = await apiClient.post<ApiEnvelope<EmployerInvite>>(`/employers/${employerId}/invites/`, payload);
  return unwrap(response.data);
}

export async function revokeEmployerInvite(employerId: string, inviteId: string): Promise<EmployerInvite> {
  const response = await apiClient.delete<ApiEnvelope<EmployerInvite>>(`/employers/${employerId}/invites/${inviteId}/`);
  return unwrap(response.data);
}

export async function getEmployerDashboard(employerId: string, params?: { branch?: string }): Promise<EmployerDashboard> {
  const response = await apiClient.get<ApiEnvelope<EmployerDashboard>>(`/employers/${employerId}/dashboard/`, { params });
  return unwrap(response.data);
}

export async function getEmployerComplianceSummary(employerId: string, params?: { branch?: string }): Promise<EmployerComplianceSummary> {
  const response = await apiClient.get<ApiEnvelope<EmployerComplianceSummary>>(`/employers/${employerId}/compliance-summary/`, { params });
  return unwrap(response.data);
}

export async function listEmployerNotifications(employerId: string): Promise<EmployerNotificationsPayload> {
  const response = await apiClient.get<ApiEnvelope<EmployerNotificationsPayload>>(`/employers/${employerId}/notifications/`);
  return unwrap(response.data);
}

export async function getEmployerSettings(employerId: string): Promise<EmployerSettings> {
  const response = await apiClient.get<ApiEnvelope<EmployerSettings>>(`/employers/${employerId}/settings/`);
  return unwrap(response.data);
}

export async function updateEmployerSettings(
  employerId: string,
  payload: Partial<Pick<EmployerSettings, "notification_preferences" | "business_settings">>
): Promise<EmployerSettings> {
  const response = await apiClient.patch<ApiEnvelope<EmployerSettings>>(`/employers/${employerId}/settings/`, payload);
  return unwrap(response.data);
}
