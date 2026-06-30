import { apiClient, unwrap, type ApiEnvelope } from "@/lib/api/client";
import type {
  BroadcastMessage,
  NotificationDelivery,
  NotificationDetail,
  NotificationPreference,
  NotificationProvider,
  NotificationRecord,
  NotificationTemplate,
  PreferenceUpdatePayload,
  ProviderCreatePayload,
  TemplateCreatePayload,
  TemplatePreview,
} from "@/types/notifications";

type PaginatedNotifications = {
  data: NotificationRecord[];
  meta?: { page: number; page_size: number; total: number; total_pages: number };
};

export async function listNotifications(params?: Record<string, string | undefined>): Promise<NotificationRecord[]> {
  const response = await apiClient.get<ApiEnvelope<NotificationRecord[]>>("/notifications/", { params });
  const data = response.data;
  if (data.meta) {
    return data.data;
  }
  return Array.isArray(data.data) ? data.data : [];
}

export async function getNotification(id: string): Promise<NotificationDetail> {
  const response = await apiClient.get<ApiEnvelope<NotificationDetail>>(`/notifications/${id}/`);
  return unwrap(response.data);
}

export async function getUnreadCount(params?: Record<string, string | undefined>): Promise<{ unread_count: number }> {
  const response = await apiClient.get<ApiEnvelope<{ unread_count: number }>>("/notifications/unread-count/", { params });
  return unwrap(response.data);
}

export async function markNotificationRead(id: string): Promise<NotificationDetail> {
  const response = await apiClient.post<ApiEnvelope<NotificationDetail>>(`/notifications/${id}/mark-read/`);
  return unwrap(response.data);
}

export async function markAllNotificationsRead(payload?: { category?: string }): Promise<{ marked_read: number }> {
  const response = await apiClient.post<ApiEnvelope<{ marked_read: number }>>("/notifications/mark-all-read/", payload ?? {});
  return unwrap(response.data);
}

export async function archiveNotification(id: string): Promise<NotificationDetail> {
  const response = await apiClient.post<ApiEnvelope<NotificationDetail>>(`/notifications/${id}/archive/`);
  return unwrap(response.data);
}

export async function unarchiveNotification(id: string): Promise<NotificationDetail> {
  const response = await apiClient.post<ApiEnvelope<NotificationDetail>>(`/notifications/${id}/unarchive/`);
  return unwrap(response.data);
}

export async function listPreferences(): Promise<NotificationPreference[]> {
  const response = await apiClient.get<ApiEnvelope<NotificationPreference[]>>("/notification-preferences/");
  const data = response.data;
  if (data.meta) {
    return data.data;
  }
  return Array.isArray(data.data) ? data.data : [];
}

export async function updatePreference(id: string, payload: Partial<NotificationPreference>): Promise<NotificationPreference> {
  const response = await apiClient.patch<ApiEnvelope<NotificationPreference>>(`/notification-preferences/${id}/`, payload);
  return unwrap(response.data);
}

export async function bulkUpdatePreferences(preferences: PreferenceUpdatePayload[]): Promise<NotificationPreference[]> {
  const response = await apiClient.post<ApiEnvelope<NotificationPreference[]>>("/notification-preferences/bulk-update/", { preferences });
  return unwrap(response.data);
}

export async function listTemplates(params?: Record<string, string>): Promise<NotificationTemplate[]> {
  const response = await apiClient.get<ApiEnvelope<NotificationTemplate[]>>("/admin/notification-templates/", { params });
  const data = response.data;
  if (data.meta) return data.data;
  return Array.isArray(data.data) ? data.data : [];
}

export async function getTemplate(id: string): Promise<NotificationTemplate> {
  const response = await apiClient.get<ApiEnvelope<NotificationTemplate>>(`/admin/notification-templates/${id}/`);
  return unwrap(response.data);
}

export async function createTemplate(payload: TemplateCreatePayload): Promise<NotificationTemplate> {
  const response = await apiClient.post<ApiEnvelope<NotificationTemplate>>("/admin/notification-templates/", payload);
  return unwrap(response.data);
}

export async function updateTemplate(id: string, payload: Partial<TemplateCreatePayload>): Promise<NotificationTemplate> {
  const response = await apiClient.patch<ApiEnvelope<NotificationTemplate>>(`/admin/notification-templates/${id}/`, payload);
  return unwrap(response.data);
}

export async function submitTemplateForApproval(id: string): Promise<NotificationTemplate> {
  const response = await apiClient.post<ApiEnvelope<NotificationTemplate>>(`/admin/notification-templates/${id}/submit-for-approval/`);
  return unwrap(response.data);
}

export async function approveTemplate(id: string): Promise<NotificationTemplate> {
  const response = await apiClient.post<ApiEnvelope<NotificationTemplate>>(`/admin/notification-templates/${id}/approve/`);
  return unwrap(response.data);
}

