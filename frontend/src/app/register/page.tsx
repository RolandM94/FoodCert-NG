"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  UserPlus,
  ShieldCheck,
  UsersRound,
  Building2,
  ArrowRight,
  AlertCircle,
  CheckCircle2,
} from "lucide-react";
import { register } from "@/lib/api/auth";

type Step = "choice" | "food_handler" | "employer_account" | "employer_profile" | "done";

export default function RegisterPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("choice");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [account, setAccount] = useState({
    first_name: "",
    last_name: "",
    username: "",
    email: "",
    phone: "",
    password: "",
  });

  const [business, setBusiness] = useState({
    business_name: "",
    business_registration_number: "",
    establishment_category: "restaurant_cafe",
    contact_person_name: "",
    contact_person_phone: "",
    contact_person_email: "",
    address: "",
    number_of_food_handlers: 0,
  });

  function updateAccount(field: string, value: string) {
    setAccount((prev) => ({ ...prev, [field]: value }));
  }

  function updateBusiness(field: string, value: string) {
    setBusiness((prev) => ({ ...prev, [field]: value }));
  }

  async function handleFoodHandlerSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await register({
        username: account.username,
        email: account.email,
        password: account.password,
        first_name: account.first_name,
        last_name: account.last_name,
        phone: account.phone,
        role: "food_handler",
      });
      router.push("/login");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleEmployerAccountSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await register({
        username: account.username,
        email: account.email,
        password: account.password,
        first_name: account.first_name,
        last_name: account.last_name,
        phone: account.phone,
        role: "employer",
      });
      setBusiness((prev) => ({
        ...prev,
        contact_person_name: `${account.first_name} ${account.last_name}`.trim(),
        contact_person_phone: account.phone,
        contact_person_email: account.email,
      }));
      setStep("employer_profile");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Account creation failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleEmployerProfileSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const token = localStorage.getItem("foodcert_access_token");
      if (!token) {
        // re-login to get employer token
        const { login } = await import("@/lib/api/auth");
        const tokens = await login(account.username, account.password);
        localStorage.setItem("foodcert_access_token", tokens.access);
        localStorage.setItem("foodcert_refresh_token", tokens.refresh);
        localStorage.setItem("foodcert_user_role", tokens.user.role);
      }

      const { apiClient, unwrap } = await import("@/lib/api/client");
      const res = await apiClient.post("/employers/", {
        business_name: business.business_name || `${business.contact_person_name}'s Business`,
        business_registration_number: business.business_registration_number,
        establishment_category: business.establishment_category,
        contact_person_name: business.contact_person_name,
        contact_person_phone: business.contact_person_phone,
        contact_person_email: business.contact_person_email,
        address: business.address,
        number_of_food_handlers: Number(business.number_of_food_handlers),
      });
      unwrap(res.data);
      setStep("done");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Business profile creation failed.");
    } finally {
      setLoading(false);
    }
  }

  const establishmentCategories = [
    { value: "restaurant_cafe", label: "Restaurant / Cafe" },
    { value: "bakery", label: "Bakery / Pastry Shop" },
    { value: "abattoir_butcher", label: "Abattoir / Butcher Shop" },
    { value: "grocery_supermarket", label: "Grocery / Supermarket" },
    { value: "food_truck_street_vendor", label: "Food Truck / Street Vendor" },
    { value: "catering", label: "Catering Service" },
    { value: "school_cafeteria", label: "School Cafeteria" },
    { value: "hospital_kitchen", label: "Hospital Kitchen" },
    { value: "bar_pub", label: "Bar / Pub" },
    { value: "food_processing_plant", label: "Food Processing Plant" },
    { value: "hotel_resort", label: "Hotel / Resort" },
    { value: "corporate_dining", label: "Corporate Dining" },
    { value: "food_market_stall", label: "Food Market / Stall" },
    { value: "farm_feed_processing", label: "Farm / Feed Processing" },
    { value: "daycare", label: "Daycare Centre" },
    { value: "other", label: "Other" },
  ];

  if (step === "done") {
    return (
      <main className="min-h-screen bg-neutral-50 flex items-center justify-center p-4">
        <div className="flex flex-col items-center gap-4 rounded-2xl border border-brand-200 bg-white p-10 shadow-lg max-w-md text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-50 text-brand-600">
            <CheckCircle2 size={36} />
          </div>
          <h1 className="text-xl font-bold text-neutral-900">Business registered!</h1>
          <p className="text-sm text-neutral-600">
            Your employer account is ready. You can now manage branches, invite food handlers, and monitor compliance.
          </p>
          <Link
            href="/employer/dashboard"
            className="inline-flex h-11 items-center gap-2 rounded-lg bg-brand-600 px-6 text-sm font-bold text-white hover:bg-brand-700"
          >
            Go to Dashboard
            <ArrowRight size={16} />
          </Link>
        </div>
      </main>
    );
  }

  if (step === "choice") {
    return (
      <main className="min-h-screen bg-neutral-50 flex items-center justify-center p-4">
        <div className="w-full max-w-lg space-y-6">
          <div className="text-center">
            <div className="flex items-center justify-center gap-3 mb-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-600 text-white">
                <ShieldCheck size={22} />
              </div>
              <p className="text-sm font-bold text-neutral-900">FoodCert NG</p>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-neutral-900">Create your account</h1>
            <p className="mt-2 text-sm text-neutral-600">Select your account type to get started.</p>
          </div>

          <button
            onClick={() => setStep("food_handler")}
            className="w-full rounded-2xl border-2 border-brand-100 bg-white p-6 text-left shadow-sm hover:border-brand-300 hover:shadow-md transition-all"
          >
            <div className="flex items-start gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-brand-50 text-brand-700">
                <UsersRound size={24} />
              </div>
              <div className="flex-1">
                <p className="text-base font-bold text-neutral-900">I am a Food Handler</p>
                <p className="mt-1 text-sm text-neutral-600">
                  I need a medical fitness certificate to handle food. I will register, verify my identity, complete an assessment, and receive a QR-coded certificate.
                </p>
              </div>
              <ArrowRight size={20} className="mt-2 text-neutral-300" />
            </div>
          </button>

          <button
            onClick={() => setStep("employer_account")}
            className="w-full rounded-2xl border-2 border-brand-100 bg-white p-6 text-left shadow-sm hover:border-brand-300 hover:shadow-md transition-all"
          >
            <div className="flex items-start gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-brand-50 text-brand-700">
                <Building2 size={24} />
              </div>
              <div className="flex-1">
                <p className="text-base font-bold text-neutral-900">I am an Employer / Food Business</p>
                <p className="mt-1 text-sm text-neutral-600">
                  I run a food business and need to manage my staff&apos;s certifications, compliance, branches, and inspections.
                </p>
              </div>
              <ArrowRight size={20} className="mt-2 text-neutral-300" />
            </div>
          </button>

          <p className="text-center text-sm text-neutral-500">
            Already have an account?{" "}
            <Link href="/login" className="font-semibold text-brand-700 hover:underline">Sign in</Link>
          </p>

          <p className="text-center text-xs text-neutral-400">
            Medical facilities, state ministries, and federal agencies are invited by an administrator.
          </p>
        </div>
      </main>
    );
  }

  // Shared account form (food_handler or employer_account step)
  const isEmployerAccount = step === "employer_account";

  return (
    <main className="min-h-screen bg-neutral-50 flex items-center justify-center p-4">
      <div className="w-full max-w-5xl grid gap-0 rounded-2xl border border-neutral-200 bg-white shadow-lg overflow-hidden lg:grid-cols-[0.85fr_1fr]">
        {/* Left panel */}
        <div className="hidden bg-neutral-50 p-8 lg:flex lg:flex-col lg:justify-center">
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-600 text-white">
                <ShieldCheck size={22} />
              </div>
              <div>
                <p className="text-sm font-bold text-neutral-900">FoodCert NG</p>
                <p className="text-xs text-neutral-500">National certification platform</p>
              </div>
            </div>
            <h1 className="text-xl font-bold text-neutral-900">
              {isEmployerAccount ? "Register your business" : "Become a certified food handler"}
            </h1>
            <p className="mt-2 text-sm text-neutral-600">
              {isEmployerAccount
                ? "Step 1 of 2: Create your employer account. You'll set up your business profile next."
                : "Create your profile, verify your identity, complete a medical assessment, and receive a QR-coded fitness certificate."}
            </p>
          </div>

          {isEmployerAccount && (
            <div className="flex items-center gap-3 text-sm">
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-brand-600 text-xs font-bold text-white">1</span>
              <span className="font-semibold text-neutral-800">Create account</span>
              <ArrowRight size={14} className="text-neutral-300" />
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-neutral-200 text-xs font-bold text-neutral-500">2</span>
              <span className="text-neutral-400">Business profile</span>
              <ArrowRight size={14} className="text-neutral-300" />
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-neutral-200 text-xs font-bold text-neutral-500">3</span>
              <span className="text-neutral-400">Subscription</span>
            </div>
          )}

          {!isEmployerAccount && (
            <div className="grid gap-3 mt-4">
              {[
                { step: 1, label: "Register your profile" },
                { step: 2, label: "Verify your NIN" },
                { step: 3, label: "Book a medical assessment" },
                { step: 4, label: "Receive your QR certificate" },
              ].map((s) => (
                <div key={s.step} className="flex items-center gap-3 rounded-lg border border-neutral-200 bg-white p-3">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-600 text-xs font-bold text-white">{s.step}</div>
                  <span className="text-sm font-medium text-neutral-700">{s.label}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right panel — form */}
        <div className="flex flex-col justify-center p-8 sm:p-10">
          <div className="mb-6 lg:hidden text-center">
            <h1 className="text-xl font-bold text-neutral-900">
              {isEmployerAccount ? "Create employer account" : "Create account"}
            </h1>
          </div>

          {isEmployerAccount ? (
            <form className="grid gap-4" onSubmit={handleEmployerAccountSubmit}>
              <div className="flex items-center gap-2 mb-2 rounded-lg bg-brand-50 px-4 py-3">
                <Building2 size={16} className="text-brand-700 shrink-0" />
                <span className="text-sm font-semibold text-brand-700">Registering as: Employer</span>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
                  First name
                  <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3" required autoFocus value={account.first_name} onChange={(e) => updateAccount("first_name", e.target.value)} />
                </label>
                <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
                  Last name
                  <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3" required value={account.last_name} onChange={(e) => updateAccount("last_name", e.target.value)} />
                </label>
                <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
                  Username <span className="text-danger-500">*</span>
                  <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3" required value={account.username} onChange={(e) => updateAccount("username", e.target.value)} />
                </label>
                <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
                  Email <span className="text-danger-500">*</span>
                  <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3" required type="email" value={account.email} onChange={(e) => updateAccount("email", e.target.value)} />
                </label>
                <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
                  Phone <span className="text-danger-500">*</span>
                  <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3" required type="tel" value={account.phone} onChange={(e) => updateAccount("phone", e.target.value)} placeholder="08030000000" />
                </label>
                <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
                  Password <span className="text-danger-500">*</span>
                  <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3" required type="password" value={account.password} onChange={(e) => updateAccount("password", e.target.value)} placeholder="Min 8 characters" />
                </label>
              </div>
              {error && <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700"><AlertCircle size={16} className="mt-0.5 shrink-0" /><span>{error}</span></div>}
              <button className="mt-2 inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-brand-600 text-sm font-bold text-white hover:bg-brand-700 disabled:opacity-60" disabled={loading} type="submit">
                {loading ? "Creating..." : "Continue to Business Profile"}
                {!loading && <ArrowRight size={16} />}
              </button>
              <p className="text-center text-sm text-neutral-500">
                Already registered? <Link href="/login" className="font-semibold text-brand-700 hover:underline">Sign in</Link>
              </p>
            </form>
          ) : step === "employer_profile" ? (
            // Step 2: Business Profile
            <form className="grid gap-4" onSubmit={handleEmployerProfileSubmit}>
              <div className="flex items-center gap-2 mb-2 rounded-lg bg-info-50 px-4 py-3">
                <Building2 size={16} className="text-blue-600 shrink-0" />
                <span className="text-sm font-semibold text-info-700">Step 2: Business Profile</span>
              </div>
              <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
                Business name <span className="text-danger-500">*</span>
                <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3" required autoFocus value={business.business_name} onChange={(e) => updateBusiness("business_name", e.target.value)} />
              </label>
              <div className="grid gap-4 sm:grid-cols-2">
                <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
                  Registration number
                  <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3" value={business.business_registration_number} onChange={(e) => updateBusiness("business_registration_number", e.target.value)} placeholder="Optional" />
                </label>
                <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
                  Category <span className="text-danger-500">*</span>
                  <select className="h-11 rounded-lg border border-neutral-200 bg-white px-3" value={business.establishment_category} onChange={(e) => updateBusiness("establishment_category", e.target.value)}>
                    {establishmentCategories.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
                  </select>
                </label>
              </div>
              <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
                Address <span className="text-danger-500">*</span>
                <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3" required value={business.address} onChange={(e) => updateBusiness("address", e.target.value)} />
              </label>
              <div className="grid gap-4 sm:grid-cols-2">
                <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
                  Contact person
                  <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3" value={business.contact_person_name} onChange={(e) => updateBusiness("contact_person_name", e.target.value)} />
                </label>
                <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
                  Contact phone
                  <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3" value={business.contact_person_phone} onChange={(e) => updateBusiness("contact_person_phone", e.target.value)} />
                </label>
                <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
                  Contact email
                  <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3" type="email" value={business.contact_person_email} onChange={(e) => updateBusiness("contact_person_email", e.target.value)} />
                </label>
                <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
                  Est. food handlers
                  <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3" type="number" min={0} value={business.number_of_food_handlers} onChange={(e) => updateBusiness("number_of_food_handlers", e.target.value)} />
                </label>
              </div>
              {error && <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700"><AlertCircle size={16} className="mt-0.5 shrink-0" /><span>{error}</span></div>}
              <button className="mt-2 inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-brand-600 text-sm font-bold text-white hover:bg-brand-700 disabled:opacity-60" disabled={loading} type="submit">
                {loading ? "Creating..." : "Complete Registration"}
                {!loading && <CheckCircle2 size={16} />}
              </button>
              <p className="text-center text-xs text-neutral-400">Next step: Select a subscription plan to activate all features.</p>
            </form>
          ) : (
            // Step: Food Handler registration
            <form className="grid gap-4" onSubmit={handleFoodHandlerSubmit}>
              <div className="flex items-center gap-2 mb-2 rounded-lg bg-brand-50 px-4 py-3">
                <UsersRound size={16} className="text-brand-700 shrink-0" />
                <span className="text-sm font-semibold text-brand-700">Registering as: Food Handler</span>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
                  First name
                  <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3" autoFocus value={account.first_name} onChange={(e) => updateAccount("first_name", e.target.value)} autoComplete="given-name" />
                </label>
                <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
                  Last name
                  <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3" value={account.last_name} onChange={(e) => updateAccount("last_name", e.target.value)} autoComplete="family-name" />
                </label>
                <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
                  Username <span className="text-danger-500">*</span>
                  <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3" required value={account.username} onChange={(e) => updateAccount("username", e.target.value)} autoComplete="username" />
                </label>
                <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
                  Email <span className="text-danger-500">*</span>
                  <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3" required type="email" value={account.email} onChange={(e) => updateAccount("email", e.target.value)} autoComplete="email" />
                </label>
                <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
                  Phone <span className="text-danger-500">*</span>
                  <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3" required type="tel" value={account.phone} onChange={(e) => updateAccount("phone", e.target.value)} autoComplete="tel" placeholder="08030000000" />
                </label>
                <label className="grid gap-1.5 text-sm font-semibold text-neutral-700">
                  Password <span className="text-danger-500">*</span>
                  <input className="h-11 rounded-lg border border-neutral-200 bg-neutral-50 px-3" required type="password" value={account.password} onChange={(e) => updateAccount("password", e.target.value)} autoComplete="new-password" placeholder="Min 8 characters" />
                </label>
              </div>
              {error && <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700"><AlertCircle size={16} className="mt-0.5 shrink-0" /><span>{error}</span></div>}
              <button className="mt-2 inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-brand-600 text-sm font-bold text-white hover:bg-brand-700 disabled:opacity-60" disabled={loading} type="submit">
                <UserPlus size={18} />
                {loading ? "Creating..." : "Create account"}
              </button>
              <p className="text-center text-sm text-neutral-500">
                Already registered? <Link href="/login" className="font-semibold text-brand-700 hover:underline">Sign in</Link>
              </p>
              <div className="rounded-lg border border-warning-100 bg-warning-50 p-3">
                <div className="flex items-start gap-2">
                  <AlertCircle size={14} className="mt-0.5 shrink-0 text-amber-600" />
                  <p className="text-xs text-warning-700">
                    Not a food handler? Employers, facilities, and government staff are invited by an admin.{" "}
                    <Link href="/login" className="font-semibold underline">Sign in here</Link>.
                  </p>
                </div>
              </div>
            </form>
          )}
        </div>
      </div>
    </main>
  );
}
