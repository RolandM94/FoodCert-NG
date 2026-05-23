"use client";

import { Save } from "lucide-react";

import { StatusBadge } from "@/components/status/status-badge";
import type { VaccinationRecord } from "@/types/assessments";

export type VaccinationReviewValue = {
  vaccine_type: string;
  action: string;
  status: string;
  vaccine_name: string;
  brand_name: string;
  batch_number: string;
  vaccinator_name: string;
  vaccination_facility_name: string;
  vaccination_facility_address: string;
  dose_number: string;
  date_administered: string;
  expiry_date: string;
  reminder_date: string;
  notes: string;
};

export function VaccinationReviewPanel({
  records,
  value,
  busy,
  onChange,
  onSubmit,
}: {
  records?: VaccinationRecord[];
  value: VaccinationReviewValue;
  busy?: boolean;
  onChange: (next: VaccinationReviewValue) => void;
  onSubmit: () => void;
}) {
  function update(patch: Partial<VaccinationReviewValue>) {
    onChange({ ...value, ...patch });
  }

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <div className="grid gap-2">
        {records?.length ? records.map((record) => (
          <div className="rounded border border-slate-200 bg-slate-50 p-3" key={record.id}>
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="font-bold capitalize text-slate-950">{record.vaccine_name || record.vaccine_type.replaceAll("_", " ")}</p>
              <StatusBadge status={record.status} />
            </div>
            <p className="mt-1 text-xs text-slate-500">Dose {record.dose_number} · administered {record.date_administered || "not set"} · expires {record.expiry_date || "not set"}</p>
            {record.brand_name || record.batch_number ? <p className="text-xs text-slate-500">{record.brand_name || "Brand not set"} · {record.batch_number || "No batch"}</p> : null}
            {record.next_dose_date || record.reminder_date ? <p className="text-xs font-semibold text-amber-700">Next dose due {record.next_dose_date || record.reminder_date}</p> : null}
            <p className="mt-1 text-xs font-semibold text-slate-600">Compliance: {record.compliance_status?.replaceAll("_", " ") || "due"}</p>
          </div>
        )) : <p className="text-sm text-slate-500">No vaccination records yet.</p>}
      </div>
      <div className="grid gap-3">
        <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={value.vaccine_type} onChange={(event) => update({ vaccine_type: event.target.value })}>
          <option value="typhoid">Typhoid</option>
          <option value="hepatitis_a">Hepatitis A</option>
          <option value="other">Other</option>
        </select>
        <select className="h-10 rounded border border-slate-200 bg-white px-3 text-sm" value={value.action} onChange={(event) => update({ action: event.target.value })}>
          <option value="mark_valid">Mark valid</option>
          <option value="mark_missing">Mark missing</option>
          <option value="mark_expired">Mark expired</option>
          <option value="mark_incomplete">Mark incomplete</option>
          <option value="prescribe">Prescribe</option>
          <option value="administer">Administer</option>
        </select>
        <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" placeholder="Vaccine name" value={value.vaccine_name} onChange={(event) => update({ vaccine_name: event.target.value })} />
        <div className="grid gap-2 md:grid-cols-2">
          <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" placeholder="Brand" value={value.brand_name} onChange={(event) => update({ brand_name: event.target.value })} />
          <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" placeholder="Batch number" value={value.batch_number} onChange={(event) => update({ batch_number: event.target.value })} />
        </div>
        <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" placeholder="Vaccinator name" value={value.vaccinator_name} onChange={(event) => update({ vaccinator_name: event.target.value })} />
        <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" placeholder="Vaccination facility" value={value.vaccination_facility_name} onChange={(event) => update({ vaccination_facility_name: event.target.value })} />
        <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" placeholder="Facility address" value={value.vaccination_facility_address} onChange={(event) => update({ vaccination_facility_address: event.target.value })} />
        <input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm" min={1} type="number" value={value.dose_number} onChange={(event) => update({ dose_number: event.target.value })} />
        <div className="grid gap-2 md:grid-cols-3">
          <label className="grid gap-1 text-xs font-bold uppercase text-slate-500">Administered<input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm normal-case text-slate-700" type="date" value={value.date_administered} onChange={(event) => update({ date_administered: event.target.value })} /></label>
          <label className="grid gap-1 text-xs font-bold uppercase text-slate-500">Expiry<input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm normal-case text-slate-700" type="date" value={value.expiry_date} onChange={(event) => update({ expiry_date: event.target.value })} /></label>
          <label className="grid gap-1 text-xs font-bold uppercase text-slate-500">Next dose<input className="h-10 rounded border border-slate-200 bg-slate-50 px-3 text-sm normal-case text-slate-700" type="date" value={value.reminder_date} onChange={(event) => update({ reminder_date: event.target.value })} /></label>
        </div>
        <textarea className="min-h-20 rounded border border-slate-200 bg-slate-50 p-3 text-sm" placeholder="Vaccination notes" value={value.notes} onChange={(event) => update({ notes: event.target.value })} />
        <button className="inline-flex h-10 w-fit items-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white disabled:opacity-60" disabled={busy} type="button" onClick={onSubmit}><Save size={16} /> Save vaccination review</button>
      </div>
    </div>
  );
}
