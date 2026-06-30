"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  Building2,
  CheckCircle2,
  ClipboardCheck,
  Clock3,
  FileCheck2,
  FlaskConical,
  MapPinned,
  Megaphone,
  RefreshCw,
  ShieldCheck,
  Stethoscope,
} from "lucide-react";

import { OperationalSnapshot } from "@/components/dashboards/operational-snapshot";
import { PortalShell } from "@/components/layout/portal-shell";
import { DashboardCard } from "@/components/ui/dashboard-card";
import { AnalyticsWorkspaceHome } from "@/features/reports/analytics-workspace-home";
import { getApiErrorMessage } from "@/lib/api/client";
import { listBroadcasts } from "@/lib/api/notifications";
import { getStateDashboard } from "@/lib/api/reports";
import {
  fetchStateFacilities,
  fetchStateLgas,
  fetchStateProfileSettings,
  fetchStateReports,
} from "@/lib/api/state";

const FOOD_HANDLER_CATEGORY_OPTIONS = [
  ["", "All handler categories"],
  ["kitchen_staff", "Kitchen staff"],
  ["food_preparer", "Food preparers"],
  ["serving_catering", "Serving and catering staff"],
  ["food_packer", "Food packers"],
  ["bakery_worker", "Bakery workers"],
  ["food_processing_operator", "Food processing operators"],
  ["bartender", "Bartenders"],
  ["dishwasher", "Dishwashers"],
  ["food_delivery", "Food delivery personnel"],
  ["street_vendor", "Street food vendors"],
  ["food_storage_handler", "Food storage handlers"],
  ["concession_worker", "Concession stand workers"],
  ["airline_catering", "Airline catering vendors"],
  ["train_catering", "Train catering vendors"],
  ["vessel_catering", "Vessel catering vendors"],
  ["livestock_meat", "Livestock, butchery and meat workers"],
  ["emergency_food_worker", "Emergency food workers"],
] as const;

const CERTIFICATE_STATUS_OPTIONS = [
  ["", "All certificate statuses"],
  ["active", "Active"],
  ["expired", "Expired"],
  ["suspended", "Suspended"],
  ["revoked", "Revoked"],
  ["pending_validation", "Pending validation"],
] as const;

type DashboardFilters = {
  date_from: string;
  date_to: string;
  lga: string;
  facility: string;
  food_handler_category: string;
  certificate_status: string;
};

function dateTimeLabel(value?: string | null) {
  if (!value) return "Not set";
  return new Date(value).toLocaleString("en-NG", { dateStyle: "medium", timeStyle: "short" });
}

function statusTone(status: string) {
  if (status === "active") return "bg-brand-50 text-brand-800 border-brand-100";
  if (status === "implementation_in_progress") return "bg-warning-50 text-warning-900 border-warning-100";
  return "bg-neutral-100 text-neutral-700 border-neutral-200";
}

function reportStatusTone(status: string) {
  if (status === "accepted") return "bg-brand-50 text-brand-800";
  if (status === "submitted") return "bg-info-100 text-blue-800";
  if (status === "returned") return "bg-warning-100 text-warning-900";
  return "bg-neutral-100 text-neutral-700";
}

