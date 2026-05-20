import { apiClient, unwrap, type ApiEnvelope } from "@/lib/api/client";
import type {
  Appointment,
  FitnessDecision,
  HealthDeclaration,
  LabTest,
  MedicalAssessment,
  PhysicalExamination,
  VaccinationRecord
} from "@/types/assessments";

export async function createAppointment(payload: Record<string, unknown>): Promise<Appointment> {
  const response = await apiClient.post<ApiEnvelope<Appointment>>("/appointments/", payload);
  return unwrap(response.data);
}

export async function listAppointments(): Promise<Appointment[]> {
  const response = await apiClient.get<ApiEnvelope<Appointment[]>>("/appointments/");
  return unwrap(response.data);
}

export async function updateAppointment(id: string, payload: Record<string, unknown>): Promise<Appointment> {
  const response = await apiClient.patch<ApiEnvelope<Appointment>>(`/appointments/${id}/`, payload);
  return unwrap(response.data);
}

export async function createAssessment(payload: Record<string, unknown>): Promise<MedicalAssessment> {
  const response = await apiClient.post<ApiEnvelope<MedicalAssessment>>("/assessments/", payload);
  return unwrap(response.data);
}

export async function listAssessments(): Promise<MedicalAssessment[]> {
  const response = await apiClient.get<ApiEnvelope<MedicalAssessment[]>>("/assessments/");
  return unwrap(response.data);
}

export async function getAssessment(id: string): Promise<MedicalAssessment> {
  const response = await apiClient.get<ApiEnvelope<MedicalAssessment>>(`/assessments/${id}/`);
  return unwrap(response.data);
}

export async function submitDeclaration(id: string, payload: Record<string, unknown>): Promise<HealthDeclaration> {
  const response = await apiClient.post<ApiEnvelope<HealthDeclaration>>(`/assessments/${id}/declaration/`, payload);
  return unwrap(response.data);
}

export async function validateDeclaration(id: string): Promise<HealthDeclaration> {
  const response = await apiClient.patch<ApiEnvelope<HealthDeclaration>>(`/declarations/${id}/validate/`);
  return unwrap(response.data);
}

export async function submitPhysicalExamination(id: string, payload: Record<string, unknown>): Promise<PhysicalExamination> {
  const response = await apiClient.post<ApiEnvelope<PhysicalExamination>>(`/assessments/${id}/physical-examination/`, payload);
  return unwrap(response.data);
}

export async function requestLabTests(id: string, tests: Array<Record<string, unknown>>): Promise<LabTest[]> {
  const response = await apiClient.post<ApiEnvelope<LabTest[]>>(`/assessments/${id}/lab-tests/`, { tests });
  return unwrap(response.data);
}

export async function recordLabResult(id: string, payload: Record<string, unknown>): Promise<LabTest> {
  const response = await apiClient.patch<ApiEnvelope<LabTest>>(`/lab-tests/${id}/result/`, payload);
  return unwrap(response.data);
}

export async function reviewLabTest(id: string): Promise<LabTest> {
  const response = await apiClient.patch<ApiEnvelope<LabTest>>(`/lab-tests/${id}/review/`);
  return unwrap(response.data);
}

export async function recordVaccination(id: string, payload: Record<string, unknown>): Promise<VaccinationRecord> {
  const response = await apiClient.post<ApiEnvelope<VaccinationRecord>>(`/assessments/${id}/vaccinations/`, payload);
  return unwrap(response.data);
}

export async function listFoodHandlerVaccinations(foodHandlerId: string): Promise<VaccinationRecord[]> {
  const response = await apiClient.get<ApiEnvelope<VaccinationRecord[]>>(`/food-handlers/${foodHandlerId}/vaccinations/`);
  return unwrap(response.data);
}

export async function setFitnessDecision(
  id: string,
  payload: { final_decision: FitnessDecision; return_to_work_date?: string; doctor_notes?: string }
): Promise<MedicalAssessment> {
  const response = await apiClient.patch<ApiEnvelope<MedicalAssessment>>(`/assessments/${id}/fitness-decision/`, payload);
  return unwrap(response.data);
}
