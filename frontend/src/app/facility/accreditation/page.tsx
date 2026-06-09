"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertCircle, Download, FileText, RefreshCw, Save, Send, Upload } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import { downloadAccreditationCertificatePdf, listAccreditationCertificates, type AccreditationCertificate } from "@/lib/api/certificates";
import {
  createFacilityAccreditation,
  getCurrentMedicalFacility,
  listFacilityAccreditations,
  listFacilityDocuments,
  startFacilityReAccreditation,
  submitFacilityAccreditation,
  updateFacilityAccreditation,
  uploadFacilityDocument,
} from "@/lib/api/facilities";
import type { FacilityAccreditationApplication, FacilityDocument, MedicalFacility } from "@/types/facilities";

const CHECKLIST = [
  ["has_valid_facility_license", "Valid facility license"],
  ["has_reporting_policy", "Written reporting and documentation policy"],
  ["has_medical_records_computers", "Computers in medical records unit"],
  ["has_computer_operators", "Computer operators in records unit"],
  ["has_standard_forms", "Standard health declaration forms"],
  ["has_laboratory_request_forms", "Laboratory request forms"],
  ["has_patient_files", "Patient file system"],
  ["has_qr_certificate_capability", "QR-enabled certificate workflow readiness"],
  ["has_internet_access", "Reliable internet access"],
  ["has_trained_records_staff", "Trained medical records staff"],
  ["has_trained_clinical_staff", "Trained clinical staff"],
  ["has_trained_non_clinical_staff", "Trained non-clinical staff"],
  ["has_laboratory_capacity", "Required food handler lab capacity"],
  ["has_valid_doctor_credentials", "Valid doctor credentials"],
  ["has_valid_lab_staff_credentials", "Valid lab staff credentials"],
  ["has_infection_prevention_readiness", "Infection prevention and control readiness"],
  ["has_confidentiality_policy", "Data protection and confidentiality procedure"],
] as const;

const DOCUMENT_TYPES = [
  ["facility_license", "Facility license"],
  ["corporate_registration", "Corporate registration"],
  ["medical_director_credential", "Medical director credential"],
  ["doctor_license", "Doctor license"],
  ["lab_staff_credential", "Lab staff credential"],
  ["laboratory_license", "Laboratory license"],
  ["documentation_policy", "Documentation policy"],
  ["confidentiality_policy", "Confidentiality policy"],
  ["facility_photo", "Facility photo"],
  ["equipment_list", "Equipment list"],
  ["digital_readiness", "Digital readiness"],
  ["bank_details", "Bank details"],
  ["state_required_form", "State required form"],
  ["other", "Other"],
];

type ChecklistKey = typeof CHECKLIST[number][0];
type ChecklistForm = Record<ChecklistKey, boolean>;

const emptyChecklist = CHECKLIST.reduce((acc, [key]) => ({ ...acc, [key]: false }), {} as ChecklistForm);

function buildChecklist(application?: FacilityAccreditationApplication): ChecklistForm {
  if (!application) return emptyChecklist;
  return CHECKLIST.reduce((acc, [key]) => ({ ...acc, [key]: Boolean(application[key]) }), {} as ChecklistForm);
}

function formatDate(value?: string) {
  if (!value) return "Not set";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

function latestApplication(applications: FacilityAccreditationApplication[]) {
  return [...applications].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0];
}

