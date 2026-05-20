const ROUTING_SUGGESTIONS = [
  { workflow: "Certificate validation", unit_type: "unit", label: "Certificate Verification Desk" },
  { workflow: "Facility accreditation", unit_type: "unit", label: "Facility Accreditation Unit" },
  { workflow: "Fee configuration", unit_type: "unit", label: "Policy and Finance Unit" },
  { workflow: "Inspection assignment", unit_type: "department", label: "Inspectorate" },
  { workflow: "LGA inspections", unit_type: "lga_office", label: "LGA Office" },
];

export function QueueRoutingPanel({
  units,
}: {
  units: { id: string; name: string; unit_type: string }[];
}) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="mb-3 text-sm font-bold text-slate-950">Queue Routing</h3>
      <p className="mb-4 text-xs text-slate-500">
        Assign workflows to units for default queue filtering.
      </p>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-slate-100 text-left">
              <th className="pb-2 font-semibold text-slate-600">Workflow</th>
              <th className="pb-2 font-semibold text-slate-600">Suggested Unit</th>
              <th className="pb-2 font-semibold text-slate-600">Assigned</th>
            </tr>
          </thead>
          <tbody>
            {ROUTING_SUGGESTIONS.map((row) => (
              <tr key={row.workflow} className="border-b border-slate-50">
                <td className="py-2 pr-4 font-medium text-slate-800">{row.workflow}</td>
                <td className="py-2 pr-4 text-slate-500">{row.label}</td>
                <td className="py-2 pr-4">
                  <select
                    className="h-8 rounded border border-slate-200 bg-white px-2 text-xs"
                    defaultValue=""
                  >
                    <option value="">-- Select --</option>
                    {units.map((u) => (
                      <option key={u.id} value={u.id}>
                        {u.name}
                      </option>
                    ))}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <button className="mt-4 inline-flex h-9 items-center gap-2 rounded bg-brand-green px-4 text-xs font-bold text-white hover:bg-brand-deep">
        Save Routing
      </button>
    </div>
  );
}
