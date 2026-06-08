import { apiClient, unwrap, type ApiEnvelope } from "@/lib/api/client";
import type {
  Appointment,
  AssessmentAuditTimelineItem,
  AssessmentFormQuestion,
  AssessmentFormResponse,
  AssessmentFormSection,
  AssessmentFormTemplate,
  AssessmentRequirementResolution,
  AssessmentStatusSnapshot,
  FitnessDecision,
  HealthDeclaration,
  LabTest,
  MedicalAssessment,
  PhysicalExamination,
  VaccinationRecord
} from "@/types/assessments";

function normalizeList<T>(value: T[] | { results?: T[] }): T[] {
  return Array.isArray(value) ? value : value.results ?? [];
}

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

export async function listFacilityAppointments(facilityId: string): Promise<Appointment[]> {
  const response = await apiClient.get<ApiEnvelope<Appointment[]>>(`/facilities/${facilityId}/appointments/`);
  return unwrap(response.data);
}

export async function confirmFacilityAppointment(facilityId: string, appointmentId: string, payload: Record<string, unknown> = {}): Promise<Appointment> {
  const response = await apiClient.patch<ApiEnvelope<Appointment>>(`/facilities/${facilityId}/appointments/${appointmentId}/confirm/`, payload);
  return unwrap(response.data);
}

export async function rescheduleFacilityAppointment(facilityId: string, appointmentId: string, payload: Record<string, unknown>): Promise<Appointment> {
  const response = await apiClient.patch<ApiEnvelope<Appointment>>(`/facilities/${facilityId}/appointments/${appointmentId}/reschedule/`, payload);
  return unwrap(response.data);
}

export async function cancelFacilityAppointment(facilityId: string, appointmentId: string, payload: Record<string, unknown> = {}): Promise<Appointment> {
  const response = await apiClient.patch<ApiEnvelope<Appointment>>(`/facilities/${facilityId}/appointments/${appointmentId}/cancel/`, payload);
  return unwrap(response.data);
}

export async function noShowFacilityAppointment(facilityId: string, appointmentId: string, payload: Record<string, unknown> = {}): Promise<Appointment> {
  const response = await apiClient.patch<ApiEnvelope<Appointment>>(`/facilities/${facilityId}/appointments/${appointmentId}/no-show/`, payload);
  return unwrap(response.data);
}

export async function assignFacilityAppointmentDoctor(facilityId: string, appointmentId: string, doctorId: string): Promise<Appointment> {
  const response = await apiClient.patch<ApiEnvelope<Appointment>>(`/facilities/${facilityId}/appointments/${appointmentId}/assign-doctor/`, { doctor: doctorId });
  return unwrap(response.data);
}

export async function createAssessment(payload: Record<string, unknown>): Promise<MedicalAssessment> {
  const response = await apiClient.post<ApiEnvelope<MedicalAssessment>>("/assessments/", payload);
  return unwrap(response.data);
}

export async function listAssessments(): Promise<MedicalAssessment[]> {
  const response = await apiClient.get<ApiEnvelope<MedicalAssessment[]>>("/assessments/");
  return normalizeList(unwrap(response.data));
}

export async function listFacilityAssessments(facilityId: string, params?: Record<string, string>): Promise<MedicalAssessment[]> {
  const response = await apiClient.get<ApiEnvelope<MedicalAssessment[]>>(`/facilities/${facilityId}/assessments/`, { params });
  return unwrap(response.data);
}

export async function getAssessment(id: string): Promise<MedicalAssessment> {
  const response = await apiClient.get<ApiEnvelope<MedicalAssessment>>(`/assessments/${id}/`);
  return unwrap(response.data);
}

export async function getAssessmentStatus(id: string): Promise<AssessmentStatusSnapshot> {
  const response = await apiClient.get<ApiEnvelope<AssessmentStatusSnapshot>>(`/assessments/${id}/status/`);
  return unwrap(response.data);
}