export default function StateDashboardPage() {
  const [draftFilters, setDraftFilters] = useState<DashboardFilters>({
    date_from: "",
    date_to: "",
    lga: "",
    facility: "",
    food_handler_category: "",
    certificate_status: "",
  });
  const [appliedFilters, setAppliedFilters] = useState<DashboardFilters>({
    date_from: "",
    date_to: "",
    lga: "",
    facility: "",
    food_handler_category: "",
    certificate_status: "",
  });

  const profileQuery = useQuery({
    queryKey: ["state-profile-settings-dashboard"],
    queryFn: fetchStateProfileSettings,
  });

  const stateId = profileQuery.data?.state ?? "";
  const lgaQuery = useQuery({
    queryKey: ["state-dashboard-lgas", stateId],
    queryFn: () => fetchStateLgas(stateId),
    enabled: Boolean(stateId),
  });

  const facilityQuery = useQuery({
    queryKey: ["state-dashboard-facilities", draftFilters.lga],
    queryFn: () => fetchStateFacilities({ lga: draftFilters.lga || undefined }),
  });

  const snapshotQuery = useQuery({
    queryKey: ["state-operational-dashboard", appliedFilters],
    queryFn: () =>
      getStateDashboard({
        date_from: appliedFilters.date_from || undefined,
        date_to: appliedFilters.date_to || undefined,
        lga: appliedFilters.lga || undefined,
        facility: appliedFilters.facility || undefined,
        food_handler_category: appliedFilters.food_handler_category || undefined,
        certificate_status: appliedFilters.certificate_status || undefined,
      }),
  });

  const reportsQuery = useQuery({
    queryKey: ["state-dashboard-reports"],
    queryFn: () => fetchStateReports(),
  });

  const awarenessQuery = useQuery({
    queryKey: ["state-public-awareness-dashboard"],
    queryFn: listBroadcasts,
  });

  const reports = useMemo(() => reportsQuery.data ?? [], [reportsQuery.data]);
  const broadcasts = useMemo(() => awarenessQuery.data ?? [], [awarenessQuery.data]);
  const publishedAwareness = useMemo(() => broadcasts.filter((item) => item.status === "sent"), [broadcasts]);

  const latestReport = useMemo(
    () =>
      [...reports].sort(
        (a, b) =>
          new Date(b.submitted_at || b.updated_at).getTime() - new Date(a.submitted_at || a.updated_at).getTime(),
      )[0],
    [reports],
  );

  const implementationStatus = useMemo(() => {
    const approvedFacilities = Number(snapshotQuery.data?.cards.approved_facilities ?? 0);
    const pendingAdoption = Number(snapshotQuery.data?.cards.pending_facility_adoption ?? 0);
    if (approvedFacilities > 0 && pendingAdoption === 0) {
      return { label: "Active", tone: "active", helper: "Core state implementation queues are active and facility template adoption is in place." };
    }
    if (approvedFacilities > 0 || Number(snapshotQuery.data?.cards.pending_facility_applications ?? 0) > 0) {
      return { label: "Implementation in progress", tone: "implementation_in_progress", helper: "State rollout is underway, but some facilities or queues still need closure." };
    }
    return { label: "Policy adoption pending", tone: "pending", helper: "State profile exists, but implementation activity is still limited." };
  }, [snapshotQuery.data?.cards.approved_facilities, snapshotQuery.data?.cards.pending_facility_adoption, snapshotQuery.data?.cards.pending_facility_applications]);

  const topCards = useMemo(() => {
    const riskRows = (snapshotQuery.data?.charts?.high_risk_declaration_trends as Array<{ total?: number }> | undefined) ?? [];
    return [
      {
        label: "Facility adoption",
        value: snapshotQuery.data?.cards.facilities_adopted_state_template,
        icon: Building2,
        detail: "Facilities that have adopted the current state declaration template chain.",
      },
      {
        label: "Latest template",
        value: snapshotQuery.data?.cards.facilities_using_latest_template,
        icon: RefreshCw,
        detail: "Facilities aligned to the latest state declaration version.",
      },
      {
        label: "Declarations",
        value: snapshotQuery.data?.cards.declarations_submitted_in_state,
        icon: ClipboardCheck,
        detail: "Total declarations submitted within this state.",
      },
      {
        label: "Pending adoption",
        value: snapshotQuery.data?.cards.pending_facility_adoption,
        icon: Clock3,
        detail: "Approved facilities still pending declaration template adoption.",
      },
      {
        label: "Risk flags",
        value: riskRows.reduce((sum, row) => sum + Number(row.total ?? 0), 0),
        icon: AlertTriangle,
        detail: "Total flagged declarations across facilities in this state.",
      },
      {
        label: "Awareness campaigns",
        value: publishedAwareness.length,
        icon: Megaphone,
        detail: "Published state notices and campaigns currently available to platform audiences.",
      },
    ];
  }, [publishedAwareness.length, snapshotQuery.data]);

  const oversightCards = useMemo(
    () => [
      { label: "Federal policies adopted", value: profileQuery.data ? 1 : 0, icon: ShieldCheck, detail: "The current state policy configuration inherited from the federal policy layer." },
      { label: "Approved facilities", value: Number(snapshotQuery.data?.cards.approved_facilities ?? 0), icon: Building2, detail: "Facilities currently approved to operate in the state programme." },
      { label: "Pending facility applications", value: Number(snapshotQuery.data?.cards.pending_facility_applications ?? 0), icon: Clock3, detail: "Facility applications awaiting accreditation review or decision." },
      { label: "Facilities expiring soon", value: Number(snapshotQuery.data?.cards.facilities_due_for_reaccreditation ?? 0), icon: AlertTriangle, detail: "Approved facilities nearing re-accreditation deadline." },
      { label: "Assessments completed", value: Number(snapshotQuery.data?.cards.assessments_completed ?? 0), icon: Stethoscope, detail: "Assessments that have moved through to a completed downstream decision state." },
      { label: "Certificates issued", value: Number(snapshotQuery.data?.cards.certificates_issued_total ?? 0), icon: FileCheck2, detail: "Certificates in scope for the current filter set." },
      { label: "Temporary unfit reports", value: Number(snapshotQuery.data?.cards.temporary_unfit_reports ?? 0), icon: AlertTriangle, detail: "Assessments currently resolved as temporarily not fit." },
      { label: "Pending lab results", value: Number(snapshotQuery.data?.cards.pending_lab_results ?? 0), icon: FlaskConical, detail: "Lab work that has not yet fully cleared into the medical decision flow." },
      { label: "Overdue doctor reviews", value: Number(snapshotQuery.data?.cards.overdue_doctor_reviews ?? 0), icon: Clock3, detail: "Doctor review steps still open beyond the expected internal turnaround window." },
      { label: "Expired certificates", value: Number(snapshotQuery.data?.cards.expired_certificates ?? 0), icon: AlertTriangle, detail: "Certificates whose validity windows have elapsed." },
      { label: "Compliance cases", value: Number(snapshotQuery.data?.cards.compliance_cases ?? 0), icon: ClipboardCheck, detail: "Inspection and enforcement records requiring compliance follow-up." },
      { label: "Public awareness campaigns", value: publishedAwareness.length, icon: Megaphone, detail: "Published state notices and awareness campaigns." },
    ],
    [profileQuery.data, publishedAwareness.length, snapshotQuery.data],
  );

  const lgaRows = useMemo(
    () =>
      ((snapshotQuery.data?.charts?.lga_drill_down as Array<Record<string, string | number>> | undefined) ?? []).sort(
        (a, b) => Number(b.certification_coverage ?? 0) - Number(a.certification_coverage ?? 0),
      ),
    [snapshotQuery.data?.charts],
  );

  const operationalQueues = useMemo(
    () => (snapshotQuery.data?.sections?.operational_queues as Array<Record<string, string | number>> | undefined) ?? [],
    [snapshotQuery.data?.sections],
  );

  return (
    <PortalShell
      role="state_admin"
      title="Dashboard Analytics"
      description="Track implementation, facility oversight, compliance pressure, reporting posture, and LGA performance while still building state analytics workbooks and dashboards."
    >
      <div className="grid gap-6">
        <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <div className="flex flex-col gap-3 xl:flex-row xl:items-end xl:justify-between">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-brand-700">Dashboard Filters</p>
              <h2 className="mt-1 text-lg font-bold text-neutral-900">Filter the state oversight picture</h2>
              <p className="mt-1 text-sm text-neutral-500">Use date, geography, facility, handler category, and certificate status to focus the state dashboard.</p>
            </div>
            <div className="flex gap-2">
              <button
                className="inline-flex h-10 items-center justify-center rounded-lg border border-neutral-200 px-4 text-sm font-semibold text-neutral-700"
                onClick={() => {
                  const empty = { date_from: "", date_to: "", lga: "", facility: "", food_handler_category: "", certificate_status: "" };
                  setDraftFilters(empty);
                  setAppliedFilters(empty);
                }}
                type="button"
              >
                Reset
              </button>
              <button
                className="inline-flex h-10 items-center justify-center rounded-lg bg-brand-700 px-4 text-sm font-semibold text-white"
                onClick={() => setAppliedFilters(draftFilters)}
                type="button"
              >
                Apply filters
              </button>
            </div>
          </div>

          <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-6">
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Date from
              <input className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm" type="date" value={draftFilters.date_from} onChange={(event) => setDraftFilters((current) => ({ ...current, date_from: event.target.value }))} />
            </label>
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Date to
              <input className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm" type="date" value={draftFilters.date_to} onChange={(event) => setDraftFilters((current) => ({ ...current, date_to: event.target.value }))} />
            </label>
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              LGA
              <select className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm" value={draftFilters.lga} onChange={(event) => setDraftFilters((current) => ({ ...current, lga: event.target.value, facility: "" }))}>
                <option value="">All LGAs</option>
                {(lgaQuery.data ?? []).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
              </select>
            </label>
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Facility
              <select className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm" value={draftFilters.facility} onChange={(event) => setDraftFilters((current) => ({ ...current, facility: event.target.value }))}>
                <option value="">All facilities</option>
                {(facilityQuery.data ?? []).map((item) => <option key={item.id} value={item.id}>{item.facility_name}</option>)}
              </select>
            </label>
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Handler category
              <select className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm" value={draftFilters.food_handler_category} onChange={(event) => setDraftFilters((current) => ({ ...current, food_handler_category: event.target.value }))}>
                {FOOD_HANDLER_CATEGORY_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </label>
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Certificate status
              <select className="h-11 rounded-lg border border-neutral-200 bg-white px-3 text-sm" value={draftFilters.certificate_status} onChange={(event) => setDraftFilters((current) => ({ ...current, certificate_status: event.target.value }))}>
                {CERTIFICATE_STATUS_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </label>
          </div>
        </section>

        <section className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
          <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-brand-700">Implementation Status</p>
            <h2 className="mt-1 text-lg font-bold text-neutral-900">{profileQuery.data?.state_name || snapshotQuery.data?.state?.name || "State Ministry"}</h2>
            <div className={`mt-4 inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${statusTone(implementationStatus.tone)}`}>
              {implementationStatus.label}
            </div>
            <p className="mt-3 text-sm text-neutral-600">{implementationStatus.helper}</p>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <div className="rounded-lg border border-neutral-200 bg-neutral-50 px-4 py-3">
                <p className="text-xs font-bold uppercase tracking-[0.16em] text-neutral-500">Policy baseline</p>
                <p className="mt-2 text-2xl font-bold text-neutral-900">{profileQuery.data ? 1 : 0}</p>
                <p className="mt-1 text-sm text-neutral-500">Federal policy configuration adopted into state settings.</p>
              </div>
              <div className="rounded-lg border border-neutral-200 bg-neutral-50 px-4 py-3">
                <p className="text-xs font-bold uppercase tracking-[0.16em] text-neutral-500">M&amp;E posture</p>
                <p className={`mt-2 inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${reportStatusTone(latestReport?.status || "draft")}`}>
                  {latestReport ? latestReport.status.replaceAll("_", " ") : "No report yet"}
                </p>
                <p className="mt-2 text-sm text-neutral-500">
                  {latestReport ? `${latestReport.report_type.replaceAll("_", " ")} updated ${dateTimeLabel(latestReport.submitted_at || latestReport.updated_at)}.` : "No state report has been generated yet."}
                </p>
              </div>
            </div>
          </div>

          <OperationalSnapshot
            title="State Snapshot"
            description="Keep declaration adoption, facility rollout, risk signals, and awareness activity in view."
            cards={topCards}
            loading={snapshotQuery.isLoading}
            error={snapshotQuery.isError ? getApiErrorMessage(snapshotQuery.error, "Could not load state dashboard snapshot.") : ""}
          />
        </section>

        <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {oversightCards.map((card) => (
            <DashboardCard key={card.label} icon={card.icon} label={card.label} value={card.value} detail={card.detail} />
          ))}
        </section>

        <section className="grid gap-4 xl:grid-cols-[1.15fr_0.85fr]">
          <div className="rounded-lg border border-neutral-200 bg-white shadow-sm">
            <div className="flex items-center justify-between border-b border-neutral-200 px-5 py-4">
              <div>
                <p className="text-sm font-bold text-neutral-900">LGA performance table</p>
                <p className="mt-1 text-sm text-neutral-500">Compare certification and vaccination coverage by LGA for the current filter set.</p>
              </div>
              <div className="inline-flex items-center gap-2 rounded-full bg-neutral-100 px-3 py-1 text-xs font-semibold text-neutral-700">
                <MapPinned size={12} />
                {lgaRows.length} LGAs
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-neutral-200 text-sm">
                <thead className="bg-neutral-50 text-left text-xs font-bold uppercase tracking-[0.16em] text-neutral-500">
                  <tr>
                    <th className="px-5 py-3">LGA</th>
                    <th className="px-5 py-3">Handlers</th>
                    <th className="px-5 py-3">Certified</th>
                    <th className="px-5 py-3">Certification %</th>
                    <th className="px-5 py-3">Vaccination %</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-200 bg-white">
                  {lgaRows.map((row) => (
                    <tr key={String(row.lga_id || row.lga_name)}>
                      <td className="px-5 py-4 font-semibold text-neutral-900">{String(row.lga_name || "Unassigned")}</td>
                      <td className="px-5 py-4 text-neutral-600">{Number(row.registered_handlers ?? 0)}</td>
                      <td className="px-5 py-4 text-neutral-600">{Number(row.certified_handlers ?? 0)}</td>
                      <td className="px-5 py-4">
                        <span className="rounded-full bg-brand-50 px-2.5 py-1 text-xs font-semibold text-brand-800">{Number(row.certification_coverage ?? 0)}%</span>
                      </td>
                      <td className="px-5 py-4">
                        <span className="rounded-full bg-info-100 px-2.5 py-1 text-xs font-semibold text-blue-800">{Number(row.vaccination_coverage ?? 0)}%</span>
                      </td>
                    </tr>
                  ))}
                  {!snapshotQuery.isLoading && lgaRows.length === 0 ? (
                    <tr><td className="px-5 py-6 text-neutral-500" colSpan={5}>No LGA performance rows match the current filters.</td></tr>
                  ) : null}
                </tbody>
              </table>
            </div>
          </div>

          <div className="grid gap-4">
            <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
              <p className="text-sm font-bold text-neutral-900">Operational queues</p>
              <div className="mt-4 grid gap-3">
                {operationalQueues.map((queue) => (
                  <a key={String(queue.name)} className="rounded-lg border border-neutral-200 bg-neutral-50 px-4 py-3" href={String(queue.href || "#")}>
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="text-sm font-semibold text-neutral-900">{String(queue.name)}</p>
                        <p className="mt-1 text-xs uppercase tracking-[0.16em] text-neutral-500">{String(queue.status || "").replaceAll("_", " ")}</p>
                      </div>
                      <span className="text-xl font-bold text-neutral-900">{Number(queue.count ?? 0)}</span>
                    </div>
                  </a>
                ))}
              </div>
            </div>

            <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
              <p className="text-sm font-bold text-neutral-900">State reporting & awareness</p>
              <div className="mt-4 space-y-4">
                <div className="rounded-lg border border-neutral-200 bg-neutral-50 px-4 py-3">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 size={14} className="text-brand-700" />
                    <p className="text-sm font-semibold text-neutral-900">Latest M&amp;E report</p>
                  </div>
                  <p className="mt-2 text-sm text-neutral-600">
                    {latestReport ? `${latestReport.report_type.replaceAll("_", " ")} • ${latestReport.status.replaceAll("_", " ")}` : "No generated state report yet."}
                  </p>
                  <p className="mt-1 text-xs text-neutral-500">{latestReport ? dateTimeLabel(latestReport.submitted_at || latestReport.updated_at) : "Generate the first report from Reports & M&E."}</p>
                </div>

                <div className="rounded-lg border border-neutral-200 bg-neutral-50 px-4 py-3">
                  <div className="flex items-center gap-2">
                    <Megaphone size={14} className="text-brand-700" />
                    <p className="text-sm font-semibold text-neutral-900">Public awareness</p>
                  </div>
                  <p className="mt-2 text-sm text-neutral-600">
                    {publishedAwareness[0] ? publishedAwareness[0].title : "No published awareness campaign yet."}
                  </p>
                  <p className="mt-1 text-xs text-neutral-500">
                    {publishedAwareness[0] ? `Published ${dateTimeLabel(publishedAwareness[0].sent_at)}` : "Use Public Awareness to publish notices and campaigns."}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <AnalyticsWorkspaceHome
          role="state_admin"
          title="Dashboard Analytics"
          description="Choose the right state dataset, shape your workbook, and publish focused dashboards for ministry operations and oversight."
          reportsHref="/state/reports"
          templatesHref="/state/dashboard/templates"
          worksheetBuilderHref="/state/dashboard/worksheet-builder"
          dashboardBuilderHref="/state/dashboard/dashboard-builder"
          canvasBuilderHref="/state/dashboard/canvas-builder"
          publishedBaseHref="/state/dashboard/published"
          datasetLibraryBaseHref="/state/dashboard/datasets"
        />
      </div>
    </PortalShell>
  );
}
