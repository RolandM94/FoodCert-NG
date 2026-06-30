"use client";

import { Suspense, useEffect, useState } from "react";
import type { ReactNode } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Bell, IdCard, Landmark, LockKeyhole, Settings, ShieldCheck } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { CertificateTemplateEditor } from "@/components/certificates/certificate-template-editor";
import { DataTable } from "@/components/ui/data-table";
import {
  fetchFederalAccountAuditLogs,
  fetchFederalPolicy,
  fetchFederalProfile,
  fetchFederalStateOverrides,
  updateFederalPolicy,
  updateFederalProfile,
  type FederalAuditLogItem,
  type FederalProfile,
  type FederalStateOverrideItem,
} from "@/lib/api/federal";
import { getApiErrorMessage } from "@/lib/api/client";

type TabKey = "federal-profile" | "national-policy" | "certificate-templates" | "security-access" | "audit-logs";

const TABS: { key: TabKey; label: string; icon: typeof Settings }[] = [
  { key: "federal-profile", label: "Federal Profile", icon: IdCard },
  { key: "national-policy", label: "National Policy", icon: Landmark },
  { key: "certificate-templates", label: "Certificate Templates", icon: ShieldCheck },
  { key: "security-access", label: "Security & Access", icon: LockKeyhole },
  { key: "audit-logs", label: "Audit Logs", icon: Bell },
];

function SettingCard({ title, description, children }: { title: string; description?: string; children: ReactNode }) {
  return (
    <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
      <h2 className="text-base font-bold text-neutral-900">{title}</h2>
      {description ? <p className="mt-1 text-sm leading-6 text-neutral-500">{description}</p> : null}
      <div className="mt-5">{children}</div>
    </section>
  );
}

function NumberField({ label, value, onChange }: { label: string; value: number; onChange: (value: number) => void }) {
  return (
    <label className="grid gap-1 text-sm font-semibold text-neutral-700">
      {label}
      <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3 text-sm" min={0} type="number" value={value} onChange={(event) => onChange(Number(event.target.value))} />
    </label>
  );
}

function ToggleRow({ label, checked, onChange }: { label: string; checked: boolean; onChange: (value: boolean) => void }) {
  return (
    <label className="flex items-center justify-between gap-4 rounded-lg border border-neutral-100 bg-neutral-50 px-4 py-3 text-sm font-semibold text-neutral-700">
      {label}
      <input checked={checked} className="h-4 w-4 accent-brand-600" onChange={(event) => onChange(event.target.checked)} type="checkbox" />
    </label>
  );
}

