"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { StandardsPolicyWorkspaceShell } from "@/features/standards/standards-policy-workspaces";
import {
  getPolicyVersion,
  submitPolicyVersion,
  approvePolicyVersion,
  publishPolicyVersion,
  retirePolicyVersion,
  archivePolicyVersion,
  returnPolicyVersion,
  listStandardsAuditLogs,
} from "@/lib/api/standards";
import type { PolicyVersionDetail, StandardsAuditLog } from "@/types/standards";
import { getApiErrorMessage } from "@/lib/api/client";

const TABS = [
  "Categories",
  "Medical Tests",
  "Vaccinations",
  "Certificate",
  "Return-to-Work",
  "Facility Reqs",
  "Reporting",
  "M&E",
  "Documents",
  "Acknowledgements",
  "History",
] as const;

type Tab = (typeof TABS)[number];

const COMPLETENESS_LABELS: Record<string, string> = {
  has_certificate_template: "Certificate Template",
  has_medical_test_rules: "Medical Test Rules",
  has_validity_rules: "Validity Rules",
  has_reporting_template: "Reporting Template",
  has_handler_categories: "Handler Categories",
  has_vaccination_rules: "Vaccination Rules",
};

function statusBadgeClass(status: string) {
  switch (status) {
    case "active":
      return "bg-brand-50 text-brand-700";
    case "draft":
      return "bg-neutral-100 text-neutral-700";
    case "under_review":
      return "bg-info-50 text-info-700";
    case "retired":
      return "bg-neutral-100 text-neutral-500";
    case "approved":
      return "bg-brand-50 text-brand-700";
    case "archived":
      return "bg-neutral-100 text-neutral-500";
    default:
      return "bg-warning-50 text-warning-700";
  }
}

