export type ActiveStatus = "active" | "inactive";
export type BillingCycle = "monthly" | "yearly";
export type PaymentStatus = "pending" | "success" | "failed" | "cancelled" | "refunded";
export type SettlementStatus = "pending" | "processing" | "paid" | "failed" | "cancelled";
export type SubscriptionStatus = "trial" | "active" | "past_due" | "suspended" | "cancelled" | "expired";

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

export type EmployerSubscriptionPlan = {
  id: string;
  name: string;
  description: string;
  max_food_handlers: number;
  max_locations: number;
  price_monthly: string;
  price_yearly: string;
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
  last_payment_transaction?: string;
  payment_reference?: string;
  is_active: boolean;
  handlers_used?: number;
  max_food_handlers?: number;
  max_locations?: number;
  days_until_expiry?: number;
  usage_percentage?: number;
  created_at: string;
  updated_at: string;
};

export type EmployerInvoice = {
  id: string;
  invoice_number: string;
  date: string;
  amount: string;
  currency: string;
  status: PaymentStatus;
  payment_reference: string;
  receipt_url?: string | null;
};

export type Settlement = {
  id: string;
  facility: string;
  facility_name?: string;
  state: string;
  state_name?: string;
  payment_transaction: string;
  assessment?: string;
  gross_amount: string;
  facility_amount: string;
  state_amount: string;
  platform_amount: string;
  settlement_status: SettlementStatus;
  settlement_reference: string;
  settled_at?: string;
  created_at: string;
  updated_at: string;
};
