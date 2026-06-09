"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Search, Link2, AlertCircle, CheckCircle2 } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { FitnessStatusBadge } from "@/components/ui/fitness-status-badge";
import { apiClient, unwrap } from "@/lib/api/client";

type SearchResult = {
  id: string;
  full_name: string;
  phone: string;
  fitness_status: string;
  system_identifier?: string;
};

export default function Page() {
  const router = useRouter();
  const [employerId, setEmployerId] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [linking, setLinking] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("foodcert_access_token");
    if (!token) { router.push("/login"); return; }
    apiClient.get("/employers/me/").then((res) => {
      setEmployerId((unwrap(res.data) as { id: string }).id);
    }).catch(() => {});
  }, [router]);

  function handleSearch() {
    if (query.length < 3 || !employerId) return;
    setLoading(true);
    setError("");
    setSuccess("");
    apiClient.get(`/employers/${employerId}/food-handlers/search/?q=${encodeURIComponent(query)}`)
      .then((res) => setResults(unwrap(res.data) as SearchResult[]))
      .catch(() => setError("Search failed."))
      .finally(() => setLoading(false));
  }

  function handleLink(fhId: string, name: string) {
    if (!employerId) return;
    setLinking(fhId);
    setError("");
    setSuccess("");
    apiClient.post(`/employers/${employerId}/food-handlers/${fhId}/link/`, {})
      .then(() => {
        setSuccess(`${name} has been linked to your business.`);
        setResults((prev) => prev.filter((r) => r.id !== fhId));
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to link handler."))
      .finally(() => setLinking(null));
  }

  return (
    <PortalShell role="employer" title="Link Existing Handler" description="Search for a food handler who already has a certificate and link them to your business.">
      <div className="max-w-2xl space-y-5">
        <div className="flex gap-2">
          <label className="flex flex-1 items-center gap-2 rounded border border-neutral-200 bg-white px-3 h-11">
            <Search size={14} className="text-neutral-400" />
            <input className="flex-1 bg-transparent text-sm outline-none" placeholder="Search by name, phone, or ID..." value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={(e) => e.key === "Enter" && handleSearch()} />
          </label>
          <button className="inline-flex h-11 items-center gap-2 rounded-lg bg-brand-600 px-4 text-sm font-bold text-white hover:bg-brand-700 disabled:opacity-60" disabled={query.length < 3 || loading} onClick={handleSearch}>
            {loading ? "Searching..." : "Search"}
          </button>
        </div>

        {error && <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-3 text-sm font-semibold text-danger-700"><AlertCircle size={16} className="mt-0.5" /><span>{error}</span></div>}
        {success && <div className="flex items-start gap-2 rounded-lg bg-brand-50 p-3 text-sm font-semibold text-brand-800"><CheckCircle2 size={16} className="mt-0.5" /><span>{success}</span></div>}

        {results.length > 0 && (
          <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-neutral-100 bg-neutral-50 text-left"><th className="px-4 py-2 text-xs font-bold uppercase text-neutral-500">Handler</th><th className="px-4 py-2 text-xs font-bold uppercase text-neutral-500">Status</th><th className="px-4 py-2 text-xs font-bold uppercase text-neutral-500">Action</th></tr></thead>
              <tbody className="divide-y divide-neutral-50">
                {results.map((r) => (
                  <tr key={r.id} className="hover:bg-neutral-50">
                    <td className="px-4 py-2">
                      <p className="font-semibold text-neutral-800">{r.full_name}</p>
                      <p className="text-xs text-neutral-500">{r.phone} {r.system_identifier ? `· ${r.system_identifier}` : ""}</p>
                    </td>
                    <td className="px-4 py-2"><FitnessStatusBadge status={r.fitness_status || "not_linked"} /></td>
                    <td className="px-4 py-2">
                      <button className="inline-flex h-8 items-center gap-1.5 rounded bg-brand-600 px-3 text-xs font-bold text-white hover:bg-brand-700 disabled:opacity-60" disabled={linking === r.id} onClick={() => handleLink(r.id, r.full_name)}>
                        <Link2 size={12} />
                        {linking === r.id ? "Linking..." : "Link"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {!loading && results.length === 0 && query.length >= 3 && (
          <div className="rounded-lg border border-neutral-200 bg-white p-8 text-center">
            <p className="text-sm text-neutral-500">No unlinked food handlers found matching &quot;{query}&quot;.</p>
          </div>
        )}
      </div>
    </PortalShell>
  );
}