function formatLabel(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function auditEvent(row: StandardsAuditLog) {
  return row.event || String(row.metadata?.event ?? "") || row.action;
}

function auditValueSummary(value: Record<string, unknown> | null) {
  if (!value || Object.keys(value).length === 0) return "\u2014";
  return Object.entries(value)
    .slice(0, 3)
    .map(([key, item]) => `${formatLabel(key)}: ${String(item)}`)
    .join("; ");
}

export default function PolicyVersionDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<Tab>("Categories");
  const [actionError, setActionError] = useState<string | null>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ["policy-version", id],
    queryFn: () => getPolicyVersion(id),
  });
  const { data: history } = useQuery({
    queryKey: ["standards-change-history", "PolicyVersion", id],
    queryFn: () => listStandardsAuditLogs({ target_type: "PolicyVersion", target_id: id }),
  });

  const pv = data as PolicyVersionDetail | undefined;
  const historyRows = Array.isArray(history) ? history : [];

  const invalidateKeys = () => {
    queryClient.invalidateQueries({ queryKey: ["policy-version", id] });
    queryClient.invalidateQueries({ queryKey: ["standards-policy-versions"] });
  };

  const submitMutation = useMutation({
    mutationFn: () => submitPolicyVersion(id),
    onSuccess: invalidateKeys,
    onError: (err) => setActionError(getApiErrorMessage(err, "Failed to submit")),
  });

  const approveMutation = useMutation({
    mutationFn: () => approvePolicyVersion(id),
    onSuccess: invalidateKeys,
    onError: (err) => setActionError(getApiErrorMessage(err, "Failed to approve")),
  });

  const returnMutation = useMutation({
    mutationFn: () => returnPolicyVersion(id),
    onSuccess: invalidateKeys,
    onError: (err) => setActionError(getApiErrorMessage(err, "Failed to return")),
  });

  const publishMutation = useMutation({
    mutationFn: () => publishPolicyVersion(id),
    onSuccess: invalidateKeys,
    onError: (err) => setActionError(getApiErrorMessage(err, "Failed to publish")),
  });

  const retireMutation = useMutation({
    mutationFn: () => retirePolicyVersion(id),
    onSuccess: invalidateKeys,
    onError: (err) => setActionError(getApiErrorMessage(err, "Failed to retire")),
  });

  const archiveMutation = useMutation({
    mutationFn: () => archivePolicyVersion(id),
    onSuccess: invalidateKeys,
    onError: (err) => setActionError(getApiErrorMessage(err, "Failed to archive")),
  });

  return (
    <StandardsPolicyWorkspaceShell workspace="policy-governance"
      title="Policy Version Detail"
      description="View and manage this policy version."
    >
      <div className="grid gap-5">
        {error && (
          <div className="rounded-lg border border-danger-200 bg-danger-50 p-4 text-sm text-danger-700">
            {getApiErrorMessage(error, "Failed to load policy version")}
          </div>
        )}

        {actionError && (
          <div className="rounded-lg border border-danger-200 bg-danger-50 p-4 text-sm text-danger-700">
            {actionError}
          </div>
        )}

        {isLoading && (
          <p className="text-sm text-neutral-500">Loading...</p>
        )}

        {pv && (
          <>
            <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div className="grid gap-1">
                  <h2 className="text-2xl font-semibold text-neutral-900">
                    {pv.version_code}
                  </h2>
                  <p className="text-base text-neutral-700">{pv.title}</p>
                  <div className="mt-2 flex flex-wrap items-center gap-2">
                    <span
                      className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${statusBadgeClass(pv.status)}`}
                    >
                      {formatLabel(pv.status)}
                    </span>
                    <span className="inline-flex rounded-full bg-neutral-100 px-2.5 py-0.5 text-xs font-medium text-neutral-700">
                      {formatLabel(pv.version_type)}
                    </span>
                  </div>
                  <div className="mt-3 grid gap-1 text-sm text-neutral-600">
                    {pv.effective_start_date && (
                      <p>
                        Effective:{" "}
                        {new Date(pv.effective_start_date).toLocaleDateString()}
                      </p>
                    )}
                    <p>
                      Created by {pv.created_by_name} on{" "}
                      {new Date(pv.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  {pv.status === "draft" && (
                    <button
                      className="inline-flex h-10 items-center gap-2 rounded-md bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
                      disabled={submitMutation.isPending}
                      onClick={() => {
                        setActionError(null);
                        submitMutation.mutate();
                      }}
                    >
                      Submit for Review
                    </button>
                  )}
                  {pv.status === "under_review" && (
                    <>
                      <button
                        className="inline-flex h-10 items-center gap-2 rounded-md bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
                        disabled={approveMutation.isPending}
                        onClick={() => {
                          setActionError(null);
                          approveMutation.mutate();
                        }}
                      >
                        Approve
                      </button>
                      <button
                        className="inline-flex h-10 items-center gap-2 rounded-md border border-neutral-200 bg-white px-4 text-sm font-medium text-neutral-700 hover:bg-neutral-50 disabled:opacity-50"
                        disabled={returnMutation.isPending}
                        onClick={() => {
                          setActionError(null);
                          returnMutation.mutate();
                        }}
                      >
                        Return
                      </button>
                    </>
                  )}
                  {pv.status === "approved" && (
                    <button
                      className="inline-flex h-10 items-center gap-2 rounded-md bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
                      disabled={publishMutation.isPending}
                      onClick={() => {
                        setActionError(null);
                        publishMutation.mutate();
                      }}
                    >
                      Publish
                    </button>
                  )}
                  {pv.status === "active" && (
                    <button
                      className="inline-flex h-10 items-center gap-2 rounded-md bg-danger-50 px-4 text-sm font-medium text-danger-700 hover:bg-danger-100 disabled:opacity-50"
                      disabled={retireMutation.isPending}
                      onClick={() => {
                        setActionError(null);
                        retireMutation.mutate();
                      }}
                    >
                      Retire
                    </button>
                  )}
                  {pv.status === "retired" && (
                    <button
                      className="inline-flex h-10 items-center gap-2 rounded-md border border-neutral-200 bg-white px-4 text-sm font-medium text-neutral-700 hover:bg-neutral-50 disabled:opacity-50"
                      disabled={archiveMutation.isPending}
                      onClick={() => {
                        setActionError(null);
                        archiveMutation.mutate();
                      }}
                    >
                      Archive
                    </button>
                  )}
                </div>
              </div>
            </div>

            <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
              <h3 className="mb-3 text-sm font-semibold text-neutral-900">
                Completeness
              </h3>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {Object.entries(COMPLETENESS_LABELS).map(([key, label]) => {
                  const complete =
                    pv.completeness?.[
                      key as keyof typeof pv.completeness
                    ] ?? false;
                  return (
                    <div key={key} className="flex items-center gap-2 text-sm">
                      {complete ? (
                        <span className="text-brand-600 font-bold">&#10003;</span>
                      ) : (
                        <span className="text-danger-400 font-bold">&#10005;</span>
                      )}
                      <span className="text-neutral-700">{label}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="rounded-lg border border-neutral-200 bg-white shadow-sm">
              <div className="flex gap-0 overflow-x-auto border-b border-neutral-200">
                {TABS.map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`whitespace-nowrap px-4 py-3 text-sm font-medium ${
                      activeTab === tab
                        ? "border-b-2 border-brand-600 text-brand-700"
                        : "text-neutral-600 hover:text-neutral-900"
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              <div className="p-5">
                {activeTab === "Categories" && (
                  <div className="grid gap-6">
                    <div>
                      <h4 className="mb-2 text-sm font-semibold text-neutral-900">
                        Food Handler Categories
                      </h4>
                      <table className="w-full text-left text-sm">
                        <thead>
                          <tr className="border-b border-neutral-200 text-neutral-500">
                            <th className="pb-2 pr-4 font-medium">Name</th>
                            <th className="pb-2 pr-4 font-medium">Code</th>
                            <th className="pb-2 font-medium">Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          {pv.food_handler_categories?.length ? (
                            pv.food_handler_categories.map((item) => (
                              <tr
                                key={item.id}
                                className="border-b border-neutral-100"
                              >
                                <td className="py-2 pr-4">{item.name}</td>
                                <td className="py-2 pr-4">{item.code}</td>
                                <td className="py-2">{formatLabel(item.status)}</td>
                              </tr>
                            ))
                          ) : (
                            <tr>
                              <td
                                colSpan={3}
                                className="py-4 text-neutral-500"
                              >
                                No food handler categories.
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                    <div>
                      <h4 className="mb-2 text-sm font-semibold text-neutral-900">
                        Establishment Categories
                      </h4>
                      <table className="w-full text-left text-sm">
                        <thead>
                          <tr className="border-b border-neutral-200 text-neutral-500">
                            <th className="pb-2 pr-4 font-medium">Name</th>
                            <th className="pb-2 pr-4 font-medium">Code</th>
                            <th className="pb-2 font-medium">Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          {pv.establishment_categories?.length ? (
                            pv.establishment_categories.map((item) => (
                              <tr
                                key={item.id}
                                className="border-b border-neutral-100"
                              >
                                <td className="py-2 pr-4">{item.name}</td>
                                <td className="py-2 pr-4">{item.code}</td>
                                <td className="py-2">{formatLabel(item.status)}</td>
                              </tr>
                            ))
                          ) : (
                            <tr>
                              <td
                                colSpan={3}
                                className="py-4 text-neutral-500"
                              >
                                No establishment categories.
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {activeTab === "Medical Tests" && (
                  <div className="grid gap-6">
                    <div>
                      <h4 className="mb-2 text-sm font-semibold text-neutral-900">
                        Medical Test Rules
                      </h4>
                      <table className="w-full text-left text-sm">
                        <thead>
                          <tr className="border-b border-neutral-200 text-neutral-500">
                            <th className="pb-2 pr-4 font-medium">Name</th>
                            <th className="pb-2 pr-4 font-medium">Code</th>
                            <th className="pb-2 pr-4 font-medium">Rule Type</th>
                            <th className="pb-2 pr-4 font-medium">Test Type</th>
                            <th className="pb-2 pr-4 font-medium">Blocks Cert</th>
                            <th className="pb-2 font-medium">Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          {pv.medical_test_rules?.length ? (
                            pv.medical_test_rules.map((item) => (
                              <tr
                                key={item.id}
                                className="border-b border-neutral-100"
                              >
                                <td className="py-2 pr-4">{item.name}</td>
                                <td className="py-2 pr-4">{item.code}</td>
                                <td className="py-2 pr-4">
                                  {formatLabel(item.rule_type)}
                                </td>
                                <td className="py-2 pr-4">
                                  {formatLabel(item.test_type)}
                                </td>
                                <td className="py-2 pr-4">
                                  {item.blocks_certification ? "Yes" : "No"}
                                </td>
                                <td className="py-2">{formatLabel(item.status)}</td>
                              </tr>
                            ))
                          ) : (
                            <tr>
                              <td
                                colSpan={6}
                                className="py-4 text-neutral-500"
                              >
                                No medical test rules.
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                    <div>
                      <h4 className="mb-2 text-sm font-semibold text-neutral-900">
                        Physical Examination Rules
                      </h4>
                      <table className="w-full text-left text-sm">
                        <thead>
                          <tr className="border-b border-neutral-200 text-neutral-500">
                            <th className="pb-2 pr-4 font-medium">Indicator</th>
                            <th className="pb-2 pr-4 font-medium">Code</th>
                            <th className="pb-2 pr-4 font-medium">Severity</th>
                            <th className="pb-2 pr-4 font-medium">Blocks Cert</th>
                            <th className="pb-2 font-medium">Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          {pv.physical_examination_rules?.length ? (
                            pv.physical_examination_rules.map((item) => (
                              <tr
                                key={item.id}
                                className="border-b border-neutral-100"
                              >
                                <td className="py-2 pr-4">
                                  {item.indicator_name}
                                </td>
                                <td className="py-2 pr-4">{item.code}</td>
                                <td className="py-2 pr-4">
                                  {formatLabel(item.severity)}
                                </td>
                                <td className="py-2 pr-4">
                                  {item.blocks_certification ? "Yes" : "No"}
                                </td>
                                <td className="py-2">{formatLabel(item.status)}</td>
                              </tr>
                            ))
                          ) : (
                            <tr>
                              <td
                                colSpan={5}
                                className="py-4 text-neutral-500"
                              >
                                No physical examination rules.
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {activeTab === "Vaccinations" && (
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-neutral-200 text-neutral-500">
                        <th className="pb-2 pr-4 font-medium">Vaccine</th>
                        <th className="pb-2 pr-4 font-medium">Code</th>
                        <th className="pb-2 pr-4 font-medium">Required</th>
                        <th className="pb-2 pr-4 font-medium">
                          Validity (months)
                        </th>
                        <th className="pb-2 font-medium">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {pv.vaccination_rules?.length ? (
                        pv.vaccination_rules.map((item) => (
                          <tr
                            key={item.id}
                            className="border-b border-neutral-100"
                          >
                            <td className="py-2 pr-4">{item.vaccine_name}</td>
                            <td className="py-2 pr-4">{item.vaccine_code}</td>
                            <td className="py-2 pr-4">
                              {item.required ? "Yes" : "No"}
                            </td>
                            <td className="py-2 pr-4">
                              {item.validity_months ?? "\u2014"}
                            </td>
                            <td className="py-2">{formatLabel(item.status)}</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={5} className="py-4 text-neutral-500">
                            No vaccination rules.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                )}

                {activeTab === "Certificate" && (
                  <div className="grid gap-6">
                    <div>
                      <h4 className="mb-2 text-sm font-semibold text-neutral-900">
                        Certificate Templates
                      </h4>
                      <table className="w-full text-left text-sm">
                        <thead>
                          <tr className="border-b border-neutral-200 text-neutral-500">
                            <th className="pb-2 pr-4 font-medium">Name</th>
                            <th className="pb-2 pr-4 font-medium">Version</th>
                            <th className="pb-2 font-medium">Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          {pv.certificate_templates?.length ? (
                            pv.certificate_templates.map((item) => (
                              <tr
                                key={item.id}
                                className="border-b border-neutral-100"
                              >
                                <td className="py-2 pr-4">
                                  {item.template_name}
                                </td>
                                <td className="py-2 pr-4">
                                  {item.template_version}
                                </td>
                                <td className="py-2">{formatLabel(item.status)}</td>
                              </tr>
                            ))
                          ) : (
                            <tr>
                              <td
                                colSpan={3}
                                className="py-4 text-neutral-500"
                              >
                                No certificate templates.
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                    <div>
                      <h4 className="mb-2 text-sm font-semibold text-neutral-900">
                        Validity Rules
                      </h4>
                      <table className="w-full text-left text-sm">
                        <thead>
                          <tr className="border-b border-neutral-200 text-neutral-500">
                            <th className="pb-2 pr-4 font-medium">
                              Validity (days)
                            </th>
                            <th className="pb-2 pr-4 font-medium">
                              Assessment Interval (days)
                            </th>
                            <th className="pb-2 font-medium">Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          {pv.certificate_validity_rules?.length ? (
                            pv.certificate_validity_rules.map((item) => (
                              <tr
                                key={item.id}
                                className="border-b border-neutral-100"
                              >
                                <td className="py-2 pr-4">
                                  {item.certificate_validity_days}
                                </td>
                                <td className="py-2 pr-4">
                                  {item.routine_assessment_interval_days}
                                </td>
                                <td className="py-2">{formatLabel(item.status)}</td>
                              </tr>
                            ))
                          ) : (
                            <tr>
                              <td
                                colSpan={3}
                                className="py-4 text-neutral-500"
                              >
                                No validity rules.
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {activeTab === "Return-to-Work" && (
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-neutral-200 text-neutral-500">
                        <th className="pb-2 pr-4 font-medium">Condition</th>
                        <th className="pb-2 pr-4 font-medium">Code</th>
                        <th className="pb-2 pr-4 font-medium">
                          Exclusion Hours
                        </th>
                        <th className="pb-2 font-medium">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {pv.return_to_work_rules?.length ? (
                        pv.return_to_work_rules.map((item) => (
                          <tr
                            key={item.id}
                            className="border-b border-neutral-100"
                          >
                            <td className="py-2 pr-4">
                              {item.condition_name}
                            </td>
                            <td className="py-2 pr-4">
                              {item.condition_code}
                            </td>
                            <td className="py-2 pr-4">
                              {item.default_exclusion_hours}
                            </td>
                            <td className="py-2">{formatLabel(item.status)}</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={4} className="py-4 text-neutral-500">
                            No return-to-work rules.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                )}

                {activeTab === "Facility Reqs" && (
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-neutral-200 text-neutral-500">
                        <th className="pb-2 pr-4 font-medium">Requirement</th>
                        <th className="pb-2 pr-4 font-medium">Code</th>
                        <th className="pb-2 pr-4 font-medium">Category</th>
                        <th className="pb-2 pr-4 font-medium">Mandatory</th>
                        <th className="pb-2 font-medium">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {pv.facility_requirement_rules?.length ? (
                        pv.facility_requirement_rules.map((item) => (
                          <tr
                            key={item.id}
                            className="border-b border-neutral-100"
                          >
                            <td className="py-2 pr-4">
                              {item.requirement_name}
                            </td>
                            <td className="py-2 pr-4">
                              {item.requirement_code}
                            </td>
                            <td className="py-2 pr-4">
                              {formatLabel(item.category)}
                            </td>
                            <td className="py-2 pr-4">
                              {item.mandatory ? "Yes" : "No"}
                            </td>
                            <td className="py-2">{formatLabel(item.status)}</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={5} className="py-4 text-neutral-500">
                            No facility requirements.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                )}

                {activeTab === "Reporting" && (
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-neutral-200 text-neutral-500">
                        <th className="pb-2 pr-4 font-medium">Template</th>
                        <th className="pb-2 pr-4 font-medium">Code</th>
                        <th className="pb-2 pr-4 font-medium">Frequency</th>
                        <th className="pb-2 font-medium">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {pv.reporting_templates?.length ? (
                        pv.reporting_templates.map((item) => (
                          <tr
                            key={item.id}
                            className="border-b border-neutral-100"
                          >
                            <td className="py-2 pr-4">
                              {item.template_name}
                            </td>
                            <td className="py-2 pr-4">
                              {item.template_code}
                            </td>
                            <td className="py-2 pr-4">
                              {formatLabel(item.reporting_frequency)}
                            </td>
                            <td className="py-2">{formatLabel(item.status)}</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={4} className="py-4 text-neutral-500">
                            No reporting templates.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                )}

                {activeTab === "M&E" && (
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-neutral-200 text-neutral-500">
                        <th className="pb-2 pr-4 font-medium">Indicator</th>
                        <th className="pb-2 pr-4 font-medium">Code</th>
                        <th className="pb-2 pr-4 font-medium">Data Source</th>
                        <th className="pb-2 pr-4 font-medium">Mandatory</th>
                        <th className="pb-2 font-medium">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {pv.me_indicators?.length ? (
                        pv.me_indicators.map((item) => (
                          <tr
                            key={item.id}
                            className="border-b border-neutral-100"
                          >
                            <td className="py-2 pr-4">
                              {item.indicator_name}
                            </td>
                            <td className="py-2 pr-4">
                              {item.indicator_code}
                            </td>
                            <td className="py-2 pr-4">
                              {formatLabel(item.data_source)}
                            </td>
                            <td className="py-2 pr-4">
                              {item.mandatory ? "Yes" : "No"}
                            </td>
                            <td className="py-2">{formatLabel(item.status)}</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={5} className="py-4 text-neutral-500">
                            No M&E indicators.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                )}

                {activeTab === "Documents" && (
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-neutral-200 text-neutral-500">
                        <th className="pb-2 pr-4 font-medium">Title</th>
                        <th className="pb-2 pr-4 font-medium">Type</th>
                        <th className="pb-2 pr-4 font-medium">Version</th>
                        <th className="pb-2 font-medium">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {pv.policy_documents?.length ? (
                        pv.policy_documents.map((item) => (
                          <tr
                            key={item.id}
                            className="border-b border-neutral-100"
                          >
                            <td className="py-2 pr-4">{item.title}</td>
                            <td className="py-2 pr-4">
                              {formatLabel(item.document_type)}
                            </td>
                            <td className="py-2 pr-4">
                              {item.version_label}
                            </td>
                            <td className="py-2">{formatLabel(item.status)}</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={4} className="py-4 text-neutral-500">
                            No documents.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                )}

                {activeTab === "Acknowledgements" && (
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-neutral-200 text-neutral-500">
                        <th className="pb-2 pr-4 font-medium">State</th>
                        <th className="pb-2 pr-4 font-medium">Status</th>
                        <th className="pb-2 font-medium">Acknowledged At</th>
                      </tr>
                    </thead>
                    <tbody>
                      {pv.state_acknowledgements?.length ? (
                        pv.state_acknowledgements.map((item) => (
                          <tr
                            key={item.id}
                            className="border-b border-neutral-100"
                          >
                            <td className="py-2 pr-4">
                              {item.state__name}
                            </td>
                            <td className="py-2 pr-4">
                              {formatLabel(item.status)}
                            </td>
                            <td className="py-2">
                              {item.acknowledged_at
                                ? new Date(
                                    item.acknowledged_at
                                  ).toLocaleDateString()
                                : "\u2014"}
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={3} className="py-4 text-neutral-500">
                            No acknowledgements.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                )}

                {activeTab === "History" && (
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-neutral-200 text-neutral-500">
                        <th className="pb-2 pr-4 font-medium">Date</th>
                        <th className="pb-2 pr-4 font-medium">Actor</th>
                        <th className="pb-2 pr-4 font-medium">Action</th>
                        <th className="pb-2 pr-4 font-medium">Event</th>
                        <th className="pb-2 pr-4 font-medium">Old Value</th>
                        <th className="pb-2 font-medium">New Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      {historyRows.length ? (
                        historyRows.map((item) => (
                          <tr key={item.id} className="border-b border-neutral-100 align-top">
                            <td className="py-2 pr-4">{new Date(item.created_at).toLocaleString()}</td>
                            <td className="py-2 pr-4">{item.actor_name || item.actor_email || "System"}</td>
                            <td className="py-2 pr-4">{formatLabel(item.action)}</td>
                            <td className="py-2 pr-4">{formatLabel(auditEvent(item))}</td>
                            <td className="max-w-xs py-2 pr-4 text-neutral-600">{auditValueSummary(item.old_value)}</td>
                            <td className="max-w-xs py-2 text-neutral-600">{auditValueSummary(item.new_value)}</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={6} className="py-4 text-neutral-500">
                            No policy version history found.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </StandardsPolicyWorkspaceShell>
  );
}