export async function getAssessmentAuditTimeline(id: string): Promise<AssessmentAuditTimelineItem[]> {
  const response = await apiClient.get<ApiEnvelope<AssessmentAuditTimelineItem[]>>(`/assessments/${id}/audit-timeline/`);
  return unwrap(response.data);
}

export async function cancelAssessment(id: string, payload: Record<string, unknown> = {}): Promise<MedicalAssessment> {
  const response = await apiClient.post<ApiEnvelope<MedicalAssessment>>(`/assessments/${id}/cancel/`, payload);
  return unwrap(response.data);
}

export async function closeAssessment(id: string, payload: Record<string, unknown> = {}): Promise<MedicalAssessment> {
  const response = await apiClient.post<ApiEnvelope<MedicalAssessment>>(`/assessments/${id}/close/`, payload);
  return unwrap(response.data);
}

export async function getFacilityAssessment(facilityId: string, assessmentId: string): Promise<MedicalAssessment> {
  const response = await apiClient.get<ApiEnvelope<MedicalAssessment>>(`/facilities/${facilityId}/assessments/${assessmentId}/`);
  return unwrap(response.data);
}

export async function assignFacilityAssessmentDoctor(facilityId: string, assessmentId: string, doctorId: string): Promise<MedicalAssessment> {
  const response = await apiClient.patch<ApiEnvelope<MedicalAssessment>>(`/facilities/${facilityId}/assessments/${assessmentId}/assign-doctor/`, { doctor: doctorId });
  return unwrap(response.data);
}

export async function listDoctorAssessments(): Promise<MedicalAssessment[]> {
  const response = await apiClient.get<ApiEnvelope<MedicalAssessment[]>>("/doctor/assessments/");
  return normalizeList(unwrap(response.data));
}

export async function getDoctorAssessment(assessmentId: string): Promise<MedicalAssessment> {
  const response = await apiClient.get<ApiEnvelope<MedicalAssessment>>(`/doctor/assessments/${assessmentId}/`);
  return unwrap(response.data);
}

export async function validateDoctorDeclaration(assessmentId: string): Promise<HealthDeclaration> {
  const response = await apiClient.patch<ApiEnvelope<HealthDeclaration>>(`/doctor/assessments/${assessmentId}/declaration/validate/`);
  return unwrap(response.data);
}

export async function requestDoctorDeclarationChanges(assessmentId: string, reason: string): Promise<HealthDeclaration> {
  const response = await apiClient.patch<ApiEnvelope<HealthDeclaration>>(
    `/doctor/assessments/${assessmentId}/declaration/request-changes/`,
    { reason }
  );
  return unwrap(response.data);
}

export async function submitDoctorPhysicalExam(assessmentId: string, payload: Record<string, unknown>): Promise<PhysicalExamination> {
  const response = await apiClient.post<ApiEnvelope<PhysicalExamination>>(`/doctor/assessments/${assessmentId}/physical-exam/`, payload);
  return unwrap(response.data);
}

export async function saveDoctorPhysicalExamDraft(assessmentId: string, payload: Record<string, unknown>): Promise<PhysicalExamination> {
  const response = await apiClient.patch<ApiEnvelope<PhysicalExamination>>(`/doctor/assessments/${assessmentId}/physical-exam/draft/`, payload);
  return unwrap(response.data);
}

export async function submitDeclaration(id: string, payload: Record<string, unknown>): Promise<HealthDeclaration> {
  const response = await apiClient.post<ApiEnvelope<HealthDeclaration>>(`/assessments/${id}/declaration/`, payload);
  return unwrap(response.data);
}

export async function getAssessmentDeclaration(id: string): Promise<HealthDeclaration> {
  const response = await apiClient.get<ApiEnvelope<HealthDeclaration>>(`/assessments/${id}/declaration/`);
  return unwrap(response.data);
}

export async function saveDeclarationDraft(id: string, payload: Record<string, unknown>): Promise<HealthDeclaration> {
  const response = await apiClient.patch<ApiEnvelope<HealthDeclaration>>(`/assessments/${id}/declaration/`, payload);
  return unwrap(response.data);
}

