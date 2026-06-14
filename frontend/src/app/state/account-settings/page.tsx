"use client";

import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Bell, Building2, ClipboardCheck, IdCard, Landmark, Pencil, ReceiptText, Settings, ShieldCheck } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { CertificateTemplateEditor } from "@/components/certificates/certificate-template-editor";
import { StateFeesSettingsPanel } from "@/app/state/fees/page";
import { FormBuilderContent } from "@/features/organizations/forms-tool-layout";
import { fetchFormTemplates, type FormTemplate } from "@/lib/api/forms";
import {
  fetchInspectionSettings,
  fetchStateAuditLogs,
  fetchStateMedicalFacilitySettings,
  fetchStateNotificationSettings,
  fetchStateProfileSettings,
  fetchStateSecurityAccessSettings,
  updateInspectionSettings,
  updateStateMedicalFacilitySettings,
  updateStateNotificationSettings,
  updateStateProfileSettings,
  updateStateSecurityAccessSettings,
  type InspectionSettingsPolicy,
  type MedicalFacilityAccreditationSettings,
  type StateNotificationSettings,
  type StateProfileSettings,
  type StateSecurityAccessSettings,
} from "@/lib/api/state";
import { getApiErrorMessage } from "@/lib/api/client";

type TabKey =
  | "state-profile"
  | "fees-payments"
  | "certificate-settings"
  | "medical-facility-settings"
  | "inspection-settings"
  | "form-builder"
  | "notification-settings"
  | "security-access"
  | "audit-logs";

const TABS: { key: TabKey; label: string; icon: typeof Settings }[] = [
  { key: "state-profile", label: "State Profile", icon: IdCard },
  { key: "fees-payments", label: "Fees & Payments", icon: ReceiptText },
  { key: "certificate-settings", label: "Certificate Settings", icon: ShieldCheck },
  { key: "medical-facility-settings", label: "Medical Facility Settings", icon: Building2 },
  { key: "inspection-settings", label: "Inspection Settings", icon: ClipboardCheck },
  { key: "form-builder", label: "Form Builder", icon: Pencil },
  { key: "notification-settings", label: "Notification Settings", icon: Bell },
  { key: "security-access", label: "Security & Access", icon: ShieldCheck },
  { key: "audit-logs", label: "Audit Logs", icon: Landmark },
];

type PlaceholderTabKey = Exclude<TabKey, "fees-payments" | "certificate-settings" | "medical-facility-settings" | "form-builder" | "inspection-settings" | "state-profile" | "notification-settings" | "security-access" | "audit-logs">;

const PLACEHOLDERS: Record<PlaceholderTabKey, { title: string; description: string; items: string[] }> = {
};

type FacilitySettingsState = {
  accreditationTemplate: string;
  reaccreditationTemplate: string;
  validityDuration: number;
  validityUnit: "months" | "years" | "days";
  initialReviewSla: number;
  reviewDayType: "working_days" | "calendar_days";
  correctionWindow: number;
  correctionDayType: "working_days" | "calendar_days";
  renewalWindowDays: number;
  gracePeriodDays: number;
  reminderDaysBeforeExpiry: string;
  escalationDaysAfterSla: string;
  disableAssessmentsWhenExpired: boolean;
  disableAssessmentsWhenSuspended: boolean;
  allowRenewalAfterExpiry: boolean;
  allowSuspendedRenewal: boolean;
  autoExpireOnExpiryDate: boolean;
  requireStateApprovalToReactivate: boolean;
  requireReinspectionBeforeReactivation: boolean;
};

const defaultFacilitySettings: FacilitySettingsState = {
  accreditationTemplate: "",
  reaccreditationTemplate: "",
  validityDuration: 12,
  validityUnit: "months",
  initialReviewSla: 14,
  reviewDayType: "working_days",
  correctionWindow: 7,
  correctionDayType: "calendar_days",
  renewalWindowDays: 60,
  gracePeriodDays: 0,
  reminderDaysBeforeExpiry: "60, 30, 7",
  escalationDaysAfterSla: "3, 7",
  disableAssessmentsWhenExpired: true,
  disableAssessmentsWhenSuspended: true,
  allowRenewalAfterExpiry: true,
  allowSuspendedRenewal: false,
  autoExpireOnExpiryDate: true,
  requireStateApprovalToReactivate: true,
  requireReinspectionBeforeReactivation: false,
};

function templateLabel(template: FormTemplate) {
  return `${template.title} v${template.current_version}`;
}

function parseNumberList(value: string) {
  return value
    .split(",")
    .map((item) => Number(item.trim()))
    .filter((item) => Number.isInteger(item) && item >= 0);
}

function settingsFromApi(settings?: MedicalFacilityAccreditationSettings): FacilitySettingsState {
  if (!settings) return defaultFacilitySettings;
  return {
    accreditationTemplate: settings.accreditation_template ?? "",
    reaccreditationTemplate: settings.reaccreditation_template ?? "",
    validityDuration: settings.validity_duration ?? defaultFacilitySettings.validityDuration,
    validityUnit: settings.validity_unit ?? defaultFacilitySettings.validityUnit,
    initialReviewSla: settings.initial_review_sla ?? defaultFacilitySettings.initialReviewSla,
    reviewDayType: settings.review_day_type ?? defaultFacilitySettings.reviewDayType,
    correctionWindow: settings.correction_window ?? defaultFacilitySettings.correctionWindow,
    correctionDayType: settings.correction_day_type ?? defaultFacilitySettings.correctionDayType,
    renewalWindowDays: settings.renewal_window_days ?? defaultFacilitySettings.renewalWindowDays,
    gracePeriodDays: settings.grace_period_days ?? defaultFacilitySettings.gracePeriodDays,
    reminderDaysBeforeExpiry: (settings.reminder_days_before_expiry ?? [60, 30, 7]).join(", "),
    escalationDaysAfterSla: (settings.escalation_days_after_sla ?? [3, 7]).join(", "),
    disableAssessmentsWhenExpired: settings.disable_assessments_when_expired ?? true,
    disableAssessmentsWhenSuspended: settings.disable_assessments_when_suspended ?? true,
    allowRenewalAfterExpiry: settings.allow_renewal_after_expiry ?? true,
    allowSuspendedRenewal: settings.allow_suspended_renewal ?? false,
    autoExpireOnExpiryDate: settings.auto_expire_on_expiry_date ?? true,
    requireStateApprovalToReactivate: settings.require_state_approval_to_reactivate ?? true,
    requireReinspectionBeforeReactivation: settings.require_reinspection_before_reactivation ?? false,
  };
}

