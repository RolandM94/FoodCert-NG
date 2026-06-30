import { redirect } from "next/navigation";

function buildDashboardHref(searchParams?: Record<string, string | string[] | undefined>) {
  const params = new URLSearchParams();

  for (const [key, value] of Object.entries(searchParams ?? {})) {
    if (Array.isArray(value)) {
      value.forEach((item) => params.append(key, item));
      continue;
    }
    if (typeof value === "string") {
      params.set(key, value);
    }
  }

  const query = params.toString();
  return query ? `/employer/dashboard/worksheet-builder?${query}` : "/employer/dashboard/worksheet-builder";
}

export default async function EmployerReportsWorksheetBuilderRedirect({
  searchParams,
}: {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
}) {
  redirect(buildDashboardHref(await searchParams));
}