export async function submitDeclarationVersion(id: string, payload: Record<string, unknown>): Promise<HealthDeclaration> {
  const response = await apiClient.post<ApiEnvelope<HealthDeclaration>>(`/assessments/${id}/declaration/submit/`, payload);
  return unwrap(response.data);
}

export async function validateAssessmentDeclaration(id: string): Promise<HealthDeclaration> {
  const response = await apiClient.post<ApiEnvelope<HealthDeclaration>>(`/assessments/${id}/declaration/validate/`);
  return unwrap(response.data);
}

export async function reopenAssessmentDeclaration(id: string, reason: string): Promise<HealthDeclaration> {
  const response = await apiClient.post<ApiEnvelope<HealthDeclaration>>(`/assessments/${id}/declaration/reopen/`, { reason });
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

export async function getPhysicalExamination(id: string): Promise<PhysicalExamination> {
  const response = await apiClient.get<ApiEnvelope<PhysicalExamination>>(`/assessments/${id}/physical-exam/`);
  return unwrap(response.data);
}

export async function savePhysicalExaminationDraft(id: string, payload: Record<string, unknown>): Promise<PhysicalExamination> {
  const response = await apiClient.patch<ApiEnvelope<PhysicalExamination>>(`/assessments/${id}/physical-exam/`, payload);
  return unwrap(response.data);
}

export async function completePhysicalExamination(id: string, payload: Record<string, unknown>): Promise<PhysicalExamination> {
  const response = await apiClient.post<ApiEnvelope<PhysicalExamination>>(`/assessments/${id}/physical-exam/complete/`, payload);
  return unwrap(response.data);
}

export async function requestLabTests(id: string, tests: Array<Record<string, unknown>>, includeRequired = true): Promise<LabTest[]> {
  const response = await apiClient.post<ApiEnvelope<LabTest[]>>(`/assessments/${id}/lab-tests/`, { tests, include_required: includeRequired });
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
  payload: { final_decision: FitnessDecision; return_to_work_date?: string; doctor_notes?: string; digital_signature_confirmation?: boolean }
): Promise<MedicalAssessment> {
  const response = await apiClient.patch<ApiEnvelope<MedicalAssessment>>(`/assessments/${id}/fitness-decision/`, payload);
  return unwrap(response.data);
}

export async function saveDoctorFitnessDecisionDraft(
  id: string,
  payload: { final_decision: FitnessDecision; return_to_work_date?: string; doctor_notes?: string }
): Promise<MedicalAssessment> {
  const response = await apiClient.patch<ApiEnvelope<MedicalAssessment>>(`/doctor/assessments/${id}/fitness-decision/draft/`, payload);
  return unwrap(response.data);
}

export async function setDoctorFitnessDecision(
  id: string,
  payload: { final_decision: FitnessDecision; return_to_work_date?: string; doctor_notes?: string; digital_signature_confirmation?: boolean }
): Promise<MedicalAssessment> {
  const response = await apiClient.patch<ApiEnvelope<MedicalAssessment>>(`/doctor/assessments/${id}/fitness-decision/`, payload);
  return unwrap(response.data);
}

export async function listAssessmentFormTemplates(params?: Record<string, string>): Promise<AssessmentFormTemplate[]> {
  const response = await apiClient.get<ApiEnvelope<AssessmentFormTemplate[] | { results?: AssessmentFormTemplate[] }>>("/forms/templates/", { params });
  return normalizeList(unwrap(response.data));
}

export async function createAssessmentFormTemplate(payload: Record<string, unknown>): Promise<AssessmentFormTemplate> {
  const response = await apiClient.post<ApiEnvelope<AssessmentFormTemplate>>("/forms/templates/", payload);
  return unwrap(response.data);
}

export async function updateAssessmentFormTemplate(id: string, payload: Record<string, unknown>): Promise<AssessmentFormTemplate> {
  const response = await apiClient.patch<ApiEnvelope<AssessmentFormTemplate>>(`/forms/templates/${id}/`, payload);
  return unwrap(response.data);
}

export async function duplicateAssessmentFormTemplate(id: string): Promise<AssessmentFormTemplate> {
  const response = await apiClient.post<ApiEnvelope<AssessmentFormTemplate>>(`/forms/templates/${id}/duplicate/`);
  return unwrap(response.data);
}

export async function transitionAssessmentFormTemplate(id: string, action: "submit-for-approval" | "approve" | "reject" | "request-changes" | "publish" | "activate" | "retire", payload: Record<string, unknown> = {}): Promise<AssessmentFormTemplate> {
  const response = await apiClient.post<ApiEnvelope<AssessmentFormTemplate>>(`/forms/templates/${id}/${action}/`, payload);
  return unwrap(response.data);
}

export async function createAssessmentFormSection(payload: Record<string, unknown>): Promise<AssessmentFormSection> {
  const response = await apiClient.post<ApiEnvelope<AssessmentFormSection>>("/forms/sections/", payload);
  return unwrap(response.data);
}

export async function createAssessmentFormQuestion(payload: Record<string, unknown>): Promise<AssessmentFormQuestion> {
  const response = await apiClient.post<ApiEnvelope<AssessmentFormQuestion>>("/forms/questions/", payload);
  return unwrap(response.data);
}

export async function getAssessmentRequirements(assessmentId: string): Promise<AssessmentRequirementResolution> {
  const response = await apiClient.get<ApiEnvelope<AssessmentRequirementResolution>>(`/assessments/${assessmentId}/requirements/`);
  return unwrap(response.data);
}

export async function listAssessmentFormResponses(params?: Record<string, string>): Promise<AssessmentFormResponse[]> {
  const response = await apiClient.get<ApiEnvelope<AssessmentFormResponse[] | { results?: AssessmentFormResponse[] }>>("/form-responses/", { params });
  return normalizeList(unwrap(response.data));
}

export async function listAssignedAssessmentForms(assessmentId: string): Promise<AssessmentFormResponse[]> {
  const response = await apiClient.get<ApiEnvelope<AssessmentFormResponse[]>>(`/assessments/${assessmentId}/forms/`);
  return normalizeList(unwrap(response.data));
}

export async function assignAssessmentForms(assessmentId: string): Promise<AssessmentFormResponse[]> {
  const response = await apiClient.post<ApiEnvelope<AssessmentFormResponse[]>>(`/assessments/${assessmentId}/forms/assign/`);
  return normalizeList(unwrap(response.data));
}

export async function saveAssessmentFormResponse(responseId: string, responseData: Record<string, unknown>): Promise<AssessmentFormResponse> {
  const response = await apiClient.patch<ApiEnvelope<AssessmentFormResponse>>(`/form-responses/${responseId}/`, { response_data: responseData });
  return unwrap(response.data);
}

export async function submitAssessmentFormResponse(responseId: string): Promise<AssessmentFormResponse> {
  const response = await apiClient.post<ApiEnvelope<AssessmentFormResponse>>(`/form-responses/${responseId}/submit/`);
  return unwrap(response.data);
}

export async function reviewAssessmentFormResponse(responseId: string): Promise<AssessmentFormResponse> {
  const response = await apiClient.post<ApiEnvelope<AssessmentFormResponse>>(`/form-responses/${responseId}/review/`);
  return unwrap(response.data);
}

export async function validateAssessmentFormResponse(responseId: string): Promise<AssessmentFormResponse> {
  const response = await apiClient.post<ApiEnvelope<AssessmentFormResponse>>(`/form-responses/${responseId}/validate/`);
  return unwrap(response.data);
}

export async function reopenAssessmentFormResponse(responseId: string, reason: string): Promise<AssessmentFormResponse> {
  const response = await apiClient.post<ApiEnvelope<AssessmentFormResponse>>(`/form-responses/${responseId}/reopen/`, { reason });
  return unwrap(response.data);
}
