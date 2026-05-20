"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { UnitManagementPage } from "@/features/organizations/unit-management-page";
import { createStateInvite, createStateUnit, deleteStateUnit, fetchStateUnits, updateStateUnit } from "@/lib/api/state";
import type { UserRole } from "@/types/auth";

export default function Page() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("foodcert_access_token");
    if (!token) {
      router.push("/login");
      return;
    }
    setReady(true);
  }, [router]);

  const { data: units = [] } = useQuery({
    queryKey: ["state-units"],
    queryFn: fetchStateUnits,
    enabled: ready,
  });

  const createMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => createStateUnit(data as { name: string; unit_type: string }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["state-units"] }),
  });

  const updateMutation = useMutation({
    mutationFn: ({ unitId, data }: { unitId: string; data: Record<string, unknown> }) =>
      updateStateUnit(unitId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["state-units"] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (unitId: string) => deleteStateUnit(unitId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["state-units"] }),
  });

  const inviteMutation = useMutation({
    mutationFn: (data: { email: string; role: UserRole; unit?: string; phone?: string; message?: string; expires_at?: string }) =>
      createStateInvite({ ...data, role: data.role === "inspector" ? "inspector" : "state_admin" }),
  });

  if (!ready) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-slate-500">Loading...</p>
      </div>
    );
  }

  return (
    <UnitManagementPage
      role="state_admin"
      title="Units & Offices"
      description="Manage directorates, verification desks, LGA offices, and inspectorate."
      units={units}
      onCreateUnit={(data) => createMutation.mutate(data)}
      onUpdateUnit={(unitId, data) => updateMutation.mutate({ unitId, data })}
      onDeleteUnit={(unitId) => deleteMutation.mutate(unitId)}
      onInviteUser={(data) => inviteMutation.mutate(data)}
    />
  );
}
