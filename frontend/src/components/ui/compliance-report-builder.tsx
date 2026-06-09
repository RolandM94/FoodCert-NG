"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Download, FileSpreadsheet, FileText, Loader2 } from "lucide-react";
import {
  generateEmployerReport,
  listGeneratedReports,
  type EmployerReportFilters,
} from "@/lib/api/reports";
import type { GeneratedReport, ReportFormat } from "@/types/reports";

type EmployerReportKind = "compliance" | "certificates" | "vaccinations";

const reportKinds: Array<{ value: EmployerReportKind; label: string; description: string }> = [
  { value: "compliance", label: "Compliance overview", description: "Handler totals, certification rate, vaccination coverage, and inspections." },
  { value: "certificates", label: "Certificate expiry", description: "Active, expired, expiring, revoked, and suspended certificates." },
  { value: "vaccinations", label: "Vaccination compliance", description: "Typhoid and hepatitis A coverage by handler and branch." },
];

const formats: Array<{ value: ReportFormat; label: string }> = [
  { value: "pdf", label: "PDF" },
  { value: "excel", label: "Excel" },
  { value: "csv", label: "CSV" },
  { value: "json", label: "JSON" },
];

const certificateStatuses = ["active", "expired", "revoked", "suspended", "pending_validation", "rejected"];
const fitnessStatuses = ["fit", "certification_pending", "temporarily_excluded", "temporarily_not_fit", "excluded"];

function titleize(value: string) {
  return value.replaceAll("_", " ");
}

function reportTypeLabel(value: string) {
  if (value === "employer_compliance") return "Compliance overview";
  if (value === "employer_certificates") return "Certificate expiry";
  if (value === "employer_vaccinations") return "Vaccination compliance";
  return titleize(value);
}

function formatDate(value: string) {
  return new Date(value).toLocaleString("en-NG", { dateStyle: "medium", timeStyle: "short" });
}

function MetricGrid({ report }: { report?: GeneratedReport }) {
  const cards = report?.summary.cards || {};
  const entries = Object.entries(cards).slice(0, 8);
  if (!entries.length) {
    return <div className="rounded-lg border border-neutral-200 bg-white p-5 text-sm text-neutral-500 shadow-sm">Generate a report to preview metrics.</div>;
  }
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {entries.map(([key, value]) => (
        <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm" key={key}>
          <p className="text-xs font-bold uppercase tracking-wide text-neutral-500">{titleize(key)}</p>
          <p className="mt-2 text-2xl font-bold text-neutral-900">{value ?? 0}</p>
        </div>
      ))}
    </div>
  );
}

function GeneratedReportRow({ report }: { report: GeneratedReport }) {
  return (
    <tr>
      <td className="border-b border-neutral-50 py-3 pr-4">
        <p className="font-semibold text-neutral-900">{reportTypeLabel(report.report_type)}</p>
        <p className="mt-1 text-xs text-neutral-500">{formatDate(report.created_at)}</p>
      </td>
      <td className="border-b border-neutral-50 py-3 pr-4 text-sm font-semibold uppercase text-neutral-600">{report.file_format}</td>
      <td className="border-b border-neutral-50 py-3 pr-4 text-sm capitalize text-neutral-600">{report.status}</td>
      <td className="border-b border-neutral-50 py-3 text-right">
        {report.file_url ? (
          <a className="inline-flex h-9 items-center gap-2 rounded border border-neutral-200 px-3 text-sm font-bold text-brand-700 hover:bg-brand-50" href={report.file_url}>
            <Download size={15} />
            Download
          </a>
        ) : (
          <span className="text-sm text-neutral-400">Preview only</span>
        )}
      </td>
    </tr>
  );
}

