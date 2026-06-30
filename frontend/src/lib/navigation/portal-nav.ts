import {
  Activity,
  AlertTriangle,
  BadgeCheck,
  Banknote,
  BarChart3,
  Bell,
  BookOpen,
  Building2,
  CalendarDays,
  FileStack,
  ClipboardCheck,
  ClipboardList,
  FileCheck2,
  FlaskConical,
  HeartPulse,
  IdCard,
  Landmark,
  LayoutDashboard,
  MapPin,
  Megaphone,
  ReceiptText,
  QrCode,
  Scale,
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
    { label: "Illness", href: "/food-handler/illness", icon: HeartPulse },
    { label: "Return-to-Work", href: "/food-handler/return-to-work", icon: ClipboardCheck },
    { label: "Notifications", href: "/food-handler/notifications", icon: Bell }
  ],
  employer: [
    { label: "Dashboard Analytics", href: "/employer/dashboard", icon: LayoutDashboard },
    { label: "Business Profile", href: "/employer/business-profile", icon: Building2 },
    { label: "Directory & Registry", href: "/employer/directory", icon: BookOpen },
    { label: "Compliance", href: "/employer/compliance", icon: ClipboardCheck },
    { label: "Vaccinations", href: "/employer/vaccinations", icon: Syringe },
    { label: "Illness Reports", href: "/employer/illness-reports", icon: HeartPulse },
    { label: "Return-to-Work", href: "/employer/return-to-work", icon: ClipboardCheck },
    { label: "Notices", href: "/employer/notices", icon: AlertTriangle },
    { label: "Subscription", href: "/employer/subscription", icon: Banknote },
    { label: "Bulk Payments", href: "/employer/bulk-assessment-payments", icon: ReceiptText },
    { label: "Notifications", href: "/employer/notifications", icon: Bell },
    { label: "Reports", href: "/employer/reports", icon: BarChart3 },
    { label: "Stakeholder Management", href: "/employer/stakeholder-management", icon: UsersRound },
    { label: "Inspections", href: "/employer/inspections", icon: ClipboardList },
    { label: "Settings", href: "/employer/settings", icon: Settings }
  ],
  facility_admin: [
    { label: "Dashboard", href: "/facility/dashboard", icon: LayoutDashboard },
    { label: "Profile", href: "/facility/profile", icon: Building2 },
    { label: "Stakeholder Management", href: "/facility/stakeholder-management", icon: UsersRound },
    { label: "Accreditation", href: "/facility/accreditation", icon: ShieldCheck },
    { label: "Appointments", href: "/facility/appointments", icon: CalendarDays },
    { label: "Assessments", href: "/facility/assessments", icon: Stethoscope },
    { label: "Forms", href: "/facility/forms", icon: FileStack },
    { label: "Lab Tests", href: "/facility/lab-tests", icon: FlaskConical },
    { label: "Compliance", href: "/facility/compliance", icon: ClipboardCheck },
    { label: "Certificates", href: "/facility/certificates", icon: BadgeCheck },
    { label: "Settlements", href: "/facility/settlements", icon: Banknote },
    { label: "Reports", href: "/facility/reports", icon: BarChart3 },
    { label: "Audit Logs", href: "/facility/audit-logs", icon: Bell },
  ],
  doctor: [
    { label: "Dashboard", href: "/doctor/dashboard", icon: Activity },
    { label: "Assessments", href: "/doctor/assessments", icon: Stethoscope },
    { label: "Declarations", href: "/doctor/declarations", icon: ClipboardList },
    { label: "Reviews", href: "/doctor/reviews", icon: FileCheck2 },
    { label: "Forms", href: "/doctor/forms", icon: FileStack }
  ],
  lab_staff: [
    { label: "Dashboard", href: "/lab/dashboard", icon: Activity },
    { label: "Test Requests", href: "/lab/test-requests", icon: FlaskConical },
    { label: "Results", href: "/lab/results", icon: FileCheck2 },
    { label: "Forms", href: "/lab/forms", icon: FileStack }
  ],
  state_admin: [
    { label: "Dashboard Analytics", href: "/state/dashboard", icon: LayoutDashboard },
    { label: "Directory & Registry", href: "/state/directory", icon: BookOpen },
    { label: "Medical Facilities", href: "/state/medical-facilities", icon: Building2 },

    { label: "Certificates", href: "/state/certificates", icon: FileCheck2 },
    { label: "Inspections & Enforcement", href: "/state/inspections-enforcement", icon: ClipboardCheck },
    { label: "Payments & Revenue", href: "/state/revenue", icon: Landmark },
    { label: "Public Awareness", href: "/state/public-awareness", icon: Megaphone },
    { label: "Reports", href: "/state/reports", icon: BarChart3 },
    { label: "Audit Logs", href: "/state/audit-logs", icon: Bell },
    { label: "Stakeholder Management", href: "/state/stakeholder-management", icon: UsersRound },
    { label: "Account Settings", href: "/state/account-settings", icon: Settings },
  ],
  federal_admin: [
    { label: "Dashboard Analytics", href: "/federal/dashboard", icon: LayoutDashboard },
    { label: "States Overview", href: "/federal/states", icon: MapPin },
    { label: "Standards & Policy", href: "/federal/standards-policy", icon: Scale },
    { label: "Directory & Registry", href: "/federal/directory", icon: BookOpen },
    { label: "Reports", href: "/federal/reports", icon: BarChart3 },
    { label: "Account Settings", href: "/federal/account-settings", icon: Settings },
  ],
  inspector: [
    { label: "Dashboard", href: "/inspector/dashboard", icon: Activity },
    { label: "Directory & Registry", href: "/inspector/directory", icon: BookOpen },
    { label: "Scan", href: "/inspector/scan", icon: QrCode },
    { label: "Businesses", href: "/inspector/businesses", icon: Building2 },
    { label: "Inspections", href: "/inspector/inspections", icon: ClipboardCheck },
    { label: "New Inspection", href: "/inspector/inspections/new", icon: ClipboardList },
    { label: "Dashboard Builder", href: "/inspector/reports/dashboard-builder", icon: LayoutDashboard }
  ],
  super_admin: [
    { label: "Dashboard Analytics", href: "/federal/dashboard", icon: LayoutDashboard },
    { label: "Directory & Registry", href: "/admin/directory", icon: BookOpen },
    { label: "States", href: "/federal/states", icon: MapPin },
    { label: "Standards & Policy", href: "/federal/standards-policy", icon: Scale },
    { label: "Certificates", href: "/federal/certificates", icon: BadgeCheck },
    { label: "Facilities", href: "/federal/facilities", icon: Building2 },
    { label: "Data Quality", href: "/federal/data-quality", icon: ShieldCheck },
    { label: "Queries", href: "/federal/queries", icon: Bell },
    { label: "Reports", href: "/federal/reports", icon: ClipboardList },
    { label: "Stakeholder Management", href: "/admin/stakeholder-management", icon: UsersRound },
    { label: "Account Settings", href: "/federal/account-settings", icon: Settings }
  ]
};
