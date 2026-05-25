import { PublicVerificationResult } from "@/components/certificates/public-verification-result";

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

  return (
    <main className="min-h-screen bg-[#f7faf8] px-4 py-8 text-slate-950 sm:px-6 lg:px-8">
      <PublicVerificationResult certificate={certificate} />
    </main>
  );
}
