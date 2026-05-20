"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { UserPlus } from "lucide-react";
import { register } from "@/lib/api/auth";

export function RegisterForm() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setLoading(true);
    setError("");
    try {
      await register({
        username: String(form.get("username")),
        email: String(form.get("email")),
        password: String(form.get("password")),
        first_name: String(form.get("first_name") ?? ""),
        last_name: String(form.get("last_name") ?? ""),
        phone: String(form.get("phone") ?? ""),
        role: form.get("role") as "food_handler" | "employer"
      });
      router.push("/login");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed. Review the fields and try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="grid gap-4 rounded-lg border border-slate-200 bg-white p-5 shadow-sm" onSubmit={submit}>
      <div className="grid gap-4 sm:grid-cols-2">
        {["first_name", "last_name", "username", "email", "phone"].map((name) => (
          <label key={name} className="grid gap-1 text-sm font-semibold text-slate-700">
            {name.split("_").join(" ")}
            <input className="h-11 rounded border border-slate-200 bg-slate-50 px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2" name={name} required={name !== "phone"} type={name === "email" ? "email" : "text"} />
          </label>
        ))}
      </div>
      <label className="grid gap-1 text-sm font-semibold text-slate-700">
        Role
        <select className="h-11 rounded border border-slate-200 bg-white px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2" name="role">
          <option value="food_handler">Food Handler</option>
          <option value="employer">Employer</option>
        </select>
      </label>
      <label className="grid gap-1 text-sm font-semibold text-slate-700">
        Password
        <input className="h-11 rounded border border-slate-200 bg-slate-50 px-3 outline-none ring-brand-green/20 focus:border-brand-green focus:ring-2" name="password" required type="password" />
      </label>
      {error ? <p className="rounded bg-rose-50 p-3 text-sm font-semibold text-rose-800">{error}</p> : null}
      <button className="inline-flex h-11 items-center justify-center gap-2 rounded bg-brand-green px-4 text-sm font-bold text-white disabled:opacity-60" disabled={loading} type="submit">
        <UserPlus aria-hidden="true" size={18} />
        {loading ? "Creating account..." : "Create account"}
      </button>
    </form>
  );
}
