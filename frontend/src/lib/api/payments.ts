import { apiClient, unwrap, type ApiEnvelope } from "@/lib/api/client";
import type {
  AssessmentFee,
  BillingCycle,
  EmployerInvoice,
  EmployerSubscription,
  EmployerSubscriptionPlan,
  PaymentTransaction,
  Settlement
} from "@/types/payments";

export async function listAssessmentFees(): Promise<AssessmentFee[]> {
  const response = await apiClient.get<ApiEnvelope<AssessmentFee[]>>("/assessment-fees/");
  return unwrap(response.data);
}

export async function createAssessmentFee(payload: Record<string, unknown>): Promise<AssessmentFee> {
  const response = await apiClient.post<ApiEnvelope<AssessmentFee>>("/assessment-fees/", payload);
  return unwrap(response.data);
}

export async function updateAssessmentFee(id: string, payload: Record<string, unknown>): Promise<AssessmentFee> {
  const response = await apiClient.patch<ApiEnvelope<AssessmentFee>>(`/assessment-fees/${id}/`, payload);
  return unwrap(response.data);
}

export async function initiateAssessmentPayment(payload: {
  food_handler_id: string;
  facility: string;
}): Promise<PaymentTransaction> {
  const response = await apiClient.post<ApiEnvelope<PaymentTransaction>>("/payments/assessment/initiate/", payload);
  return unwrap(response.data);
}

export async function initiateSubscriptionPayment(payload: {
  employer_id: string;
  plan_id: string;
  billing_cycle: BillingCycle;
}): Promise<PaymentTransaction> {
  const response = await apiClient.post<ApiEnvelope<PaymentTransaction>>("/payments/subscription/initiate/", payload);
  return unwrap(response.data);
}

export async function verifyPayment(reference: string): Promise<PaymentTransaction> {
  const response = await apiClient.get<ApiEnvelope<PaymentTransaction>>(`/payments/verify/${reference}/`);
  return unwrap(response.data);
}

export async function listSubscriptionPlans(): Promise<EmployerSubscriptionPlan[]> {
  const response = await apiClient.get<ApiEnvelope<EmployerSubscriptionPlan[]>>("/subscription-plans/");
  return unwrap(response.data);
}

export async function createSubscriptionPlan(payload: Record<string, unknown>): Promise<EmployerSubscriptionPlan> {
  const response = await apiClient.post<ApiEnvelope<EmployerSubscriptionPlan>>("/subscription-plans/", payload);
  return unwrap(response.data);
}

export async function subscribeEmployer(
  employerId: string,
  payload: { plan: string; billing_cycle: BillingCycle }
): Promise<EmployerSubscription> {
  const response = await apiClient.post<ApiEnvelope<EmployerSubscription>>(`/employers/${employerId}/subscribe/`, payload);
  return unwrap(response.data);
}

export async function getEmployerSubscription(employerId: string): Promise<EmployerSubscription | null> {
  const response = await apiClient.get<ApiEnvelope<EmployerSubscription | null>>(`/employers/${employerId}/subscription/`);
  return unwrap(response.data);
}

export async function checkoutEmployerSubscription(
  employerId: string,
  payload: { plan_id: string; billing_cycle: BillingCycle }
): Promise<EmployerSubscription> {
  const response = await apiClient.post<ApiEnvelope<EmployerSubscription>>(
    `/employers/${employerId}/subscription/checkout/`,
    payload
  );
  return unwrap(response.data);
}

export async function changeEmployerSubscriptionPlan(
  employerId: string,
  payload: { plan_id: string; billing_cycle: BillingCycle }
): Promise<EmployerSubscription> {
  const response = await apiClient.patch<ApiEnvelope<EmployerSubscription>>(
    `/employers/${employerId}/subscription/change-plan/`,
    payload
  );
  return unwrap(response.data);
}

export async function listEmployerInvoices(employerId: string): Promise<EmployerInvoice[]> {
  const response = await apiClient.get<ApiEnvelope<EmployerInvoice[]>>(`/employers/${employerId}/invoices/`);
  return unwrap(response.data);
}

export async function listEmployerPayments(employerId: string): Promise<PaymentTransaction[]> {
  const response = await apiClient.get<ApiEnvelope<PaymentTransaction[]>>(`/employers/${employerId}/payments/`);
  return unwrap(response.data);
}

export async function listSettlements(): Promise<Settlement[]> {
  const response = await apiClient.get<ApiEnvelope<Settlement[]>>("/settlements/");
  return unwrap(response.data);
}

export async function processSettlement(id: string): Promise<Settlement> {
  const response = await apiClient.post<ApiEnvelope<Settlement>>(`/settlements/${id}/process/`);
  return unwrap(response.data);
}

export async function listFacilitySettlements(facilityId: string): Promise<Settlement[]> {
  const response = await apiClient.get<ApiEnvelope<Settlement[]>>(`/facilities/${facilityId}/settlements/`);
  return unwrap(response.data);
}
