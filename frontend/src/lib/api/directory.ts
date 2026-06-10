import { apiClient, unwrap, type ApiEnvelope } from "./client";

export type DirectoryFoodHandler = {
  id: string;
  user_id: string;
  full_name: string;
  system_identifier: string;
  masked_nin: string;
  phone: string;
  email: string;
  gender: string;
  date_of_birth?: string;
  passport_photo?: string;
  employer_id?: string;
  employer_name?: string;
  business_branch_id?: string;
  branch_name?: string;
  state_id?: string;
  state_name?: string;
  lga_id?: string;
  lga_name?: string;
  food_handler_category: string;
  current_status: string;
  active_illness_status?: string;
  return_to_work_status?: string;
  exclusion_start_date?: string;
  earliest_return_date?: string;
  home_address?: string;
  emergency_contact?: string;
  work_location?: string;
  created_at: string;
  updated_at: string;
};

export type DirectoryEmployer = {
  id: string;
  user_id?: string;
  organization_id?: string;
  business_name: string;
  business_registration_number?: string;
  business_type?: string;
  establishment_category: string;
  contact_person_name: string;
  contact_person_phone?: string;
  contact_person_email?: string;
  address: string;
  state_id?: string;
  state_name?: string;
  lga_id?: string;
  lga_name?: string;
  branch_count: number;
  food_handler_count: number;
  compliance_status: string;
  subscription_status: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type DirectoryBranch = {
  id: string;
  organization_id: string;
  employer_id?: string;
  employer_name?: string;
  name: string;
  unit_type: string;
  parent_id?: string;
  manager_id?: string;
  manager_name?: string;
  state_id?: string;
  state_name?: string;
  lga_id?: string;
  lga_name?: string;
  address: string;
  phone: string;
  email: string;
  status: string;
  food_handler_count: number;
  created_at: string;
  updated_at: string;
};

export type GlobalSearchResults = {
  results: {
    food_handlers?: { id: string; full_name: string; system_identifier: string; employer__business_name?: string }[];
    employers?: { id: string; business_name: string; state__name?: string }[];
    certificates?: { id: string; certificate_number: string; status: string }[];
  };
};

// ── Food Handlers Directory ──
export async function fetchDirectoryFoodHandlers(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<DirectoryFoodHandler[]>>("/directory/food-handlers/", { params });
  return unwrap(res.data);
}

export async function fetchDirectoryFoodHandler(id: string) {
  const res = await apiClient.get<ApiEnvelope<DirectoryFoodHandler>>(`/directory/food-handlers/${id}/`);
  return unwrap(res.data);
}

// ── Employers Directory ──
export async function fetchDirectoryEmployers(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<DirectoryEmployer[]>>("/directory/employers/", { params });
  return unwrap(res.data);
}

export async function fetchDirectoryEmployer(id: string) {
  const res = await apiClient.get<ApiEnvelope<DirectoryEmployer>>(`/directory/employers/${id}/`);
  return unwrap(res.data);
}

// ── Branches Directory ──
export async function fetchDirectoryBranches(params?: Record<string, string>) {
  const res = await apiClient.get<ApiEnvelope<DirectoryBranch[]>>("/directory/branches/", { params });
  return unwrap(res.data);
}

export async function fetchDirectoryBranch(id: string) {
  const res = await apiClient.get<ApiEnvelope<DirectoryBranch>>(`/directory/branches/${id}/`);
  return unwrap(res.data);
}

// ── Global Search ──
export async function fetchGlobalSearch(q: string) {
  const res = await apiClient.get<ApiEnvelope<GlobalSearchResults>>("/directory/global-search/", { params: { q } });
  return unwrap(res.data);
}
