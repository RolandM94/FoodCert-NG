import { apiClient, unwrap, type ApiEnvelope } from "./client";

function unwrapMaybe<T>(value: ApiEnvelope<T> | T): T {
  return value && typeof value === "object" && "data" in value ? (value as ApiEnvelope<T>).data : value as T;
}

export type FormTemplate = {
  id: string;
  title: string;
  description: string;
  purpose: string;
  owner_organization: string;
  owner_name?: string;
  target_respondent_type: string;
  primary_module: string;
  module_context: string;
  default_context_type: string;
  language: string;
  settings_json: Record<string, unknown>;
  visibility: "state_owned" | "federal_private" | "federal_shared" | "federal_standard";
  shared_with_states?: string[];
  shared_state_names?: string[];
  source_template?: string;
  source_template_title?: string;
  source_version?: string;
  status: "draft" | "published" | "archived" | "deprecated";
  current_version: number;
  created_by?: string;
  created_by_name?: string;
  response_count: number;
  adoption_count?: number;
  created_at: string;
  updated_at: string;
};

export type FormTemplateVersion = {
  id: string;
  template: string;
  version_number: number;
  schema_json: Record<string, unknown>;
  logic_json?: Record<string, unknown>;
  scoring_json?: Record<string, unknown>;
  conditional_logic_json?: Record<string, unknown>;
  settings_json?: Record<string, unknown>;
  published_by?: string;
  published_by_name?: string;
  published_at?: string;
  status: string;
  created_at: string;
};

export type FormAssignment = {
  id: string;
  title: string;
  template: string;
  template_title?: string;
  template_version?: string;
  purpose: string;
  assigned_by: string;
  assigned_by_name?: string;
  assigned_to_type: string;
  assigned_to_id: string;
  recipient_role: string;
  context_type: string;
  context_id: string;
  start_date?: string;
  due_date?: string;
  allow_draft: boolean;
  allow_offline: boolean;
  allow_multiple_submissions: boolean;
  allow_late_submission: boolean;
  requires_review: boolean;
  reviewer_role: string;
  status: string;
  response_count: number;
  total_recipients: number;
  status_summary?: {
    total_recipients: number;
    not_started: number;
    in_progress: number;
    submitted: number;
    reviewed: number;
    returned: number;
    overdue: number;
    cancelled: number;
    draft_responses: number;
    sync_pending: number;
    sync_failed: number;
  };
  response_rate: number;
  completion_rate: number;
  created_at: string;
  updated_at: string;
};

