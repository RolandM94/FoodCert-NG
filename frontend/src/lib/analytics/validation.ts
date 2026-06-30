import type { UserRole } from "@/types/auth";
import type { AnalyticsField, AnalyticsChartType } from "@/lib/analytics/fields";

export type DashboardScope = {
  role: UserRole | string;
  countryId?: string;
  stateId?: string;
  lgaIds?: string[];
  employerId?: string;
  facilityId?: string;
  laboratoryId?: string;
  inspectorId?: string;
};

export function resolveDashboardScope(user: {
  role?: UserRole | string;
  state_id?: string | null;
  state?: string | null;
  organization_id?: string | null;
  organization?: string | null;
  facility_id?: string | null;
  laboratory_id?: string | null;
  id?: string | null;
}): DashboardScope {
  const role = user.role || "";
  const stateId = user.state_id || user.state || undefined;
  const orgId = user.organization_id || user.organization || undefined;

  if (role === "super_admin") {
    return { role, countryId: "ng" };
  }
  if (role === "federal_admin") {
    return {
      role,
      countryId: "ng",
      stateId: stateId || undefined,
    };
  }
  if (role === "state_admin") {
    return {
      role,
      countryId: "ng",
      stateId: stateId || undefined,
    };
  }
  if (role === "employer") {
    return {
      role,
      employerId: orgId || undefined,
    };
  }
  if (role === "facility_admin") {
    return {
      role,
      facilityId: orgId || user.facility_id || undefined,
      stateId: stateId || undefined,
    };
  }
  if (role === "doctor") {
    return {
      role,
      facilityId: orgId || user.facility_id || undefined,
    };
  }
  if (role === "lab_staff") {
    return {
      role,
      laboratoryId: orgId || user.laboratory_id || undefined,
      facilityId: user.facility_id || undefined,
    };
  }
  if (role === "food_handler") {
    return {
      role,
      employerId: orgId || undefined,
    };
  }
  if (role === "inspector") {
    return {
      role,
      inspectorId: user.id || undefined,
      stateId: stateId || undefined,
    };
  }
  return { role };
}

export function validateChartConfig(config: {
  chartType: AnalyticsChartType;
  dimensions: AnalyticsField[];
  measures: AnalyticsField[];
  filters?: unknown[];
}): {
  valid: boolean;
  errors: string[];
  warnings: string[];
  suggestedChartTypes: AnalyticsChartType[];
} {
  const { chartType, dimensions, measures } = config;
  const errors: string[] = [];
  const warnings: string[] = [];
  const timeDimensions = dimensions.filter((field) => field.isTimeDimension);
  const geoDimensions = dimensions.filter((field) => field.isGeographicDimension);

  if (chartType === "kpi") {
    if (measures.length !== 1) errors.push("KPI cards should use one primary measure.");
  }
  if (chartType === "bar") {
    if (dimensions.length < 1 || measures.length < 1) errors.push("Bar charts require one dimension and one measure.");
  }
  if (chartType === "grouped_bar") {
    if (dimensions.length < 2 || measures.length < 1) errors.push("Grouped bar charts require a primary dimension, a secondary dimension, and one measure.");
  }
  if (chartType === "line") {
    if (!timeDimensions.length) errors.push("Line charts require a time-based dimension such as Month, Quarter, Year, Issue Date, Test Date, or Inspection Date.");
    if (!measures.length) errors.push("Line charts require at least one measure.");
  }
  if (chartType === "map") {
    if (!geoDimensions.length) errors.push("Map charts require a geographic dimension such as State, LGA, Ward, or Facility Location.");
    if (!measures.length) errors.push("Map charts require one measure.");
  }
  if (chartType === "pie" || chartType === "donut") {
    if (dimensions.length !== 1 || measures.length !== 1) errors.push("Pie and donut charts require one dimension and one measure.");
    if (dimensions.length === 1 && dimensions[0].isTimeDimension) warnings.push("Pie charts are best used with low-cardinality dimensions such as Certificate Status, Test Result, Risk Category, or Compliance Status.");
  }

  const suggestedChartTypes: AnalyticsChartType[] = [];
  if (timeDimensions.length && measures.length) suggestedChartTypes.push("line");
  if (geoDimensions.length && measures.length) suggestedChartTypes.push("map");
  if (dimensions.length === 1 && measures.length === 1) suggestedChartTypes.push("bar", "pie", "donut");
  if (dimensions.length >= 2 && measures.length) suggestedChartTypes.push("grouped_bar", "table");
  if (measures.length === 1 && !dimensions.length) suggestedChartTypes.push("kpi");
  if (!suggestedChartTypes.includes("table")) suggestedChartTypes.push("table");

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    suggestedChartTypes: Array.from(new Set(suggestedChartTypes)),
  };
}

export function getFieldCompatibilityReason(field: AnalyticsField, chartType: AnalyticsChartType): string | null {
  if (!field.allowedChartTypes.includes(chartType)) {
    if (field.fieldType === "dimension") {
      if (chartType === "line") {
        return "This chart works best with a time-based dimension such as Month, Quarter, Year, Issue Date, Test Date, or Inspection Date.";
      }
      if (chartType === "map") {
        return "This chart needs a geographic dimension such as State, LGA, Ward, or Facility Location.";
      }
      return "This dimension is not compatible with the selected chart type.";
    }
    return "This measure is not compatible with the selected chart type.";
  }
  if (field.fieldType === "dimension" && field.fieldName.toLowerCase().includes("id")) {
    return "This field is an ID and can be used for grouping or filtering, but not as a summed value.";
  }
  return null;
}

export function buildAnalyticsInsightInput(config: {
  dimensions: AnalyticsField[];
  measures: AnalyticsField[];
  filters: Array<Record<string, unknown>>;
  chartType: AnalyticsChartType;
  role: UserRole | string;
  scope: DashboardScope;
  aggregatedData: Array<Record<string, unknown>>;
  comparisonPeriod?: string;
  timePeriod?: string;
}): AnalyticsInsightInput {
  return {
    dimensions: config.dimensions.map((field) => ({
      fieldName: field.fieldName,
      label: field.label,
      fieldType: field.fieldType,
    })),
    measures: config.measures.map((field) => ({
      fieldName: field.fieldName,
      label: field.label,
      fieldType: field.fieldType,
      defaultAggregation: field.defaultAggregation,
    })),
    filters: config.filters,
    chartType: config.chartType,
    role: config.role,
    scope: config.scope,
    aggregatedData: config.aggregatedData,
    comparisonPeriod: config.comparisonPeriod,
    timePeriod: config.timePeriod,
  };
}

export type AnalyticsInsightInput = {
  dimensions: Array<Pick<AnalyticsField, "fieldName" | "label" | "fieldType">>;
  measures: Array<Pick<AnalyticsField, "fieldName" | "label" | "fieldType" | "defaultAggregation">>;
  filters: Array<Record<string, unknown>>;
  chartType: AnalyticsChartType;
  role: UserRole | string;
  scope: DashboardScope;
  aggregatedData: Array<Record<string, unknown>>;
  comparisonPeriod?: string;
  timePeriod?: string;
};

export type AnalyticsInsightOutput = {
  summary: string;
  findings: string[];
  riskAreas: string[];
  recommendedActions: string[];
  caveats: string[];
};
