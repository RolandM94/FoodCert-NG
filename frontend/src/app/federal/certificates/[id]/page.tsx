"use client";

import { useQuery } from "@tanstack/react-query";
import { Download, ShieldCheck } from "lucide-react";
import { useParams } from "next/navigation";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusCell } from "@/components/ui/data-table";
import { downloadCertificatePdf } from "@/lib/api/certificates";
import { fetchFederalCertificate } from "@/lib/api/federal";

function dateLabel(value?: string | null) {
  if (!value) return "Not set";
  return new Date(value).toLocaleDateString("en-NG", { dateStyle: "medium" });
}

export default function Page() {
  const params = useParams<{ id: string }>();
  const certificateQuery = useQuery({
    queryKey: ["federal-certificate", params.id],
    queryFn: () => fetchFederalCertificate(params.id),
    enabled: Boolean(params.id),
  });
  const certificate = certificateQuery.data;

  return (
    <PortalShell role="federal_admin" title="Certificate detail" description="Privacy-safe federal certificate view. Detail access is audited.">
      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        {certificate ? (
          <div className="grid gap-5">
            <div className="flex flex-wrap items-start justify-between gap-4 border-b border-slate-100 pb-4">
              <div>
                <p className="text-sm font-semibold uppercase text-slate-500">Certificate</p>
                <h1 className="mt-1 text-2xl font-bold text-slate-950">{certificate.certificate_number}</h1>
              </div>
              <StatusCell status={certificate.effective_status} />
            </div>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[
                ["Food handler", certificate.food_handler_name || "Not linked"],
                ["Employer", certificate.employer_name || "Not linked"],
                ["Facility", certificate.facility_name || "Not set"],
                ["Issuing state", certificate.issuing_state_name || "Not set"],
                ["Issue date", dateLabel(certificate.issue_date)],
                ["Expiry date", dateLabel(certificate.expiry_date)],
                ["Suspicious reports", String(certificate.suspicious_report_count)],
              ].map(([label, value]) => (
                <div key={label} className="rounded border border-slate-100 bg-slate-50 p-3">
                  <p className="text-xs font-semibold uppercase text-slate-500">{label}</p>
                  <p className="mt-1 text-sm font-bold text-slate-950">{value}</p>
                </div>
              ))}
            </div>
            <div className="flex items-center gap-2 rounded border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm font-semibold text-emerald-800">
              <ShieldCheck size={16} />
              Federal detail access is recorded in the audit trail.
            </div>
            <div>
              <button className="inline-flex h-10 items-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white hover:bg-brand-deep" onClick={() => void downloadCertificatePdf(certificate.id, certificate.certificate_number)} type="button">
                <Download size={16} />
                Download PDF certificate
              </button>
            </div>
          </div>
        ) : (
          <p className="text-sm font-semibold text-slate-500">{certificateQuery.isLoading ? "Loading certificate..." : "Certificate not available."}</p>
        )}
      </section>
    </PortalShell>
  );
}
