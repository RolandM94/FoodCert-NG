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
  headquarters: "bg-purple-50 text-purple-700 ring-purple-200",
  directorate: "bg-blue-50 text-blue-700 ring-blue-200",
  department: "bg-cyan-50 text-cyan-700 ring-cyan-200",
  unit: "bg-slate-50 text-slate-700 ring-slate-200",
  desk: "bg-sky-50 text-sky-700 ring-sky-200",
  office: "bg-teal-50 text-teal-700 ring-teal-200",
  branch: "bg-amber-50 text-amber-700 ring-amber-200",
  regional_office: "bg-rose-50 text-rose-700 ring-rose-200",
  site: "bg-orange-50 text-orange-700 ring-orange-200",
  outlet: "bg-lime-50 text-lime-700 ring-lime-200",
  store: "bg-yellow-50 text-yellow-700 ring-yellow-200",
  lga_office: "bg-orange-50 text-orange-700 ring-orange-200",
  inspectorate: "bg-red-50 text-red-700 ring-red-200",
  lab_department: "bg-teal-50 text-teal-700 ring-teal-200",
  clinical_department: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  medical_records_department: "bg-indigo-50 text-indigo-700 ring-indigo-200",
  records_department: "bg-indigo-50 text-indigo-700 ring-indigo-200",
  finance_unit: "bg-green-50 text-green-700 ring-green-200",
  administration_unit: "bg-gray-50 text-gray-700 ring-gray-200",
  support_unit: "bg-violet-50 text-violet-700 ring-violet-200",
  technical_unit: "bg-slate-50 text-slate-700 ring-slate-200",
  other: "bg-slate-50 text-slate-600 ring-slate-200",
};

export const ORG_STATUS_COLORS: Record<string, string> = {
  active: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  draft: "bg-slate-50 text-slate-600 ring-slate-200",
  "pending-approval": "bg-amber-50 text-amber-700 ring-amber-200",
  "pending_approval": "bg-amber-50 text-amber-700 ring-amber-200",
  suspended: "bg-rose-50 text-rose-700 ring-rose-200",
  inactive: "bg-slate-100 text-slate-500 ring-slate-200",
  archived: "bg-slate-50 text-slate-400 ring-slate-200",
};