function settingsToApi(settings: FacilitySettingsState): MedicalFacilityAccreditationSettings {
  return {
    accreditation_template: settings.accreditationTemplate,
    reaccreditation_template: settings.reaccreditationTemplate,
    validity_duration: settings.validityDuration,
    validity_unit: settings.validityUnit,
    initial_review_sla: settings.initialReviewSla,
    review_day_type: settings.reviewDayType,
    correction_window: settings.correctionWindow,
    correction_day_type: settings.correctionDayType,
    renewal_window_days: settings.renewalWindowDays,
    grace_period_days: settings.gracePeriodDays,
    reminder_days_before_expiry: parseNumberList(settings.reminderDaysBeforeExpiry),
    escalation_days_after_sla: parseNumberList(settings.escalationDaysAfterSla),
    disable_assessments_when_expired: settings.disableAssessmentsWhenExpired,
    disable_assessments_when_suspended: settings.disableAssessmentsWhenSuspended,
    allow_renewal_after_expiry: settings.allowRenewalAfterExpiry,
    allow_suspended_renewal: settings.allowSuspendedRenewal,
    auto_expire_on_expiry_date: settings.autoExpireOnExpiryDate,
    require_state_approval_to_reactivate: settings.requireStateApprovalToReactivate,
    require_reinspection_before_reactivation: settings.requireReinspectionBeforeReactivation,
  };
}

type BooleanFacilitySettingKey = {
  [K in keyof FacilitySettingsState]: FacilitySettingsState[K] extends boolean ? K : never;
}[keyof FacilitySettingsState];