export type FormResponse = {
  id: string;
  assignment: string;
  assignment_title?: string;
  template: string;
  template_title?: string;
  template_version?: string;
  recipient?: string;
  respondent_user: string;
  respondent_name?: string;
  respondent_email?: string;
  respondent_organization?: string;
  context_type: string;
  context_id: string;
  response_json: Record<string, unknown>;
  score?: number;
  risk_rating: string;
  status: string;
  sync_status: string;
  device_id?: string;
  offline_created_at?: string;
  started_at?: string;
  last_saved_at?: string;
  submitted_at?: string;
  reviewed_by?: string;
  reviewed_by_name?: string;
  reviewed_at?: string;
  review_notes: string;
  returned_reason: string;
  template_schema?: Record<string, unknown>;
  template_logic?: Record<string, unknown>;
  template_settings?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type FormResponseAttachment = {
  id: string;
  response: string;
  question_key: string;
  repeat_group_key?: string;
  repeat_item_id?: string;
  file?: string;
  file_url?: string;
  file_type?: string;
  file_name: string;
  file_size?: number;
  mime_type?: string;
  uploaded_by?: string;
  uploaded_by_name?: string;
  captured_at?: string;
  gps_latitude?: string;
  gps_longitude?: string;
  metadata_json?: Record<string, unknown>;
  sync_status: string;
  created_at: string;
  updated_at: string;
};

export type OfflineFormPackage = {
  assignment: FormAssignment;
  template: FormTemplate;
  template_version: FormTemplateVersion | null;
  response: FormResponse | null;
  downloaded_at: string;
  sync_statuses: string[];
};

export type OfflineSyncResult = {
  status: string;
  sync_job: {
    id: string;
    local_response_id: string;
    operation_type: string;
    status: string;
    attempt_count: number;
    error_message?: string;
  };
  response?: FormResponse;
  errors?: Array<{ key: string; label: string; message: string }>;
  error?: string;
};

export type FormResponseActivity = {
  id: string;
  response: string;
  actor?: string;
  actor_name?: string;
  action: string;
  details_json: Record<string, unknown>;
  ip_address?: string;
  device_id?: string;
  created_at: string;
};

export type FormAssignmentSummary = FormAssignment & {
  responses: FormResponse[];
  recipients: Array<{
    id: string;
    assignment: string;
    recipient_type: string;
    recipient_id: string;
    organization?: string;
    organization_name?: string;
    role_id?: string;
    status: string;
    notified_at?: string;
    started_at?: string;
    submitted_at?: string;
    reviewed_at?: string;
  }>;
};

export type FederalFormResponseSummary = {
  assignment_id: string;
  assignment_title: string;
  template_id: string;
  template_title: string;
  purpose: string;
  total_assigned_states: number;
  submitted_states: number;
  pending_states: number;
  overdue_states: number;
  response_rate: number;
  returned_responses: number;
};

export type FederalStateResponseMatrixRow = {
  recipient_id: string;
  state_id: string;
  state_name: string;
  organization_id: string | null;
  organization_name: string;
  assigned_forms: number;
  submitted: number;
  pending: number;
  overdue: number;
  response_rate: number;
  status: string;
  last_submission: string | null;
};

export type FederalFormsReport = {
  key: string;
  title: string;
  description: string;
};

export type FederalFormsReportPayload = {
  reports: FederalFormsReport[];
  report_key?: string | null;
  filters: Record<string, string | null>;
  summary: {
    total_templates: number;
    total_assignments: number;
    total_responses: number;
    submitted_responses: number;
    total_assigned_states: number;
    submitted_states: number;
    pending_states: number;
    overdue_states: number;
    response_rate: number;
    returned_responses: number;
    average_score: number | null;
  };
  state_response_comparison: FederalStateResponseMatrixRow[];
  assignment_summary: Array<Record<string, unknown>>;
  overdue_submissions: Array<Record<string, unknown>>;
  template_usage: Array<Record<string, unknown>>;
  template_adoption_by_state: Array<Record<string, unknown>>;
  purpose_breakdown: Array<Record<string, unknown>>;
  status_breakdown: Array<Record<string, unknown>>;
};

export type FederalFormsExportJob = {
  id: string;
  format: "csv" | "json" | "xlsx" | "pdf";
  download_url: string;
  response_count: number;
};

// ── Templates ──
export async function fetchFormTemplates(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<FormTemplate[]>>("/forms/templates/", { params });
  return unwrap(res.data);
}

export async function fetchFormTemplate(id: string) {
  const res = await apiClient.get<ApiEnvelope<FormTemplate>>(`/forms/templates/${id}/`);
  return unwrap(res.data);
}

export async function createFormTemplate(data: {
  title: string; description?: string; purpose: string;
  owner_organization?: string; target_respondent_type?: string; primary_module?: string;
  module_context?: string; default_context_type?: string; language?: string;
  visibility?: FormTemplate["visibility"];
  settings_json?: Record<string, unknown>;
}) {
  const res = await apiClient.post<ApiEnvelope<FormTemplate>>("/forms/templates/", data);
  return unwrap(res.data);
}

export async function updateFormTemplate(id: string, data: Partial<{
  title: string; description: string; purpose: string; target_respondent_type: string;
  primary_module: string; module_context: string; default_context_type: string;
  language: string; visibility: FormTemplate["visibility"]; settings_json: Record<string, unknown>;
}>) {
  const res = await apiClient.patch<ApiEnvelope<FormTemplate>>(`/forms/templates/${id}/`, data);
  return unwrap(res.data);
}

export async function saveFormTemplateDraft(id: string, data: {
  schema_json: Record<string, unknown>; logic_json?: Record<string, unknown>;
  scoring_json?: Record<string, unknown>; settings_json?: Record<string, unknown>;
}) {
  const res = await apiClient.post<ApiEnvelope<FormTemplateVersion>>(`/forms/templates/${id}/save-draft/`, data);
  return unwrap(res.data);
}

export async function publishFormTemplate(id: string, data?: {
  schema_json?: Record<string, unknown>; logic_json?: Record<string, unknown>;
  scoring_json?: Record<string, unknown>; settings_json?: Record<string, unknown>;
}) {
  const res = await apiClient.post<ApiEnvelope<FormTemplate>>(`/forms/templates/${id}/publish/`, data || {});
  return unwrap(res.data);
}

export async function shareFormTemplateToStates(id: string, data: { state_ids?: string[]; all_states?: boolean }) {
  const res = await apiClient.post<ApiEnvelope<FormTemplate>>(`/forms/templates/${id}/share-to-states/`, data);
  return unwrap(res.data);
}

export async function markFormTemplateStandard(id: string) {
  const res = await apiClient.post<ApiEnvelope<FormTemplate>>(`/forms/templates/${id}/mark-standard/`);
  return unwrap(res.data);
}

export async function archiveFormTemplate(id: string) {
  const res = await apiClient.post<ApiEnvelope<FormTemplate>>(`/forms/templates/${id}/archive/`);
  return unwrap(res.data);
}

export async function deleteFormTemplate(id: string) {
  await apiClient.delete(`/forms/templates/${id}/`);
}

export async function fetchFormTemplateVersions(id: string) {
  const res = await apiClient.get<ApiEnvelope<FormTemplateVersion[]>>(`/forms/templates/${id}/versions/`);
  return unwrap(res.data);
}

export async function fetchStateFederalFormTemplates() {
  const res = await apiClient.get<ApiEnvelope<FormTemplate[]> | FormTemplate[]>("/state/forms/federal-templates/");
  return unwrapMaybe(res.data);
}

export async function adoptStateFederalFormTemplate(id: string) {
  const res = await apiClient.post<ApiEnvelope<FormTemplate> | FormTemplate>(`/state/forms/federal-templates/${id}/adopt/`);
  return unwrapMaybe(res.data);
}

export async function cloneStateFederalFormTemplate(id: string, data?: { title?: string }) {
  const res = await apiClient.post<ApiEnvelope<FormTemplate> | FormTemplate>(`/state/forms/federal-templates/${id}/clone/`, data || {});
  return unwrapMaybe(res.data);
}

// ── Assignments ──
export async function fetchFormAssignments(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<FormAssignment[]>>("/forms/assignments/", { params });
  return unwrap(res.data);
}

export async function createFormAssignment(data: {
  title: string; template: string; template_version?: string; purpose: string;
  assigned_to_type: string; assigned_to_id?: string; recipient_role?: string;
  context_type?: string; context_id?: string;
  due_date?: string; allow_draft?: boolean; requires_review?: boolean;
}) {
  const res = await apiClient.post<ApiEnvelope<FormAssignment>>("/forms/assignments/", data);
  return unwrap(res.data);
}

export async function cancelFormAssignment(id: string) {
  const res = await apiClient.post<ApiEnvelope<FormAssignment>>(`/forms/assignments/${id}/cancel/`);
  return unwrap(res.data);
}

export async function fetchFormAssignmentSummary(id: string) {
  const res = await apiClient.get<FormAssignmentSummary>(`/forms/assignments/${id}/summary/`);
  return res.data;
}

export async function sendFormAssignmentReminder(id: string) {
  const res = await apiClient.post<{ assignment: FormAssignment; reminded_count: number; message: string }>(`/forms/assignments/${id}/send-reminder/`);
  return res.data;
}

export async function fetchFederalFormAssignments(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<FormAssignment[]> | FormAssignment[]>("/federal/forms/assignments/", { params });
  return unwrapMaybe(res.data);
}

export async function fetchFederalFormAssignment(id: string) {
  const res = await apiClient.get<ApiEnvelope<FormAssignmentSummary> | FormAssignmentSummary>(`/federal/forms/assignments/${id}/`);
  return unwrapMaybe(res.data);
}

export async function createFederalFormAssignment(data: {
  title?: string;
  template: string;
  recipient_scope: "all_states" | "selected_states" | "employer" | "facility" | "food_handler" | "inspector";
  state_ids?: string[];
  purpose?: string;
  due_date?: string;
  allow_draft?: boolean;
  allow_offline?: boolean;
  allow_multiple_submissions?: boolean;
  allow_late_submission?: boolean;
  requires_review?: boolean;
  reviewer_role?: string;
}) {
  const res = await apiClient.post<ApiEnvelope<FormAssignment> | FormAssignment>("/federal/forms/assignments/", data);
  return unwrapMaybe(res.data);
}

export async function fetchFederalFormAssignmentRecipients(id: string) {
  const res = await apiClient.get<ApiEnvelope<FormAssignmentSummary["recipients"]> | FormAssignmentSummary["recipients"]>(`/federal/forms/assignments/${id}/recipients/`);
  return unwrapMaybe(res.data);
}

export async function fetchFederalFormAssignmentResponseSummary(id: string) {
  const res = await apiClient.get<ApiEnvelope<FederalFormResponseSummary> | FederalFormResponseSummary>(`/federal/forms/assignments/${id}/response-summary/`);
  return unwrapMaybe(res.data);
}

export async function fetchFederalFormAssignmentStateResponseMatrix(id: string) {
  const res = await apiClient.get<ApiEnvelope<FederalStateResponseMatrixRow[]> | FederalStateResponseMatrixRow[]>(`/federal/forms/assignments/${id}/state-response-matrix/`);
  return unwrapMaybe(res.data);
}

export async function fetchStateFederalFormAssignments(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<FormAssignment[]> | FormAssignment[]>("/state/forms/federal-assignments/", { params });
  return unwrapMaybe(res.data);
}

export async function fetchStateFederalFormAssignment(id: string) {
  const res = await apiClient.get<ApiEnvelope<FormAssignmentSummary> | FormAssignmentSummary>(`/state/forms/federal-assignments/${id}/`);
  return unwrapMaybe(res.data);
}

export async function submitStateFederalFormAssignmentResponse(id: string, data: {
  response_json: Record<string, unknown>;
  submit?: boolean;
  score?: number;
  sync_status?: string;
}) {
  const res = await apiClient.post<ApiEnvelope<FormResponse> | FormResponse>(`/state/forms/federal-assignments/${id}/response/`, data);
  return unwrapMaybe(res.data);
}

// ── Responses ──
export async function fetchFormResponses(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<FormResponse[]>>("/forms/responses/", { params });
  return unwrap(res.data);
}

export async function fetchFormResponse(id: string) {
  const res = await apiClient.get<ApiEnvelope<FormResponse>>(`/forms/responses/${id}/`);
  return unwrap(res.data);
}

export async function fetchFederalFormResponses(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<FormResponse[]> | FormResponse[]>("/federal/forms/responses/", { params });
  return unwrapMaybe(res.data);
}

export async function fetchFederalFormResponse(id: string) {
  const res = await apiClient.get<ApiEnvelope<FormResponse> | FormResponse>(`/federal/forms/responses/${id}/`);
  return unwrapMaybe(res.data);
}

export async function fetchFederalFormsReports(params?: Record<string, string>): Promise<FederalFormsReportPayload> {
  const res = await apiClient.get<ApiEnvelope<FederalFormsReportPayload> | FederalFormsReportPayload>("/federal/forms/reports/", { params });
  return unwrapMaybe(res.data);
}

export async function fetchFederalFormsReport(reportKey: string, params?: Record<string, string>): Promise<FederalFormsReportPayload> {
  const res = await apiClient.get<ApiEnvelope<FederalFormsReportPayload> | FederalFormsReportPayload>(`/federal/forms/reports/${reportKey}/`, { params });
  return unwrapMaybe(res.data);
}

export async function createFederalFormsExport(data: {
  format: "csv" | "json" | "xlsx" | "excel" | "pdf";
  filters?: Record<string, string>;
}): Promise<FederalFormsExportJob> {
  const res = await apiClient.post<ApiEnvelope<FederalFormsExportJob> | FederalFormsExportJob>("/federal/forms/exports/", data);
  return unwrapMaybe(res.data);
}

export async function downloadFederalFormsExport(exportId: string): Promise<Blob> {
  const res = await apiClient.get<Blob>(`/federal/forms/exports/${exportId}/download/`, { responseType: "blob" });
  return res.data;
}

export async function createFormResponse(data: {
  assignment: string; template: string; template_version?: string;
  respondent_organization?: string; context_type?: string; context_id?: string;
  response_json?: Record<string, unknown>;
}) {
  const res = await apiClient.post<ApiEnvelope<FormResponse>>("/forms/responses/", data);
  return unwrap(res.data);
}

export async function submitFormResponse(id: string, data?: { response_json?: Record<string, unknown>; score?: number }) {
  const res = await apiClient.post<ApiEnvelope<FormResponse>>(`/forms/responses/${id}/submit/`, data || {});
  return unwrap(res.data);
}

export async function saveFormResponseDraft(id: string, data: { response_json: Record<string, unknown>; device_id?: string }) {
  const res = await apiClient.post<ApiEnvelope<FormResponse>>(`/forms/responses/${id}/save_draft/`, data);
  return unwrap(res.data);
}

export async function reviewFormResponse(id: string, review_notes?: string) {
  const res = await apiClient.post<ApiEnvelope<FormResponse>>(`/forms/responses/${id}/review/`, { review_notes: review_notes || "" });
  return unwrap(res.data);
}

export async function returnFormResponse(id: string, reason?: string) {
  const res = await apiClient.post<ApiEnvelope<FormResponse>>(`/forms/responses/${id}/return_response/`, { reason: reason || "" });
  return unwrap(res.data);
}

export async function fetchFormResponseActivity(id: string) {
  const res = await apiClient.get<FormResponseActivity[]>(`/forms/responses/${id}/activity/`);
  return res.data;
}

export async function fetchFormResponseAttachments(id: string) {
  const res = await apiClient.get<ApiEnvelope<FormResponseAttachment[]> | FormResponseAttachment[]>(`/forms/responses/${id}/attachments/`);
  return unwrapMaybe(res.data);
}

export async function uploadFormResponseAttachment(id: string, data: {
  question_key: string;
  file: File;
  repeat_group_key?: string;
  repeat_item_id?: string;
  gps_latitude?: string;
  gps_longitude?: string;
  metadata_json?: Record<string, unknown>;
}) {
  const formData = new FormData();
  formData.append("question_key", data.question_key);
  formData.append("file", data.file);
  formData.append("file_name", data.file.name);
  formData.append("file_size", String(data.file.size));
  formData.append("mime_type", data.file.type);
  formData.append("file_type", data.file.type.split("/")[0] || "file");
  if (data.repeat_group_key) formData.append("repeat_group_key", data.repeat_group_key);
  if (data.repeat_item_id) formData.append("repeat_item_id", data.repeat_item_id);
  if (data.gps_latitude) formData.append("gps_latitude", data.gps_latitude);
  if (data.gps_longitude) formData.append("gps_longitude", data.gps_longitude);
  if (data.metadata_json) formData.append("metadata_json", JSON.stringify(data.metadata_json));
  const res = await apiClient.post<ApiEnvelope<FormResponseAttachment> | FormResponseAttachment>(`/forms/responses/${id}/attachments/`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return unwrapMaybe(res.data);
}

export async function fetchOfflineAssignments() {
  const res = await apiClient.get<FormAssignment[]>("/forms/offline/assignments/");
  return res.data;
}

export async function fetchOfflineAssignmentPackage(assignmentId: string) {
  const res = await apiClient.get<OfflineFormPackage>(`/forms/offline/assignments/${assignmentId}/package/`);
  return res.data;
}

export async function syncOfflineFormResponse(data: {
  local_response_id: string;
  operation_type: "save_draft" | "submit_response";
  payload_json: Record<string, unknown>;
  media_payload_ref?: string;
}) {
  const res = await apiClient.post<OfflineSyncResult>("/forms/offline/sync/", data);
  return res.data;
}

export async function fetchOfflineSyncStatus(syncJobId: string) {
  const res = await apiClient.get<OfflineSyncResult["sync_job"]>(`/forms/offline/sync/${syncJobId}/status/`);
  return res.data;
}

export async function downloadFormResponsesExport(params: {
  format: "csv" | "json" | "pdf";
  assignment?: string;
  template?: string;
  status?: string;
  sync_status?: string;
  date_from?: string;
  date_to?: string;
}) {
  const res = await apiClient.get<Blob>("/forms/exports/responses/", {
    params,
    responseType: "blob",
  });
  return res.data;
}

export async function downloadFormAttachmentsExport(params: {
  assignment?: string;
  template?: string;
  status?: string;
  date_from?: string;
  date_to?: string;
}) {
  const res = await apiClient.get<Blob>("/forms/exports/attachments/", {
    params,
    responseType: "blob",
  });
  return res.data;
}

// ── Permissions ──

export type FormsPermissions = {
  permissions: string[];
  role: string;
};

export async function fetchFormsPermissions(): Promise<FormsPermissions> {
  const res = await apiClient.get<ApiEnvelope<FormsPermissions> | FormsPermissions>("/forms/permissions/");
  return unwrapMaybe(res.data);
}

// ── Analytics ──

export type FormsAnalytics = {
  summary: {
    total_templates: number;
    total_assignments: number;
    total_responses: number;
    submitted_responses: number;
    completion_rate: number;
    average_score: number | null;
  };
  status_breakdown: Array<{ status: string; count: number }>;
  purpose_breakdown: Array<{ purpose: string; count: number; response_count: number }>;
  submissions_over_time: Array<{ date: string; count: number }>;
  score_distribution: Array<{ range: string; count: number }>;
  risk_breakdown: Array<{ risk_rating: string; count: number }>;
  assignment_stats: Array<{
    assignment_id: string;
    assignment_title: string;
    template_title: string;
    purpose: string;
    context_type: string;
    recipient_count: number;
    response_count: number;
    submitted_count: number;
    response_rate: number;
    completion_rate: number;
  }>;
  structured_response_analytics: Array<{
    template_id: string;
    template_title: string;
    question_key: string;
    question_label: string;
    question_type: string;
    answered: number;
    top_values: Array<{ value: string; count: number }>;
    average: number | null;
  }>;
  inspection_analytics: {
    inspection_count: number;
    average_score: number | null;
    status_breakdown: Array<{ status: string; count: number }>;
    enforcement_breakdown: Array<{ enforcement_action: string; count: number }>;
  };
  organization_breakdown: Array<{ organization_id: string | null; organization_name: string; count: number }>;
  location_breakdown: Array<{ state_id: string | null; state_name: string; count: number }>;
  template_stats: Array<{
    template_title: string;
    template_id: string;
    total: number;
    submitted: number;
    completion_rate: number;
    average_score: number | null;
  }>;
  filters: Record<string, string | null>;
};

export async function fetchFormsAnalytics(params?: Record<string, string>): Promise<FormsAnalytics> {
  const res = await apiClient.get<ApiEnvelope<FormsAnalytics> | FormsAnalytics>("/forms/reports/analytics/", { params });
  return unwrapMaybe(res.data);
}

// ── Portal Assigned Forms ──

export type PortalAssignedForm = FormAssignment & {
  response: FormResponse | null;
  response_id: string | null;
  response_status: string;
  response_history?: FormResponse[];
  template_schema?: Record<string, unknown>;
  template_logic?: Record<string, unknown>;
  template_settings?: Record<string, unknown>;
};

export type PortalContext = "employer" | "facility" | "food-handler";

export async function fetchPortalAssignedForms(portal: PortalContext, params?: Record<string, string>): Promise<PortalAssignedForm[]> {
  const res = await apiClient.get<ApiEnvelope<PortalAssignedForm[]> | PortalAssignedForm[]>(`/${portal}/assigned-forms/`, { params });
  return unwrapMaybe(res.data);
}

export async function fetchPortalAssignedForm(portal: PortalContext, assignmentId: string): Promise<PortalAssignedForm> {
  const res = await apiClient.get<ApiEnvelope<PortalAssignedForm> | PortalAssignedForm>(`/${portal}/assigned-forms/${assignmentId}/`);
  return unwrapMaybe(res.data);
}

export async function createPortalFormResponse(portal: PortalContext, assignmentId: string, responseJson?: Record<string, unknown>): Promise<FormResponse> {
  const res = await apiClient.post<ApiEnvelope<FormResponse> | FormResponse>(`/${portal}/assigned-forms/${assignmentId}/response/`, {
    response_json: responseJson || {},
  });
  return unwrapMaybe(res.data);
}
