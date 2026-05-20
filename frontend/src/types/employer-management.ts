import type { UserStatus } from "@/types/auth";
import type { InviteStatus } from "@/types/organizations";

export type EmployerStaffRole = "employer_admin" | "compliance_officer" | "branch_manager" | "finance_user";

export type EmployerUser = {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name?: string;
  phone: string;
  role: "employer";
  employer_staff_role: EmployerStaffRole;
  status: UserStatus;
  organization: string;
  unit?: string | null;
  unit_name?: string | null;
  unit_restricted: boolean;
  state?: string | null;
  created_at: string;
  updated_at: string;
};

export type EmployerInvite = {
  id: string;
  organization: string;
  organization_name?: string;
  unit?: string | null;
  unit_name?: string | null;
  invited_by: string;
  invited_by_name?: string;
  email: string;
  phone: string;
  role: "employer";
  employer_staff_role: EmployerStaffRole;
  message: string;
  status: InviteStatus;
  token?: string;
  accepted_by?: string | null;
  accepted_by_name?: string | null;
  accepted_at?: string | null;
  expires_at: string;
  created_at: string;
  updated_at: string;
};

export type EmployerDashboardCards = {
  total_handlers: number;
  fit: number;
  certification_pending: number;
  expired_certificates: number;
  expiring_soon: number;
  expiring_7d: number;
  temporarily_not_fit: number;
  excluded: number;
  vaccination_due: number;
  active_branches: number;
  open_inspections: number;
  subscription_status: string;
  compliance_percentage: number;
};

export type EmployerDashboardScope = {
  branch?: string | null;
  branch_name?: string | null;
  locked: boolean;
};

export type BranchCompliance = {
  branch: string;
  branch_name: string;
  total_handlers: number;
  certified_handlers: number;
  compliance_percentage: number;
};

export type CountRow = {
  label?: string;
  status?: string;
  vaccine_type?: string;
  count?: number;
  valid?: number;
  expired?: number;
  due?: number;
  missing?: number;
};

export type EmployerDashboard = {
  employer: {
    id: string;
    business_name: string;
    organization?: string | null;
    subscription_status: string;
  };
  scope: EmployerDashboardScope;
  cards: EmployerDashboardCards;
  charts: EmployerComplianceSummary;
  open_inspection_notices: Array<{
    id: string;
    branch_name: string;
    inspection_date: string;
    status: string;
    enforcement_action: string;
    findings_summary: string;
  }>;
  recent_activity: Array<{
    id: string;
    kind: string;
    title: string;
    description: string;
    created_at: string;
    status: string;
  }>;
};

export type EmployerComplianceSummary = {
  branch_breakdown: BranchCompliance[];
  certificate_status_distribution: CountRow[];
  vaccination_coverage_summary: CountRow[];
  expiring_certificates_timeline: CountRow[];
  illness_reports_trend: CountRow[];
};

export type EmployerNotification = {
  id: string;
  recipient_name: string;
  notification_type: string;
  status: string;
  subject: string;
  body: string;
  created_at: string;
  read_at?: string | null;
};

export type EmployerNotificationsPayload = {
  unread_count: number;
  notifications: EmployerNotification[];
};

export type EmployerSettings = {
  id: string;
  notification_preferences: Record<string, Record<string, boolean>>;
  business_settings: Record<string, unknown>;
  subscription_status: string;
  updated_at: string;
};
