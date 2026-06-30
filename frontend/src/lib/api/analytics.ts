import { apiClient, unwrap, type ApiEnvelope } from "@/lib/api/client";

export type AnalyticsDataset = {
  id: string;
  code: string;
  name: string;
  description: string;
  module_source: string;
  allowed_account_types: string[];
  allowed_roles: string[];
  available_fields: string[];
  field_labels: Record<string, string>;
  field_types: Record<string, string>;
  field_type_metadata: Record<string, { inferredType: string; type: string }>;
  sensitive_fields: string[];
  default_filters: Record<string, unknown>;
  joinable_datasets: string[];
  aggregation_rules: Record<string, unknown>;
  required_permissions: string[];
  privacy_level: string;
  is_active: boolean;
};

export type AnalyticsWorksheetMetric = {
  field: string;
  aggregation: string;
  label?: string;
};

export type AnalyticsWorksheetDimension = {
  field: string;
};

export type AnalyticsWorksheetFilter = {
  field: string;
  operator: string;
  value: string | number | boolean | string[];
};

export type AnalyticsWorksheetPayload = {
  name: string;
  description: string;
  dataset: string;
  scope_type?: string;
  metrics: AnalyticsWorksheetMetric[];
  dimensions: AnalyticsWorksheetDimension[];
  filters: AnalyticsWorksheetFilter[];
  aggregations: string[];
  derived_fields: Array<Record<string, unknown>>;
  query_rules: Record<string, unknown>;
  chart_recommendation: string;
  preview_output?: Record<string, unknown>;
  is_template?: boolean;
};

export type AnalyticsWorksheet = {
  id: string;
  name: string;
  description: string;
  dataset: string;
  dataset_code: string;
  scope_type: string;
  metrics: AnalyticsWorksheetMetric[];
  dimensions: AnalyticsWorksheetDimension[];
  filters: AnalyticsWorksheetFilter[];
  aggregations: string[];
  derived_fields: Array<Record<string, unknown>>;
  query_rules: Record<string, unknown>;
  chart_recommendation: string;
  preview_output: AnalyticsWorksheetPreview;
  is_template: boolean;
  created_at: string;
  updated_at: string;
};