export default function Page() {
  const [facility, setFacility] = useState<MedicalFacility | null>(null);
  const [applications, setApplications] = useState<FacilityAccreditationApplication[]>([]);
  const [accreditationCertificates, setAccreditationCertificates] = useState<AccreditationCertificate[]>([]);
  const [documents, setDocuments] = useState<FacilityDocument[]>([]);
  const [checklist, setChecklist] = useState<ChecklistForm>(emptyChecklist);
  const [documentType, setDocumentType] = useState("facility_license");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const activeApplication = useMemo(() => latestApplication(applications), [applications]);
  const checklistComplete = Object.values(checklist).every(Boolean);

  async function loadData() {
    setLoading(true);
    setError("");
    try {
      const profile = await getCurrentMedicalFacility();
      const [apps, docs, certificates] = await Promise.all([
        listFacilityAccreditations(),
        listFacilityDocuments({ facility: profile.id }),
        listAccreditationCertificates({ certificate_type: "facility_accreditation" }),
      ]);
      setFacility(profile);
      setApplications(apps);
      setDocuments(docs);
      setAccreditationCertificates(certificates);
      setChecklist(buildChecklist(latestApplication(apps)));
    } catch {
      setError("Could not load accreditation workflow.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  function toggle(key: ChecklistKey) {
    setChecklist((current) => ({ ...current, [key]: !current[key] }));
    setSuccess("");
  }

  async function saveChecklist() {
    if (!facility) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      const application = activeApplication && ["draft", "more_information_required"].includes(activeApplication.application_status)
        ? await updateFacilityAccreditation(activeApplication.id, checklist)
        : await createFacilityAccreditation({ facility: facility.id, ...checklist });
      setApplications((current) => [application, ...current.filter((item) => item.id !== application.id)]);
      setChecklist(buildChecklist(application));
      setSuccess("Accreditation checklist saved.");
    } catch {
      setError("Could not save accreditation checklist.");
    } finally {
      setBusy(false);
    }
  }

  async function submitChecklist() {
    if (!activeApplication) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      const application = await submitFacilityAccreditation(activeApplication.id);
      setApplications((current) => [application, ...current.filter((item) => item.id !== application.id)]);
      setSuccess("Accreditation application submitted to the State Ministry.");
    } catch {
      setError("Checklist must be complete before submission.");
    } finally {
      setBusy(false);
    }
  }

  async function uploadDocument() {
    if (!facility || !file) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      const formData = new FormData();
      formData.append("facility", facility.id);
      if (activeApplication) formData.append("accreditation_application", activeApplication.id);
      formData.append("document_type", documentType);
      formData.append("file", file);
      const document = await uploadFacilityDocument(formData);
      setDocuments((current) => [document, ...current]);
      setFile(null);
      setSuccess("Document uploaded.");
    } catch {
      setError("Could not upload document. Use PDF, PNG, or JPG under the upload limit.");
    } finally {
      setBusy(false);
    }
  }

  async function startRenewal() {
    if (!facility) return;
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      const renewal = await startFacilityReAccreditation(facility.id);
      setApplications((current) => [renewal, ...current]);
      setChecklist(buildChecklist(renewal));
      setSuccess("Re-accreditation workflow started.");
      await loadData();
    } catch {
      setError("Could not start re-accreditation for this facility.");
    } finally {
      setBusy(false);
    }
  }

  if (loading) {
    return (
      <PortalShell role="facility_admin" title="Accreditation" description="Complete checklist submission and monitor State review status.">
        <p className="rounded-lg border border-neutral-200 bg-white p-4 text-sm font-semibold text-neutral-600 shadow-sm">Loading accreditation workflow...</p>
      </PortalShell>
    );
  }

  return (
    <PortalShell role="facility_admin" title="Accreditation" description="Complete checklist submission and monitor State review status.">
      <div className="grid gap-5">
        {facility ? (
          <section className="grid gap-4 md:grid-cols-4">
            <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Facility status</p>
              <div className="mt-2"><StatusBadge status={facility.accreditation_status} /></div>
            </div>
            <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Current application</p>
              <div className="mt-2"><StatusBadge status={activeApplication?.application_status || "draft"} /></div>
            </div>
            <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Expiry</p>
              <p className="mt-2 text-sm font-bold text-neutral-800">{formatDate(facility.accreditation_expiry_date)}</p>
            </div>
            <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">Checklist</p>
              <p className={`mt-2 text-sm font-bold ${checklistComplete ? "text-brand-700" : "text-warning-700"}`}>{checklistComplete ? "Complete" : "Incomplete"}</p>
            </div>
          </section>
        ) : null}

        <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-sm font-bold text-neutral-900">Facility Accreditation Certificate</h2>
              <p className="mt-1 text-xs text-neutral-500">Your accreditation document is linked directly to this medical facility.</p>
            </div>
            {accreditationCertificates[0]?.certificate_number ? (
              <button
                className="inline-flex h-10 items-center justify-center gap-2 rounded border border-neutral-200 px-3 text-sm font-bold text-neutral-700 hover:bg-neutral-50"
                onClick={() => void downloadAccreditationCertificatePdf(accreditationCertificates[0].id, accreditationCertificates[0].certificate_number)}
                type="button"
              >
                <Download size={16} />
                Download PDF
              </button>
            ) : null}
          </div>
          {accreditationCertificates[0] ? (
            <div className="mt-4 grid gap-3 text-sm sm:grid-cols-4">
              <div><span className="text-xs font-bold uppercase text-neutral-500">Certificate</span><p className="font-semibold text-neutral-900">{accreditationCertificates[0].certificate_number}</p></div>
              <div><span className="text-xs font-bold uppercase text-neutral-500">Status</span><p className="font-semibold capitalize text-neutral-900">{accreditationCertificates[0].effective_status.replaceAll("_", " ")}</p></div>
              <div><span className="text-xs font-bold uppercase text-neutral-500">Issued</span><p className="font-semibold text-neutral-900">{formatDate(accreditationCertificates[0].issue_date)}</p></div>
              <div><span className="text-xs font-bold uppercase text-neutral-500">Expires</span><p className="font-semibold text-neutral-900">{formatDate(accreditationCertificates[0].expiry_date)}</p></div>
            </div>
          ) : (
            <p className="mt-4 rounded bg-neutral-50 p-3 text-sm text-neutral-600">No facility accreditation certificate has been issued yet.</p>
          )}
        </section>

        <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-sm font-bold text-neutral-900">Accreditation Checklist</h2>
              <p className="text-xs text-neutral-500">Every item must be confirmed before State review.</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <button className="inline-flex h-10 items-center justify-center gap-2 rounded bg-white px-4 text-sm font-bold text-neutral-700 ring-1 ring-neutral-200 hover:bg-neutral-50 disabled:opacity-60" disabled={busy} type="button" onClick={saveChecklist}>
                <Save size={16} /> Save
              </button>
              <button className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-600 px-4 text-sm font-bold text-white hover:bg-brand-700 disabled:opacity-60" disabled={busy || !activeApplication || !checklistComplete} type="button" onClick={submitChecklist}>
                <Send size={16} /> Submit
              </button>
            </div>
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            {CHECKLIST.map(([key, label]) => (
              <label key={key} className="flex min-h-11 items-center gap-3 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm font-semibold text-neutral-700">
                <input checked={checklist[key]} className="h-4 w-4 accent-brand-600" type="checkbox" onChange={() => toggle(key)} />
                <span>{label}</span>
              </label>
            ))}
          </div>
        </section>

        <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex items-center gap-2">
            <Upload className="text-brand-700" size={18} />
            <h2 className="text-sm font-bold text-neutral-900">Evidence Documents</h2>
          </div>
          <div className="grid gap-3 md:grid-cols-[240px_1fr_auto] md:items-end">
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-neutral-500">
              Document type
              <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm normal-case tracking-normal text-neutral-700" value={documentType} onChange={(event) => setDocumentType(event.target.value)}>
                {DOCUMENT_TYPES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </label>
            <label className="grid gap-1 text-xs font-bold uppercase tracking-wide text-neutral-500">
              File
              <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm normal-case tracking-normal text-neutral-700" type="file" onChange={(event) => setFile(event.target.files?.[0] || null)} />
            </label>
            <button className="inline-flex h-10 items-center justify-center gap-2 rounded bg-brand-600 px-4 text-sm font-bold text-white hover:bg-brand-700 disabled:opacity-60" disabled={busy || !file} type="button" onClick={uploadDocument}>
              <Upload size={16} /> Upload
            </button>
          </div>
          <div className="mt-5 overflow-hidden rounded-lg border border-neutral-200">
            <table className="w-full text-left text-sm">
              <thead className="bg-neutral-50 text-xs font-bold uppercase tracking-wide text-neutral-500">
                <tr><th className="p-3">Type</th><th className="p-3">Status</th><th className="p-3">Uploaded</th></tr>
              </thead>
              <tbody className="divide-y divide-neutral-200">
                {documents.length ? documents.map((document) => (
                  <tr key={document.id}>
                    <td className="p-3 font-semibold text-neutral-800">{document.document_type.replaceAll("_", " ")}</td>
                    <td className="p-3"><StatusBadge status={document.status} /></td>
                    <td className="p-3 text-neutral-600">{formatDate(document.created_at)}</td>
                  </tr>
                )) : (
                  <tr><td className="p-3 text-neutral-500" colSpan={3}>No accreditation documents uploaded yet.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-sm font-bold text-neutral-900">Application History</h2>
              <p className="text-xs text-neutral-500">State review decisions and renewal applications.</p>
            </div>
            <button className="inline-flex h-10 items-center justify-center gap-2 rounded bg-white px-4 text-sm font-bold text-neutral-700 ring-1 ring-neutral-200 hover:bg-neutral-50 disabled:opacity-60" disabled={busy || !facility || !["approved", "expired", "reaccreditation_due"].includes(facility.accreditation_status)} type="button" onClick={startRenewal}>
              <RefreshCw size={16} /> Start renewal
            </button>
          </div>
          <div className="grid gap-3">
            {applications.length ? applications.map((application) => (
              <div key={application.id} className="rounded border border-neutral-200 bg-neutral-50 p-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <FileText size={16} className="text-brand-700" />
                    <p className="text-sm font-bold text-neutral-900">{application.is_renewal ? "Renewal application" : "Accreditation application"}</p>
                  </div>
                  <StatusBadge status={application.application_status} />
                </div>
                {application.review_comment ? <p className="mt-2 text-sm text-neutral-600">{application.review_comment}</p> : null}
                <p className="mt-2 text-xs font-semibold text-neutral-500">Created {formatDate(application.created_at)} · Submitted {formatDate(application.submitted_at)}</p>
              </div>
            )) : <p className="rounded border border-neutral-200 bg-neutral-50 p-3 text-sm text-neutral-500">No application has been started yet.</p>}
          </div>
        </section>

        {error ? <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700"><AlertCircle size={16} className="mt-0.5 shrink-0" />{error}</div> : null}
        {success ? <div className="rounded-lg bg-brand-50 p-3 text-sm font-semibold text-brand-800">{success}</div> : null}
      </div>
    </PortalShell>
  );
}
