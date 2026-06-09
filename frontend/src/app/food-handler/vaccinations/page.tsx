"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { AlertCircle, Syringe } from "lucide-react";

import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { listFoodHandlers } from "@/lib/api/identity";
import { listFoodHandlerVaccinations } from "@/lib/api/assessments";
import type { VaccinationRecord } from "@/types/assessments";

function dateLabel(value?: string) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium" }).format(new Date(value));
}

export default function Page() {
  const [rows, setRows] = useState<VaccinationRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const handlers = await listFoodHandlers();
      const handler = handlers[0];
      setRows(handler ? await listFoodHandlerVaccinations(handler.id) : []);
    } catch {
      setError("Could not load vaccination records.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const nextDue = useMemo(() => rows.find((row) => row.next_dose_date || row.reminder_date), [rows]);

  return (
    <PortalShell role="food_handler" title="Vaccinations" description="Review vaccination status, due dates, and compliance readiness.">
      <div className="grid gap-5">
        {loading ? <p className="rounded-lg border border-neutral-200 bg-white p-4 text-sm font-semibold text-neutral-600 shadow-sm">Loading vaccinations...</p> : null}
        {error ? <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700"><AlertCircle size={16} />{error}</div> : null}
        <section className="grid gap-3 md:grid-cols-3">
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><Syringe className="text-brand-700" size={18} /><p className="mt-2 text-xs font-bold uppercase text-neutral-500">Records</p><p className="text-2xl font-bold text-neutral-900">{rows.length}</p></div>
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><p className="text-xs font-bold uppercase text-neutral-500">Next due</p><p className="mt-2 text-sm font-bold text-neutral-900">{dateLabel(nextDue?.next_dose_date || nextDue?.reminder_date)}</p></div>
          <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm"><p className="text-xs font-bold uppercase text-neutral-500">Latest status</p><div className="mt-2"><StatusBadge status={rows[0]?.compliance_status || "due"} /></div></div>
        </section>
        <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
          <div className="divide-y divide-neutral-200">
            {rows.map((row) => (
              <div className="grid gap-3 p-4 md:grid-cols-[1fr_auto]" key={row.id}>
                <div>
                  <p className="font-bold capitalize text-neutral-900">{row.vaccine_name || row.vaccine_type.replaceAll("_", " ")}</p>
                  <p className="text-xs text-neutral-500">Dose {row.dose_number} · administered {dateLabel(row.date_administered)} · expires {dateLabel(row.expiry_date)}</p>
                  {row.next_dose_date || row.reminder_date ? <p className="mt-1 text-xs font-semibold text-warning-700">Next dose due {dateLabel(row.next_dose_date || row.reminder_date)}</p> : null}
                </div>
                <div className="flex items-center gap-2"><StatusBadge status={row.status} /><StatusBadge status={row.compliance_status || "due"} /></div>
              </div>
            ))}
            {!rows.length && !loading ? <p className="p-4 text-sm text-neutral-500">No vaccination records found.</p> : null}
          </div>
        </section>
      </div>
    </PortalShell>
  );
}
