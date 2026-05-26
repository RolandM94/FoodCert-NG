export type ActiveStatus = "active" | "inactive";
export type BillingCycle = "monthly" | "yearly";
export type PaymentStatus = "pending" | "success" | "failed" | "cancelled" | "refunded";
export type InvoiceStatus = "issued" | "paid" | "overdue" | "cancelled";
export type SettlementStatus = "pending" | "processing" | "paid" | "failed" | "cancelled";
export type SubscriptionStatus = "trial" | "active" | "past_due" | "suspended" | "cancelled" | "expired";
export type ReconciliationStatus =
  | "matched"
  | "missing_internal"
  | "missing_provider"
  | "amount_mismatch"
  | "currency_mismatch"
  | "duplicate_provider_reference"
  | "manually_resolved";

export type AssessmentFee = {
  id: string;
  state: string;
  state_name?: string;
  facility_type: string;
  amount: string;
  currency: string;
  state_fee: string;
  facility_fee: string;
  platform_fee: string;
  effective_from: string;
  effective_to?: string;
  status: ActiveStatus;
  created_by?: string;
  created_at: string;
  updated_at: string;
};

export type PaymentTransaction = {
  id: string;
  payer_user: string;
  payer_email?: string;
  payer_type: "food_handler" | "employer" | "facility" | "platform";
  related_entity_type: string;
  related_entity_id: string;
  amount: string;
  currency: string;
  payment_provider: string;
  provider_reference: string;
  internal_reference: string;
  status: PaymentStatus;
  paid_at?: string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type AssessmentPaymentQuote = {
  assessment_id: string;
  fee_schedule_id: string;
  fee_name: string;
  facility_name: string;
  state_name: string;
  amount: string;
  currency: string;
  state_fee: string;
  facility_fee: string;
  platform_fee: string;
  refund_policy_summary: string;
  terms_notice: string;
};

export type BulkAssessmentPaymentLineItem = {
  assessment_id: string;
  food_handler_id: string;
  food_handler_name: string;
  facility_id: string;
  facility_name: string;
  state_id: string;
  state_name: string;
  fee_schedule_id: string;
  fee_name: string;
  amount: string;
  currency: string;
  state_fee: string;
  facility_fee: string;
  platform_fee: string;
};

export type BulkAssessmentPaymentQuote = {
  employer_id: string;
  employer_name: string;
  assessment_count: number;
  amount: string;
  currency: string;
  line_items: BulkAssessmentPaymentLineItem[];
  terms_notice: string;
};

export type PaymentReceipt = {
  id: string;
  receipt_number: string;
  payment_transaction: string;
  payment_reference: string;
  payer_name: string;
  payer_email: string;
  payer_type: "food_handler" | "employer" | "facility" | "platform";
  payment_purpose: string;
  amount: string;
  currency: string;
  payment_method?: string;
  provider_reference?: string;
  facility?: string | null;
  facility_name?: string;
  state?: string | null;
  state_name?: string;
  line_items?: Array<Record<string, unknown>>;
  issued_at: string;
  receipt_url?: string;
};

export type RefundRequestStatus =
  | "requested"
  | "under_review"
  | "approved"
  | "rejected"
  | "processing"
  | "refunded"
  | "failed"
  | "cancelled";

export type RefundRequest = {
  id: string;
  payment_transaction: string;
  payment_reference: string;
  requested_by?: string | null;
  requested_by_email?: string;
  approved_by?: string | null;
  amount: string;
  reason: string;
  status: RefundRequestStatus;
  provider_refund_reference?: string;
  approved_at?: string | null;
  processed_at?: string | null;
  created_at: string;
  updated_at: string;
};

export type PaymentReconciliationRecord = {
  id: string;
  provider_code: string;
  provider_reference: string;
  internal_reference: string;
  payment_transaction?: string | null;
  payment_reference?: string;
  amount: string;
  currency: string;
  status: ReconciliationStatus;
  provider_payload?: Record<string, unknown>;
  matched_at?: string | null;
  resolved_by?: string | null;
  resolved_by_email?: string;
  resolved_at?: string | null;
  resolution_notes?: string;
  created_at: string;
  updated_at: string;
};

export type ProviderPerformanceRow = {
  provider_code: string;
  total_records: number;
  matched_records: number;
  issue_records: number;
  manually_resolved_records: number;
  total_amount?: string | null;
};

export type EmployerSubscriptionPlan = {
  id: string;
  name: string;
  description: string;
  max_food_handlers: number;
  max_locations: number;
  max_users: number;
  trial_days: number;
  price_monthly: string;
  price_yearly: string;
  currency: string;
  features: Record<string, unknown>;
  status: ActiveStatus;
  created_at: string;
  updated_at: string;
};

export type EmployerSubscription = {
  id: string;
  employer: string;
  employer_name?: string;
  plan: string;
  plan_name?: string;
  billing_cycle: BillingCycle;
  status: SubscriptionStatus;
  starts_at: string;
  expires_at: string;
  cancelled_at?: string;
  grace_period_ends_at?: string | null;
  renewal_reminder_sent_at?: string | null;
  auto_renew?: boolean;
  cancellation_reason?: string;
  last_payment_transaction?: string;
  payment_reference?: string;
  is_active: boolean;
  handlers_used?: number;
  max_food_handlers?: number;
  max_locations?: number;
  max_users?: number;
  entitlements?: EmployerEntitlements;
  days_until_expiry?: number;
  usage_percentage?: number;
  created_at: string;
  updated_at: string;
};

export type EmployerEntitlements = {
  regulatory_access: boolean;
  premium_features_active: boolean;
  subscription_status: SubscriptionStatus | "none";
  plan_id?: string | null;
  plan_name?: string | null;
  limits: {
    max_food_handlers: number;
    max_locations: number;
    max_users: number;
  };
  features: Record<string, unknown>;
  restricted_features: string[];
};

export type EmployerInvoice = {
  id: string;
  invoice_number: string;
  employer: string;
  subscription?: string | null;
  plan_name?: string;
  payment_transaction?: string | null;
  date: string;
  description?: string;
  line_items?: Array<Record<string, unknown>>;
  amount_due?: string;
  amount_paid?: string;
  amount: string;
  currency: string;
  status: InvoiceStatus;
  payment_reference?: string;
  due_date?: string;
  issued_at?: string;
  paid_at?: string | null;
  receipt_url?: string | null;
};

export type Settlement = {
  id: string;
  facility: string;
  facility_name?: string;
  state: string;
  state_name?: string;
  payment_transaction: string;
  payment_allocation?: string | null;
  payment_allocation_reference?: string;
  assessment?: string;
  fee_schedule?: string | null;
  fee_schedule_name?: string;
  gross_amount: string;
  facility_amount: string;
  state_amount: string;
  platform_amount: string;
  eligibility_checked_at?: string | null;
  eligibility_reason?: string;
  settlement_status: SettlementStatus;
  settlement_reference: string;
  settled_at?: string;
  created_at: string;
  updated_at: string;
};
