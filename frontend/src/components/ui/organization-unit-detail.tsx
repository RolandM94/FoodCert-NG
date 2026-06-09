"use client";

import { Building2, ClipboardCheck, FlaskConical, FolderCheck, ListTree, Mail, MapPin, Phone, UsersRound } from "lucide-react";
import type { OrganizationUnit } from "@/types/organizations";

const UNIT_TYPE_LABELS: Record<string, string> = {
  headquarters: "Headquarters",
  directorate: "Directorate",
  department: "Department",
  unit: "Unit",
  branch: "Branch",
  lab_department: "Lab Department",
  clinical_department: "Clinical Department",
  records_department: "Records Department",
  lga_office: "LGA Office",
  regional_office: "Regional Office",
  other: "Other",
};

export function OrganizationUnitDetail({
  unit,
  memberCount,
}: {
  unit: OrganizationUnit;
  memberCount?: number;
}) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-bold text-neutral-900">{unit.name}</h3>
          <span className="mt-1 inline-block rounded bg-neutral-100 px-2 py-0.5 text-xs font-semibold text-neutral-600 uppercase">
            {UNIT_TYPE_LABELS[unit.unit_type] ?? unit.unit_type}
          </span>
          {!unit.is_active && (
            <span className="ml-2 inline-block rounded bg-danger-50 px-2 py-0.5 text-xs font-semibold text-danger-500 uppercase">
              Inactive
            </span>
          )}
        </div>
      </div>

      <div className="mt-4 grid gap-2 text-sm">
        {unit.parent_name && (
          <div className="flex items-center gap-2 text-neutral-600">
            <ListTree size={14} className="text-neutral-400" />
            <span>Parent: <span className="font-semibold text-neutral-800">{unit.parent_name}</span></span>
          </div>
        )}
        {unit.description && (
          <div className="flex items-start gap-2 text-neutral-600">
            <span className="mt-0.5 text-neutral-400">&mdash;</span>
            <span>{unit.description}</span>
          </div>
        )}
        {unit.state_name && (
          <div className="flex items-center gap-2 text-neutral-600">
            <MapPin size={14} className="text-neutral-400" />
            <span>State: <span className="font-semibold text-neutral-800">{unit.state_name}</span></span>
          </div>
        )}
        {unit.lga_name && (
          <div className="flex items-center gap-2 text-neutral-600">
            <MapPin size={14} className="text-neutral-400" />
            <span>LGA: <span className="font-semibold text-neutral-800">{unit.lga_name}</span></span>
          </div>
        )}
        {unit.address && (
          <div className="flex items-center gap-2 text-neutral-600">
            <Building2 size={14} className="text-neutral-400" />
            <span>{unit.address}</span>
          </div>
        )}
        {unit.phone && (
          <div className="flex items-center gap-2 text-neutral-600">
            <Phone size={14} className="text-neutral-400" />
            <span>{unit.phone}</span>
          </div>
        )}
        {unit.email && (
          <div className="flex items-center gap-2 text-neutral-600">
            <Mail size={14} className="text-neutral-400" />
            <span className="break-all">{unit.email}</span>
          </div>
        )}
        {memberCount !== undefined && (
          <div className="flex items-center gap-2 text-neutral-600">
            <UsersRound size={14} className="text-neutral-400" />
            <span><span className="font-bold text-neutral-800">{memberCount}</span> members</span>
          </div>
        )}
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-3">
        <div className="rounded border border-neutral-100 bg-neutral-50 p-3">
          <ClipboardCheck className="text-brand-700" size={16} />
          <p className="mt-2 text-xs font-bold uppercase text-neutral-500">Open assessments</p>
          <p className="text-xl font-bold text-neutral-900">{unit.open_assessment_count ?? 0}</p>
        </div>
        <div className="rounded border border-neutral-100 bg-neutral-50 p-3">
          <FlaskConical className="text-brand-700" size={16} />
          <p className="mt-2 text-xs font-bold uppercase text-neutral-500">Pending labs</p>
          <p className="text-xl font-bold text-neutral-900">{unit.pending_lab_test_count ?? 0}</p>
        </div>
        <div className="rounded border border-neutral-100 bg-neutral-50 p-3">
          <FolderCheck className="text-brand-700" size={16} />
          <p className="mt-2 text-xs font-bold uppercase text-neutral-500">Records ready</p>
          <p className="text-xl font-bold text-neutral-900">{unit.records_ready_count ?? 0}</p>
        </div>
      </div>
    </div>
  );
}
