import { apiClient, unwrap, type ApiEnvelope } from "@/lib/api/client";
import type { Employer, FoodHandlerProfile, NINVerification } from "@/types/identity";

export async function listFoodHandlers(): Promise<FoodHandlerProfile[]> {
  const response = await apiClient.get<ApiEnvelope<FoodHandlerProfile[]>>("/food-handlers/");
  return unwrap(response.data);
}

export async function createFoodHandlerProfile(payload: FormData | Record<string, unknown>) {
  const response = await apiClient.post<ApiEnvelope<FoodHandlerProfile>>("/food-handlers/", payload);
  return unwrap(response.data);
}

export async function verifyFoodHandlerNIN(foodHandlerId: string): Promise<NINVerification> {
  const response = await apiClient.post<ApiEnvelope<NINVerification>>(`/food-handlers/${foodHandlerId}/verify-nin/`);
  return unwrap(response.data);
}

export async function getFoodHandlerNINVerification(foodHandlerId: string): Promise<NINVerification> {
  const response = await apiClient.get<ApiEnvelope<NINVerification>>(`/food-handlers/${foodHandlerId}/nin-verification/`);
  return unwrap(response.data);
}

export async function listEmployers(): Promise<Employer[]> {
  const response = await apiClient.get<ApiEnvelope<Employer[]>>("/employers/");
  return unwrap(response.data);
}

export async function createEmployer(payload: Record<string, unknown>): Promise<Employer> {
  const response = await apiClient.post<ApiEnvelope<Employer>>("/employers/", payload);
  return unwrap(response.data);
}

export async function approveNINOverride(verificationId: string, review_notes = "") {
  const response = await apiClient.patch<ApiEnvelope<NINVerification>>(
    `/nin-verifications/${verificationId}/approve-override/`,
    { review_notes }
  );
  return unwrap(response.data);
}

export async function rejectNINOverride(verificationId: string, review_notes = "") {
  const response = await apiClient.patch<ApiEnvelope<NINVerification>>(
    `/nin-verifications/${verificationId}/reject-override/`,
    { review_notes }
  );
  return unwrap(response.data);
}
