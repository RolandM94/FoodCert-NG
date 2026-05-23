export type SettlementStatus = "pending" | "processing" | "paid" | "failed" | "cancelled";
export type SettlementDisputeStatus = "none" | "open" | "under_review" | "resolved" | "rejected";

export type Settlement = {
  id: string;
  facility: string;
  facility_name?: string;
  state: string;
  state_name?: string;
  payment_transaction: string;
  payment_reference?: string;
  payment_status?: string;
  assessment?: string;
  gross_amount: string;
  facility_amount: string;
  state_amount: string;
  platform_amount: string;
  settlement_status: SettlementStatus;
  settlement_reference: string;
  settled_at?: string;
  dispute_status: SettlementDisputeStatus;
  dispute_reason: string;
  disputed_by?: string;
  disputed_by_name?: string;
  disputed_at?: string;
  dispute_resolution: string;
  created_at: string;
  updated_at: string;
};

export type FacilitySettlementReport = {
  cards: {
    paid_assessments: number;
    completed_assessments: number;
    pending_settlements: number;
    processing_settlements: number;
    paid_settlements: number;
    failed_settlements: number;
    gross_amount: string | number;
    facility_amount: string | number;
    state_amount: string | number;
    platform_amount: string | number;
    refunds: number;
    disputes: number;
  };
  status: Record<string, number>;
};
