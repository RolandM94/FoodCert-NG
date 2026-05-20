"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { useState } from "react";
import { ShieldCheck, QrCode, IdCard, Building2, Stethoscope, FlaskConical, ClipboardCheck, Landmark, UsersRound, MapPin, BadgeCheck, ArrowRight, SearchCheck, HeartPulse } from "lucide-react";

const trustStats = [
  { label: "36 States + FCT", detail: "National rollout ready", icon: MapPin },
  { label: "QR Verification", detail: "Public certificate checks", icon: QrCode },
  { label: "State Validation", detail: "Certificate review workflow", icon: ShieldCheck },
  { label: "2024 Guidelines", detail: "Aligned with national guidance", icon: ClipboardCheck },
];

const processSteps = [
  {
    step: 1,
    title: "Register",
    detail: "Food handler creates a profile.",
    icon: IdCard,
  },
  {
    step: 2,
    title: "Verify Identity",
    detail: "Identity is checked through configured provider integration.",
    icon: ShieldCheck,
  },
  {
    step: 3,
    title: "Complete Assessment",
    detail: "Approved facility handles declaration, examination, lab tests, and vaccination review.",
    icon: Stethoscope,
  },
  {
    step: 4,
    title: "State Review",
    detail: "State Ministry workflow validates eligible certificate requests.",
    icon: Landmark,
  },
  {
    step: 5,
    title: "Get Certificate",
    detail: "Food handler receives a QR-coded certificate for public verification.",
    icon: BadgeCheck,
  },
];

const roleCards = [
  {
    role: "Food Handlers",
    description: "Register, verify identity, complete assessment, and access certificate status.",
    cta: "Get Certified",
    href: "/register",
    icon: UsersRound,
  },
  {
    role: "Employers",
    description: "Manage branches, food handlers, subscriptions, compliance, illness reports, and inspections.",
    cta: "Sign In",
    href: "/login",
    icon: Building2,
  },
  {
    role: "Medical Facilities",
    description: "Submit accreditation, conduct approved assessments, manage appointments and records.",
    cta: "Sign In",
    href: "/login",
    icon: Building2,
  },
  {
    role: "Doctors",
    description: "Review declarations, perform exams, request lab tests, and make fitness decisions.",
    cta: "Sign In",
    href: "/login",
    icon: HeartPulse,
  },
  {
    role: "Lab Staff",
    description: "Manage lab requests, enter results, and support assessment workflows.",
    cta: "Sign In",
    href: "/login",
    icon: FlaskConical,
  },
  {
    role: "Inspectors",
    description: "Conduct workplace inspections and verify certificates in the field.",
    cta: "Sign In",
    href: "/login",
    icon: SearchCheck,
  },
  {
    role: "State MOH",
    description: "Manage facilities, fees, certificate validation, inspections, and state reports.",
    cta: "Sign In",
    href: "/login",
    icon: Landmark,
  },
  {
    role: "Federal MOH",
    description: "View national dashboards, trends, reports, and oversight data.",
    cta: "Sign In",
    href: "/login",
    icon: ShieldCheck,
  },
];

const capabilities = [
  {
    title: "Identity Verification",
    description: "Food handler identity checks through configured provider integration.",
    icon: IdCard,
  },
  {
    title: "Medical Assessment",
    description: "Declarations, physical examinations, lab tests, vaccinations, and doctor decisions.",
    icon: Stethoscope,
  },
  {
    title: "Facility Accreditation",
    description: "State-reviewed facility approval and reaccreditation workflows.",
    icon: ClipboardCheck,
  },
  {
    title: "Employer Compliance",
    description: "Branches, food handler status, subscriptions, illness reporting, and compliance views.",
    icon: Building2,
  },
  {
    title: "Inspections",
    description: "Inspector workflows for workplace checks, evidence, and enforcement actions.",
    icon: SearchCheck,
  },
  {
    title: "Dashboards & Reports",
    description: "Employer, facility, state, and federal analytics with exportable reports.",
    icon: BadgeCheck,
  },
];

function CertificateVerifyForm({ compact }: { compact?: boolean }) {
  const router = useRouter();
  const [certNumber, setCertNumber] = useState("");
  const [error, setError] = useState("");

  const handleVerify = () => {
    const trimmed = certNumber.trim();
    if (!trimmed) {
      setError("Enter a certificate number.");
      return;
    }
    setError("");
    router.push(`/verify/${encodeURIComponent(trimmed)}`);
  };

  return (
    <div className={compact ? "" : "w-full max-w-md"}>
      <div className="flex gap-2">
        <label className="flex flex-1 items-center gap-2 rounded border border-slate-200 bg-white px-3 h-11">
          <QrCode size={16} className="text-slate-400 shrink-0" />
          <input
            className="flex-1 bg-transparent text-sm outline-none placeholder:text-slate-400"
            placeholder="Enter certificate number"
            value={certNumber}
            onChange={(e) => { setCertNumber(e.target.value); setError(""); }}
            onKeyDown={(e) => e.key === "Enter" && handleVerify()}
          />
        </label>
        <button
          className="inline-flex h-11 items-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white hover:bg-brand-deep shrink-0"
          onClick={handleVerify}
        >
          <SearchCheck size={16} />
          <span className={compact ? "" : "hidden sm:inline"}>Verify Certificate</span>
          <span className={compact ? "hidden" : "sm:hidden"}>Verify</span>
        </button>
      </div>
      {error && <p className="mt-1.5 text-xs font-semibold text-red-600">{error}</p>}
    </div>
  );
}