function TextField({ label, value, onChange, placeholder }: { label: string; value: string; onChange: (value: string) => void; placeholder?: string }) {
  return (
    <label className="grid gap-1 text-sm font-semibold text-neutral-700">
      {label}
      <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3 text-sm" value={value} placeholder={placeholder} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

const EMPTY_PROFILE: Partial<FederalProfile> = {
  ministry_name: "",
  department_name: "",
  programme_name: "",
  national_coordinator: "",
  official_email: "",
  official_phone: "",
  logo_url: "",
  active_guideline_version: "",
  reporting_cycle: "quarterly",
  central_portal_status: "active",
};

function FederalProfilePanel() {
  const queryClient = useQueryClient();
  const profileQuery = useQuery({ queryKey: ["federal-profile"], queryFn: fetchFederalProfile });
  const [form, setForm] = useState<Partial<FederalProfile>>(EMPTY_PROFILE);

  useEffect(() => {
    if (profileQuery.data) setForm(profileQuery.data);
  }, [profileQuery.data]);

  const updateMutation = useMutation({
    mutationFn: () => updateFederalProfile(form),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["federal-profile"] }),
  });

  const set = (key: keyof FederalProfile) => (value: string) => setForm((prev) => ({ ...prev, [key]: value }));

  return (
    <div className="grid gap-5">
      {updateMutation.isError ? <p className="rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{getApiErrorMessage(updateMutation.error, "Could not save federal profile.")}</p> : null}
      <div className="grid gap-5 lg:grid-cols-2">
        <SettingCard title="Federal Profile" description="Official federal identity used across national certificates, reports, receipts, public verification, and oversight notices.">
          <div className="grid gap-4">
            <TextField label="Ministry Name" value={form.ministry_name ?? ""} onChange={set("ministry_name")} placeholder="Federal Ministry of Health and Social Welfare" />
            <TextField label="Department" value={form.department_name ?? ""} onChange={set("department_name")} placeholder="Food and Drug Services" />
            <TextField label="Programme Name" value={form.programme_name ?? ""} onChange={set("programme_name")} placeholder="National Food Handlers Medical Test Programme" />
            <TextField label="National Coordinator" value={form.national_coordinator ?? ""} onChange={set("national_coordinator")} placeholder="Programme lead" />
            <TextField label="Official Email" value={form.official_email ?? ""} onChange={set("official_email")} placeholder="support@health.gov.ng" />
            <TextField label="Official Phone" value={form.official_phone ?? ""} onChange={set("official_phone")} placeholder="+234..." />
          </div>
        </SettingCard>
        <SettingCard title="Programme & Portal" description="Guideline version, branding, reporting cadence, and central portal status.">
          <div className="grid gap-4">
            <TextField label="Logo / Seal URL" value={form.logo_url ?? ""} onChange={set("logo_url")} placeholder="https://..." />
            <TextField label="Active Guideline Version" value={form.active_guideline_version ?? ""} onChange={set("active_guideline_version")} placeholder="National Guidelines for Food Handlers' Medical Test 2024" />
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Reporting Cycle
              <select className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm" value={form.reporting_cycle ?? "quarterly"} onChange={(event) => set("reporting_cycle")(event.target.value)}>
                <option value="monthly">Monthly</option>
                <option value="quarterly">Quarterly</option>
                <option value="annual">Annual</option>
              </select>
            </label>
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Central Portal Status
              <select className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm" value={form.central_portal_status ?? "active"} onChange={(event) => set("central_portal_status")(event.target.value)}>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </label>
          </div>
        </SettingCard>
      </div>
      <div>
        <button className="h-11 rounded-lg bg-brand-600 px-5 text-sm font-bold text-white hover:bg-brand-700 disabled:bg-neutral-300" disabled={updateMutation.isPending || profileQuery.isLoading} onClick={() => updateMutation.mutate()} type="button">
          {updateMutation.isPending ? "Saving..." : "Save federal profile"}
        </button>
      </div>
    </div>
  );
}

function NationalPolicyPanel() {
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
  const [stateTemplateOverrides, setStateTemplateOverrides] = useState(true);

  useEffect(() => {
    if (!policyQuery.data) return;
    setCertificateValidityMonths(policyQuery.data.certificate_validity_months);
    setTyphoidValidityYears(policyQuery.data.typhoid_validity_years);
    setHepatitisSecondDoseMonths(policyQuery.data.hepatitis_a_second_dose_months);
    setNinRequired(policyQuery.data.nin_required);
    setPaymentBeforeAssessment(policyQuery.data.payment_before_assessment_required);
    setStateValidationRequired(policyQuery.data.state_validation_before_certificate_required);
    setQrVerification(policyQuery.data.public_qr_verification_enabled);
    setStateTemplateOverrides(policyQuery.data.state_certificate_template_overrides_enabled);
  }, [policyQuery.data]);

  const updateMutation = useMutation({
    mutationFn: () => updateFederalPolicy({
      certificate_validity_months: certificateValidityMonths,
      typhoid_validity_years: typhoidValidityYears,
      hepatitis_a_second_dose_months: hepatitisSecondDoseMonths,
      nin_required: ninRequired,
      payment_before_assessment_required: paymentBeforeAssessment,
      state_validation_before_certificate_required: stateValidationRequired,
      public_qr_verification_enabled: qrVerification,
      state_certificate_template_overrides_enabled: stateTemplateOverrides,
    }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["federal-policy"] }),
  });

  return (
    <div className="grid gap-6">
      <SettingCard title="National Policy Defaults" description="Configure national certificate, assessment, verification, payment, and state override rules.">
        {updateMutation.isError ? <p className="mb-4 rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{getApiErrorMessage(updateMutation.error, "Could not save national policy.")}</p> : null}
        <div className="grid gap-4 md:grid-cols-3">
          <NumberField label="Certificate validity months" value={certificateValidityMonths} onChange={setCertificateValidityMonths} />
          <NumberField label="Typhoid validity years" value={typhoidValidityYears} onChange={setTyphoidValidityYears} />
          <NumberField label="Hep A second dose months" value={hepatitisSecondDoseMonths} onChange={setHepatitisSecondDoseMonths} />
        </div>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          <ToggleRow label="NIN required" checked={ninRequired} onChange={setNinRequired} />
          <ToggleRow label="Payment before assessment" checked={paymentBeforeAssessment} onChange={setPaymentBeforeAssessment} />
          <ToggleRow label="State validation before certificate" checked={stateValidationRequired} onChange={setStateValidationRequired} />
          <ToggleRow label="Public QR verification" checked={qrVerification} onChange={setQrVerification} />
          <ToggleRow label="State certificate template overrides" checked={stateTemplateOverrides} onChange={setStateTemplateOverrides} />
        </div>
        <button className="mt-4 h-11 rounded-lg bg-brand-600 px-5 text-sm font-bold text-white hover:bg-brand-700 disabled:bg-neutral-300" disabled={updateMutation.isPending} onClick={() => updateMutation.mutate()} type="button">
          {updateMutation.isPending ? "Saving..." : "Save national policy"}
        </button>
      </SettingCard>
      <SettingCard title="State Override Monitoring">
        <DataTable<FederalStateOverrideItem>
          columns={[
            { key: "state", header: "State", render: (row) => <span className="font-bold text-neutral-900">{row.state_name}</span> },
            { key: "validation", header: "State validation", render: (row) => row.requires_state_certificate_validation ? "Enabled" : "Disabled" },
            { key: "cert", header: "Certificate months", render: (row) => row.certificate_validity_months },
            { key: "reminders", header: "Reminders", render: (row) => row.auto_renewal_reminder_days.join(", ") || "Not set" },
          ]}
          rows={overridesQuery.data || []}
          empty={overridesQuery.isLoading ? "Loading state overrides..." : "No state overrides configured yet."}
        />
      </SettingCard>
    </div>
  );
}

function SecurityAccessPanel() {
  return (
    <div className="grid gap-5 lg:grid-cols-2">
      <SettingCard title="Security & Access" description="Federal account-level security controls. User and role assignment remains in Stakeholder Management.">
        <div className="grid gap-3">
          <ToggleRow label="Require MFA for federal admins" checked onChange={() => undefined} />
          <ToggleRow label="Require MFA for policy approvers" checked onChange={() => undefined} />
          <ToggleRow label="Audit all federal exports" checked onChange={() => undefined} />
          <ToggleRow label="Restrict medical data exports" checked onChange={() => undefined} />
        </div>
      </SettingCard>
      <SettingCard title="Access Review">
        <div className="grid gap-4">
          <NumberField label="Access review frequency days" value={90} onChange={() => undefined} />
          <NumberField label="Session timeout minutes" value={480} onChange={() => undefined} />
          <NumberField label="Failed login lockout threshold" value={5} onChange={() => undefined} />
        </div>
      </SettingCard>
    </div>
  );
}

function AuditLogsPanel() {
  const [filters, setFilters] = useState({ search: "", action: "" });
  const logsQuery = useQuery({
    queryKey: ["federal-account-settings", "audit", filters],
    queryFn: () => fetchFederalAccountAuditLogs(Object.fromEntries(Object.entries(filters).filter(([, value]) => value))),
  });
  return (
    <SettingCard title="Federal Audit Logs" description="Organization-scoped audit activity for this Federal Ministry account, including settings, security, certificate, payment, and workflow events.">
      <div className="mb-4 grid gap-3 md:grid-cols-[1fr_220px]">
        <label className="grid gap-1 text-sm font-semibold text-neutral-700">Search<input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3 text-sm" value={filters.search} onChange={(event) => setFilters((prev) => ({ ...prev, search: event.target.value }))} /></label>
        <label className="grid gap-1 text-sm font-semibold text-neutral-700">Action<select className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm" value={filters.action} onChange={(event) => setFilters((prev) => ({ ...prev, action: event.target.value }))}><option value="">All actions</option><option value="update">Update</option><option value="security_event">Security event</option><option value="certificate_event">Certificate event</option><option value="payment_event">Payment event</option></select></label>
      </div>
      <DataTable<FederalAuditLogItem>
        columns={[
          { key: "created", header: "Date", render: (row) => new Date(row.created_at).toLocaleString() },
          { key: "actor", header: "Actor", render: (row) => row.actor_name || row.actor_email || "System" },
          { key: "action", header: "Action", render: (row) => row.action.replaceAll("_", " ") },
          { key: "target", header: "Target", render: (row) => row.target_type || "-" },
          { key: "state", header: "State", render: (row) => row.state_name || "National" },
          { key: "risk", header: "Risk", render: (row) => row.risk_level },
        ]}
        rows={logsQuery.data || []}
        empty={logsQuery.isLoading ? "Loading audit logs..." : "No audit logs match these filters."}
      />
    </SettingCard>
  );
}

function FederalAccountSettingsPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const tabParam = searchParams.get("tab") as TabKey | null;
  const activeTab = TABS.some((tab) => tab.key === tabParam) ? tabParam! : "federal-profile";

  return (
    <PortalShell role="federal_admin" title="Account Settings" description="Configure federal identity, national policy, templates, security controls, and audit visibility.">
      <nav className="mb-6 flex gap-0 overflow-x-auto border-b border-neutral-200">
        {TABS.map(({ key, label, icon: Icon }) => (
          <button
            className={`flex shrink-0 items-center gap-2 border-b-2 px-4 py-3 text-sm font-medium ${activeTab === key ? "border-brand-600 text-brand-700" : "border-transparent text-neutral-500 hover:text-neutral-800"}`}
            key={key}
            onClick={() => router.replace(`/federal/account-settings?tab=${key}`)}
            type="button"
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </nav>
      {activeTab === "federal-profile" ? <FederalProfilePanel /> : null}
      {activeTab === "national-policy" ? <NationalPolicyPanel /> : null}
      {activeTab === "certificate-templates" ? <CertificateTemplateEditor scope="national" /> : null}
      {activeTab === "security-access" ? <SecurityAccessPanel /> : null}
      {activeTab === "audit-logs" ? <AuditLogsPanel /> : null}
    </PortalShell>
  );
}

export default function FederalAccountSettingsPage() {
  return (
    <Suspense fallback={null}>
      <FederalAccountSettingsPageContent />
    </Suspense>
  );
}
