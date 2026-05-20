import { apiClient, unwrap, type ApiEnvelope } from "@/lib/api/client";
import type { DashboardPayload, GeneratedReport, ReportFormat, ReportSchedule } from "@/types/reports";

export async function getEmployerDashboard(params?: Record<string, string>): Promise<DashboardPayload> {
  const response = await apiClient.get<ApiEnvelope<DashboardPayload>>("/dashboard/employer/", { params });
  return unwrap(response.data);
}

export async function getFacilityDashboard(params?: Record<string, string>): Promise<DashboardPayload> {
  const response = await apiClient.get<ApiEnvelope<DashboardPayload>>("/dashboard/facility/", { params });
  return unwrap(response.data);
}

export async function getStateDashboard(params?: Record<string, string>): Promise<DashboardPayload> {
  const response = await apiClient.get<ApiEnvelope<DashboardPayload>>("/dashboard/state/", { params });
  return unwrap(response.data);
}

export async function getFederalDashboard(): Promise<DashboardPayload> {
  const response = await apiClient.get<ApiEnvelope<DashboardPayload>>("/dashboard/federal/");
  return unwrap(response.data);
}

export async function generateReport(
  reportPath: string,
  file_format: ReportFormat = "json"
): Promise<GeneratedReport> {
  const response = await apiClient.get<ApiEnvelope<GeneratedReport>>(reportPath, { params: { file_format } });
  return unwrap(response.data);
}

export type EmployerReportFilters = {
  branch?: string;
  state?: string;
  lga?: string;
  category?: string;
  certificate_status?: string;
  fitness_status?: string;
  vaccine_type?: string;
  date_from?: string;
  date_to?: string;
};

export async function generateEmployerReport(
  employerId: string,
  report: "compliance" | "certificates" | "vaccinations",
  file_format: ReportFormat = "json",
  filters: EmployerReportFilters = {}
): Promise<GeneratedReport> {
  const response = await apiClient.get<ApiEnvelope<GeneratedReport>>(`/employers/${employerId}/reports/${report}/`, {
    params: { ...filters, format: file_format }
  });
  return unwrap(response.data);
}

export async function createReportSchedule(payload: Record<string, unknown>): Promise<ReportSchedule> {
  const response = await apiClient.post<ApiEnvelope<ReportSchedule>>("/reports/schedule/", payload);
  return unwrap(response.data);
}

export async function listReportSchedules(): Promise<ReportSchedule[]> {
  const response = await apiClient.get<ApiEnvelope<ReportSchedule[]>>("/reports/schedule/");
  return unwrap(response.data);
}

export async function listGeneratedReports(): Promise<GeneratedReport[]> {
  const response = await apiClient.get<ApiEnvelope<GeneratedReport[]>>("/reports/generated/");
  return unwrap(response.data);
}
