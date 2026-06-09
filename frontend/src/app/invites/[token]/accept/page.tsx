"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { CheckCircle, Loader2, ShieldCheck } from "lucide-react";
import { acceptInvite, declineInvite, fetchInvitePreview } from "@/lib/api/organizations";
import { ROLE_LABELS } from "@/lib/permissions/roles";
import type { UserInvite } from "@/types/organizations";
import type { UserRole } from "@/types/auth";

export default function Page() {
  const params = useParams<{ token: string }>();
  const router = useRouter();
  const [invite, setInvite] = useState<UserInvite | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [declined, setDeclined] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [form, setForm] = useState({ username: "", password: "", first_name: "", last_name: "", phone: "" });

  useEffect(() => {
    if (!params.token) return;

    setIsAuthenticated(Boolean(localStorage.getItem("foodcert_access_token")));
    fetchInvitePreview(params.token)
      .then((data) => setInvite(data as UserInvite))
      .catch((err: unknown) => setError(err instanceof Error ? err.message : "Could not load invitation."))
      .finally(() => setLoading(false));
  }, [params.token, router]);

  const handleAccept = async () => {
    if (!params.token) return;
    setError(null);
    setLoading(true);
    try {
      const data = await acceptInvite(params.token, form);
      setInvite(data.invite as UserInvite);
      setSuccess(true);
      setTimeout(() => {
        const role = data.user?.role as UserRole;
        const home: Record<string, string> = {
          food_handler: "/food-handler/dashboard",
          employer: "/employer/dashboard",
          facility_admin: "/facility/dashboard",
          doctor: "/doctor/dashboard",
          lab_staff: "/lab/dashboard",
          state_admin: "/state/dashboard",
          inspector: "/inspector/dashboard",
          federal_admin: "/federal/dashboard",
          super_admin: "/federal/dashboard",
        };
        router.push(home[role] || "/login");
      }, 2000);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to accept invite.");
      setLoading(false);
    }
  };

  const handleDecline = async () => {
    if (!params.token) return;
    setError(null);
    setLoading(true);
    try {
      const data = await declineInvite(params.token);
      setInvite(data as UserInvite);
      setDeclined(true);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to decline invite.");
    } finally {
      setLoading(false);
    }
  };

  if (declined) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-neutral-50 p-4">
        <div className="flex w-full max-w-md flex-col items-center gap-4 rounded-lg border border-neutral-200 bg-white p-8 text-center shadow-lg">
          <h1 className="text-xl font-bold text-neutral-900">Invitation Declined</h1>
          <p className="text-sm text-neutral-600">This invitation has been declined.</p>
        </div>
      </main>
    );
  }

  if (success) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-neutral-50 p-4">
        <div className="flex flex-col items-center gap-4 rounded-lg border border-brand-200 bg-white p-8 text-center shadow-lg max-w-md w-full">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-50 text-brand-600">
            <CheckCircle size={36} />
          </div>
          <h1 className="text-xl font-bold text-neutral-900">Invitation Accepted!</h1>
          <p className="text-sm text-neutral-600">
            You have been added to <strong>{invite?.organization_name || invite?.organization}</strong>
            {invite?.unit_name ? ` / ${invite.unit_name}` : ""} as{" "}
            {ROLE_LABELS[invite?.role as UserRole] || invite?.role}.
          </p>
          <p className="text-xs text-neutral-400">Redirecting to your dashboard...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-neutral-50 p-4">
      <div className="w-full max-w-md space-y-6 rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-600 text-white">
            <ShieldCheck size={20} />
          </div>
          <div>
            <p className="text-sm font-bold text-neutral-900">FoodCert NG</p>
            <p className="text-xs text-neutral-500">Invitation</p>
          </div>
        </div>

        {invite && (
          <div className="rounded bg-neutral-50 p-4 text-sm">
            <p className="text-neutral-600">
              You have been invited to join <strong>{invite.organization_name || invite.organization}</strong>
              {invite.unit_name ? ` / ${invite.unit_name}` : ""}
            </p>
            <p className="mt-1 text-neutral-600">
              Role: <strong>{ROLE_LABELS[invite.role as UserRole] || invite.role}</strong>
            </p>
          </div>
        )}

        {!loading && (
          <form
            className="grid gap-3"
            onSubmit={(e) => {
              e.preventDefault();
              handleAccept();
            }}
          >
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Email
              <input
                className="h-10 rounded border border-neutral-200 bg-neutral-50 px-3 text-neutral-500"
                disabled
                value={invite?.email || ""}
              />
            </label>
            {!isAuthenticated && (
              <>
                <label className="grid gap-1 text-sm font-semibold text-neutral-700">
                  Username
                  <input
                    className="h-10 rounded border border-neutral-200 bg-white px-3"
                    required
                    value={form.username}
                    onChange={(e) => setForm((p) => ({ ...p, username: e.target.value }))}
                  />
                </label>
                <label className="grid gap-1 text-sm font-semibold text-neutral-700">
                  Password
                  <input
                    className="h-10 rounded border border-neutral-200 bg-white px-3"
                    type="password"
                    required
                    value={form.password}
                    onChange={(e) => setForm((p) => ({ ...p, password: e.target.value }))}
                  />
                </label>
              </>
            )}
            <label className="grid gap-1 text-sm font-semibold text-neutral-700">
              Full name
              <input
                className="h-10 rounded border border-neutral-200 bg-white px-3"
                value={form.first_name}
                onChange={(e) => setForm((p) => ({ ...p, first_name: e.target.value }))}
                placeholder="First name"
              />
            </label>
            <input
              className="h-10 rounded border border-neutral-200 bg-white px-3"
              value={form.last_name}
              onChange={(e) => setForm((p) => ({ ...p, last_name: e.target.value }))}
              placeholder="Last name"
            />

            {error && (
              <p className="rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{error}</p>
            )}

            <button
              type="submit"
              className="inline-flex h-10 w-full items-center justify-center gap-2 rounded bg-brand-600 text-sm font-bold text-white hover:bg-brand-700"
            >
              Accept Invitation
            </button>
            <button
              type="button"
              onClick={handleDecline}
              className="inline-flex h-10 w-full items-center justify-center gap-2 rounded border border-neutral-200 text-sm font-bold text-neutral-600 hover:bg-neutral-50"
            >
              Decline
            </button>
          </form>
        )}

        {loading && (
          <div className="flex items-center justify-center gap-3 py-6 text-neutral-500">
            <Loader2 size={18} className="animate-spin" />
            <span className="text-sm">Processing invitation...</span>
          </div>
        )}
      </div>
    </main>
  );
}