function MedicalFacilitySettingsPanel() {
  const [settings, setSettings] = useState<FacilitySettingsState>(defaultFacilitySettings);
  const [saved, setSaved] = useState(false);

  const settingsQuery = useQuery({
    queryKey: ["state-account-settings", "medical-facility-settings"],
    queryFn: fetchStateMedicalFacilitySettings,
  });

  useEffect(() => {
    if (settingsQuery.data?.medical_facility_settings) {
      setSettings(settingsFromApi(settingsQuery.data.medical_facility_settings));
    }
  }, [settingsQuery.data?.medical_facility_settings]);

  const saveMutation = useMutation({
    mutationFn: () => updateStateMedicalFacilitySettings(settingsToApi(settings)),
    onSuccess: (config) => {
      setSettings(settingsFromApi(config.medical_facility_settings));
      setSaved(true);
    },
  });

  const templatesQuery = useQuery({
    queryKey: ["state-account-settings", "facility-accreditation-templates"],
    queryFn: () => fetchFormTemplates({ status: "published" }),
  });

  const publishedTemplates = useMemo(() => templatesQuery.data ?? [], [templatesQuery.data]);
  const accreditationTemplates = useMemo(
    () => publishedTemplates.filter((template) => ["accreditation_checklist", "facility_registration"].includes(template.purpose) || template.module_context === "accreditation" || template.primary_module === "medical_facilities"),
    [publishedTemplates]
  );
  const reaccreditationTemplates = useMemo(
    () => publishedTemplates.filter((template) => ["re_accreditation_checklist", "accreditation_checklist"].includes(template.purpose) || template.module_context === "re_accreditation" || template.primary_module === "medical_facilities"),
    [publishedTemplates]
  );

  function update<K extends keyof FacilitySettingsState>(key: K, value: FacilitySettingsState[K]) {
    setSettings((prev) => ({ ...prev, [key]: value }));
    setSaved(false);
  }

  function updateBoolean(key: BooleanFacilitySettingKey, value: boolean) {
    update(key, value);
  }

  return (
    <div className="grid gap-6">
      <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
        <p className="text-xs font-bold uppercase tracking-wide text-brand-700">Medical Facility Settings</p>
        <h2 className="mt-2 text-lg font-bold text-neutral-950">Accreditation rules</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-neutral-600">
          Select active Forms Tool templates and configure validity, review timelines, reminders, renewal windows, and suspension behaviour used by Medical Facilities workflows.
        </p>
      </section>

      {settingsQuery.isLoading ? <p className="rounded-lg border border-neutral-200 bg-white px-4 py-3 text-sm font-semibold text-neutral-600">Loading current medical facility settings...</p> : null}
      {settingsQuery.isError ? <p className="rounded-lg border border-danger-100 bg-danger-50 px-4 py-3 text-sm font-semibold text-danger-700">{getApiErrorMessage(settingsQuery.error, "Could not load medical facility settings.")}</p> : null}
      {saveMutation.isError ? <p className="rounded-lg border border-danger-100 bg-danger-50 px-4 py-3 text-sm font-semibold text-danger-700">{getApiErrorMessage(saveMutation.error, "Could not save medical facility settings.")}</p> : null}
      {saved ? <p className="rounded-lg border border-brand-100 bg-brand-50 px-4 py-3 text-sm font-semibold text-brand-700">Medical facility settings saved.</p> : null}

      <section className="grid gap-5 lg:grid-cols-2">
        <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <h3 className="text-base font-bold text-neutral-900">Accreditation Templates</h3>
          <p className="mt-1 text-sm text-neutral-500">Only published Forms Tool templates can be selected for live accreditation workflows.</p>
          <div className="mt-5 grid gap-4">
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Active accreditation template
              <select className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm" value={settings.accreditationTemplate} onChange={(event) => update("accreditationTemplate", event.target.value)}>
                <option value="">Select published template</option>
                {accreditationTemplates.map((template) => <option key={template.id} value={template.id}>{templateLabel(template)}</option>)}
              </select>
            </label>
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Active re-accreditation template
              <select className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm" value={settings.reaccreditationTemplate} onChange={(event) => update("reaccreditationTemplate", event.target.value)}>
                <option value="">Select published template</option>
                {reaccreditationTemplates.map((template) => <option key={template.id} value={template.id}>{templateLabel(template)}</option>)}
              </select>
            </label>
            {templatesQuery.isLoading ? <p className="text-xs font-semibold text-neutral-500">Loading published templates...</p> : null}
            {!templatesQuery.isLoading && accreditationTemplates.length === 0 ? <p className="rounded bg-warning-50 px-3 py-2 text-xs font-semibold text-warning-700">No published medical facility accreditation templates found. Create and publish one in Forms Tool first.</p> : null}
          </div>
        </div>

        <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <h3 className="text-base font-bold text-neutral-900">Accreditation Validity</h3>
          <p className="mt-1 text-sm text-neutral-500">Approval date becomes the accreditation start date. Expiry is calculated from this validity rule.</p>
          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Validity duration
              <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3 text-sm" min={1} type="number" value={settings.validityDuration} onChange={(event) => update("validityDuration", Number(event.target.value))} />
            </label>
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Validity unit
              <select className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm" value={settings.validityUnit} onChange={(event) => update("validityUnit", event.target.value as FacilitySettingsState["validityUnit"])}>
                <option value="months">Months</option>
                <option value="years">Years</option>
                <option value="days">Days</option>
              </select>
            </label>
          </div>
        </div>
      </section>

      <section className="grid gap-5 lg:grid-cols-2">
        <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <h3 className="text-base font-bold text-neutral-900">Review Timelines</h3>
          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Initial review SLA
              <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3 text-sm" min={1} type="number" value={settings.initialReviewSla} onChange={(event) => update("initialReviewSla", Number(event.target.value))} />
            </label>
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Review day type
              <select className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm" value={settings.reviewDayType} onChange={(event) => update("reviewDayType", event.target.value as FacilitySettingsState["reviewDayType"])}>
                <option value="working_days">Working days</option>
                <option value="calendar_days">Calendar days</option>
              </select>
            </label>
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Correction window
              <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3 text-sm" min={1} type="number" value={settings.correctionWindow} onChange={(event) => update("correctionWindow", Number(event.target.value))} />
            </label>
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Correction day type
              <select className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm" value={settings.correctionDayType} onChange={(event) => update("correctionDayType", event.target.value as FacilitySettingsState["correctionDayType"])}>
                <option value="calendar_days">Calendar days</option>
                <option value="working_days">Working days</option>
              </select>
            </label>
          </div>
        </div>

        <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <h3 className="text-base font-bold text-neutral-900">Re-accreditation Rules</h3>
          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Opens before expiry
              <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3 text-sm" min={0} type="number" value={settings.renewalWindowDays} onChange={(event) => update("renewalWindowDays", Number(event.target.value))} />
            </label>
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Grace period after expiry
              <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3 text-sm" min={0} type="number" value={settings.gracePeriodDays} onChange={(event) => update("gracePeriodDays", Number(event.target.value))} />
            </label>
          </div>
          <div className="mt-5 grid gap-3">
            {[
              ["allowRenewalAfterExpiry", "Allow renewal after expiry"],
              ["allowSuspendedRenewal", "Allow suspended facility to apply for renewal"],
              ["autoExpireOnExpiryDate", "Auto-change facility status to expired on expiry date"],
            ].map(([key, label]) => (
              <label className="flex items-center justify-between gap-4 rounded-lg border border-neutral-100 bg-neutral-50 px-4 py-3 text-sm font-semibold text-neutral-700" key={key}>
                {label}
                <input checked={settings[key as BooleanFacilitySettingKey]} className="h-4 w-4 accent-brand-600" onChange={(event) => updateBoolean(key as BooleanFacilitySettingKey, event.target.checked)} type="checkbox" />
              </label>
            ))}
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
        <h3 className="text-base font-bold text-neutral-900">Reminder & Escalation Rules</h3>
        <p className="mt-1 text-sm text-neutral-500">Enter days as comma-separated values. These rules drive renewal reminders and delayed-review escalations.</p>
        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <label className="grid gap-1 text-sm font-semibold text-neutral-700">
            Reminder days before expiry
            <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3 text-sm" value={settings.reminderDaysBeforeExpiry} onChange={(event) => update("reminderDaysBeforeExpiry", event.target.value)} placeholder="60, 30, 7" />
          </label>
          <label className="grid gap-1 text-sm font-semibold text-neutral-700">
            Escalation days after SLA
            <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3 text-sm" value={settings.escalationDaysAfterSla} onChange={(event) => update("escalationDaysAfterSla", event.target.value)} placeholder="3, 7" />
          </label>
        </div>
      </section>

      <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
        <h3 className="text-base font-bold text-neutral-900">Suspension & Expiry Rules</h3>
        <div className="mt-5 grid gap-3 md:grid-cols-2">
          {[
            ["disableAssessmentsWhenExpired", "Disable assessments when expired"],
            ["disableAssessmentsWhenSuspended", "Disable assessments when suspended"],
            ["requireStateApprovalToReactivate", "Require State approval to reactivate"],
            ["requireReinspectionBeforeReactivation", "Require re-inspection before reactivation"],
          ].map(([key, label]) => (
            <label className="flex items-center justify-between gap-4 rounded-lg border border-neutral-100 bg-neutral-50 px-4 py-3 text-sm font-semibold text-neutral-700" key={key}>
              {label}
              <input checked={settings[key as BooleanFacilitySettingKey]} className="h-4 w-4 accent-brand-600" onChange={(event) => updateBoolean(key as BooleanFacilitySettingKey, event.target.checked)} type="checkbox" />
            </label>
          ))}
        </div>
      </section>

      <div className="flex justify-end">
        <button className="h-11 rounded-lg bg-brand-600 px-5 text-sm font-bold text-white hover:bg-brand-700 disabled:cursor-not-allowed disabled:bg-neutral-300" disabled={saveMutation.isPending} onClick={() => saveMutation.mutate()} type="button">
          {saveMutation.isPending ? "Saving..." : "Save medical facility settings"}
        </button>
      </div>
    </div>
  );
}