export default function Home() {
  return (
    <main className="min-h-screen bg-[#f7faf8] text-slate-950">
      {/* 1. Header */}
      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <Link href="/" className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-green text-white">
              <ShieldCheck size={22} />
            </div>
            <div>
              <p className="text-sm font-bold text-slate-950">FoodCert NG</p>
              <p className="text-xs text-slate-500">Certification platform</p>
            </div>
          </Link>
          <div className="flex items-center gap-2 sm:gap-3">
            <a href="#verify" className="hidden rounded px-3 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-50 sm:inline-flex items-center gap-1.5">
              <QrCode size={15} />
              Verify Certificate
            </a>
            <a href="/register" className="rounded border border-brand-green px-3 py-2 text-sm font-semibold text-brand-deep hover:bg-emerald-50">
              Get Certified
            </a>
            <a href="/login" className="rounded bg-brand-green px-3 py-2 text-sm font-bold text-white hover:bg-brand-deep">
              Sign In
            </a>
          </div>
        </div>
      </header>

      {/* 2. Hero */}
      <section className="relative overflow-hidden bg-white">
        <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 sm:py-24 lg:px-8">
          <div className="grid gap-10 lg:grid-cols-[1fr_0.9fr] lg:gap-16 items-center">
            <div>
              <p className="text-xs font-bold uppercase tracking-wide text-brand-deep">
                National platform
              </p>
              <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-950 sm:text-5xl">
                FoodCert NG
              </h1>
              <p className="mt-4 max-w-xl text-base leading-7 text-slate-600 sm:text-lg">
                A unified platform for food handler medical fitness certification, facility accreditation, inspections, and public certificate verification.
              </p>
              <p className="mt-3 max-w-xl text-sm leading-6 text-slate-500">
                Designed for food handlers, employers, medical facilities, inspectors, and State and Federal health authorities.
              </p>
              <p className="mt-3 max-w-xl text-sm leading-6 text-slate-500">
                Built around State Ministry certificate validation workflows and aligned with the National Guidelines for Food Handlers&apos; Medical Test 2024.
              </p>

              <div className="mt-8 flex flex-wrap gap-3">
                <a
                  href="/register"
                  className="inline-flex h-11 items-center gap-2 rounded bg-brand-green px-5 text-sm font-bold text-white hover:bg-brand-deep"
                >
                  Get Certified
                  <ArrowRight size={16} />
                </a>
                <a
                  href="/login"
                  className="inline-flex h-11 items-center gap-2 rounded border border-slate-200 px-5 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                >
                  Sign In
                </a>
              </div>

              <div className="mt-6">
                <CertificateVerifyForm />
              </div>
            </div>

            <div className="hidden lg:block">
              <figure className="overflow-hidden rounded-lg border border-emerald-100 bg-white shadow-sm">
                <Image
                  alt="Food safety certificate verification with a QR-coded certificate and medical assessment workflow"
                  className="aspect-[4/3] w-full object-cover"
                  height={900}
                  loading="eager"
                  priority
                  src="/landing-foodcert-hero.png"
                  width={1200}
                />
                <figcaption className="border-t border-slate-100 bg-white px-4 py-3 text-xs font-semibold text-slate-600">
                  Certificate checks stay public, fast, and privacy-limited.
                </figcaption>
              </figure>
            </div>
          </div>
        </div>
      </section>

      {/* 3. Trust Strip */}
      <section className="border-y border-slate-100 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {trustStats.map((stat) => {
              const Icon = stat.icon;
              return (
                <div key={stat.label} className="flex items-center gap-3 rounded-lg border border-slate-100 bg-slate-50 p-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-emerald-50 text-brand-deep">
                    <Icon size={18} />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-slate-950">{stat.label}</p>
                    <p className="text-xs text-slate-500">{stat.detail}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* 4. How It Works */}
      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8 lg:py-20">
        <div className="mb-10 text-center">
          <p className="text-xs font-bold uppercase tracking-wide text-brand-deep">Process</p>
          <h2 className="mt-2 text-2xl font-bold tracking-tight text-slate-950 sm:text-3xl">How certification works</h2>
          <p className="mt-2 max-w-2xl mx-auto text-sm text-slate-600">
            From registration to certificate, the platform guides food handlers, facilities, and State reviewers through each step.
          </p>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-5">
          {processSteps.map((step) => {
            const Icon = step.icon;
            return (
              <div key={step.step} className="relative rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
                <div className="mb-3 flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-green text-xs font-bold text-white">
                    {step.step}
                  </div>
                  {step.step < 5 && (
                    <ArrowRight size={14} className="hidden text-slate-300 lg:block" />
                  )}
                </div>
                <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 text-brand-deep">
                  <Icon size={20} />
                </div>
                <h3 className="text-sm font-bold text-slate-950">{step.title}</h3>
                <p className="mt-1.5 text-xs leading-5 text-slate-600">{step.detail}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* 5. Role Entry Points */}
      <section className="border-t border-slate-100 bg-white py-16 lg:py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-10 text-center">
            <p className="text-xs font-bold uppercase tracking-wide text-brand-deep">Who it&apos;s for</p>
            <h2 className="mt-2 text-2xl font-bold tracking-tight text-slate-950 sm:text-3xl">Built for every stakeholder</h2>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {roleCards.map((card) => {
              const Icon = card.icon;
              return (
                <div key={card.role} className="flex flex-col rounded-lg border border-slate-200 bg-slate-50 p-5 shadow-sm">
                  <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 text-brand-deep">
                    <Icon size={20} />
                  </div>
                  <h3 className="text-sm font-bold text-slate-950">{card.role}</h3>
                  <p className="mt-1.5 flex-1 text-xs leading-5 text-slate-600">{card.description}</p>
                  <Link
                    href={card.href}
                    className="mt-4 inline-flex h-9 w-full items-center justify-center gap-2 rounded bg-brand-green text-xs font-bold text-white hover:bg-brand-deep"
                  >
                    {card.cta}
                    <ArrowRight size={13} />
                  </Link>
                </div>
              );
            })}
          </div>

          <p className="mt-6 text-center text-xs text-slate-500">
            Food handlers self-register. All other roles are accessed through invitation by an organization administrator.
          </p>
        </div>
      </section>

      {/* 6. Platform Capabilities */}
      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8 lg:py-20">
        <div className="mb-10 text-center">
          <p className="text-xs font-bold uppercase tracking-wide text-brand-deep">Capabilities</p>
          <h2 className="mt-2 text-2xl font-bold tracking-tight text-slate-950 sm:text-3xl">What the platform does</h2>
        </div>

        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {capabilities.map((cap) => {
            const Icon = cap.icon;
            return (
              <div key={cap.title} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
                <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 text-brand-deep">
                  <Icon size={20} />
                </div>
                <h3 className="text-sm font-bold text-slate-950">{cap.title}</h3>
                <p className="mt-1.5 text-sm leading-6 text-slate-600">{cap.description}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* 7. Public Verification Section */}
      <section id="verify" className="border-t border-emerald-100 bg-white py-16 lg:py-20">
        <div className="mx-auto max-w-2xl px-4 text-center sm:px-6 lg:px-8">
          <div className="mb-4 flex items-center justify-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-brand-deep">
              <QrCode size={24} />
            </div>
          </div>
          <h2 className="text-xl font-bold tracking-tight text-slate-950 sm:text-2xl">Verify a FoodCert NG certificate</h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Enter a certificate number or scan a QR code to confirm certificate validity. Public verification shows only limited certificate information.
          </p>
          <p className="mt-2 text-xs text-slate-500">
            No full NIN, lab results, diagnosis, doctor notes, or declaration answers are shown.
          </p>
          <div className="mt-6 flex justify-center">
            <CertificateVerifyForm />
          </div>
        </div>
      </section>

      {/* 8. Footer */}
      <footer className="border-t border-slate-200 bg-slate-50">
        <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
          <div className="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
            <div className="max-w-sm">
              <div className="flex items-center gap-2">
                <ShieldCheck size={18} className="text-brand-green" />
                <p className="text-sm font-bold text-slate-950">FoodCert NG</p>
              </div>
              <p className="mt-2 text-xs leading-5 text-slate-500">
                Food handler medical fitness certification and public verification platform. Aligned with the National Guidelines for Food Handlers&apos; Medical Test 2024.
              </p>
            </div>
            <div className="flex flex-wrap gap-x-8 gap-y-2 text-sm">
              <a href="/register" className="text-slate-600 hover:text-slate-900 font-semibold">Register</a>
              <a href="/login" className="text-slate-600 hover:text-slate-900 font-semibold">Sign In</a>
              <a href="#verify" className="text-slate-600 hover:text-slate-900 font-semibold">Verify Certificate</a>
              <a href="http://localhost:8000/api/docs/" className="text-slate-600 hover:text-slate-900 font-semibold">API Docs</a>
            </div>
          </div>
          <p className="mt-8 text-xs text-slate-400">
            FoodCert NG &mdash; National food handler medical fitness certification platform.
          </p>
        </div>
      </footer>
    </main>
  );
}
