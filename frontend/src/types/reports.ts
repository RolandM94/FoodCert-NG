export type DashboardPayload = {
  employer?: { id: string; business_name: string } | null;
  facility?: { id: string; facility_name: string } | null;
  state?: { id: string; name: string } | null;
  branch?: { id: string; name: string } | null;
  filters?: Record<string, string>;
  generated_at?: string;
  cards: Record<string, string | number | null>;
  charts?: Record<string, unknown>;
  sections?: Record<string, Array<Record<string, string | number | null>>>;
};

export type ReportType =
  | "employer_compliance"
  | "employer_certificates"
  | "employer_vaccinations"
  | "facility_performance"
  | "state_monthly"
  | "national"
  | "vaccination_coverage"
  | "illness_trends"
  | "inspection_outcomes"
  | "medical_examination"
  | "temporarily_not_fit_report"
  | "return_to_work_report"
  | "assessment_completion"
  | "vaccination_review_report"
  | "restricted_lab_summary";

export type ReportFormat = "json" | "csv" | "pdf" | "excel";

export type ReportSchedule = {
  id: string;
  report_type: ReportType;
  frequency: string;
  filters: Record<string, unknown>;
  recipients: string[];
  status: "active" | "paused" | "cancelled";
  created_by?: string;
  created_by_name?: string;
  created_at: string;
  updated_at: string;
};

export type GeneratedReport = {
  id: string;
  report_type: ReportType;
  file_format: ReportFormat;
  filters: Record<string, unknown>;
  summary: DashboardPayload;
  file_url: string;
  status: "pending" | "generated" | "failed";
  generated_by?: string;
  generated_by_name?: string;
  schedule?: string;
  failure_reason: string;
  created_at: string;
  updated_at: string;
};