function InspectionSettingsPanel() {
  const [saved, setSaved] = useState(false);
  const [settings, setSettings] = useState<Partial<InspectionSettingsPolicy>>({});

  const settingsQuery = useQuery({
    queryKey: ["state-account-settings", "inspection-settings"],
    queryFn: fetchInspectionSettings,
  });

  useEffect(() => {
    if (settingsQuery.data) setSettings(settingsQuery.data);
  }, [settingsQuery.data]);

  const templatesQuery = useQuery({
    queryKey: ["state-account-settings", "inspection-checklist-templates"],
    queryFn: () => fetchFormTemplates({ purpose: "inspection_checklist", status: "published" }),
  });

  const saveMutation = useMutation({
    mutationFn: () => updateInspectionSettings(settings),
    onSuccess: (data) => { setSettings(data); setSaved(true); },
  });

  function updateBool(key: keyof InspectionSettingsPolicy, value: boolean) {
    setSettings((prev) => ({ ...prev, [key]: value }));
    setSaved(false);
  }

  function updateTemplate(inspectionType: string, templateId: string) {
    setSettings((prev) => ({
      ...prev,
      default_templates: { ...(prev.default_templates || {}), [inspectionType]: templateId },
    }));
    setSaved(false);
  }

  const templates = templatesQuery.data || [];
  const defaultTemplates = settings.default_templates || {};

  const templateTypes = [
    { key: "routine", label: "Routine Inspection" },
    { key: "complaint_based", label: "Complaint-Based Inspection" },
    { key: "follow_up", label: "Follow-up Inspection" },
    { key: "high_risk", label: "High-Risk Inspection" },
    { key: "re_inspection", label: "Re-inspection" },
    { key: "certificate_sweep", label: "Certificate Verification Sweep" },
  ];

  const booleanSettings: Array<{ key: keyof InspectionSettingsPolicy; label: string; group: string }> = [
    { key: "allow_offline_inspections", label: "Allow offline inspection forms", group: "evidence" },
    { key: "requires_gps_by_default", label: "Require GPS capture by default", group: "evidence" },
    { key: "requires_inspector_signature", label: "Require inspector signature", group: "evidence" },
    { key: "requires_employer_signature", label: "Require employer/branch representative signature", group: "evidence" },
    { key: "auto_open_case_for_high", label: "Auto-open case for High severity findings", group: "cases" },
    { key: "auto_open_case_for_critical", label: "Auto-open case for Critical severity findings", group: "cases" },
    { key: "auto_require_followup_for_high", label: "Require follow-up inspection for High findings", group: "followup" },
    { key: "auto_require_followup_for_critical", label: "Require follow-up inspection for Critical findings", group: "followup" },
    { key: "auto_close_passed_inspections", label: "Auto-close passed inspections after review", group: "closure" },
  ];

  return (
    <div className="grid gap-6">
      <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
        <p className="text-xs font-bold uppercase tracking-wide text-brand-700">Account Settings</p>
        <h2 className="mt-2 text-lg font-bold text-neutral-950">Inspection Settings</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-neutral-600">
          Configure default inspection templates, severity rules, corrective action timelines, evidence requirements, and escalation policies for your state.
        </p>
      </section>

      {settingsQuery.isLoading ? <p className="rounded-lg border border-neutral-200 bg-white px-4 py-3 text-sm font-semibold text-neutral-600">Loading inspection settings...</p> : null}
      {saveMutation.isError ? <p className="rounded-lg border border-danger-100 bg-danger-50 px-4 py-3 text-sm font-semibold text-danger-700">{getApiErrorMessage(saveMutation.error, "Could not save settings.")}</p> : null}
      {saved ? <p className="rounded-lg border border-brand-100 bg-brand-50 px-4 py-3 text-sm font-semibold text-brand-700">Inspection settings saved.</p> : null}

      <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
        <h3 className="text-base font-bold text-neutral-900">Default Inspection Templates</h3>
        <p className="mt-1 text-sm text-neutral-500">Select published Forms Tool templates for each inspection type. Only templates with purpose &quot;Inspection Checklist&quot; are shown.</p>
        <div className="mt-5 grid gap-4 md:grid-cols-2">
          {templateTypes.map(({ key, label }) => (
            <label key={key} className="grid gap-1 text-sm font-semibold text-neutral-700">
              {label}
              <select className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm" value={defaultTemplates[key] || ""} onChange={(e) => updateTemplate(key, e.target.value)}>
                <option value="">No default template</option>
                {templates.map((t) => <option key={t.id} value={t.id}>{t.title} v{t.current_version}</option>)}
              </select>
            </label>
          ))}
        </div>
        {!templatesQuery.isLoading && !templates.length ? <p className="mt-3 rounded bg-warning-50 px-3 py-2 text-xs font-semibold text-warning-700">No published inspection checklist templates found. Create and publish one in Form Builder first.</p> : null}
      </section>

      <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
        <h3 className="text-base font-bold text-neutral-900">Evidence & Submission Rules</h3>
        <div className="mt-5 grid gap-3 md:grid-cols-2">
          {booleanSettings.filter((s) => s.group === "evidence").map(({ key, label }) => (
            <label key={key} className="flex items-center justify-between gap-4 rounded-lg border border-neutral-100 bg-neutral-50 px-4 py-3 text-sm font-semibold text-neutral-700">
              {label}
              <input checked={Boolean(settings[key])} className="h-4 w-4 accent-brand-600" onChange={(e) => updateBool(key, e.target.checked)} type="checkbox" />
            </label>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
        <h3 className="text-base font-bold text-neutral-900">Case & Follow-up Rules</h3>
        <div className="mt-5 grid gap-3 md:grid-cols-2">
          {booleanSettings.filter((s) => s.group === "cases" || s.group === "followup").map(({ key, label }) => (
            <label key={key} className="flex items-center justify-between gap-4 rounded-lg border border-neutral-100 bg-neutral-50 px-4 py-3 text-sm font-semibold text-neutral-700">
              {label}
              <input checked={Boolean(settings[key])} className="h-4 w-4 accent-brand-600" onChange={(e) => updateBool(key, e.target.checked)} type="checkbox" />
            </label>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
        <h3 className="text-base font-bold text-neutral-900">Inspection Closure Rules</h3>
        <div className="mt-5 grid gap-3 md:grid-cols-2">
          {booleanSettings.filter((s) => s.group === "closure").map(({ key, label }) => (
            <label key={key} className="flex items-center justify-between gap-4 rounded-lg border border-neutral-100 bg-neutral-50 px-4 py-3 text-sm font-semibold text-neutral-700">
              {label}
              <input checked={Boolean(settings[key])} className="h-4 w-4 accent-brand-600" onChange={(e) => updateBool(key, e.target.checked)} type="checkbox" />
            </label>
          ))}
        </div>
      </section>

      <div className="flex justify-end">
        <button className="h-11 rounded-lg bg-brand-600 px-5 text-sm font-bold text-white hover:bg-brand-700 disabled:cursor-not-allowed disabled:bg-neutral-300" disabled={saveMutation.isPending} onClick={() => saveMutation.mutate()} type="button">
          {saveMutation.isPending ? "Saving..." : "Save inspection settings"}
        </button>
      </div>
    </div>
  );
}

const defaultStateProfileSettings: StateProfileSettings = {
  ministry_name: "",
  public_display_name: "",
  official_email: "",
  official_phone: "",
  website: "",
  address_line_1: "",
  address_line_2: "",
  city: "",
  country: "Nigeria",
  postal_code: "",
  state_logo_url: "",
  state_seal_url: "",
  certificate_logo_url: "",
  receipt_logo_url: "",
  primary_brand_color: "#16A34A",
  secondary_brand_color: "#0F766E",
  signatories: [],
  timezone: "Africa/Lagos",
  currency: "NGN",
  working_days: ["monday", "tuesday", "wednesday", "thursday", "friday"],
  working_hours_start: "09:00",
  working_hours_end: "17:00",
  public_holidays_source: "federal_and_state",
};

const defaultNotificationSettings: StateNotificationSettings = {
  channels: { in_app: true, email: true, sms: false, whatsapp: false, sender_name: "FoodCert NG", reply_to_email: "" },
  event_rules: { facility_accreditation: true, certificate_validation: true, inspection_enforcement: true, forms: true, payments: true, security: true },
  reminder_schedules: { certificate_expiry: [30, 14, 7], facility_accreditation_expiry: [90, 60, 30, 14, 7], inspection_due: [7, 3, 1], corrective_action_due: [3, 1, 0], form_due: [7, 3, 1] },
  recipient_roles: { state_admin: true, assigned_reviewer: true, assigned_inspector: true, facility_admin: true, employer_admin: true },
  templates_enabled: true,
  delivery_logs_visible: true,
};

const defaultSecuritySettings: StateSecurityAccessSettings = {
  minimum_password_length: 10,
  require_uppercase: true,
  require_lowercase: true,
  require_number: true,
  require_symbol: false,
  password_expiry_days: 0,
  prevent_password_reuse: 5,
  force_password_reset_for_new_users: true,
  mfa_required_for_admins: true,
  mfa_required_for_finance: false,
  mfa_required_for_certificate_approvers: true,
  allowed_mfa_methods: ["authenticator_app", "email_otp"],
  session_timeout_minutes: 480,
  idle_timeout_minutes: 30,
  concurrent_sessions_allowed: 2,
  force_logout_on_role_change: true,
  failed_login_attempts: 5,
  lockout_duration_minutes: 30,
  notify_admin_on_lockout: true,
  allowed_email_domains: [],
  block_public_email_domains: false,
  enable_api_access: false,
  allow_api_tokens: false,
  require_token_expiry: true,
  require_sensitive_export_approval: true,
  restrict_medical_data_export: true,
  watermark_pdf_exports: true,
  audit_all_exports: true,
  enable_periodic_access_review: true,
  access_review_frequency_days: 90,
};

function SettingCard({ title, description, children }: { title: string; description?: string; children: ReactNode }) {
  return (
    <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
      <h3 className="text-base font-bold text-neutral-900">{title}</h3>
      {description ? <p className="mt-1 text-sm leading-6 text-neutral-500">{description}</p> : null}
      <div className="mt-5">{children}</div>
    </section>
  );
}

function TextField({ label, value, onChange, type = "text", placeholder = "" }: { label: string; value: string | number; onChange: (value: string) => void; type?: string; placeholder?: string }) {
  return (
    <label className="grid gap-1 text-sm font-semibold text-neutral-700">
      {label}
      <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3 text-sm font-normal text-neutral-800" placeholder={placeholder} type={type} value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function ToggleRow({ label, checked, onChange }: { label: string; checked: boolean; onChange: (checked: boolean) => void }) {
  return (
    <label className="flex items-center justify-between gap-4 rounded-lg border border-neutral-100 bg-neutral-50 px-4 py-3 text-sm font-semibold text-neutral-700">
      {label}
      <input checked={checked} className="h-4 w-4 accent-brand-600" onChange={(event) => onChange(event.target.checked)} type="checkbox" />
    </label>
  );
}

function StateProfilePanel() {
  const [settings, setSettings] = useState<StateProfileSettings>(defaultStateProfileSettings);
  const [saved, setSaved] = useState(false);
  const settingsQuery = useQuery({ queryKey: ["state-account-settings", "state-profile"], queryFn: fetchStateProfileSettings });
  useEffect(() => {
    if (settingsQuery.data?.state_profile_settings) setSettings({ ...defaultStateProfileSettings, ...settingsQuery.data.state_profile_settings });
  }, [settingsQuery.data?.state_profile_settings]);
  const saveMutation = useMutation({
    mutationFn: () => updateStateProfileSettings(settings),
    onSuccess: (data) => { setSettings({ ...defaultStateProfileSettings, ...data.state_profile_settings }); setSaved(true); },
  });
  function update<K extends keyof StateProfileSettings>(key: K, value: StateProfileSettings[K]) {
    setSettings((prev) => ({ ...prev, [key]: value }));
    setSaved(false);
  }
  function updateSignatory(key: string, value: string | boolean) {
    const current = settings.signatories[0] || { name: "", title: "", signature_url: "", effective_start_date: "", effective_end_date: "", is_active: true };
    update("signatories", [{ ...current, [key]: value }]);
  }
  const signatory = settings.signatories[0] || {};
  return (
    <div className="grid gap-6">
      <SettingCard title="State Profile" description="Manage the official identity used on certificates, reports, receipts, notices, and public verification pages.">
        {settingsQuery.isLoading ? <p className="text-sm font-semibold text-neutral-500">Loading state profile...</p> : null}
        {saveMutation.isError ? <p className="rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{getApiErrorMessage(saveMutation.error, "Could not save state profile.")}</p> : null}
        {saved ? <p className="rounded bg-brand-50 px-3 py-2 text-sm font-semibold text-brand-700">State profile saved.</p> : null}
      </SettingCard>
      <div className="grid gap-5 lg:grid-cols-2">
        <SettingCard title="State Identity">
          <div className="grid gap-4">
            <TextField label="Ministry Name" value={settings.ministry_name} onChange={(value) => update("ministry_name", value)} />
            <TextField label="Public Display Name" value={settings.public_display_name} onChange={(value) => update("public_display_name", value)} />
          </div>
        </SettingCard>
        <SettingCard title="Contact Information">
          <div className="grid gap-4">
            <TextField label="Official Email" value={settings.official_email} onChange={(value) => update("official_email", value)} type="email" />
            <TextField label="Official Phone" value={settings.official_phone} onChange={(value) => update("official_phone", value)} />
            <TextField label="Website" value={settings.website} onChange={(value) => update("website", value)} />
            <TextField label="Address" value={settings.address_line_1} onChange={(value) => update("address_line_1", value)} />
          </div>
        </SettingCard>
      </div>
      <div className="grid gap-5 lg:grid-cols-2">
        <SettingCard title="Branding & Logos" description="Use hosted asset URLs for now. File upload can plug into the same fields later.">
          <div className="grid gap-4">
            <TextField label="State Logo URL" value={settings.state_logo_url} onChange={(value) => update("state_logo_url", value)} />
            <TextField label="Certificate Logo URL" value={settings.certificate_logo_url} onChange={(value) => update("certificate_logo_url", value)} />
            <div className="grid gap-4 sm:grid-cols-2">
              <TextField label="Primary Brand Color" value={settings.primary_brand_color} onChange={(value) => update("primary_brand_color", value)} type="color" />
              <TextField label="Secondary Brand Color" value={settings.secondary_brand_color} onChange={(value) => update("secondary_brand_color", value)} type="color" />
            </div>
          </div>
        </SettingCard>
        <SettingCard title="Authorized Signatory">
          <div className="grid gap-4">
            <TextField label="Name" value={String(signatory.name || "")} onChange={(value) => updateSignatory("name", value)} />
            <TextField label="Title" value={String(signatory.title || "")} onChange={(value) => updateSignatory("title", value)} />
            <TextField label="Signature URL" value={String(signatory.signature_url || "")} onChange={(value) => updateSignatory("signature_url", value)} />
            <ToggleRow label="Active signatory" checked={Boolean(signatory.is_active ?? true)} onChange={(value) => updateSignatory("is_active", value)} />
          </div>
        </SettingCard>
      </div>
      <SettingCard title="Administrative Defaults">
        <div className="grid gap-4 md:grid-cols-4">
          <TextField label="Timezone" value={settings.timezone} onChange={(value) => update("timezone", value)} />
          <TextField label="Currency" value={settings.currency} onChange={(value) => update("currency", value)} />
          <TextField label="Working Hours Start" value={settings.working_hours_start} onChange={(value) => update("working_hours_start", value)} type="time" />
          <TextField label="Working Hours End" value={settings.working_hours_end} onChange={(value) => update("working_hours_end", value)} type="time" />
        </div>
      </SettingCard>
      <div className="flex justify-end">
        <button className="h-11 rounded-lg bg-brand-600 px-5 text-sm font-bold text-white hover:bg-brand-700 disabled:bg-neutral-300" disabled={saveMutation.isPending} onClick={() => saveMutation.mutate()} type="button">{saveMutation.isPending ? "Saving..." : "Save state profile"}</button>
      </div>
    </div>
  );
}

function NotificationSettingsPanel() {
  const [settings, setSettings] = useState<StateNotificationSettings>(defaultNotificationSettings);
  const [saved, setSaved] = useState(false);
  const settingsQuery = useQuery({ queryKey: ["state-account-settings", "notification-settings"], queryFn: fetchStateNotificationSettings });
  useEffect(() => {
    if (settingsQuery.data?.notification_settings) setSettings({ ...defaultNotificationSettings, ...settingsQuery.data.notification_settings });
  }, [settingsQuery.data?.notification_settings]);
  const saveMutation = useMutation({
    mutationFn: () => updateStateNotificationSettings(settings),
    onSuccess: (data) => { setSettings({ ...defaultNotificationSettings, ...data.notification_settings }); setSaved(true); },
  });
  function setGroupValue(group: keyof StateNotificationSettings, key: string, value: boolean | string | number[]) {
    setSettings((prev) => ({ ...prev, [group]: { ...(prev[group] as Record<string, unknown>), [key]: value } }));
    setSaved(false);
  }
  return (
    <div className="grid gap-6">
      <SettingCard title="Notification Settings" description="Configure channels, event rules, reminder schedules, recipients, templates, and delivery visibility.">
        {settingsQuery.isLoading ? <p className="text-sm font-semibold text-neutral-500">Loading notification settings...</p> : null}
        {saveMutation.isError ? <p className="rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{getApiErrorMessage(saveMutation.error, "Could not save notification settings.")}</p> : null}
        {saved ? <p className="rounded bg-brand-50 px-3 py-2 text-sm font-semibold text-brand-700">Notification settings saved.</p> : null}
      </SettingCard>
      <div className="grid gap-5 lg:grid-cols-2">
        <SettingCard title="Channels">
          <div className="grid gap-3">
            {["in_app", "email", "sms", "whatsapp"].map((key) => <ToggleRow key={key} label={key.replaceAll("_", " ").toUpperCase()} checked={Boolean(settings.channels[key])} onChange={(value) => setGroupValue("channels", key, value)} />)}
            <TextField label="Default Sender Name" value={String(settings.channels.sender_name || "")} onChange={(value) => setGroupValue("channels", "sender_name", value)} />
            <TextField label="Default Reply-to Email" value={String(settings.channels.reply_to_email || "")} onChange={(value) => setGroupValue("channels", "reply_to_email", value)} />
          </div>
        </SettingCard>
        <SettingCard title="Event Rules">
          <div className="grid gap-3">
            {Object.entries(settings.event_rules).map(([key, value]) => <ToggleRow key={key} label={key.replaceAll("_", " ")} checked={Boolean(value)} onChange={(checked) => setGroupValue("event_rules", key, checked)} />)}
          </div>
        </SettingCard>
      </div>
      <div className="grid gap-5 lg:grid-cols-2">
        <SettingCard title="Reminder Schedules" description="Comma-separated days before or after due date.">
          <div className="grid gap-4">
            {Object.entries(settings.reminder_schedules).map(([key, value]) => <TextField key={key} label={key.replaceAll("_", " ")} value={value.join(", ")} onChange={(next) => setGroupValue("reminder_schedules", key, parseNumberList(next))} />)}
          </div>
        </SettingCard>
        <SettingCard title="Recipients">
          <div className="grid gap-3">
            {Object.entries(settings.recipient_roles).map(([key, value]) => <ToggleRow key={key} label={key.replaceAll("_", " ")} checked={Boolean(value)} onChange={(checked) => setGroupValue("recipient_roles", key, checked)} />)}
          </div>
        </SettingCard>
      </div>
      <SettingCard title="Templates & Delivery Logs">
        <div className="grid gap-3 md:grid-cols-2">
          <ToggleRow label="Enable notification templates" checked={settings.templates_enabled} onChange={(value) => { setSettings((prev) => ({ ...prev, templates_enabled: value })); setSaved(false); }} />
          <ToggleRow label="Show delivery logs to authorized users" checked={settings.delivery_logs_visible} onChange={(value) => { setSettings((prev) => ({ ...prev, delivery_logs_visible: value })); setSaved(false); }} />
        </div>
      </SettingCard>
      <div className="flex justify-end">
        <button className="h-11 rounded-lg bg-brand-600 px-5 text-sm font-bold text-white hover:bg-brand-700 disabled:bg-neutral-300" disabled={saveMutation.isPending} onClick={() => saveMutation.mutate()} type="button">{saveMutation.isPending ? "Saving..." : "Save notification settings"}</button>
      </div>
    </div>
  );
}

function SecurityAccessPanel() {
  const [settings, setSettings] = useState<StateSecurityAccessSettings>(defaultSecuritySettings);
  const [saved, setSaved] = useState(false);
  const settingsQuery = useQuery({ queryKey: ["state-account-settings", "security-access"], queryFn: fetchStateSecurityAccessSettings });
  useEffect(() => {
    if (settingsQuery.data?.security_access_settings) setSettings({ ...defaultSecuritySettings, ...settingsQuery.data.security_access_settings });
  }, [settingsQuery.data?.security_access_settings]);
  const saveMutation = useMutation({
    mutationFn: () => updateStateSecurityAccessSettings(settings),
    onSuccess: (data) => { setSettings({ ...defaultSecuritySettings, ...data.security_access_settings }); setSaved(true); },
  });
  function update<K extends keyof StateSecurityAccessSettings>(key: K, value: StateSecurityAccessSettings[K]) {
    setSettings((prev) => ({ ...prev, [key]: value }));
    setSaved(false);
  }
  return (
    <div className="grid gap-6">
      <SettingCard title="Security & Access" description="Configure account-wide security rules. User, role, team, and permission assignment remains in Stakeholder Management.">
        {settingsQuery.isLoading ? <p className="text-sm font-semibold text-neutral-500">Loading security settings...</p> : null}
        {saveMutation.isError ? <p className="rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{getApiErrorMessage(saveMutation.error, "Could not save security settings.")}</p> : null}
        {saved ? <p className="rounded bg-brand-50 px-3 py-2 text-sm font-semibold text-brand-700">Security settings saved.</p> : null}
      </SettingCard>
      <div className="grid gap-5 lg:grid-cols-2">
        <SettingCard title="Authentication Policy">
          <div className="grid gap-4">
            <TextField label="Minimum Password Length" value={settings.minimum_password_length} onChange={(value) => update("minimum_password_length", Number(value))} type="number" />
            <ToggleRow label="Require uppercase" checked={settings.require_uppercase} onChange={(value) => update("require_uppercase", value)} />
            <ToggleRow label="Require lowercase" checked={settings.require_lowercase} onChange={(value) => update("require_lowercase", value)} />
            <ToggleRow label="Require number" checked={settings.require_number} onChange={(value) => update("require_number", value)} />
            <ToggleRow label="Require symbol" checked={settings.require_symbol} onChange={(value) => update("require_symbol", value)} />
          </div>
        </SettingCard>
        <SettingCard title="MFA & Session Rules">
          <div className="grid gap-4">
            <ToggleRow label="MFA required for admins" checked={settings.mfa_required_for_admins} onChange={(value) => update("mfa_required_for_admins", value)} />
            <ToggleRow label="MFA required for certificate approvers" checked={settings.mfa_required_for_certificate_approvers} onChange={(value) => update("mfa_required_for_certificate_approvers", value)} />
            <TextField label="Session Timeout (minutes)" value={settings.session_timeout_minutes} onChange={(value) => update("session_timeout_minutes", Number(value))} type="number" />
            <TextField label="Idle Timeout (minutes)" value={settings.idle_timeout_minutes} onChange={(value) => update("idle_timeout_minutes", Number(value))} type="number" />
          </div>
        </SettingCard>
      </div>
      <div className="grid gap-5 lg:grid-cols-2">
        <SettingCard title="Lockout & Trusted Domains">
          <div className="grid gap-4">
            <TextField label="Failed Login Attempts" value={settings.failed_login_attempts} onChange={(value) => update("failed_login_attempts", Number(value))} type="number" />
            <TextField label="Lockout Duration (minutes)" value={settings.lockout_duration_minutes} onChange={(value) => update("lockout_duration_minutes", Number(value))} type="number" />
            <TextField label="Allowed Email Domains" value={settings.allowed_email_domains.join(", ")} onChange={(value) => update("allowed_email_domains", value.split(",").map((item) => item.trim()).filter(Boolean))} />
            <ToggleRow label="Block public email domains" checked={settings.block_public_email_domains} onChange={(value) => update("block_public_email_domains", value)} />
          </div>
        </SettingCard>
        <SettingCard title="Export & API Controls">
          <div className="grid gap-3">
            <ToggleRow label="Enable API access" checked={settings.enable_api_access} onChange={(value) => update("enable_api_access", value)} />
            <ToggleRow label="Allow API tokens" checked={settings.allow_api_tokens} onChange={(value) => update("allow_api_tokens", value)} />
            <ToggleRow label="Require approval for sensitive exports" checked={settings.require_sensitive_export_approval} onChange={(value) => update("require_sensitive_export_approval", value)} />
            <ToggleRow label="Restrict medical data export" checked={settings.restrict_medical_data_export} onChange={(value) => update("restrict_medical_data_export", value)} />
            <ToggleRow label="Watermark PDF exports" checked={settings.watermark_pdf_exports} onChange={(value) => update("watermark_pdf_exports", value)} />
            <ToggleRow label="Audit all exports" checked={settings.audit_all_exports} onChange={(value) => update("audit_all_exports", value)} />
          </div>
        </SettingCard>
      </div>
      <SettingCard title="Access Review">
        <div className="grid gap-4 md:grid-cols-2">
          <ToggleRow label="Enable periodic access review" checked={settings.enable_periodic_access_review} onChange={(value) => update("enable_periodic_access_review", value)} />
          <TextField label="Review Frequency (days)" value={settings.access_review_frequency_days} onChange={(value) => update("access_review_frequency_days", Number(value))} type="number" />
        </div>
      </SettingCard>
      <div className="flex justify-end">
        <button className="h-11 rounded-lg bg-brand-600 px-5 text-sm font-bold text-white hover:bg-brand-700 disabled:bg-neutral-300" disabled={saveMutation.isPending} onClick={() => saveMutation.mutate()} type="button">{saveMutation.isPending ? "Saving..." : "Save security settings"}</button>
      </div>
    </div>
  );
}

function AuditLogsPanel() {
  const [filters, setFilters] = useState({ action: "", module: "", search: "" });
  const logsQuery = useQuery({
    queryKey: ["state-account-settings", "audit-logs", filters],
    queryFn: () => fetchStateAuditLogs(Object.fromEntries(Object.entries(filters).filter(([, value]) => value))),
  });
  const logs = logsQuery.data || [];
  return (
    <div className="grid gap-6">
      <SettingCard title="Audit Logs" description="Review state-scoped activity, security events, settings changes, exports, and workflow actions.">
        <div className="grid gap-3 md:grid-cols-[1fr_220px_220px]">
          <TextField label="Search" value={filters.search} onChange={(value) => setFilters((prev) => ({ ...prev, search: value }))} />
          <label className="grid gap-1 text-sm font-semibold text-neutral-700">
            Action
            <select className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm" value={filters.action} onChange={(event) => setFilters((prev) => ({ ...prev, action: event.target.value }))}>
              <option value="">All actions</option>
              <option value="create">Create</option>
              <option value="update">Update</option>
              <option value="workflow_transition">Workflow transition</option>
              <option value="security_event">Security event</option>
              <option value="certificate_event">Certificate event</option>
              <option value="payment_event">Payment event</option>
            </select>
          </label>
          <TextField label="Module" value={filters.module} onChange={(value) => setFilters((prev) => ({ ...prev, module: value }))} />
        </div>
      </SettingCard>
      <section className="overflow-hidden rounded-lg border border-neutral-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-neutral-200 text-sm">
            <thead className="bg-neutral-50">
              <tr>
                {["Date", "Actor", "Action", "Module", "Entity", "Status", "IP Address"].map((header) => <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-neutral-500" key={header}>{header}</th>)}
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100">
              {logs.map((log) => (
                <tr className="bg-white" key={log.id}>
                  <td className="px-4 py-3 text-neutral-600">{new Date(log.created_at).toLocaleString()}</td>
                  <td className="px-4 py-3 text-neutral-700">{log.actor_name || log.actor_email || "System"}</td>
                  <td className="px-4 py-3 font-semibold text-neutral-800">{log.event}</td>
                  <td className="px-4 py-3 text-neutral-600">{log.module}</td>
                  <td className="px-4 py-3 text-neutral-600">{log.target_type || "-"} {log.target_id ? `#${log.target_id.slice(0, 8)}` : ""}</td>
                  <td className="px-4 py-3"><span className="rounded-full bg-brand-50 px-2 py-1 text-xs font-bold text-brand-700">{log.status}</span></td>
                  <td className="px-4 py-3 text-neutral-600">{log.ip_address || "-"}</td>
                </tr>
              ))}
              {!logsQuery.isLoading && !logs.length ? <tr><td className="px-4 py-6 text-sm text-neutral-500" colSpan={7}>No audit logs match these filters.</td></tr> : null}
              {logsQuery.isLoading ? <tr><td className="px-4 py-6 text-sm text-neutral-500" colSpan={7}>Loading audit logs...</td></tr> : null}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function PlaceholderSection({ tab }: { tab: PlaceholderTabKey }) {
  const config = PLACEHOLDERS[tab];
  return (
    <section className="rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
      <p className="text-xs font-bold uppercase tracking-wide text-brand-700">Account Settings</p>
      <h2 className="mt-2 text-lg font-bold text-neutral-950">{config.title}</h2>
      <p className="mt-2 max-w-2xl text-sm leading-6 text-neutral-600">{config.description}</p>
      <div className="mt-5 grid gap-3 md:grid-cols-3">
        {config.items.map((item) => (
          <div className="rounded-lg border border-neutral-100 bg-neutral-50 p-4 text-sm font-semibold text-neutral-700" key={item}>
            {item}
          </div>
        ))}
      </div>
    </section>
  );
}

export default function StateAccountSettingsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const tabParam = searchParams.get("tab") as TabKey | null;
  const activeTab = TABS.some((tab) => tab.key === tabParam) ? tabParam! : "state-profile";

  return (
    <PortalShell
      role="state_admin"
      title="Account Settings"
      description="Configure account-level policies, fees, templates, defaults, and security rules used by State Ministry workflows."
    >
      <nav className="mb-6 flex gap-0 overflow-x-auto border-b border-neutral-200">
        {TABS.map(({ key, label, icon: Icon }) => (
          <button
            className={`flex shrink-0 items-center gap-2 border-b-2 px-4 py-3 text-sm font-medium ${activeTab === key ? "border-brand-600 text-brand-700" : "border-transparent text-neutral-500 hover:text-neutral-800"}`}
            key={key}
            onClick={() => router.replace(`/state/account-settings?tab=${key}`)}
            type="button"
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </nav>

      {activeTab === "fees-payments" ? <StateFeesSettingsPanel /> : null}
      {activeTab === "certificate-settings" ? (
        <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <CertificateTemplateEditor scope="state" />
        </section>
      ) : null}
      {activeTab === "medical-facility-settings" ? <MedicalFacilitySettingsPanel /> : null}
      {activeTab === "form-builder" ? <FormBuilderContent basePath="/state/account-settings" tabParamName="ftab" /> : null}
      {activeTab === "inspection-settings" ? <InspectionSettingsPanel /> : null}
      {activeTab === "state-profile" ? <StateProfilePanel /> : null}
      {activeTab === "notification-settings" ? <NotificationSettingsPanel /> : null}
      {activeTab === "security-access" ? <SecurityAccessPanel /> : null}
      {activeTab === "audit-logs" ? <AuditLogsPanel /> : null}
      {activeTab !== "fees-payments" && activeTab !== "certificate-settings" && activeTab !== "medical-facility-settings" && activeTab !== "form-builder" && activeTab !== "inspection-settings" && activeTab !== "state-profile" && activeTab !== "notification-settings" && activeTab !== "security-access" && activeTab !== "audit-logs" ? <PlaceholderSection tab={activeTab} /> : null}
    </PortalShell>
  );
}
