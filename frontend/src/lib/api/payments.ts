import { apiClient, unwrap, type ApiEnvelope } from "@/lib/api/client";
import type {
  AssessmentFee,
  BulkAssessmentPaymentQuote,
  BillingCycle,
  EmployerEntitlements,
  EmployerInvoice,
  EmployerSubscription,
  EmployerSubscriptionPlan,
  AssessmentPaymentQuote,
  PaymentTransaction,
  PaymentReceipt,
  PaymentReconciliationRecord,
  ProviderPerformanceRow,
  RefundRequest,
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

export async function getAssessmentPaymentQuote(assessmentId: string): Promise<AssessmentPaymentQuote> {
  const response = await apiClient.get<ApiEnvelope<AssessmentPaymentQuote>>(`/payments/assessment/${assessmentId}/fee/`);
  return unwrap(response.data);
}

export async function initializeAssessmentPayment(assessmentId: string): Promise<PaymentTransaction> {
  const response = await apiClient.post<ApiEnvelope<PaymentTransaction>>(`/payments/assessment/${assessmentId}/initialize/`);
  return unwrap(response.data);
}

export async function quoteEmployerBulkAssessmentPayment(
  employerId: string,
  assessmentIds: string[]
): Promise<BulkAssessmentPaymentQuote> {
  const response = await apiClient.post<ApiEnvelope<BulkAssessmentPaymentQuote>>(
    `/payments/employers/${employerId}/bulk-assessments/quote/`,
    { assessment_ids: assessmentIds }
  );
  return unwrap(response.data);
}

export async function initializeEmployerBulkAssessmentPayment(
  employerId: string,
  assessmentIds: string[]
): Promise<PaymentTransaction> {
  const response = await apiClient.post<ApiEnvelope<PaymentTransaction>>(
    `/payments/employers/${employerId}/bulk-assessments/initialize/`,
    { assessment_ids: assessmentIds }
  );
  return unwrap(response.data);
}

export async function getPaymentReceipt(transactionId: string): Promise<PaymentReceipt> {
  const response = await apiClient.get<ApiEnvelope<PaymentReceipt>>(`/payments/transactions/${transactionId}/receipt/`);
  return unwrap(response.data);
}

export async function listPayments(params?: Record<string, string>): Promise<PaymentTransaction[]> {
  const response = await apiClient.get<ApiEnvelope<PaymentTransaction[]>>("/payments/", { params });
  return unwrap(response.data);
}

export async function getPayment(id: string): Promise<PaymentTransaction> {
  const response = await apiClient.get<ApiEnvelope<PaymentTransaction>>(`/payments/${id}/`);
  return unwrap(response.data);
}

export async function createRefundRequest(transactionId: string, payload: { reason: string; amount?: string }): Promise<RefundRequest> {
  const response = await apiClient.post<ApiEnvelope<RefundRequest>>(`/payments/transactions/${transactionId}/refund-request/`, payload);
  return unwrap(response.data);
}

export async function listRefundRequests(transactionId: string): Promise<RefundRequest[]> {
  const response = await apiClient.get<ApiEnvelope<RefundRequest[]>>(`/payments/transactions/${transactionId}/refund-requests/`);
  return unwrap(response.data);
}

export async function listPaymentReconciliations(
  scope: "admin" | "state" | "federal" = "admin",
  params?: Record<string, string>
): Promise<PaymentReconciliationRecord[]> {
  const basePath = scope === "state" ? "/state/finance/reconciliation/" : scope === "federal" ? "/federal/finance/reconciliation/" : "/admin/payment-reconciliations/";
  const response = await apiClient.get<ApiEnvelope<PaymentReconciliationRecord[]>>(basePath, { params });
  return unwrap(response.data);
}

export async function fetchProviderPerformance(scope: "admin" | "state" | "federal" = "admin"): Promise<ProviderPerformanceRow[]> {
  const basePath = scope === "state" ? "/state/finance/reconciliation/" : scope === "federal" ? "/federal/finance/reconciliation/" : "/admin/payment-reconciliations/";
  const response = await apiClient.get<ApiEnvelope<ProviderPerformanceRow[]>>(`${basePath}provider-performance/`);
  return unwrap(response.data);
}

export async function importPaymentReconciliations(payload: {
  provider_code: string;
  records: Array<{
    provider_reference: string;
    internal_reference?: string;
    amount: string;
    currency?: string;
    provider_payload?: Record<string, unknown>;
  }>;
}): Promise<PaymentReconciliationRecord[]> {
  const response = await apiClient.post<ApiEnvelope<PaymentReconciliationRecord[]>>("/admin/payment-reconciliations/import/", payload);
  return unwrap(response.data);
}

export async function resolvePaymentReconciliation(id: string, notes: string): Promise<PaymentReconciliationRecord> {
  const response = await apiClient.post<ApiEnvelope<PaymentReconciliationRecord>>(`/admin/payment-reconciliations/${id}/resolve/`, { notes });
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

export async function renewEmployerSubscription(employerId: string): Promise<EmployerSubscription> {
  const response = await apiClient.post<ApiEnvelope<EmployerSubscription>>(`/employers/${employerId}/subscription/renew/`);
  return unwrap(response.data);
}

export async function cancelEmployerSubscription(employerId: string, payload: { reason?: string }): Promise<EmployerSubscription> {
  const response = await apiClient.post<ApiEnvelope<EmployerSubscription>>(
    `/employers/${employerId}/subscription/cancel/`,
    payload
  );
  return unwrap(response.data);
}

export async function getEmployerEntitlements(employerId: string): Promise<EmployerEntitlements> {
  const response = await apiClient.get<ApiEnvelope<EmployerEntitlements>>(`/employers/${employerId}/subscription/entitlements/`);
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
