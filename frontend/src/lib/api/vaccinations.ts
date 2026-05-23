import { apiClient, unwrap, type ApiEnvelope } from "@/lib/api/client";
import type { VaccinationRecord } from "@/types/assessments";

export async function reviewDoctorVaccination(
  assessmentId: string,
  payload: Record<string, unknown>
): Promise<VaccinationRecord> {
  const response = await apiClient.patch<ApiEnvelope<VaccinationRecord>>(
    `/doctor/assessments/${assessmentId}/vaccination-review/`,
    payload
  );
  return unwrap(response.data);
}
