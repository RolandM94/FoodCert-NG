import { apiClient, unwrap, type ApiEnvelope } from "./client";

export type FormTemplate = {
  id: string;
  title: string;
  description: string;
  purpose: string;
  owner_organization: string;
  owner_name?: string;
  target_respondent_type: string;
  module_context: string;
  status: "draft" | "published" | "archived" | "deprecated";
  current_version: number;
  created_by?: string;
  created_by_name?: string;
  response_count: number;
  created_at: string;
  updated_at: string;
};

export type FormTemplateVersion = {
  id: string;
  template: string;
  version_number: number;
  schema_json: Record<string, unknown>;
  scoring_json?: Record<string, unknown>;
  conditional_logic_json?: Record<string, unknown>;
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
  allow_multiple_submissions: boolean;
  allow_late_submission: boolean;
  requires_review: boolean;
  reviewer_role: string;
  status: string;
  response_count: number;
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
  submitted_at?: string;
  reviewed_by?: string;
  reviewed_by_name?: string;
  reviewed_at?: string;
  review_notes: string;
  returned_reason: string;
  created_at: string;
  updated_at: string;
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
  owner_organization: string; target_respondent_type?: string; module_context?: string;
}) {
  const res = await apiClient.post<ApiEnvelope<FormTemplate>>("/forms/templates/", data);
  return unwrap(res.data);
}

export async function updateFormTemplate(id: string, data: Partial<{ title: string; description: string }>) {
  const res = await apiClient.patch<ApiEnvelope<FormTemplate>>(`/forms/templates/${id}/`, data);
  return unwrap(res.data);
}

export async function publishFormTemplate(id: string) {
  const res = await apiClient.post<ApiEnvelope<FormTemplate>>(`/forms/templates/${id}/publish/`);
  return unwrap(res.data);
}

export async function archiveFormTemplate(id: string) {
  const res = await apiClient.post<ApiEnvelope<FormTemplate>>(`/forms/templates/${id}/archive/`);
  return unwrap(res.data);
}

export async function fetchFormTemplateVersions(id: string) {
  const res = await apiClient.get<ApiEnvelope<FormTemplateVersion[]>>(`/forms/templates/${id}/versions/`);
  return unwrap(res.data);
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

// ── Responses ──
export async function fetchFormResponses(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<FormResponse[]>>("/forms/responses/", { params });
  return unwrap(res.data);
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

export async function reviewFormResponse(id: string, review_notes?: string) {
  const res = await apiClient.post<ApiEnvelope<FormResponse>>(`/forms/responses/${id}/review/`, { review_notes: review_notes || "" });
  return unwrap(res.data);
}

export async function returnFormResponse(id: string, reason?: string) {
  const res = await apiClient.post<ApiEnvelope<FormResponse>>(`/forms/responses/${id}/return_response/`, { reason: reason || "" });
  return unwrap(res.data);
}
