"use client";

import { useEffect, useState } from "react";
import type { UserRole } from "@/types/auth";

export function RoleGuard({ allowed, children }: { allowed: UserRole[]; children: React.ReactNode }) {
  const [role, setRole] = useState<UserRole | null>(null);

  useEffect(() => {
    const stored = window.localStorage.getItem("foodcert_user_role") as UserRole | null;
    setRole(stored);
  }, []);

  if (!role) {
    return <>{children}</>;
  }

  if (!allowed.includes(role)) {
    return (
      <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm font-semibold text-amber-900">
        This page is not available for your current role.
      </div>
    );
  }

  return <>{children}</>;
}