export async function archiveTemplate(id: string): Promise<NotificationTemplate> {
  const response = await apiClient.post<ApiEnvelope<NotificationTemplate>>(`/admin/notification-templates/${id}/archive/`);
  return unwrap(response.data);
}

export async function previewTemplate(id: string, context?: Record<string, string>): Promise<TemplatePreview> {
  const response = await apiClient.post<ApiEnvelope<TemplatePreview>>(`/admin/notification-templates/${id}/preview/`, { context: context ?? {} });
  return unwrap(response.data);
}

export async function listProviders(): Promise<NotificationProvider[]> {
  const response = await apiClient.get<ApiEnvelope<NotificationProvider[]>>("/admin/notification-providers/");
  const data = response.data;
  if (data.meta) return data.data;
  return Array.isArray(data.data) ? data.data : [];
}

export async function createProvider(payload: ProviderCreatePayload): Promise<NotificationProvider> {
  const response = await apiClient.post<ApiEnvelope<NotificationProvider>>("/admin/notification-providers/", payload);
  return unwrap(response.data);
}

export async function updateProvider(id: string, payload: Partial<ProviderCreatePayload>): Promise<NotificationProvider> {
  const response = await apiClient.patch<ApiEnvelope<NotificationProvider>>(`/admin/notification-providers/${id}/`, payload);
  return unwrap(response.data);
}

export async function testProvider(id: string): Promise<{ success: boolean; channel: string; provider: string; error?: string }> {
  const response = await apiClient.post<ApiEnvelope<{ success: boolean; channel: string; provider: string; error?: string }>>(`/admin/notification-providers/${id}/test/`);
  return unwrap(response.data);
}

export async function setDefaultProvider(id: string): Promise<NotificationProvider> {
  const response = await apiClient.post<ApiEnvelope<NotificationProvider>>(`/admin/notification-providers/${id}/set-default/`);
  return unwrap(response.data);
}

export async function listDeliveries(params?: Record<string, string>): Promise<NotificationDelivery[]> {
  const response = await apiClient.get<ApiEnvelope<NotificationDelivery[]>>("/admin/notification-deliveries/", { params });
  const data = response.data;
  if (data.meta) return data.data;
  return Array.isArray(data.data) ? data.data : [];
}

export async function getDelivery(id: string): Promise<NotificationDelivery> {
  const response = await apiClient.get<ApiEnvelope<NotificationDelivery>>(`/admin/notification-deliveries/${id}/`);
  return unwrap(response.data);
}

export async function retryDelivery(id: string): Promise<NotificationDelivery> {
  const response = await apiClient.post<ApiEnvelope<NotificationDelivery>>(`/admin/notification-deliveries/${id}/retry/`);
  return unwrap(response.data);
}

export async function listBroadcasts(): Promise<BroadcastMessage[]> {
  const response = await apiClient.get<ApiEnvelope<BroadcastMessage[]>>("/admin/broadcasts/");
  const data = response.data;
  if (data.meta) return data.data;
  return Array.isArray(data.data) ? data.data : [];
}

export async function createBroadcast(payload: {
  title: string; message: string; category: string; priority: string;
  audience_type: string; audience_filters?: Record<string, unknown>; channels?: string[];
}): Promise<BroadcastMessage> {
  const response = await apiClient.post<ApiEnvelope<BroadcastMessage>>("/admin/broadcasts/", payload);
  return unwrap(response.data);
}

export async function updateBroadcast(id: string, payload: Partial<BroadcastMessage>): Promise<BroadcastMessage> {
  const response = await apiClient.patch<ApiEnvelope<BroadcastMessage>>(`/admin/broadcasts/${id}/`, payload);
  return unwrap(response.data);
}

export async function estimateBroadcastAudience(id: string): Promise<{ estimated_recipient_count: number }> {
  const response = await apiClient.post<ApiEnvelope<{ estimated_recipient_count: number }>>(`/admin/broadcasts/${id}/estimate-audience/`);
  return unwrap(response.data);
}

export async function submitBroadcastForApproval(id: string): Promise<BroadcastMessage> {
  const response = await apiClient.post<ApiEnvelope<BroadcastMessage>>(`/admin/broadcasts/${id}/submit-for-approval/`);
  return unwrap(response.data);
}

export async function approveBroadcast(id: string): Promise<BroadcastMessage> {
  const response = await apiClient.post<ApiEnvelope<BroadcastMessage>>(`/admin/broadcasts/${id}/approve/`);
  return unwrap(response.data);
}

export async function sendBroadcast(id: string): Promise<BroadcastMessage> {
  const response = await apiClient.post<ApiEnvelope<BroadcastMessage>>(`/admin/broadcasts/${id}/send/`);
  return unwrap(response.data);
}

export async function archiveBroadcast(id: string): Promise<BroadcastMessage> {
  const response = await apiClient.post<ApiEnvelope<BroadcastMessage>>(`/admin/broadcasts/${id}/archive/`);
  return unwrap(response.data);
}
