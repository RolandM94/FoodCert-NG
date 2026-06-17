export type IndicatorReportingFrequency = "daily" | "weekly" | "monthly" | "quarterly" | "biannual" | "annual" | "ad_hoc" | "custom";
export type IndicatorRecordInputMode = "progress_only" | "cumulative_only" | "progress_or_cumulative";
export type IndicatorProgressRelationship = "dependent" | "same" | "independent";

export type IndicatorPeriod = {
  label: string;
  startDate: string;
  endDate: string;
  status: "baseline" | "current" | "future" | "target";
};

export type IndicatorInputConfig = {
  recordInputMode: IndicatorRecordInputMode;
  progressRelationship: IndicatorProgressRelationship;
  allowNegativeProgress?: boolean;
};

export type IndicatorSubmittedValue = {
  progressValue?: number | null;
  cumulativeValue?: number | null;
};

export type IndicatorCalculatedValue = {
  progressValue: number | null;
  cumulativeValue: number | null;
};

const FREQUENCY_MONTHS: Partial<Record<IndicatorReportingFrequency, number>> = {
  monthly: 1,
  quarterly: 3,
  biannual: 6,
  annual: 12,
};

function parseIsoDate(value: string) {
  const date = new Date(`${value}T00:00:00`);
  return Number.isNaN(date.getTime()) ? null : date;
}

function isoDate(date: Date) {
  return date.toISOString().slice(0, 10);
}

function addMonths(date: Date, months: number) {
  const next = new Date(date);
  next.setMonth(next.getMonth() + months);
  return next;
}

function addDays(date: Date, days: number) {
  const next = new Date(date);
  next.setDate(next.getDate() + days);
  return next;
}

function previousDay(date: Date) {
  const next = new Date(date);
  next.setDate(next.getDate() - 1);
  return next;
}

function periodLabel(date: Date, frequency: IndicatorReportingFrequency) {
  const year = date.getFullYear();
  const month = date.getMonth();
  if (frequency === "daily") return date.toLocaleDateString("en", { month: "short", day: "numeric", year: "numeric" });
  if (frequency === "weekly") return `Week of ${date.toLocaleDateString("en", { month: "short", day: "numeric", year: "numeric" })}`;
  if (frequency === "monthly") return date.toLocaleString("en", { month: "short", year: "numeric" });
  if (frequency === "quarterly") return `Q${Math.floor(month / 3) + 1} ${year}`;
  if (frequency === "biannual") return `${month < 6 ? "H1" : "H2"} ${year}`;
  if (frequency === "annual") return String(year);
  return "Ad hoc";
}

export function validateIndicatorInputMode(config: IndicatorInputConfig) {
  const errors: string[] = [];
  if (config.recordInputMode === "progress_or_cumulative" && config.progressRelationship === "independent") {
    errors.push("Independent relationship is not allowed when users can enter either progress or cumulative values.");
  }
  return errors;
}

