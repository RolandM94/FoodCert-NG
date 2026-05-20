import { DataTable, StatusCell } from "./data-table";

export function UnitMemberTable({
  members,
}: {
  members: {
    id: string;
    name: string;
    email: string;
    role: string;
    unit_restricted: boolean;
  }[];
}) {
  if (members.length === 0) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-6 text-center text-sm text-slate-500">
        No members assigned to this unit yet.
      </div>
    );
  }

  const rows = members.map((m) => ({
    ...m,
    status: m.unit_restricted ? "restricted" : "unrestricted",
  }));

  return (
    <DataTable
      columns={[
        { key: "name", header: "Name", render: (r) => <span className="font-medium">{r.name}</span> },
        { key: "email", header: "Email", render: (r) => r.email },
        { key: "role", header: "Role", render: (r) => r.role },
        {
          key: "status",
          header: "Scope",
          render: (r) => <StatusCell status={r.status} />,
        },
      ]}
      rows={rows}
      empty="No members in this unit."
    />
  );
}
