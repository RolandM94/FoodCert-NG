import { apiClient, unwrap, type ApiEnvelope } from "@/lib/api/client";
import type { FacilitySettlementReport, Settlement } from "@/types/settlements";

export async function listFacilitySettlements(facilityId: string, params?: Record<string, string>): Promise<Settlement[]> {
  const response = await apiClient.get<ApiEnvelope<Settlement[]>>(`/facilities/${facilityId}/settlements/`, { params });
  return unwrap(response.data);
}

export async function getFacilitySettlement(facilityId: string, settlementId: string): Promise<Settlement> {
  const response = await apiClient.get<ApiEnvelope<Settlement>>(`/facilities/${facilityId}/settlements/${settlementId}/`);
  return unwrap(response.data);
}

export async function disputeFacilitySettlement(facilityId: string, settlementId: string, reason: string): Promise<Settlement> {
  const response = await apiClient.post<ApiEnvelope<Settlement>>(`/facilities/${facilityId}/settlements/${settlementId}/dispute/`, { reason });
  return unwrap(response.data);
}

export async function getFacilitySettlementReport(facilityId: string, params?: Record<string, string>): Promise<FacilitySettlementReport> {
  const response = await apiClient.get<ApiEnvelope<FacilitySettlementReport> | FacilitySettlementReport>(`/facilities/${facilityId}/reports/settlements/`, { params });
  if ("data" in response.data) {
    return unwrap(response.data);
  }
  return response.data;
}
