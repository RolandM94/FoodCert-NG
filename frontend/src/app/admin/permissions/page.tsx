"use client";

import { useEffect, useMemo, useState } from "react";
import { Search, ShieldAlert } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { fetchPermissions } from "@/lib/api/organizations";
import { getApiErrorMessage } from "@/lib/api/client";
import type { Permission } from "@/types/organizations";

export default function PermissionsPage() {
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;
    async function load() {
      setLoading(true);
      setError("");
      try {
        const rows = await fetchPermissions();
        if (mounted) setPermissions(rows);
      } catch (err) {
        if (mounted) setError(getApiErrorMessage(err, "Could not load permissions."));
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, []);

  const grouped = useMemo(() => {
    const normalized = search.trim().toLowerCase();
    const filtered = normalized
      ? permissions.filter((permission) =>
          [permission.code, permission.name, permission.module, permission.description]
            .join(" ")
            .toLowerCase()
            .includes(normalized)
        )
      : permissions;
    return filtered.reduce<Record<string, Permission[]>>((groups, permission) => {
      groups[permission.module] = groups[permission.module] || [];
      groups[permission.module].push(permission);
      return groups;
    }, {});
  }, [permissions, search]);

  return (
    <PortalShell
      role="super_admin"
      title="Permissions"
      description="Review platform permission codes by module, including sensitive actions used by role templates and overrides."
    >
      <div className="space-y-5">
        {error ? (
          <div className="rounded border border-danger-100 bg-danger-50 px-4 py-3 text-sm font-semibold text-danger-700">
            {error}
          </div>
        ) : null}

        <label className="flex max-w-xl items-center gap-2 rounded border border-neutral-200 bg-white px-3 py-2 text-sm shadow-sm">
          <Search aria-hidden="true" className="text-neutral-400" size={16} />
          <input
            className="w-full border-0 bg-transparent outline-none"
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search permission code, module, or description"
            value={search}
          />
        </label>

        {loading ? (
          <div className="rounded border border-neutral-200 bg-white p-5 text-sm text-neutral-500 shadow-sm">
            Loading permissions...
          </div>
        ) : (
          <div className="space-y-4">
            {Object.entries(grouped).map(([module, modulePermissions]) => (
              <section className="rounded border border-neutral-200 bg-white shadow-sm" key={module}>
                <div className="flex items-center justify-between border-b border-neutral-100 px-4 py-3">
                  <h2 className="text-sm font-bold uppercase tracking-wide text-neutral-600">{module}</h2>
                  <span className="rounded bg-neutral-100 px-2 py-1 text-xs font-bold text-neutral-600">
                    {modulePermissions.length}
                  </span>
                </div>
                <div className="divide-y divide-neutral-100">
                  {modulePermissions.map((permission) => (
                    <div className="grid gap-2 px-4 py-3 md:grid-cols-[1fr_auto]" key={permission.id}>
                      <div>
                        <p className="font-mono text-sm font-bold text-neutral-900">{permission.code}</p>
                        <p className="mt-1 text-sm font-semibold text-neutral-700">{permission.name}</p>
                        {permission.description ? (
                          <p className="mt-1 text-sm text-neutral-500">{permission.description}</p>
                        ) : null}
                      </div>
                      {permission.is_sensitive ? (
                        <span className="inline-flex h-fit items-center gap-1 rounded bg-warning-50 px-2 py-1 text-xs font-bold text-warning-700 ring-1 ring-warning-100">
                          <ShieldAlert aria-hidden="true" size={14} />
                          Sensitive
                        </span>
                      ) : (
                        <span className="inline-flex h-fit rounded bg-brand-50 px-2 py-1 text-xs font-bold text-brand-700 ring-1 ring-brand-200">
                          Standard
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </section>
            ))}
            {!Object.keys(grouped).length ? (
              <div className="rounded border border-neutral-200 bg-white p-5 text-sm text-neutral-500 shadow-sm">
                No permissions match this search.
              </div>
            ) : null}
          </div>
        )}
      </div>
    </PortalShell>
  );
}
