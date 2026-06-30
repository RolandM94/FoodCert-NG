import type { AnalyticsField, AnalyticsAggregation, AnalyticsChartType } from "@/lib/analytics/fields";
import { isDimension, isMeasure, isTimeDimension, isGeographicDimension } from "@/lib/analytics/fields";
import type { DashboardScope } from "@/lib/analytics/validation";
import type { AnalyticsWorksheetFilter, AnalyticsWorksheetMetric } from "@/lib/api/analytics";

type QueryBuilderConfig = {
  datasetId: string;
  dimensions: AnalyticsField[];
  measures: Array<{ field: AnalyticsField; aggregation: AnalyticsAggregation }>;
  filters: Array<{ field: AnalyticsField; operator: string; value: string | number | boolean | string[] }>;
  scope: DashboardScope;
  chartType: AnalyticsChartType;
  limit?: number;
  name?: string;
  description?: string;
};

type QueryBuilderResult = {
  name: string;
  description: string;
  dataset: string;
  metrics: AnalyticsWorksheetMetric[];
  dimensions: Array<{ field: string }>;
  filters: AnalyticsWorksheetFilter[];
  aggregations: string[];
  derived_fields: Array<Record<string, unknown>>;
  query_rules: Record<string, unknown>;
  chart_recommendation: string;
  appliedScope: DashboardScope;
};

const AGG_LABEL: Record<AnalyticsAggregation, string> = {
  sum: "Total",
  count: "Count of",
  count_distinct: "Unique",
  avg: "Average",
  min: "Minimum",
  max: "Maximum",
  percentage: "%",
  rate: "Rate of",
  ratio: "Ratio of",
  variance: "Variance of",
};

export function buildMetricLabel(field: AnalyticsField, aggregation: AnalyticsAggregation) {
  const prefix = AGG_LABEL[aggregation] || "";
  return prefix ? `${prefix} ${field.label}` : field.label;
}

export function buildAnalyticsQuery(config: QueryBuilderConfig): QueryBuilderResult {
  const { datasetId, dimensions, measures, filters, scope, chartType, limit = 100, name, description } = config;

  const scopeFilters: AnalyticsWorksheetFilter[] = [];
  if (scope.stateId) {
    scopeFilters.push({ field: "state__id", operator: "eq", value: scope.stateId });
  }
  if (scope.employerId) {
    scopeFilters.push({ field: "employer__id", operator: "eq", value: scope.employerId });
  }
  if (scope.facilityId) {
    scopeFilters.push({ field: "facility_id", operator: "eq", value: scope.facilityId });
  }
  if (scope.laboratoryId) {
    scopeFilters.push({ field: "laboratory_id", operator: "eq", value: scope.laboratoryId });
  }

  const metricEntries: AnalyticsWorksheetMetric[] = measures.map(({ field, aggregation }) => ({
    field: field.fieldName,
    aggregation,
    label: buildMetricLabel(field, aggregation),
  }));

  const dimensionEntries = dimensions.map((field) => ({
    field: field.fieldName,
  }));

  const filterEntries: AnalyticsWorksheetFilter[] = [
    ...scopeFilters,
    ...filters.map((f) => ({
      field: f.field.fieldName,
      operator: f.operator,
      value: f.value,
    })),
  ];

  const computedFields: Array<Record<string, unknown>> = [];

  const hasPercentages = measures.some(({ aggregation }) =>
    aggregation === "percentage" || aggregation === "rate" || aggregation === "ratio",
  );

  if (hasPercentages) {
    computedFields.push({
      note: "Percentages, rates, and ratios are computed by the backend analytics engine based on row-level data.",
    });
  }

  const autoName =
    name ||
    `${chartType === "kpi" ? "KPI" : chartType === "line" ? "Trend" : "Analysis"}: ${measures.map((m) => m.field.label).join(", ")}${dimensions.length ? ` by ${dimensions.map((d) => d.label).join(", ")}` : ""}`;

  const autoDescription =
    description ||
    `Analytics worksheet generated for ${chartType} visualization. ` +
    `${measures.length} measure(s)${dimensions.length ? ` grouped by ${dimensions.length} dimension(s)` : ""}. ` +
    `Scope: ${scope.role}${scope.stateId ? ` (single state)` : scope.employerId ? ` (single employer)` : scope.facilityId ? ` (single facility)` : ` (national)`}.`;

  return {
    name: autoName,
    description: autoDescription,
    dataset: datasetId,
    metrics: metricEntries,
    dimensions: dimensionEntries,
    filters: filterEntries,
    aggregations: measures.map((m) => m.aggregation),
    derived_fields: computedFields,
    query_rules: { limit },
    chart_recommendation: chartType,
    appliedScope: scope,
  };
}

