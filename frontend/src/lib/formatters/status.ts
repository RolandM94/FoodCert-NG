export function titleCaseStatus(value?: string | null) {
  if (!value) {
    return "Unknown";
  }
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function formatNumber(value: string | number | null | undefined) {
  if (value === null || value === undefined || value === "") {
    return "0";
  }
  const numeric = Number(value);
  if (Number.isNaN(numeric)) {
    return String(value);
  }
  return new Intl.NumberFormat("en-NG").format(numeric);
}
