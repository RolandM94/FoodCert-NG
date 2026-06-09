"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { UnitManagementPage } from "@/features/organizations/unit-management-page";
import { fetchUnits, createUnit, updateUnit, deleteUnit, createInvite } from "@/lib/api/organizations";
import { getUnitLabel } from "@/lib/stakeholder-labels";
import type { UserRole } from "@/types/auth";

export default function OrganizationUnitsPage() {
  const params = useParams<{ id: string }>();
  const organizationId = params.id;
  const queryClient = useQueryClient();

  const { data: units = [] } = useQuery({
    queryKey: ["units", organizationId],
    queryFn: () => fetchUnits(organizationId),
    enabled: Boolean(organizationId),
  });

  const createMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) =>
      createUnit(organizationId, data as { name: string; unit_type: string }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["units", organizationId] }),
  });

  const updateMutation = useMutation({
    mutationFn: ({ unitId, data }: { unitId: string; data: Record<string, unknown> }) =>
      updateUnit(organizationId, unitId, data as Record<string, string | null>),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["units", organizationId] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (unitId: string) => deleteUnit(organizationId, unitId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["units", organizationId] }),
  });

  const inviteMutation = useMutation({
    mutationFn: (data: { email: string; role: UserRole; unit?: string; phone?: string; message?: string; expires_at?: string }) =>
      createInvite(organizationId, data),
  });

  return (
    <UnitManagementPage
      role="super_admin"
      title={getUnitLabel("platform_operator", "plural")}
      description="Manage organizational units, branches, departments, and offices. Assign users and invite personnel to specific units."
      units={units}
      onCreateUnit={(data) => createMutation.mutate(data)}
      onUpdateUnit={(unitId, data) => updateMutation.mutate({ unitId, data })}
      onDeleteUnit={(unitId) => deleteMutation.mutate(unitId)}
      onInviteUser={(data) => inviteMutation.mutate(data)}
    />
  );
}