export type ChartSuggestion = {
  chartType: AnalyticsChartType;
  label: string;
  reason: string;
};

export function suggestChartTypes(
  dimensions: AnalyticsField[],
  measures: AnalyticsField[],
): ChartSuggestion[] {
  const suggestions: ChartSuggestion[] = [];
  const timeDimensions = dimensions.filter(isTimeDimension);
  const geoDimensions = dimensions.filter(isGeographicDimension);
  const dimCount = dimensions.length;
  const measureCount = measures.length;

  if (measureCount === 1 && dimCount === 0) {
    suggestions.push({
      chartType: "kpi",
      label: "KPI Card",
      reason: "Single measure with no dimensions works best as a KPI card.",
    });
  }

  if (dimCount >= 1 && measureCount >= 1) {
    suggestions.push({
      chartType: "bar",
      label: "Bar Chart",
      reason: "One or more dimensions with measures suits a bar chart for comparison.",
    });
  }

  if (dimCount >= 2 && measureCount >= 1) {
    suggestions.push({
      chartType: "grouped_bar",
      label: "Grouped Bar",
      reason: "Multiple dimensions let you break down measures further with grouped bars.",
    });
  }

  if (timeDimensions.length >= 1 && measureCount >= 1) {
    suggestions.push({
      chartType: "line",
      label: "Line Chart",
      reason: "Time dimensions enable trend analysis with a line chart.",
    });
  }

  if (dimCount === 1 && measureCount === 1 && !timeDimensions.length) {
    suggestions.push({
      chartType: "pie",
      label: "Pie Chart",
      reason: "One dimension and one measure can show proportional distribution.",
    });
    suggestions.push({
      chartType: "donut",
      label: "Donut Chart",
      reason: "Same data suits a donut chart for a modern proportional view.",
    });
  }

  if (geoDimensions.length >= 1 && measureCount >= 1) {
    suggestions.push({
      chartType: "map",
      label: "Map",
      reason: "Geographic dimensions such as State or LGA can be rendered on a map.",
    });
  }

  suggestions.push({
    chartType: "table",
    label: "Table",
    reason: "Tabular view works with any combination of dimensions and measures.",
  });

  return suggestions;
}

export function computeRateFormula(numeratorField: string, denominatorField: string) {
  return `(${numeratorField} / NULLIF(${denominatorField}, 0)) * 100`;
}

export function computePercentageFormula(partField: string, totalField: string) {
  return `(${partField} / NULLIF(${totalField}, 0)) * 100`;
}

export const COMPLIANCE_RATE_FORMULA = {
  label: "Compliance Rate",
  description: "Passed Inspections / Total Inspections Conducted * 100",
  numerator: "passed_inspections",
  denominator: "total_inspections",
};

export const TEST_POSITIVITY_RATE_FORMULA = {
  label: "Test Positivity Rate",
  description: "Positive Test Results / Completed Medical Tests * 100",
  numerator: "positive_results",
  denominator: "completed_tests",
};

export const CERTIFICATE_RENEWAL_RATE_FORMULA = {
  label: "Certificate Renewal Rate",
  description: "Renewed Certificates / Certificates Due for Renewal * 100",
  numerator: "renewed_certificates",
  denominator: "certificates_due",
};

export const CORRECTIVE_ACTION_RATE_FORMULA = {
  label: "Corrective Action Completion Rate",
  description: "Closed Corrective Actions / Total Corrective Actions * 100",
  numerator: "closed_actions",
  denominator: "total_actions",
};

export const FOODCERT_RATE_FORMULAS = {
  compliance_rate: COMPLIANCE_RATE_FORMULA,
  non_compliance_rate: {
    label: "Non-Compliance Rate",
    description: "Failed Inspections / Total Inspections Conducted * 100",
    numerator: "failed_inspections",
    denominator: "total_inspections",
  },
  test_positivity_rate: TEST_POSITIVITY_RATE_FORMULA,
  certificate_renewal_rate: CERTIFICATE_RENEWAL_RATE_FORMULA,
  corrective_action_rate: CORRECTIVE_ACTION_RATE_FORMULA,
  medical_clearance_rate: {
    label: "Medical Clearance Rate",
    description: "Cleared Food Handlers / Total Tested Food Handlers * 100",
    numerator: "cleared_handlers",
    denominator: "total_tested",
  },
  policy_adoption_rate: {
    label: "Policy Adoption Rate",
    description: "States Adopting Policy / Total States * 100",
    numerator: "adopting_states",
    denominator: "total_states",
  },
};
