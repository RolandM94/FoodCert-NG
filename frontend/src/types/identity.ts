export type Gender = "male" | "female" | "other";

export type FoodHandlerStatus =
  | "profile_incomplete"
  | "nin_pending"
  | "certification_pending"
  | "fit"
  | "temporarily_not_fit"
  | "excluded";

export type NINVerificationStatus =
  | "not_submitted"
  | "pending_verification"
  | "verified"
  | "failed"
  | "mismatch"
  | "manual_review_required"
  | "override_approved";

export type FoodHandlerProfile = {
  id: string;
  full_name: string;
  date_of_birth: string;
  gender: Gender;
  masked_nin?: string;
  phone: string;
  email: string;
  nationality: string;
  home_address: string;
  state: string;
  state_name?: string;
  lga?: string;
  lga_name?: string;
  ward: string;
  employer?: string;
  employer_name?: string;
  work_location: string;
  food_handler_category: string;
  emergency_contact: string;
  system_identifier: string;
  current_status: FoodHandlerStatus;
  created_at: string;
  updated_at: string;
};

export type Employer = {
  id: string;
  organization: string;
  organization_name?: string;
  business_name: string;
  business_registration_number: string;
  establishment_category: string;
  contact_person_name: string;
  contact_person_phone: string;
  contact_person_email: string;
  address: string;
  state: string;
  state_name?: string;
  lga?: string;
  lga_name?: string;
  ward: string;
  number_of_food_handlers: number;
  compliance_status: "compliant" | "non_compliant" | "under_review";
  subscription_status: "active" | "expired" | "cancelled" | "never_subscribed";
  created_at: string;
  updated_at: string;
};

export type NINVerification = {
  id: string;
  food_handler: string;
  food_handler_name: string;
  masked_nin: string;
  provider: string;
  provider_reference: string;
  status: NINVerificationStatus;
  verified_full_name: string;
  verified_date_of_birth?: string;
  verified_gender: string;
  verified_photo_url: string;
  match_score: string;
  mismatch_fields: Record<string, unknown>;
  verified_at?: string;
  review_notes: string;
  created_at: string;
  updated_at: string;
};
