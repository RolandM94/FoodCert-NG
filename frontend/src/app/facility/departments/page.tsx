"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { UnitManagementPage } from "@/features/organizations/unit-management-page";
import { fetchUnits, createUnit, updateUnit, deleteUnit, createInvite } from "@/lib/api/organizations";
import type { UserRole } from "@/types/auth";

export default function Page() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [orgId, setOrgId] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("foodcert_access_token");
    if (!token) {
      router.push("/login");
      return;
    }
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      setOrgId(payload.organization_id || null);
    } catch {
      router.push("/login");
    }
  }, [router]);

  const { data: units = [] } = useQuery({
    queryKey: ["units", orgId],
    queryFn: () => fetchUnits(orgId!),
    enabled: !!orgId,
  });

  const createMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => createUnit(orgId!, data as { name: string; unit_type: string }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["units", orgId] }),
  });

  const updateMutation = useMutation({
    mutationFn: ({ unitId, data }: { unitId: string; data: Record<string, unknown> }) =>
      updateUnit(orgId!, unitId, data as Record<string, string | null>),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["units", orgId] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (unitId: string) => deleteUnit(orgId!, unitId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["units", orgId] }),
  });

  const inviteMutation = useMutation({
    mutationFn: (data: { email: string; role: UserRole; unit?: string; phone?: string; message?: string; expires_at?: string }) =>
      createInvite(orgId!, data),
  });

  if (!orgId) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-slate-500">Loading...</p>
      </div>
    );
  }

  return (
    <UnitManagementPage
      role="facility_admin"
      title="Departments"
      description="Manage clinical, laboratory, and records departments."
      units={units}
      unitTypeFilter={["lab_department", "clinical_department", "records_department", "department", "unit"]}
      onCreateUnit={(data) => createMutation.mutate(data)}
      onUpdateUnit={(unitId, data) => updateMutation.mutate({ unitId, data })}
      onDeleteUnit={(unitId) => deleteMutation.mutate(unitId)}
      onInviteUser={(data) => inviteMutation.mutate(data)}
    />
  );
}
