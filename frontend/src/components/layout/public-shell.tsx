import Link from "next/link";
import { ShieldCheck } from "lucide-react";

export function PublicShell({
  title,
  description,
  children
}: {
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <main className="min-h-screen bg-[#f7faf8] text-slate-950">
      <header className="border-b border-emerald-100 bg-white">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <Link className="flex items-center gap-3" href="/">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-green text-white">
              <ShieldCheck aria-hidden="true" size={22} />
            </div>
            <div>
              <p className="text-sm font-bold text-slate-950">FoodCert NG</p>
              <p className="text-xs text-slate-500">National certification registry</p>
            </div>
          </Link>
          <div className="flex items-center gap-2">
            <Link className="rounded px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" href="/facilities/approved">
              Facilities
            </Link>
            <Link className="rounded bg-brand-green px-3 py-2 text-sm font-bold text-white" href="/login">
              Sign in
            </Link>
          </div>
        </div>
      </header>
      <section className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold tracking-tight text-slate-950 sm:text-3xl">{title}</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">{description}</p>
        </div>
        {children}
      </section>
    </main>
  );
}