export type AnalyticsWidget = {
  id: string;
  worksheet: string;
  worksheet_name: string;
  title: string;
  widget_type: string;
  visual_config: Record<string, unknown>;
  filter_behavior: Record<string, unknown>;
  refresh_behavior: Record<string, unknown>;
  export_options: Record<string, boolean>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type DashboardExportJob = {
  id: string;
  owner?: string | null;
  owner_name?: string;
  published_dashboard: string;
  published_dashboard_label?: string;
  block_id: string;
  export_format: string;
  status: string;
  payload: Record<string, unknown>;
  error_message: string;
  started_at?: string | null;
  completed_at?: string | null;
  created_at: string;
  updated_at: string;
};

export type DashboardAlertRule = {
  id: string;
  owner?: string | null;
  owner_name?: string;
  organization?: string | null;
  organization_name?: string;
  state?: string | null;
  state_name?: string;
  account_type: string;
  scope_type: string;
  widget: string;
  widget_title?: string;
  name: string;
  description: string;
  metric_key: string;
  metric_label: string;
  operator: string;
  threshold_value: string;
  notification_channels: string[];
  recipient_user_ids: string[];
  required_permissions: string[];
  privacy_metadata: Record<string, unknown>;
  last_evaluated_at?: string | null;
  last_triggered_at?: string | null;
  trigger_count: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type DashboardAlertEvent = {
  id: string;
  rule: string;
  rule_name?: string;
  widget: string;
  widget_title?: string;
  status: string;
  observed_value?: string | null;
  threshold_value?: string | null;
  notification_count: number;
  notified_channels: string[];
  message: string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type DashboardCanvas = {
  id: string;
  name: string;
  description: string;
  scope_type: string;
  layout_config: Record<string, unknown>;
  global_filters: Array<Record<string, unknown>>;
  is_draft: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type DashboardCanvasBlock = {
  id: string;
  canvas: string;
  canvas_name: string;
  widget?: string | null;
  widget_title?: string;
  block_type: string;
  title: string;
  content: Record<string, unknown>;
  position: Record<string, unknown>;
  visibility_rules: Record<string, unknown>;
  required_permissions: string[];
  privacy_metadata: Record<string, unknown>;
  sort_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type PublishedDashboardSnapshotBlock = {
  id: string;
  widget_id?: string | null;
  widget_title?: string;
  block_type: string;
  title: string;
  content: Record<string, unknown>;
  position: Record<string, unknown>;
  visibility_rules: Record<string, unknown>;
  required_permissions: string[];
  preview?: AnalyticsWidgetPreviewResponse["preview"] | null;
  widget_type?: string;
  export_options?: Record<string, boolean>;
};

export type PublishedDashboardSnapshot = {
  canvas: {
    id: string;
    name: string;
    description: string;
    layout_config: Record<string, unknown>;
    global_filters: Array<Record<string, unknown>>;
    scope_type: string;
  };
  blocks: PublishedDashboardSnapshotBlock[];
};

export type PublishedDashboard = {
  id: string;
  canvas: string;
  canvas_name: string;
  published_by?: string | null;
  published_by_name?: string;
  version_label: string;
  visibility_scope: string;
  share_settings: Record<string, unknown>;
  snapshot: PublishedDashboardSnapshot;
  published_at: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type PublishedDashboardExportResponse = {
  target?: "dashboard" | "widget";
  title?: string;
  filename?: string;
  payload?: Record<string, unknown>;
  background?: boolean;
  job_id?: string;
  status?: string;
};

export type DashboardTemplate = {
  id: string;
  name: string;
  description: string;
  account_type: string;
  scope_type: string;
  source_canvas?: string | null;
  source_canvas_name?: string;
  source_published_dashboard?: string | null;
  source_published_dashboard_label?: string;
  template_config: Record<string, unknown>;
  required_permissions: string[];
  privacy_metadata: Record<string, unknown>;
  is_system_template: boolean;
  is_active: boolean;
  created_by?: string | null;
  created_by_name?: string;
  created_at: string;
  updated_at: string;
};

export type AnalyticsWorksheetPreview = {
  dataset_code: string;
  chart_recommendation: string;
  total_rows: number;
  dimensions: string[];
  metrics: Array<{
    field?: string;
    aggregation: string;
    label: string;
    value: string | number | null;
  }>;
  rows: Array<Record<string, string | number | null>>;
};

export type AnalyticsWorksheetExample = {
  key: string;
  name: string;
  description: string;
  recommended_for?: string[];
  metrics: AnalyticsWorksheetMetric[];
  dimensions: AnalyticsWorksheetDimension[];
  filters: AnalyticsWorksheetFilter[];
  chart_recommendation: string;
};

export type AnalyticsDatasetSample = {
  dataset: string;
  name: string;
  row_count: number;
  sensitive_fields: string[];
  rows: Array<Record<string, string | number | null>>;
};

export type AnalyticsDatasetFieldTypeCompatibility = {
  field: string;
  targetType: string;
  totalRows: number;
  emptyRows: number;
  compatibleRows: number;
  incompatibleRows: number;
  invalidExamples: string[];
  requiresConfirmation: boolean;
};

export type AnalyticsDatasetFieldTypeChangeResponse = {
  dataset: AnalyticsDataset;
  compatibility: AnalyticsDatasetFieldTypeCompatibility;
};

export type AnalyticsDatasetExamplesResponse = {
  dataset: string;
  examples: AnalyticsWorksheetExample[];
};

export type AnalyticsDatasetAiPromptResponse = {
  dataset: string;
  name: string;
  ai_prompt_hints: {
    dataset_code: string;
    analysis_rules: string[];
    recommended_widget_types: string[];
    prompt_scaffold: string;
  };
};

export type AnalyticsWidgetPreviewResponse = {
  widget_type: string;
  title: string;
  export_formats: string[];
  preview: {
    title: string;
    widget_type: string;
    chart_recommendation: string;
    total_rows: number;
    dimensions: string[];
    cards?: Array<{ field?: string; aggregation: string; label: string; value: string | number | null }>;
    series?: Array<Record<string, string | number | null>>;
    x_axis?: string;
    metrics?: Array<{ field?: string; aggregation: string; label: string; value: string | number | null }>;
    columns?: string[];
    rows?: Array<Record<string, string | number | null>>;
    items?: Array<Record<string, string | number | null>>;
    count_label?: string;
    insights?: string[];
    visual_config?: Record<string, unknown>;
    pagination?: {
      page_size: number;
      total_items: number;
      total_pages: number;
    };
  };
};

export type AIWorksheetSuggestion = {
  name: string;
  description: string;
  dataset: string;
  metrics: AnalyticsWorksheetMetric[];
  dimensions: AnalyticsWorksheetDimension[];
  filters: AnalyticsWorksheetFilter[];
  aggregations: string[];
  derived_fields: Array<Record<string, unknown>>;
  query_rules: Record<string, unknown>;
  chart_recommendation: string;
  reasoning: string[];
};

export type AIWidgetSuggestion = {
  worksheet: string;
  title: string;
  widget_type: string;
  scope_type: string;
  visual_config: Record<string, unknown>;
  filter_behavior: Record<string, unknown>;
  refresh_behavior: Record<string, unknown>;
  export_options: Record<string, boolean>;
  reasoning: string[];
};

export type AIDashboardSuggestion = {
  name: string;
  description: string;
  layout_config: Record<string, unknown>;
  global_filters: Array<Record<string, unknown>>;
  blocks: Array<{
    block_type: string;
    title: string;
    content: Record<string, unknown>;
    position: Record<string, unknown>;
    widget?: string | null;
    visibility_rules: Record<string, unknown>;
    sort_order: number;
  }>;
  reasoning: string[];
};

export type AIDashboardFullSuggestion = AIDashboardSuggestion & {
  worksheet_suggestion: AIWorksheetSuggestion;
  widget_suggestion: AIWidgetSuggestion;
  resolved_dataset: {
    id: string;
    code: string;
    name: string;
    match_reason: string;
  };
};

export type AIExplanation = {
  summary: string;
  insights: string[];
  recommended_actions: string[];
};

export async function listAnalyticsDatasets(): Promise<AnalyticsDataset[]> {
  const response = await apiClient.get<ApiEnvelope<AnalyticsDataset[]>>("/analytics/datasets/");
  return unwrap(response.data);
}

export async function getAnalyticsDatasetSample(datasetId: string): Promise<AnalyticsDatasetSample> {
  const response = await apiClient.get<ApiEnvelope<AnalyticsDatasetSample>>(`/analytics/datasets/${datasetId}/sample/`);
  return unwrap(response.data);
}

export async function getAnalyticsDatasetExamples(datasetId: string): Promise<AnalyticsDatasetExamplesResponse> {
  const response = await apiClient.get<ApiEnvelope<AnalyticsDatasetExamplesResponse>>(`/analytics/datasets/${datasetId}/worksheet-examples/`);
  return unwrap(response.data);
}

export async function getAnalyticsDatasetAiPrompt(datasetId: string): Promise<AnalyticsDatasetAiPromptResponse> {
  const response = await apiClient.get<ApiEnvelope<AnalyticsDatasetAiPromptResponse>>(`/analytics/datasets/${datasetId}/ai-prompt/`);
  return unwrap(response.data);
}

export async function checkAnalyticsDatasetFieldTypeCompatibility(datasetId: string, payload: {
  field: string;
  target_type: string;
}): Promise<AnalyticsDatasetFieldTypeCompatibility> {
  const response = await apiClient.post<ApiEnvelope<AnalyticsDatasetFieldTypeCompatibility>>(
    `/analytics/datasets/${datasetId}/field-type-compatibility/`,
    payload,
  );
  return unwrap(response.data);
}

export async function changeAnalyticsDatasetFieldType(datasetId: string, payload: {
  field: string;
  target_type: string;
  force?: boolean;
}): Promise<AnalyticsDatasetFieldTypeChangeResponse> {
  const response = await apiClient.post<ApiEnvelope<AnalyticsDatasetFieldTypeChangeResponse>>(
    `/analytics/datasets/${datasetId}/change-field-type/`,
    payload,
  );
  return unwrap(response.data);
}

export async function generateAnalyticsWorksheet(payload: {
  dataset?: string;
  prompt: string;
}): Promise<AIWorksheetSuggestion> {
  const response = await apiClient.post<ApiEnvelope<AIWorksheetSuggestion>>("/analytics/datasets/generate-worksheet/", payload);
  return unwrap(response.data);
}

export async function previewAnalyticsWorksheet(payload: AnalyticsWorksheetPayload): Promise<AnalyticsWorksheetPreview> {
  const response = await apiClient.post<ApiEnvelope<AnalyticsWorksheetPreview>>("/analytics/worksheets/preview/", payload);
  return unwrap(response.data);
}

export async function createAnalyticsWorksheet(payload: AnalyticsWorksheetPayload): Promise<AnalyticsWorksheet> {
  const response = await apiClient.post<ApiEnvelope<AnalyticsWorksheet>>("/analytics/worksheets/", payload);
  return unwrap(response.data);
}

export async function listAnalyticsWorksheets(): Promise<AnalyticsWorksheet[]> {
  const response = await apiClient.get<ApiEnvelope<AnalyticsWorksheet[]>>("/analytics/worksheets/");
  return unwrap(response.data);
}

export async function generateAnalyticsWidget(payload: {
  worksheet: string;
  prompt: string;
}): Promise<AIWidgetSuggestion> {
  const response = await apiClient.post<ApiEnvelope<AIWidgetSuggestion>>("/analytics/worksheets/generate-widget/", payload);
  return unwrap(response.data);
}

export async function listAnalyticsWidgets(): Promise<AnalyticsWidget[]> {
  const response = await apiClient.get<ApiEnvelope<AnalyticsWidget[]>>("/analytics/widgets/");
  return unwrap(response.data);
}

export async function previewAnalyticsWidget(payload: {
  worksheet: string;
  title: string;
  widget_type: string;
  scope_type?: string;
  visual_config: Record<string, unknown>;
  filter_behavior: Record<string, unknown>;
  refresh_behavior: Record<string, unknown>;
  export_options: Record<string, boolean>;
}): Promise<AnalyticsWidgetPreviewResponse> {
  const response = await apiClient.post<ApiEnvelope<AnalyticsWidgetPreviewResponse>>("/analytics/widgets/preview/", payload);
  return unwrap(response.data);
}

export async function createAnalyticsWidget(payload: {
  worksheet: string;
  title: string;
  widget_type: string;
  scope_type?: string;
  visual_config: Record<string, unknown>;
  filter_behavior: Record<string, unknown>;
  refresh_behavior: Record<string, unknown>;
  export_options: Record<string, boolean>;
}): Promise<AnalyticsWidget> {
  const response = await apiClient.post<ApiEnvelope<AnalyticsWidget>>("/analytics/widgets/", payload);
  return unwrap(response.data);
}

export async function refreshAnalyticsWidget(widgetId: string): Promise<AnalyticsWidgetPreviewResponse> {
  const response = await apiClient.post<ApiEnvelope<AnalyticsWidgetPreviewResponse>>(`/analytics/widgets/${widgetId}/refresh/`, {});
  return unwrap(response.data);
}

export async function listDashboardAlertRules(widgetId?: string): Promise<DashboardAlertRule[]> {
  const response = await apiClient.get<ApiEnvelope<DashboardAlertRule[]>>("/analytics/dashboard-alerts/", {
    params: widgetId ? { widget: widgetId } : undefined,
  });
  return unwrap(response.data);
}

export async function createDashboardAlertRule(payload: {
  widget: string;
  name: string;
  description?: string;
  metric_key: string;
  metric_label?: string;
  operator: string;
  threshold_value: string;
  notification_channels: string[];
  recipient_user_ids?: string[];
  is_active?: boolean;
}): Promise<DashboardAlertRule> {
  const response = await apiClient.post<ApiEnvelope<DashboardAlertRule>>("/analytics/dashboard-alerts/", payload);
  return unwrap(response.data);
}

export async function evaluateDashboardAlertRule(ruleId: string): Promise<DashboardAlertEvent> {
  const response = await apiClient.post<ApiEnvelope<DashboardAlertEvent>>(`/analytics/dashboard-alerts/${ruleId}/evaluate/`, {});
  return unwrap(response.data);
}

export async function evaluateAllDashboardAlertRules(): Promise<{
  evaluated: number;
  triggered: number;
  events: DashboardAlertEvent[];
}> {
  const response = await apiClient.post<ApiEnvelope<{ evaluated: number; triggered: number; events: DashboardAlertEvent[] }>>(
    "/analytics/dashboard-alerts/evaluate-all/",
    {},
  );
  return unwrap(response.data);
}

export async function listDashboardAlertEvents(params?: {
  rule?: string;
  widget?: string;
}): Promise<DashboardAlertEvent[]> {
  const response = await apiClient.get<ApiEnvelope<DashboardAlertEvent[]>>("/analytics/dashboard-alert-events/", {
    params,
  });
  return unwrap(response.data);
}

export async function explainAnalyticsWidget(payload: {
  widget: string;
  prompt?: string;
  insightContext?: {
    dimensions: Array<{ fieldName: string; label: string; fieldType: string }>;
    measures: Array<{ fieldName: string; label: string; fieldType: string; defaultAggregation?: string }>;
    chartType: string;
    filters: Array<Record<string, unknown>>;
    role: string;
    aggregatedData: Array<Record<string, unknown>>;
    timePeriod?: string;
    comparisonPeriod?: string;
  };
}): Promise<AIExplanation> {
  const response = await apiClient.post<ApiEnvelope<AIExplanation>>("/analytics/widgets/explain/", payload);
  return unwrap(response.data);
}

export async function listDashboardCanvases(): Promise<DashboardCanvas[]> {
  const response = await apiClient.get<ApiEnvelope<DashboardCanvas[]>>("/analytics/dashboard-canvases/");
  return unwrap(response.data);
}

export async function createDashboardCanvas(payload: {
  name: string;
  description: string;
  scope_type?: string;
  layout_config: Record<string, unknown>;
  global_filters: Array<Record<string, unknown>>;
}): Promise<DashboardCanvas> {
  const response = await apiClient.post<ApiEnvelope<DashboardCanvas>>("/analytics/dashboard-canvases/", payload);
  return unwrap(response.data);
}

export async function updateDashboardCanvas(id: string, payload: Partial<{
  name: string;
  description: string;
  scope_type: string;
  layout_config: Record<string, unknown>;
  global_filters: Array<Record<string, unknown>>;
  is_draft: boolean;
}>): Promise<DashboardCanvas> {
  const response = await apiClient.patch<ApiEnvelope<DashboardCanvas>>(`/analytics/dashboard-canvases/${id}/`, payload);
  return unwrap(response.data);
}

export async function generateDashboardCanvas(payload: {
  prompt: string;
  widget_ids?: string[];
}): Promise<AIDashboardSuggestion> {
  const response = await apiClient.post<ApiEnvelope<AIDashboardSuggestion>>("/analytics/dashboard-canvases/generate-dashboard/", payload);
  return unwrap(response.data);
}

export async function generateFullDashboard(payload: {
  prompt: string;
}): Promise<AIDashboardFullSuggestion> {
  const response = await apiClient.post<ApiEnvelope<AIDashboardFullSuggestion>>("/analytics/dashboard-canvases/generate-full/", payload);
  return unwrap(response.data);
}

export async function explainDashboardCanvas(id: string, payload: {
  prompt?: string;
  insightContext?: {
    dimensions: Array<{ fieldName: string; label: string; fieldType: string }>;
    measures: Array<{ fieldName: string; label: string; fieldType: string; defaultAggregation?: string }>;
    chartType: string;
    filters: Array<Record<string, unknown>>;
    role: string;
    aggregatedData: Array<Record<string, unknown>>;
    timePeriod?: string;
    comparisonPeriod?: string;
  };
}): Promise<AIExplanation> {
  const response = await apiClient.post<ApiEnvelope<AIExplanation>>(`/analytics/dashboard-canvases/${id}/explain/`, payload);
  return unwrap(response.data);
}

export async function listDashboardBlocks(canvasId?: string): Promise<DashboardCanvasBlock[]> {
  const response = await apiClient.get<ApiEnvelope<DashboardCanvasBlock[]>>("/analytics/dashboard-blocks/", {
    params: canvasId ? { canvas: canvasId } : undefined,
  });
  return unwrap(response.data);
}

export async function createDashboardBlock(payload: {
  canvas: string;
  widget?: string | null;
  block_type: string;
  title: string;
  content: Record<string, unknown>;
  position: Record<string, unknown>;
  visibility_rules: Record<string, unknown>;
  sort_order: number;
}): Promise<DashboardCanvasBlock> {
  const response = await apiClient.post<ApiEnvelope<DashboardCanvasBlock>>("/analytics/dashboard-blocks/", payload);
  return unwrap(response.data);
}

export async function updateDashboardBlock(id: string, payload: Partial<{
  widget: string | null;
  block_type: string;
  title: string;
  content: Record<string, unknown>;
  position: Record<string, unknown>;
  visibility_rules: Record<string, unknown>;
  sort_order: number;
  is_active: boolean;
}>): Promise<DashboardCanvasBlock> {
  const response = await apiClient.patch<ApiEnvelope<DashboardCanvasBlock>>(`/analytics/dashboard-blocks/${id}/`, payload);
  return unwrap(response.data);
}

export async function deleteDashboardBlock(id: string): Promise<void> {
  await apiClient.delete(`/analytics/dashboard-blocks/${id}/`);
}

export async function publishDashboardCanvas(
  canvasId: string,
  payload: {
    version_label?: string;
    visibility_scope: string;
    share_settings?: Record<string, unknown>;
  },
): Promise<PublishedDashboard> {
  const response = await apiClient.post<ApiEnvelope<PublishedDashboard>>(`/analytics/dashboard-canvases/${canvasId}/publish/`, payload);
  return unwrap(response.data);
}

export async function listPublishedDashboards(canvasId?: string): Promise<PublishedDashboard[]> {
  const response = await apiClient.get<ApiEnvelope<PublishedDashboard[]>>("/analytics/published-dashboards/", {
    params: canvasId ? { canvas: canvasId } : undefined,
  });
  return unwrap(response.data);
}

export async function getPublishedDashboard(id: string): Promise<PublishedDashboard> {
  const response = await apiClient.get<ApiEnvelope<PublishedDashboard>>(`/analytics/published-dashboards/${id}/`);
  return unwrap(response.data);
}

export async function exportPublishedDashboard(payload: {
  dashboardId: string;
  format: "pdf" | "png" | "csv" | "xlsx" | "json";
  block_id?: string;
}): Promise<PublishedDashboardExportResponse> {
  const response = await apiClient.post<ApiEnvelope<PublishedDashboardExportResponse>>(
    `/analytics/published-dashboards/${payload.dashboardId}/export/`,
    {
      format: payload.format,
      block_id: payload.block_id,
    },
  );
  return unwrap(response.data);
}

export async function getDashboardExportJob(jobId: string): Promise<DashboardExportJob> {
  const response = await apiClient.get<ApiEnvelope<DashboardExportJob>>(`/analytics/dashboard-export-jobs/${jobId}/`);
  return unwrap(response.data);
}

export async function recordPublishedDashboardShareEvent(payload: {
  dashboardId: string;
  event: "link_copied" | "share_viewed";
}): Promise<void> {
  await apiClient.post(`/analytics/published-dashboards/${payload.dashboardId}/share-event/`, {
    event: payload.event,
  });
}

export async function updatePublishedDashboardSharing(payload: {
  dashboardId: string;
  visibility_scope?: string;
  share_settings?: Record<string, unknown>;
}): Promise<PublishedDashboard> {
  const response = await apiClient.patch<ApiEnvelope<PublishedDashboard>>(
    `/analytics/published-dashboards/${payload.dashboardId}/sharing/`,
    {
      visibility_scope: payload.visibility_scope,
      share_settings: payload.share_settings,
    },
  );
  return unwrap(response.data);
}

export async function listDashboardTemplates(): Promise<DashboardTemplate[]> {
  const response = await apiClient.get<ApiEnvelope<DashboardTemplate[]>>("/analytics/dashboard-templates/");
  return unwrap(response.data);
}

export async function useDashboardTemplate(templateId: string): Promise<DashboardCanvas> {
  const response = await apiClient.post<ApiEnvelope<DashboardCanvas>>(`/analytics/dashboard-templates/${templateId}/use-template/`, {});
  return unwrap(response.data);
}
