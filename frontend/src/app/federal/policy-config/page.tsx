"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Save, Settings2 } from "lucide-react";
import { useEffect, useState } from "react";
import { PortalShell } from "@/components/layout/portal-shell";
import { DataTable, StatusCell } from "@/components/ui/data-table";
import {
  fetchFederalPolicy,
  fetchFederalStateOverrides,
  updateFederalPolicy,
  type FederalStateOverrideItem,
} from "@/lib/api/federal";

export default function Page() {
  const queryClient = useQueryClient();
  const policyQuery = useQuery({ queryKey: ["federal-policy"], queryFn: fetchFederalPolicy });
  const overridesQuery = useQuery({ queryKey: ["federal-state-overrides"], queryFn: fetchFederalStateOverrides });
  const [certificateValidityMonths, setCertificateValidityMonths] = useState(12);
  const [typhoidValidityYears, setTyphoidValidityYears] = useState(3);
  const [hepatitisSecondDoseMonths, setHepatitisSecondDoseMonths] = useState(6);
  const [ninRequired, setNinRequired] = useState(true);
  const [paymentBeforeAssessment, setPaymentBeforeAssessment] = useState(true);
  const [stateValidationRequired, setStateValidationRequired] = useState(true);
  const [qrVerification, setQrVerification] = useState(true);

  useEffect(() => {
    if (!policyQuery.data) return;
    setCertificateValidityMonths(policyQuery.data.certificate_validity_months);
    setTyphoidValidityYears(policyQuery.data.typhoid_validity_years);
    setHepatitisSecondDoseMonths(policyQuery.data.hepatitis_a_second_dose_months);
    setNinRequired(policyQuery.data.nin_required);
    setPaymentBeforeAssessment(policyQuery.data.payment_before_assessment_required);
    setStateValidationRequired(policyQuery.data.state_validation_before_certificate_required);
    setQrVerification(policyQuery.data.public_qr_verification_enabled);
  }, [policyQuery.data]);

  const updateMutation = useMutation({
    mutationFn: () =>
      updateFederalPolicy({
        certificate_validity_months: certificateValidityMonths,
        typhoid_validity_years: typhoidValidityYears,
        hepatitis_a_second_dose_months: hepatitisSecondDoseMonths,
        nin_required: ninRequired,
        payment_before_assessment_required: paymentBeforeAssessment,
        state_validation_before_certificate_required: stateValidationRequired,
        public_qr_verification_enabled: qrVerification,
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["federal-policy"] }),
  });

  return (
    <PortalShell role="federal_admin" title="Policy configuration" description="Configure national policy defaults and monitor state-specific overrides.">
      <div className="grid gap-5">
        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex items-center gap-2"><Settings2 className="text-brand-deep" size={18} /><h2 className="text-base font-bold text-slate-950">National Policy Defaults</h2></div>
          <div className="grid gap-4 md:grid-cols-3">
            <label className="grid gap-1 text-sm font-semibold text-slate-700">Certificate validity months<input className="h-10 rounded border border-slate-200 bg-slate-50 px-3" type="number" value={certificateValidityMonths} onChange={(event) => setCertificateValidityMonths(Number(event.target.value))} /></label>
            <label className="grid gap-1 text-sm font-semibold text-slate-700">Typhoid validity years<input className="h-10 rounded border border-slate-200 bg-slate-50 px-3" type="number" value={typhoidValidityYears} onChange={(event) => setTyphoidValidityYears(Number(event.target.value))} /></label>
            <label className="grid gap-1 text-sm font-semibold text-slate-700">Hep A second dose months<input className="h-10 rounded border border-slate-200 bg-slate-50 px-3" type="number" value={hepatitisSecondDoseMonths} onChange={(event) => setHepatitisSecondDoseMonths(Number(event.target.value))} /></label>
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {[
              ["NIN required", ninRequired, setNinRequired],
              ["Payment before assessment", paymentBeforeAssessment, setPaymentBeforeAssessment],
              ["State validation before certificate", stateValidationRequired, setStateValidationRequired],
              ["Public QR verification", qrVerification, setQrVerification],
            ].map(([label, checked, setChecked]) => (
              <label key={label as string} className="flex items-center justify-between rounded border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-semibold text-slate-700">
                {label as string}
                <input checked={checked as boolean} onChange={(event) => (setChecked as (value: boolean) => void)(event.target.checked)} type="checkbox" />
              </label>
            ))}
          </div>
          <button className="mt-4 inline-flex h-10 items-center gap-2 rounded bg-brand-deep px-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-300" disabled={updateMutation.isPending} onClick={() => updateMutation.mutate()} type="button">
            <Save size={16} />
            {updateMutation.isPending ? "Saving..." : "Save policy"}
          </button>
        </section>

        <section className="grid gap-3">
          <h2 className="text-base font-bold text-slate-950">State Override Monitoring</h2>
          <DataTable<FederalStateOverrideItem>
            columns={[
              { key: "state", header: "State", render: (row) => <span className="font-bold text-slate-950">{row.state_name}</span> },
              { key: "validation", header: "State validation", render: (row) => <StatusCell status={row.requires_state_certificate_validation ? "enabled" : "disabled"} /> },
              { key: "cert", header: "Certificate months", render: (row) => row.certificate_validity_months },
              { key: "typhoid", header: "Typhoid years", render: (row) => row.typhoid_validity_years },
              { key: "hep", header: "Hep A dose months", render: (row) => row.hepatitis_a_second_dose_months },
              { key: "reminders", header: "Reminders", render: (row) => row.auto_renewal_reminder_days.join(", ") || "Not set" },
            ]}
            rows={overridesQuery.data || []}
            empty={overridesQuery.isLoading ? "Loading state overrides..." : "No state overrides configured yet."}
          />
        </section>
      </div>
    </PortalShell>
  );
}