export function generateIndicatorPeriods({
  frequency,
  startDate,
  endDate,
  currentDate,
}: {
  frequency: IndicatorReportingFrequency;
  startDate: string;
  endDate: string;
  currentDate?: string;
}) {
  const start = parseIsoDate(startDate);
  const end = parseIsoDate(endDate);
  const current = parseIsoDate(currentDate || isoDate(new Date()));
  if (frequency === "ad_hoc" || frequency === "custom") {
    if (!start || !end || !current || start > end) return [];
    const status: IndicatorPeriod["status"] = current >= start && current <= end ? "current" : current < start ? "future" : "baseline";
    return [{
      label: frequency === "custom" ? "Custom period" : "Ad hoc",
      startDate: isoDate(start),
      endDate: isoDate(end),
      status,
    }];
  }
  const dayStep = frequency === "daily" ? 1 : frequency === "weekly" ? 7 : null;
  if (dayStep) {
    if (!start || !end || !current || start > end) return [];
    const periods: IndicatorPeriod[] = [];
    let cursor = new Date(start);
    while (cursor <= end && periods.length < 80) {
      const nextStart = addDays(cursor, dayStep);
      const periodEnd = previousDay(nextStart);
      const boundedEnd = periodEnd > end ? end : periodEnd;
      const status: IndicatorPeriod["status"] = current >= cursor && current <= boundedEnd ? "current" : current < cursor ? "future" : "baseline";
      periods.push({
        label: periodLabel(cursor, frequency),
        startDate: isoDate(cursor),
        endDate: isoDate(boundedEnd),
        status,
      });
      cursor = nextStart;
    }
    return periods;
  }
  const step = FREQUENCY_MONTHS[frequency];
  if (!start || !end || !current || !step || start > end) return [];

  const periods: IndicatorPeriod[] = [];
  let cursor = new Date(start);
  while (cursor <= end && periods.length < 80) {
    const nextStart = addMonths(cursor, step);
    const periodEnd = previousDay(nextStart);
    const boundedEnd = periodEnd > end ? end : periodEnd;
    const status: IndicatorPeriod["status"] = current >= cursor && current <= boundedEnd ? "current" : current < cursor ? "future" : "baseline";
    periods.push({
      label: periodLabel(cursor, frequency),
      startDate: isoDate(cursor),
      endDate: isoDate(boundedEnd),
      status,
    });
    cursor = nextStart;
  }
  return periods;
}

export function calculateIndicatorInputValue({
  config,
  submittedValue,
  previousCumulativeValue = 0,
}: {
  config: IndicatorInputConfig;
  submittedValue: IndicatorSubmittedValue;
  previousCumulativeValue?: number | null;
}): IndicatorCalculatedValue {
  const errors = validateIndicatorInputMode(config);
  if (errors.length) throw new Error(errors[0]);

  const previous = previousCumulativeValue ?? 0;
  const progress = submittedValue.progressValue ?? null;
  const cumulative = submittedValue.cumulativeValue ?? null;
  let next: IndicatorCalculatedValue = { progressValue: progress, cumulativeValue: cumulative };

  if (config.recordInputMode === "progress_only") {
    if (progress == null) throw new Error("Progress value is required for progress-only indicators.");
    if (config.progressRelationship === "dependent") next = { progressValue: progress, cumulativeValue: previous + progress };
    if (config.progressRelationship === "same") next = { progressValue: progress, cumulativeValue: progress };
    if (config.progressRelationship === "independent") next = { progressValue: progress, cumulativeValue: null };
  }

  if (config.recordInputMode === "cumulative_only") {
    if (cumulative == null) throw new Error("Cumulative value is required for cumulative-only indicators.");
    if (config.progressRelationship === "dependent") next = { progressValue: cumulative - previous, cumulativeValue: cumulative };
    if (config.progressRelationship === "same") next = { progressValue: cumulative, cumulativeValue: cumulative };
    if (config.progressRelationship === "independent") next = { progressValue: null, cumulativeValue: cumulative };
  }

  if (config.recordInputMode === "progress_or_cumulative") {
    if (progress == null && cumulative == null) throw new Error("Enter either progress or cumulative value.");
    if (progress != null && cumulative != null) throw new Error("Enter either progress or cumulative value, not both.");
    if (config.progressRelationship === "dependent") {
      next = progress != null
        ? { progressValue: progress, cumulativeValue: previous + progress }
        : { progressValue: (cumulative ?? 0) - previous, cumulativeValue: cumulative };
    }
    if (config.progressRelationship === "same") {
      const value = progress ?? cumulative ?? null;
      next = { progressValue: value, cumulativeValue: value };
    }
  }

  if (!config.allowNegativeProgress && next.progressValue != null && next.progressValue < 0) {
    throw new Error("Negative progress is not allowed unless reversals/corrections are enabled.");
  }

  return next;
}
