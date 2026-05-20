import { ShieldCheck, ShieldX } from "lucide-react";

type VerifyPageProps = {
  params: Promise<{ certificateNumber: string }>;
};

async function fetchCertificate(certificateNumber: string) {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";
  const response = await fetch(`${baseUrl}/public/certificates/verify/${certificateNumber}/`, {
    cache: "no-store"
  });
  if (!response.ok) {
    return {
      certificate_validity: "not_found",
      certificate_number: certificateNumber
    };
  }
  const envelope = await response.json();
  return envelope.data;
}

export default async function VerifyCertificatePage({ params }: VerifyPageProps) {
  const { certificateNumber } = await params;
  const certificate = await fetchCertificate(certificateNumber);
  const isValid = certificate.certificate_validity === "valid";

  return (
    <main className="min-h-screen bg-[#f7faf8] px-4 py-8 text-slate-950 sm:px-6 lg:px-8">
      <section className="mx-auto max-w-2xl rounded-lg border border-emerald-100 bg-white p-6 shadow-sm">
        <div className="flex items-center gap-3">
          <div className={`flex h-11 w-11 items-center justify-center rounded-lg ${isValid ? "bg-emerald-50 text-brand-deep" : "bg-rose-50 text-rose-700"}`}>
            {isValid ? <ShieldCheck aria-hidden="true" size={23} /> : <ShieldX aria-hidden="true" size={23} />}
          </div>
          <div>
            <p className="text-xs font-bold uppercase tracking-wide text-slate-500">FoodCert NG Verification</p>
            <h1 className="text-xl font-bold text-slate-950">{isValid ? "Certificate valid" : "Certificate not valid"}</h1>
          </div>
        </div>

        <dl className="mt-6 grid gap-4 text-sm">
          {[
            ["Certificate number", certificate.certificate_number],
            ["Status", certificate.certificate_validity],
            ["Food handler", certificate.food_handler_name ?? "Unavailable"],
            ["Issuing authority", certificate.issuing_state_ministry ?? "Unavailable"],
            ["Medical facility", certificate.approved_medical_facility ?? "Unavailable"],
            ["Issue date", certificate.issue_date ?? "Unavailable"],
            ["Expiry date", certificate.expiry_date ?? "Unavailable"],
            ["Fitness status", certificate.fitness_status ?? "Unavailable"],
            ["Last verified", certificate.last_verified_at ?? "Just now"]
          ].map(([label, value]) => (
            <div key={label} className="grid gap-1 border-b border-slate-100 pb-3 last:border-b-0">
              <dt className="text-xs font-bold uppercase tracking-wide text-slate-500">{label}</dt>
              <dd className="font-semibold text-slate-900">{value}</dd>
            </div>
          ))}
        </dl>
      </section>
    </main>
  );
}
