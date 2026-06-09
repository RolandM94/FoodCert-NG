import {
  Activity,
  AlertTriangle,
  BadgeCheck,
  Banknote,
  BarChart3,
  Bell,
  Building2,
  CalendarDays,
  FileStack,
  ClipboardCheck,
  ClipboardList,
  FileCheck2,
  FlaskConical,
  GitBranch,
  HeartPulse,
  IdCard,
  Landmark,
  ReceiptText,
  MapPin,
  Network,
  QrCode,
  Settings,
  ShieldCheck,
  Stethoscope,
  Syringe,
  UsersRound
} from "lucide-react";
import type { UserRole } from "@/types/auth";

export type PortalNavItem = {
  label: string;
  href: string;
  icon: typeof Activity;
};

export const ROLE_HOME: Record<UserRole, string> = {
  food_handler: "/food-handler/dashboard",
  employer: "/employer/dashboard",
  facility_admin: "/facility/dashboard",
  doctor: "/doctor/dashboard",
  lab_staff: "/lab/dashboard",
  state_admin: "/state/dashboard",
  federal_admin: "/federal/dashboard",
  inspector: "/inspector/dashboard",
  super_admin: "/federal/dashboard"
};

export const PORTAL_NAV: Record<UserRole, PortalNavItem[]> = {
  food_handler: [
    { label: "Dashboard", href: "/food-handler/dashboard", icon: Activity },
    { label: "Profile", href: "/food-handler/profile", icon: IdCard },
    { label: "NIN Verification", href: "/food-handler/nin-verification", icon: ShieldCheck },
    { label: "Appointments", href: "/food-handler/appointments", icon: CalendarDays },
    { label: "Declaration", href: "/food-handler/declaration", icon: ClipboardList },
    { label: "Assessments", href: "/food-handler/assessments", icon: Stethoscope },
    { label: "Forms", href: "/food-handler/forms", icon: FileStack },
    { label: "Vaccinations", href: "/food-handler/vaccinations", icon: Syringe },
    { label: "Certificate", href: "/food-handler/certificate", icon: BadgeCheck },
    { label: "Illness Report", href: "/food-handler/illness-report", icon: HeartPulse },
    { label: "Notifications", href: "/food-handler/notifications", icon: Bell }
  ],
  employer: [
    { label: "Dashboard", href: "/employer/dashboard", icon: Activity },
    { label: "Business Profile", href: "/employer/business-profile", icon: Building2 },
    { label: "Stakeholder Management", href: "/employer/stakeholder-management", icon: UsersRound },
    { label: "Food Handlers", href: "/employer/food-handlers", icon: UsersRound },
    { label: "Compliance", href: "/employer/compliance", icon: ClipboardCheck },
    { label: "Vaccinations", href: "/employer/vaccinations", icon: Syringe },
    { label: "Illness Reports", href: "/employer/illness-reports", icon: HeartPulse },
    { label: "Notices", href: "/employer/notices", icon: AlertTriangle },
    { label: "Subscription", href: "/employer/subscription", icon: Banknote },
    { label: "Bulk Payments", href: "/employer/bulk-assessment-payments", icon: ReceiptText },
    { label: "Notifications", href: "/employer/notifications", icon: Bell },
    { label: "Reports", href: "/employer/reports", icon: BarChart3 },
    { label: "Inspections", href: "/employer/inspections", icon: ClipboardList },
    { label: "Settings", href: "/employer/settings", icon: Settings }
  ],
  facility_admin: [
    { label: "Dashboard", href: "/facility/dashboard", icon: Activity },
    { label: "Profile", href: "/facility/profile", icon: Building2 },
    { label: "Stakeholder Management", href: "/facility/stakeholder-management", icon: UsersRound },
    { label: "Accreditation", href: "/facility/accreditation", icon: ShieldCheck },
    { label: "Appointments", href: "/facility/appointments", icon: CalendarDays },
    { label: "Assessments", href: "/facility/assessments", icon: Stethoscope },
    { label: "Forms", href: "/facility/forms", icon: FileStack },
    { label: "Lab Tests", href: "/facility/lab-tests", icon: FlaskConical },
    { label: "Certificates", href: "/facility/certificates", icon: BadgeCheck },
    { label: "Settlements", href: "/facility/settlements", icon: Banknote },
    { label: "Reports", href: "/facility/reports", icon: BarChart3 },
  ],
  doctor: [
    { label: "Dashboard", href: "/doctor/dashboard", icon: Activity },
    { label: "Assessments", href: "/doctor/assessments", icon: Stethoscope },
    { label: "Forms", href: "/doctor/forms", icon: FileStack }
  ],
  lab_staff: [
    { label: "Dashboard", href: "/lab/dashboard", icon: Activity },
    { label: "Test Requests", href: "/lab/test-requests", icon: FlaskConical },
    { label: "Results", href: "/lab/results", icon: FileCheck2 },
    { label: "Forms", href: "/lab/forms", icon: FileStack }
  ],
  state_admin: [
    { label: "Dashboard", href: "/state/dashboard", icon: Activity },
    { label: "Stakeholder Management", href: "/state/stakeholder-management", icon: UsersRound },
    { label: "Facilities", href: "/state/facilities", icon: Building2 },
    { label: "Forms", href: "/state/forms", icon: FileStack },
    { label: "Accreditation", href: "/state/facilities/accreditation", icon: ShieldCheck },
    { label: "Certificate Queue", href: "/state/certificate-requests", icon: BadgeCheck },
    { label: "Certificates", href: "/state/certificates", icon: FileCheck2 },
    { label: "Templates", href: "/state/certificate-templates", icon: Settings },
    { label: "Employers", href: "/state/employers", icon: UsersRound },
    { label: "Food Handlers", href: "/state/food-handlers", icon: IdCard },
    { label: "Illness", href: "/state/illness-reports", icon: HeartPulse },
    { label: "Inspections", href: "/state/inspections", icon: ClipboardCheck },
    { label: "Notices", href: "/state/inspectorate/notices", icon: AlertTriangle },
    { label: "Cases", href: "/state/inspectorate/cases", icon: ShieldCheck },
    { label: "Enforcement", href: "/state/enforcement/dashboard", icon: BarChart3 },
    { label: "Fees", href: "/state/fees", icon: Banknote },
    { label: "Revenue", href: "/state/revenue", icon: Landmark },
    { label: "Reports", href: "/state/reports", icon: BarChart3 },
  ],
  federal_admin: [
    { label: "Dashboard", href: "/federal/dashboard", icon: Activity },
    { label: "Stakeholder Management", href: "/federal/stakeholder-management", icon: UsersRound },
    { label: "States", href: "/federal/states", icon: MapPin },
    { label: "Certificates", href: "/federal/certificates", icon: BadgeCheck },
    { label: "Facilities", href: "/federal/facilities", icon: Building2 },
    { label: "Forms", href: "/federal/forms", icon: FileStack },
    { label: "Employers", href: "/federal/employers", icon: UsersRound },
    { label: "Analytics", href: "/federal/analytics", icon: BarChart3 },
    { label: "Data Quality", href: "/federal/data-quality", icon: ShieldCheck },
    { label: "Enforcement", href: "/federal/enforcement/dashboard", icon: AlertTriangle },
    { label: "Audit", href: "/federal/audit", icon: ClipboardCheck },
    { label: "Queries", href: "/federal/queries", icon: Bell },
    { label: "Reports", href: "/federal/reports", icon: ClipboardList },
    { label: "Policy Config", href: "/federal/policy-config", icon: Landmark },
    { label: "Templates", href: "/admin/certificate-templates", icon: Settings },
  ],
  inspector: [
    { label: "Dashboard", href: "/inspector/dashboard", icon: Activity },
    { label: "Scan", href: "/inspector/scan", icon: QrCode },
    { label: "Businesses", href: "/inspector/businesses", icon: Building2 },
    { label: "Inspections", href: "/inspector/inspections", icon: ClipboardCheck },
    { label: "New Inspection", href: "/inspector/inspections/new", icon: ClipboardList }
  ],
  super_admin: [
    { label: "Dashboard", href: "/federal/dashboard", icon: Activity },
    { label: "Stakeholder Management", href: "/admin/stakeholder-management", icon: UsersRound },
    { label: "States", href: "/federal/states", icon: MapPin },
    { label: "Certificates", href: "/federal/certificates", icon: BadgeCheck },
    { label: "Facilities", href: "/federal/facilities", icon: Building2 },
    { label: "Employers", href: "/federal/employers", icon: UsersRound },
    { label: "Analytics", href: "/federal/analytics", icon: BarChart3 },
    { label: "Data Quality", href: "/federal/data-quality", icon: ShieldCheck },
    { label: "Audit", href: "/federal/audit", icon: ClipboardCheck },
    { label: "Queries", href: "/federal/queries", icon: Bell },
    { label: "Reports", href: "/federal/reports", icon: ClipboardList },
    { label: "Policy Config", href: "/federal/policy-config", icon: Landmark }
  ]
};