export function ComplianceReportBuilder({ employerId }: { employerId?: string }) {
  const queryClient = useQueryClient();
  const [reportKind, setReportKind] = useState<EmployerReportKind>("compliance");
  const [format, setFormat] = useState<ReportFormat>("pdf");
  const [branch, setBranch] = useState("");
  const [state, setState] = useState("");
  const [lga, setLga] = useState("");
  const [category, setCategory] = useState("");
  const [certificateStatus, setCertificateStatus] = useState("");
  const [fitnessStatus, setFitnessStatus] = useState("");
  const [vaccineType, setVaccineType] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [latestReport, setLatestReport] = useState<GeneratedReport | undefined>();

  const generatedReportsQuery = useQuery({
    queryKey: ["generated-reports", "employer"],
    queryFn: listGeneratedReports,
  });

  const filters = useMemo<EmployerReportFilters>(() => {
    const next: EmployerReportFilters = {};
    if (branch) next.branch = branch;
    if (state) next.state = state;
    if (lga) next.lga = lga;
    if (category) next.category = category;
    if (certificateStatus) next.certificate_status = certificateStatus;
    if (fitnessStatus) next.fitness_status = fitnessStatus;
    if (vaccineType) next.vaccine_type = vaccineType;
    if (dateFrom) next.date_from = dateFrom;
    if (dateTo) next.date_to = dateTo;
    return next;
  }, [branch, category, certificateStatus, dateFrom, dateTo, fitnessStatus, lga, state, vaccineType]);

  const mutation = useMutation({
    mutationFn: () => generateEmployerReport(employerId!, reportKind, format, filters),
    onSuccess: (report) => {
      setLatestReport(report);
      queryClient.invalidateQueries({ queryKey: ["generated-reports", "employer"] });
    },
  });

  const recentReports = (generatedReportsQuery.data || [])
    .filter((report) => report.report_type.startsWith("employer_"))
    .slice(0, 8);

  return (
    <div className="grid gap-6">
      <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
        <div className="mb-5 flex items-center gap-2">
          <FileText className="text-brand-700" size={18} />
          <h2 className="text-base font-bold text-neutral-900">Report Builder</h2>
        </div>

        <div className="grid gap-4 lg:grid-cols-3">
          {reportKinds.map((kind) => (
            <button
              className={`rounded-lg border p-4 text-left transition ${
                reportKind === kind.value ? "border-brand-300 bg-brand-50 text-brand-700" : "border-neutral-200 bg-white text-neutral-700 hover:bg-neutral-50"
              }`}
              key={kind.value}
              onClick={() => setReportKind(kind.value)}
              type="button"
            >
              <span className="text-sm font-bold">{kind.label}</span>
              <span className="mt-2 block text-sm leading-6 text-neutral-600">{kind.description}</span>
            </button>
          ))}
        </div>

        <div className="mt-5 grid gap-4 md:grid-cols-4">
          <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
            Format
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={format} onChange={(event) => setFormat(event.target.value as ReportFormat)}>
              {formats.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
            </select>
          </label>
          <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
            Branch ID
            <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" value={branch} onChange={(event) => setBranch(event.target.value)} />
          </label>
          <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
            State ID
            <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" value={state} onChange={(event) => setState(event.target.value)} />
          </label>
          <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
            LGA ID
            <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" value={lga} onChange={(event) => setLga(event.target.value)} />
          </label>
          <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
            Category
            <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" placeholder="food_preparer" value={category} onChange={(event) => setCategory(event.target.value)} />
          </label>
          <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
            Certificate status
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={certificateStatus} onChange={(event) => setCertificateStatus(event.target.value)}>
              <option value="">Any</option>
              {certificateStatuses.map((status) => <option key={status} value={status}>{titleize(status)}</option>)}
            </select>
          </label>
          <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
            Fitness status
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={fitnessStatus} onChange={(event) => setFitnessStatus(event.target.value)}>
              <option value="">Any</option>
              {fitnessStatuses.map((status) => <option key={status} value={status}>{titleize(status)}</option>)}
            </select>
          </label>
          <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
            Vaccine
            <select className="h-10 rounded border border-neutral-200 bg-white px-3 text-sm" value={vaccineType} onChange={(event) => setVaccineType(event.target.value)}>
              <option value="">Any</option>
              <option value="typhoid">Typhoid</option>
              <option value="hepatitis_a">Hepatitis A</option>
            </select>
          </label>
          <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
            From
            <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" type="date" value={dateFrom} onChange={(event) => setDateFrom(event.target.value)} />
          </label>
          <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
            To
            <input className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-sm" type="date" value={dateTo} onChange={(event) => setDateTo(event.target.value)} />
          </label>
        </div>

        <button
          className="mt-5 inline-flex h-11 items-center gap-2 rounded-lg bg-brand-600 px-5 text-sm font-bold text-white hover:bg-brand-700 disabled:opacity-60"
          disabled={!employerId || mutation.isPending}
          onClick={() => mutation.mutate()}
          type="button"
        >
          {mutation.isPending ? <Loader2 className="animate-spin" size={16} /> : <FileSpreadsheet size={16} />}
          {mutation.isPending ? "Generating..." : "Generate Report"}
        </button>
        {mutation.isError ? <p className="mt-3 text-sm font-semibold text-danger-500">Could not generate report. Check the filters and try again.</p> : null}
      </section>

      <MetricGrid report={latestReport} />

      <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
        <div className="mb-4 flex items-center justify-between gap-3">
          <h2 className="text-base font-bold text-neutral-900">Generated Reports</h2>
          <span className="text-sm font-semibold text-neutral-500">{generatedReportsQuery.isFetching ? "Loading..." : `${recentReports.length} recent`}</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead className="text-xs font-bold uppercase tracking-wide text-neutral-500">
              <tr>
                <th className="border-b border-neutral-100 py-2 pr-4">Report</th>
                <th className="border-b border-neutral-100 py-2 pr-4">Format</th>
                <th className="border-b border-neutral-100 py-2 pr-4">Status</th>
                <th className="border-b border-neutral-100 py-2 text-right">File</th>
              </tr>
            </thead>
            <tbody>
              {recentReports.map((report) => <GeneratedReportRow key={report.id} report={report} />)}
              {!recentReports.length ? <tr><td className="py-6 text-center text-neutral-500" colSpan={4}>No generated employer reports yet.</td></tr> : null}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
