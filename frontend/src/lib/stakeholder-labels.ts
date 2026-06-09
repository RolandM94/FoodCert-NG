import type { OrganizationType, OrganizationUnitType } from "@/types/organizations";

type LabelConfig = {
  plural: string;
  singular: string;
};

const ORG_TYPE_LABELS: Record<OrganizationType, string> = {
  platform_operator: "Platform Operator",
  federal_ministry: "Federal Ministry",
  state_ministry: "State Ministry",
  medical_facility: "Medical Facility",
  employer: "Employer",
};

const UNIT_LABEL_MAP: Record<OrganizationType, LabelConfig> = {
  federal_ministry: { plural: "Departments & Directorates", singular: "Department" },
  state_ministry: { plural: "Units & Offices", singular: "Unit" },
  medical_facility: { plural: "Departments", singular: "Department" },
  employer: { plural: "Branches", singular: "Branch" },
  platform_operator: { plural: "Teams", singular: "Team" },
};

export function getOrgTypeLabel(orgType: OrganizationType): string {
  return ORG_TYPE_LABELS[orgType] ?? orgType;
}

export function getUnitLabel(orgType: OrganizationType, kind: "plural" | "singular" = "plural"): string {
  return UNIT_LABEL_MAP[orgType]?.[kind] ?? "Units";
}

export function getUserLabel(orgType: OrganizationType): string {
  switch (orgType) {
    case "state_ministry":
      return "Officers";
    case "medical_facility":
      return "Staff";
    case "federal_ministry":
      return "Federal Users";
    default:
      return "Users";
  }
}

export const UNIT_TYPE_LABELS: Record<string, string> = {
  headquarters: "Headquarters",
  directorate: "Directorate",
  department: "Department",
  unit: "Unit",
  desk: "Desk",
  office: "Office",
  branch: "Branch",
  regional_office: "Regional Office",
  site: "Site",
  outlet: "Outlet",
  store: "Store",
  lga_office: "LGA Office",
  inspectorate: "Inspectorate",
  lab_department: "Lab Department",
  clinical_department: "Clinical Department",
  medical_records_department: "Medical Records Dept",
  records_department: "Records Department",
  finance_unit: "Finance Unit",
  administration_unit: "Admin Unit",
  support_unit: "Support Unit",
  technical_unit: "Technical Unit",
  other: "Other",
};

export const UNIT_TYPE_COLORS: Record<string, string> = {
  headquarters: "bg-neutral-100 text-neutral-700 ring-neutral-200",
  directorate: "bg-info-50 text-info-700 ring-blue-200",
  department: "bg-info-50 text-info-700 ring-cyan-200",
  unit: "bg-neutral-50 text-neutral-700 ring-neutral-200",
  desk: "bg-info-50 text-info-700 ring-info-100",
  office: "bg-brand-50 text-brand-700 ring-teal-200",
  branch: "bg-warning-50 text-warning-700 ring-warning-100",
  regional_office: "bg-danger-50 text-danger-700 ring-danger-100",
  site: "bg-warning-50 text-warning-700 ring-warning-100",
  outlet: "bg-brand-50 text-brand-700 ring-lime-200",
  store: "bg-warning-50 text-warning-700 ring-yellow-200",
  lga_office: "bg-warning-50 text-warning-700 ring-warning-100",
  inspectorate: "bg-danger-50 text-danger-700 ring-danger-100",
  lab_department: "bg-brand-50 text-brand-700 ring-teal-200",
  clinical_department: "bg-brand-50 text-brand-700 ring-brand-200",
  medical_records_department: "bg-indigo-50 text-indigo-700 ring-indigo-200",
  records_department: "bg-indigo-50 text-indigo-700 ring-indigo-200",
  finance_unit: "bg-brand-50 text-brand-700 ring-green-200",
  administration_unit: "bg-gray-50 text-neutral-700 ring-gray-200",
  support_unit: "bg-violet-50 text-neutral-700 ring-violet-200",
  technical_unit: "bg-neutral-50 text-neutral-700 ring-neutral-200",
  other: "bg-neutral-50 text-neutral-600 ring-neutral-200",
};

export const ORG_STATUS_COLORS: Record<string, string> = {
  active: "bg-brand-50 text-brand-700 ring-brand-200",
  draft: "bg-neutral-50 text-neutral-600 ring-neutral-200",
  "pending-approval": "bg-warning-50 text-warning-700 ring-warning-100",
  "pending_approval": "bg-warning-50 text-warning-700 ring-warning-100",
  suspended: "bg-danger-50 text-danger-700 ring-danger-100",
  inactive: "bg-neutral-100 text-neutral-500 ring-neutral-200",
  archived: "bg-neutral-50 text-neutral-400 ring-neutral-200",
};
