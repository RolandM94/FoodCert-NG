export type NotificationCategory =
  | "account"
  | "identity_verification"
  | "employer_management"
  | "facility_accreditation"
  | "appointment"
  | "assessment"
  | "lab_workflow"
  | "vaccination"
  | "certificate"
  | "renewal"
  | "payments"
  | "subscriptions"
  | "settlements"
  | "inspection"
  | "enforcement"
  | "reports"
  | "m_and_e"
  | "data_quality"
  | "security"
  | "system";

export type NotificationPriority = "low" | "normal" | "high" | "critical";

export type NotificationRecord = {
  id: string;
  category: NotificationCategory;
  category_display: string;
  priority: NotificationPriority;
  priority_display: string;
  title: string;
  message: string;
  action_url: string;
  related_object_type: string;
  related_object_id: string | null;
  is_read: boolean;
  is_archived: boolean;
  read_at: string | null;
  created_at: string;
};

export type NotificationDetail = NotificationRecord & {
  recipient: string | null;
  recipient_name: string;
  recipient_email: string;
  recipient_phone: string;
  recipient_type: string;
  organization: string | null;
  organization_name: string;
  organization_unit: string | null;
  organization_unit_name: string;
};

export type NotificationFilters = {
  category?: NotificationCategory[];
  priority?: NotificationPriority[];
  is_read?: boolean | null;
  is_archived?: boolean | null;
  search?: string;
};

export type NotificationChannel = "email" | "sms" | "in_app" | "whatsapp";

export type NotificationPreference = {
  id: string;
  user: string;
  category: NotificationCategory;
  category_display: string;
  channel: NotificationChannel;
  channel_display: string;
  is_enabled: boolean;
  digest_enabled: boolean;
  quiet_hours_start: string | null;
  quiet_hours_end: string | null;
  created_at: string;
  updated_at: string;
};

export type PreferenceUpdatePayload = {
  category: NotificationCategory;
  channel: NotificationChannel;
  is_enabled?: boolean;
  digest_enabled?: boolean;
  quiet_hours_start?: string | null;
  quiet_hours_end?: string | null;
};

export type TemplateScope = "system" | "national" | "state";

export type TemplateStatus = "draft" | "pending_approval" | "active" | "archived" | "rejected";

export type NotificationTemplate = {
  id: string;
  template_key: string;
  name: string;
  category: NotificationCategory;
  category_display: string;
  channel: NotificationChannel;
  channel_display: string;
  subject: string;
  body: string;
  allowed_variables: string[];
  language: string;
  scope: TemplateScope;
  scope_display: string;
  state: string | null;
  state_name: string;
  version: number;
  status: TemplateStatus;
  status_display: string;
  created_by: string | null;
  created_by_name: string;
  approved_by: string | null;
  approved_by_name: string;
  approved_at: string | null;
  created_at: string;
  updated_at: string;
};

export type TemplateCreatePayload = {
  template_key: string;
  name: string;
  category: NotificationCategory;
  channel: NotificationChannel;
  subject: string;
  body: string;
  allowed_variables: string[];
  language: string;
  scope: TemplateScope;
  state?: string | null;
};

export type TemplatePreview = {
  subject: string;
  body: string;
};

export type NotificationProvider = {
  id: string;
  name: string;
  channel: NotificationChannel;
  channel_display: string;
  sender_id: string;
  config: Record<string, unknown>;
  is_default: boolean;
  is_active: boolean;
  priority_order: number;
  rate_limit_per_minute: number | null;
  created_at: string;
  updated_at: string;
};

export type ProviderCreatePayload = {
  name: string;
  channel: NotificationChannel;
  sender_id?: string;
  config?: Record<string, unknown>;
  is_default?: boolean;
  is_active?: boolean;
  priority_order?: number;
  rate_limit_per_minute?: number | null;
};

export type DeliveryStatus =
  | "pending" | "queued" | "sending" | "sent" | "delivered"
  | "failed" | "bounced" | "rejected" | "opened" | "clicked"
  | "read" | "cancelled";

export type NotificationDelivery = {
  id: string;
  notification: string;
  notification_title: string;
  channel: NotificationChannel;
  channel_display: string;
  provider: string;
  destination: string;
  status: DeliveryStatus;
  status_display: string;
  provider_message_id: string;
  provider_response: Record<string, unknown>;
  error_code: string;
  error_message: string;
  retry_count: number;
  next_retry_at: string | null;
  sent_at: string | null;
  delivered_at: string | null;
  created_at: string;
  updated_at: string;
};

export type BroadcastStatus = "draft" | "pending_approval" | "approved" | "sending" | "sent" | "failed" | "cancelled";

export type BroadcastMessage = {
  id: string;
  title: string;
  message: string;
  category: NotificationCategory;
  category_display: string;
  priority: NotificationPriority;
  priority_display: string;
  audience_type: string;
  audience_filters: Record<string, unknown>;
  channels: NotificationChannel[];
  status: BroadcastStatus;
  status_display: string;
  estimated_recipient_count: number;
  sent_count: number;
  failed_count: number;
  created_by: string | null;
  created_by_name: string;
  approved_by: string | null;
  approved_by_name: string;
  sent_at: string | null;
  created_at: string;
  updated_at: string;
};
