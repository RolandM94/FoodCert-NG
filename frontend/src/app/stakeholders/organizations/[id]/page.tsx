"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Building2, MapPin, Mail, Phone, Globe, User, AlertTriangle, ShieldCheck } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { OrganizationStatusBadge } from "@/components/ui/organization-status-badge";
import { OrganizationTypeBadge } from "@/components/ui/organization-type-badge";
import { OrganizationProfileForm } from "@/components/ui/organization-profile-form";
import { fetchOrganization, updateOrganization, suspendOrganization, reactivateOrganization } from "@/lib/api/organizations";
import { getOrgTypeLabel, getUnitLabel } from "@/lib/stakeholder-labels";
import { getApiErrorMessage } from "@/lib/api/client";
import type { Organization } from "@/types/organizations";

function formatDate(value?: string) {
  if (!value) return "N/A";
  return new Date(value).toLocaleString("en-NG", { dateStyle: "long" });
}

export default function OrganizationProfilePage() {
  const params = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const organizationId = params.id;

  const [editing, setEditing] = useState(false);
  const [statusBusy, setStatusBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { data: organization, isLoading } = useQuery({
    queryKey: ["organization", organizationId],
    queryFn: () => fetchOrganization(organizationId),
    enabled: Boolean(organizationId),
  });

  const updateMutation = useMutation({
    mutationFn: (data: Parameters<typeof updateOrganization>[1]) => updateOrganization(organizationId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organization", organizationId] });
      setEditing(false);
      setError(null);
    },
    onError: (err) => setError(getApiErrorMessage(err, "Could not update organization.")),
  });

  async function handleStatusToggle() {
    if (!organization) return;
    setStatusBusy(true);
    setError(null);
    try {
      if (organization.status === "suspended") {
        await reactivateOrganization(organizationId);
      } else {
        await suspendOrganization(organizationId);
      }
      queryClient.invalidateQueries({ queryKey: ["organization", organizationId] });
    } catch (err) {
      setError(getApiErrorMessage(err, "Could not change organization status."));
    } finally {
      setStatusBusy(false);
    }
  }

  if (isLoading || !organization) {
    return (
      <PortalShell role="super_admin" title="Organization Profile" description="Loading...">
        <div className="flex items-center justify-center py-20">
          <p className="text-neutral-500">Loading organization profile...</p>
        </div>
      </PortalShell>
    );
  }

  const isSuspended = organization.status === "suspended";

  return (
    <PortalShell
      role="super_admin"
      title={organization.name}
      description="View and manage this organization's profile and status."
    >
      <div className="space-y-6">
        {error ? (
          <div className="rounded border border-danger-100 bg-danger-50 px-4 py-3 text-sm font-semibold text-danger-700">
            {error}
          </div>
        ) : null}

        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <OrganizationTypeBadge type={organization.organization_type} />
            <OrganizationStatusBadge status={organization.status} />
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              className="inline-flex h-10 items-center gap-2 rounded border border-neutral-200 px-4 text-sm font-semibold text-neutral-700 hover:bg-neutral-50"
              onClick={() => setEditing(!editing)}
              type="button"
            >
              {editing ? "Cancel Edit" : "Edit Profile"}
            </button>
            <button
              className={`inline-flex h-10 items-center gap-2 rounded px-4 text-sm font-bold text-white disabled:opacity-60 ${
                isSuspended ? "bg-brand-600 hover:bg-brand-700" : "bg-danger-500 hover:bg-danger-700"
              }`}
              disabled={statusBusy || organization.status === "archived"}
              onClick={handleStatusToggle}
              type="button"
            >
              {isSuspended ? (
                <>
                  <ShieldCheck size={16} />
                  Reactivate
                </>
              ) : (
                <>
                  <AlertTriangle size={16} />
                  Suspend
                </>
              )}
            </button>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="space-y-4 lg:col-span-2">
            {editing ? (
              <OrganizationProfileForm
                initial={organization}
                onSubmit={(data) => updateMutation.mutate(data)}
                onCancel={() => setEditing(false)}
                error={error}
                loading={updateMutation.isPending}
              />
            ) : (
              <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
                <h3 className="text-base font-bold text-neutral-900">Profile Details</h3>
                <div className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
                  <div className="flex items-center gap-2 text-neutral-600">
                    <Building2 size={14} className="text-neutral-400 shrink-0" />
                    <span className="font-semibold text-neutral-800">{organization.name}</span>
                  </div>
                  {organization.contact_person_name && (
                    <div className="flex items-center gap-2 text-neutral-600">
                      <User size={14} className="text-neutral-400 shrink-0" />
                      <span>{organization.contact_person_name}</span>
                    </div>
                  )}
                  {organization.email && (
                    <div className="flex items-center gap-2 text-neutral-600">
                      <Mail size={14} className="text-neutral-400 shrink-0" />
                      <span className="break-all">{organization.email}</span>
                    </div>
                  )}
                  {organization.phone && (
                    <div className="flex items-center gap-2 text-neutral-600">
                      <Phone size={14} className="text-neutral-400 shrink-0" />
                      <span>{organization.phone}</span>
                    </div>
                  )}
                  {organization.website && (
                    <div className="flex items-center gap-2 text-neutral-600">
                      <Globe size={14} className="text-neutral-400 shrink-0" />
                      <span className="break-all">{organization.website}</span>
                    </div>
                  )}
                  {organization.address && (
                    <div className="flex items-start gap-2 text-neutral-600 sm:col-span-2">
                      <MapPin size={14} className="text-neutral-400 shrink-0 mt-0.5" />
                      <span>{organization.address}</span>
                    </div>
                  )}
                </div>
              </section>
            )}

            {organization.parent_name && (
              <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
                <h3 className="text-base font-bold text-neutral-900">Parent Organization</h3>
                <p className="mt-2 text-sm text-neutral-600">{organization.parent_name}</p>
              </section>
            )}
          </div>

          <div className="space-y-4">
            <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
              <h3 className="text-base font-bold text-neutral-900">Quick Stats</h3>
              <div className="mt-4 space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-neutral-600">{getUnitLabel(organization.organization_type)}</span>
                  <span className="font-bold text-neutral-900">{organization.unit_count ?? 0}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-neutral-600">Active Members</span>
                  <span className="font-bold text-neutral-900">{organization.membership_count ?? 0}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-neutral-600">Child Organizations</span>
                  <span className="font-bold text-neutral-900">{organization.children_count ?? 0}</span>
                </div>
              </div>
            </section>

            <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
              <h3 className="text-base font-bold text-neutral-900">Timestamps</h3>
              <div className="mt-4 space-y-2 text-sm">
                <div>
                  <span className="text-neutral-500">Created</span>
                  <p className="font-semibold text-neutral-800">{formatDate(organization.created_at)}</p>
                </div>
                <div>
                  <span className="text-neutral-500">Last Updated</span>
                  <p className="font-semibold text-neutral-800">{formatDate(organization.updated_at)}</p>
                </div>
                {organization.created_by_email && (
                  <div>
                    <span className="text-neutral-500">Created By</span>
                    <p className="font-semibold text-neutral-800">{organization.created_by_email}</p>
                  </div>
                )}
              </div>
            </section>

            <nav className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
              <h3 className="text-xs font-bold uppercase tracking-wide text-neutral-500">Quick Links</h3>
              <div className="mt-3 flex flex-col gap-2">
                <a
                  className="text-sm font-semibold text-brand-600 hover:text-brand-700"
                  href={`/stakeholders/organizations/${organizationId}/units`}
                >
                  {getUnitLabel(organization.organization_type)}
                </a>
                <a
                  className="text-sm font-semibold text-brand-600 hover:text-brand-700"
                  href={`/stakeholders/organizations/${organizationId}/roles`}
                >
                  Roles
                </a>
                <a
                  className="text-sm font-semibold text-brand-600 hover:text-brand-700"
                  href={`/stakeholders/organizations/${organizationId}/invites`}
                >
                  Invites
                </a>
              </div>
            </nav>
          </div>
        </div>
      </div>
    </PortalShell>
  );
}
