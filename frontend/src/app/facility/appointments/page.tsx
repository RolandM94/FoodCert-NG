"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertCircle, CalendarDays, CheckCircle2, Clock3, RefreshCw, UserRoundCheck, XCircle } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import {
  assignFacilityAppointmentDoctor,
  cancelFacilityAppointment,
  confirmFacilityAppointment,
  listFacilityAppointments,
  noShowFacilityAppointment,
  rescheduleFacilityAppointment,
} from "@/lib/api/assessments";
import { getCurrentMedicalFacility, listFacilityStaff } from "@/lib/api/facilities";
import type { Appointment, AppointmentStatus } from "@/types/assessments";
import type { FacilityStaffProfile, MedicalFacility } from "@/types/facilities";

const STATUS_OPTIONS: Array<["all" | AppointmentStatus, string]> = [
  ["all", "All statuses"],
  ["pending", "Pending"],
  ["confirmed", "Confirmed"],
  ["rescheduled", "Rescheduled"],
  ["cancelled", "Cancelled"],
  ["completed", "Completed"],
  ["no_show", "No show"],
];

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

function label(value?: string) {
  return value ? value.replaceAll("_", " ") : "Not set";
}

export default function Page() {
  const [facility, setFacility] = useState<MedicalFacility | null>(null);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [staff, setStaff] = useState<FacilityStaffProfile[]>([]);
  const [status, setStatus] = useState<"all" | AppointmentStatus>("all");
  const [doctor, setDoctor] = useState("all");
  const [view, setView] = useState<"table" | "calendar">("table");
  const [busyId, setBusyId] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [rescheduleId, setRescheduleId] = useState("");
  const [rescheduleDate, setRescheduleDate] = useState("");

  async function loadData() {
    setLoading(true);
    setError("");
    try {
      const profile = await getCurrentMedicalFacility();
      const [appointmentRows, staffRows] = await Promise.all([
        listFacilityAppointments(profile.id),
        listFacilityStaff(profile.id),
      ]);
      setFacility(profile);
      setAppointments(appointmentRows);
      setStaff(staffRows.filter((row) => row.is_active && row.staff_type === "doctor"));
    } catch {
      setError("Could not load facility appointments.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  const filtered = useMemo(() => {
    return appointments.filter((appointment) => {
      const statusMatch = status === "all" || appointment.status === status;
      const doctorMatch = doctor === "all" || appointment.doctor === doctor;
      return statusMatch && doctorMatch;
    });
  }, [appointments, doctor, status]);

  const groupedByDay = useMemo(() => {
    return filtered.reduce<Record<string, Appointment[]>>((groups, appointment) => {
      const key = new Intl.DateTimeFormat("en-NG", { dateStyle: "medium" }).format(new Date(appointment.appointment_date));
      groups[key] = [...(groups[key] || []), appointment];
      return groups;
    }, {});
  }, [filtered]);

  function replaceAppointment(updated: Appointment) {
    setAppointments((rows) => rows.map((row) => row.id === updated.id ? updated : row));
  }

  async function runAction(appointment: Appointment, action: "confirm" | "cancel" | "no_show") {
    if (!facility) return;
    setBusyId(appointment.id);
    setError("");
    setSuccess("");
    try {
      const updated = action === "confirm"
        ? await confirmFacilityAppointment(facility.id, appointment.id)
        : action === "cancel"
          ? await cancelFacilityAppointment(facility.id, appointment.id, { reason: "Cancelled by facility." })
          : await noShowFacilityAppointment(facility.id, appointment.id, { notes: "Food handler did not attend." });
      replaceAppointment(updated);
      setSuccess(`Appointment ${label(updated.status)}.`);
    } catch {
      setError("Could not update appointment. Check payment, accreditation, and facility permissions.");
    } finally {
      setBusyId("");
    }
  }

  async function assignDoctor(appointment: Appointment, doctorId: string) {
    if (!facility || !doctorId) return;
    setBusyId(appointment.id);
    setError("");
    setSuccess("");
    try {
      const updated = await assignFacilityAppointmentDoctor(facility.id, appointment.id, doctorId);
      replaceAppointment(updated);
      setSuccess("Doctor assigned.");
    } catch {
      setError("Could not assign doctor.");
    } finally {
      setBusyId("");
    }
  }

  async function submitReschedule(appointment: Appointment) {
    if (!facility || !rescheduleDate) return;
    setBusyId(appointment.id);
    setError("");
    setSuccess("");
    try {
      const updated = await rescheduleFacilityAppointment(facility.id, appointment.id, {
        appointment_date: new Date(rescheduleDate).toISOString(),
        reason: "Rescheduled by facility.",
      });
      replaceAppointment(updated);
      setRescheduleId("");
      setRescheduleDate("");
      setSuccess("Appointment rescheduled.");
    } catch {
      setError("Could not reschedule appointment.");
    } finally {
      setBusyId("");
    }
  }

  return (
    <PortalShell role="facility_admin" title="Appointments" description="Manage bookings, payment-gated confirmations, doctor assignment, reschedules, cancellations, and no-shows.">
      <div className="grid gap-5">
        {loading ? <p className="rounded-lg border border-neutral-200 bg-white p-4 text-sm font-semibold text-neutral-600 shadow-sm">Loading appointments...</p> : null}

        <section className="grid gap-3 md:grid-cols-4">
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <CalendarDays className="text-brand-700" size={18} />
            <p className="mt-2 text-xs font-bold uppercase text-neutral-500">Appointments</p>
            <p className="text-2xl font-bold text-neutral-900">{appointments.length}</p>
          </div>
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <Clock3 className="text-brand-700" size={18} />
            <p className="mt-2 text-xs font-bold uppercase text-neutral-500">Pending</p>
            <p className="text-2xl font-bold text-neutral-900">{appointments.filter((row) => row.status === "pending").length}</p>
          </div>
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <CheckCircle2 className="text-brand-700" size={18} />
            <p className="mt-2 text-xs font-bold uppercase text-neutral-500">Confirmed</p>
            <p className="text-2xl font-bold text-neutral-900">{appointments.filter((row) => row.status === "confirmed").length}</p>
          </div>
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
            <UserRoundCheck className="text-brand-700" size={18} />
            <p className="mt-2 text-xs font-bold uppercase text-neutral-500">Assigned</p>
            <p className="text-2xl font-bold text-neutral-900">{appointments.filter((row) => row.doctor).length}</p>
          </div>
        </section>

        <section className="flex flex-wrap items-center gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={status} onChange={(event) => setStatus(event.target.value as "all" | AppointmentStatus)}>
            {STATUS_OPTIONS.map(([value, text]) => <option key={value} value={value}>{text}</option>)}
          </select>
          <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={doctor} onChange={(event) => setDoctor(event.target.value)}>
            <option value="all">All doctors</option>
            {staff.map((profile) => <option key={profile.user} value={profile.user}>{profile.user_name || profile.user_email}</option>)}
          </select>
          <div className="inline-flex h-10 overflow-hidden rounded border border-neutral-200">
            <button className={`px-3 text-sm font-bold ${view === "table" ? "bg-brand-700 text-white" : "bg-white text-neutral-700"}`} type="button" onClick={() => setView("table")}>Table</button>
            <button className={`px-3 text-sm font-bold ${view === "calendar" ? "bg-brand-700 text-white" : "bg-white text-neutral-700"}`} type="button" onClick={() => setView("calendar")}>Calendar</button>
          </div>
          <button className="inline-flex h-10 items-center gap-2 rounded border border-neutral-200 px-3 text-sm font-bold text-neutral-700" type="button" onClick={() => void loadData()}>
            <RefreshCw size={16} /> Refresh
          </button>
        </section>

        {view === "calendar" ? (
          <section className="grid gap-3">
            {Object.entries(groupedByDay).map(([day, rows]) => (
              <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm" key={day}>
                <h2 className="text-sm font-bold text-neutral-900">{day}</h2>
                <div className="mt-3 grid gap-2">
                  {rows.map((appointment) => (
                    <div className="flex flex-wrap items-center justify-between gap-2 rounded border border-neutral-100 bg-neutral-50 p-3" key={appointment.id}>
                      <div><p className="font-bold text-neutral-900">{appointment.food_handler_name}</p><p className="text-xs text-neutral-500">{formatDate(appointment.appointment_date)} · {appointment.doctor_name || "Unassigned"}</p></div>
                      <StatusBadge status={appointment.status} />
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </section>
        ) : (
          <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
            <div className="border-b border-neutral-200 p-4">
              <h2 className="text-sm font-bold text-neutral-900">Appointment Register</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-neutral-50 text-xs font-bold uppercase text-neutral-500">
                  <tr><th className="p-3">Food handler</th><th className="p-3">Date</th><th className="p-3">Payment</th><th className="p-3">Doctor</th><th className="p-3">Status</th><th className="p-3">Actions</th></tr>
                </thead>
                <tbody className="divide-y divide-neutral-200">
                  {filtered.length ? filtered.map((appointment) => (
                    <tr key={appointment.id}>
                      <td className="p-3"><p className="font-bold text-neutral-900">{appointment.food_handler_name}</p><p className="text-xs text-neutral-500">{appointment.employer_name || "Individual"}</p></td>
                      <td className="p-3">{formatDate(appointment.appointment_date)}</td>
                      <td className="p-3 capitalize"><StatusBadge status={appointment.payment_status || "missing"} /></td>
                      <td className="p-3">
                        <select className="h-9 rounded border border-neutral-200 bg-white px-2 text-xs" disabled={busyId === appointment.id} value={appointment.doctor || ""} onChange={(event) => void assignDoctor(appointment, event.target.value)}>
                          <option value="">Unassigned</option>
                          {staff.map((profile) => <option key={profile.user} value={profile.user}>{profile.user_name || profile.user_email}</option>)}
                        </select>
                      </td>
                      <td className="p-3"><StatusBadge status={appointment.status} /></td>
                      <td className="min-w-[340px] p-3">
                        <div className="flex flex-wrap gap-2">
                          <button className="inline-flex h-8 items-center gap-1 rounded border border-neutral-200 px-2 text-xs font-bold text-neutral-700 disabled:opacity-60" disabled={busyId === appointment.id} type="button" onClick={() => void runAction(appointment, "confirm")}><CheckCircle2 size={14} /> Confirm</button>
                          <button className="inline-flex h-8 items-center gap-1 rounded border border-neutral-200 px-2 text-xs font-bold text-neutral-700 disabled:opacity-60" disabled={busyId === appointment.id} type="button" onClick={() => setRescheduleId(rescheduleId === appointment.id ? "" : appointment.id)}><CalendarDays size={14} /> Reschedule</button>
                          <button className="inline-flex h-8 items-center gap-1 rounded border border-neutral-200 px-2 text-xs font-bold text-neutral-700 disabled:opacity-60" disabled={busyId === appointment.id} type="button" onClick={() => void runAction(appointment, "no_show")}><Clock3 size={14} /> No-show</button>
                          <button className="inline-flex h-8 items-center gap-1 rounded border border-danger-100 px-2 text-xs font-bold text-danger-700 disabled:opacity-60" disabled={busyId === appointment.id} type="button" onClick={() => void runAction(appointment, "cancel")}><XCircle size={14} /> Cancel</button>
                        </div>
                        {rescheduleId === appointment.id ? (
                          <div className="mt-2 flex flex-wrap gap-2">
                            <input className="h-9 rounded border border-neutral-200 bg-neutral-50 px-2 text-xs" type="datetime-local" value={rescheduleDate} onChange={(event) => setRescheduleDate(event.target.value)} />
                            <button className="h-9 rounded bg-brand-600 px-3 text-xs font-bold text-white disabled:opacity-60" disabled={busyId === appointment.id || !rescheduleDate} type="button" onClick={() => void submitReschedule(appointment)}>Save</button>
                          </div>
                        ) : null}
                      </td>
                    </tr>
                  )) : (
                    <tr><td className="p-3 text-neutral-500" colSpan={6}>No appointments match the current filters.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {error ? <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700"><AlertCircle size={16} />{error}</div> : null}
        {success ? <div className="rounded-lg bg-brand-50 p-3 text-sm font-semibold text-brand-800">{success}</div> : null}
      </div>
    </PortalShell>
  );
}
