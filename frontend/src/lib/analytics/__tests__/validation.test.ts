import { describe, it, expect } from "vitest";
import {
  validateChartConfig,
  resolveDashboardScope,
  getFieldCompatibilityReason,
  buildAnalyticsInsightInput,
} from "@/lib/analytics/validation";
import type { AnalyticsField } from "@/lib/analytics/fields";

function dim(fieldName: string, overrides: Partial<AnalyticsField> = {}): AnalyticsField {
  return {
    id: `test:${fieldName}`,
    label: fieldName,
    fieldName,
    fieldType: "dimension",
    dataType: "string",
    entity: "food_handler",
    allowedChartTypes: ["bar", "grouped_bar", "line", "pie", "donut", "table", "map"],
    isFilterable: true,
    isGroupable: true,
    ...overrides,
  };
}

function meas(fieldName: string, overrides: Partial<AnalyticsField> = {}): AnalyticsField {
  return {
    id: `test:${fieldName}`,
    label: fieldName,
    fieldName,
    fieldType: "measure",
    dataType: "number",
    entity: "food_handler",
    allowedChartTypes: ["kpi", "bar", "grouped_bar", "line", "pie", "donut", "table", "map"],
    isFilterable: false,
    isGroupable: false,
    allowedAggregations: ["sum", "count", "avg"],
    defaultAggregation: "sum",
    ...overrides,
  };
}

describe("validateChartConfig", () => {
  it("validates KPI card with exactly 1 measure", () => {
    const result = validateChartConfig({
      chartType: "kpi",
      dimensions: [],
      measures: [meas("total")],
    });
    expect(result.valid).toBe(true);
  });

  it("rejects KPI card with 0 measures", () => {
    const result = validateChartConfig({
      chartType: "kpi",
      dimensions: [],
      measures: [],
    });
    expect(result.valid).toBe(false);
    expect(result.errors).toContain("KPI cards should use one primary measure.");
  });

  it("rejects KPI card with 2 measures", () => {
    const result = validateChartConfig({
      chartType: "kpi",
      dimensions: [],
      measures: [meas("a"), meas("b")],
    });
    expect(result.valid).toBe(false);
  });

  it("validates bar chart with 1+ dimension and 1+ measure", () => {
    const result = validateChartConfig({
      chartType: "bar",
      dimensions: [dim("state")],
      measures: [meas("total")],
    });
    expect(result.valid).toBe(true);
  });

  it("rejects bar chart with no dimension", () => {
    const result = validateChartConfig({
      chartType: "bar",
      dimensions: [],
      measures: [meas("total")],
    });
    expect(result.valid).toBe(false);
    expect(result.errors).toContain("Bar charts require one dimension and one measure.");
  });

  it("validates grouped bar chart with 2+ dimensions and 1+ measure", () => {
    const result = validateChartConfig({
      chartType: "grouped_bar",
      dimensions: [dim("state"), dim("status")],
      measures: [meas("total")],
    });
    expect(result.valid).toBe(true);
  });

  it("rejects grouped bar with only 1 dimension", () => {
    const result = validateChartConfig({
      chartType: "grouped_bar",
      dimensions: [dim("state")],
      measures: [meas("total")],
    });
    expect(result.valid).toBe(false);
  });

  it("validates line chart with time dimension and 1+ measure", () => {
    const timeDim = dim("month", { isTimeDimension: true, allowedChartTypes: ["line", "bar", "table"] });
    const result = validateChartConfig({
      chartType: "line",
      dimensions: [timeDim],
      measures: [meas("total")],
    });
    expect(result.valid).toBe(true);
  });

  it("rejects line chart without time dimension", () => {
    const result = validateChartConfig({
      chartType: "line",
      dimensions: [dim("state")],
      measures: [meas("total")],
    });
    expect(result.valid).toBe(false);
    expect(result.errors).toContain("Line charts require a time-based dimension such as Month, Quarter, Year, Issue Date, Test Date, or Inspection Date.");
  });

  it("validates map chart with geographic dimension and 1+ measure", () => {
    const geoDim = dim("state__name", { isGeographicDimension: true });
    const result = validateChartConfig({
      chartType: "map",
      dimensions: [geoDim],
      measures: [meas("total")],
    });
    expect(result.valid).toBe(true);
  });

  it("rejects map chart without geographic dimension", () => {
    const result = validateChartConfig({
      chartType: "map",
      dimensions: [dim("status")],
      measures: [meas("total")],
    });
    expect(result.valid).toBe(false);
    expect(result.errors).toContain("Map charts require a geographic dimension such as State, LGA, Ward, or Facility Location.");
  });

  it("validates pie chart with exactly 1 dimension and 1 measure", () => {
    const result = validateChartConfig({
      chartType: "pie",
      dimensions: [dim("category")],
      measures: [meas("total")],
    });
    expect(result.valid).toBe(true);
  });

  it("rejects pie chart with 0 dimensions", () => {
    const result = validateChartConfig({
      chartType: "pie",
      dimensions: [],
      measures: [meas("total")],
    });
    expect(result.valid).toBe(false);
  });

  it("validates donut chart with exactly 1 dimension and 1 measure", () => {
    const result = validateChartConfig({
      chartType: "donut",
      dimensions: [dim("status")],
      measures: [meas("total")],
    });
    expect(result.valid).toBe(true);
  });

  it("warns when pie chart uses time dimension", () => {
    const timeDim = dim("month", { isTimeDimension: true });
    const result = validateChartConfig({
      chartType: "pie",
      dimensions: [timeDim],
      measures: [meas("total")],
    });
    expect(result.warnings.length).toBeGreaterThan(0);
  });

  it("table chart always validates", () => {
    const result = validateChartConfig({
      chartType: "table",
      dimensions: [],
      measures: [],
    });
    expect(result.valid).toBe(true);
  });

  it("suggests line chart when time dimensions and measures present", () => {
    const timeDim = dim("month", { isTimeDimension: true });
    const result = validateChartConfig({
      chartType: "bar",
      dimensions: [timeDim],
      measures: [meas("total")],
    });
    expect(result.suggestedChartTypes).toContain("line");
  });

  it("suggests map chart when geo dimensions and measures present", () => {
    const geoDim = dim("state__name", { isGeographicDimension: true });
    const result = validateChartConfig({
      chartType: "table",
      dimensions: [geoDim],
      measures: [meas("total")],
    });
    expect(result.suggestedChartTypes).toContain("map");
  });

  it("suggests KPI card when single measure with no dimensions", () => {
    const result = validateChartConfig({
      chartType: "table",
      dimensions: [],
      measures: [meas("total")],
    });
    expect(result.suggestedChartTypes).toContain("kpi");
  });
});

describe("resolveDashboardScope", () => {
  it("resolves federal_admin to national scope", () => {
    const scope = resolveDashboardScope({ role: "federal_admin" });
    expect(scope.role).toBe("federal_admin");
    expect(scope.countryId).toBe("ng");
    expect(scope.stateId).toBeUndefined();
  });

  it("resolves super_admin to national scope", () => {
    const scope = resolveDashboardScope({ role: "super_admin" });
    expect(scope.role).toBe("super_admin");
    expect(scope.countryId).toBe("ng");
  });

  it("resolves state_admin to state scope", () => {
    const scope = resolveDashboardScope({ role: "state_admin", state_id: "st-lagos" });
    expect(scope.role).toBe("state_admin");
    expect(scope.stateId).toBe("st-lagos");
  });

  it("resolves employer to employer scope", () => {
    const scope = resolveDashboardScope({ role: "employer", organization_id: "org-1" });
    expect(scope.role).toBe("employer");
    expect(scope.employerId).toBe("org-1");
  });

  it("resolves facility_admin to facility scope", () => {
    const scope = resolveDashboardScope({ role: "facility_admin", organization_id: "fac-1" });
    expect(scope.role).toBe("facility_admin");
    expect(scope.facilityId).toBe("fac-1");
  });

  it("resolves doctor to facility scope", () => {
    const scope = resolveDashboardScope({ role: "doctor", organization_id: "fac-2" });
    expect(scope.role).toBe("doctor");
    expect(scope.facilityId).toBe("fac-2");
  });

  it("resolves lab_staff to laboratory scope", () => {
    const scope = resolveDashboardScope({ role: "lab_staff", organization_id: "lab-1" });
    expect(scope.role).toBe("lab_staff");
    expect(scope.laboratoryId).toBe("lab-1");
  });

  it("resolves food_handler to employer scope", () => {
    const scope = resolveDashboardScope({ role: "food_handler", organization_id: "org-2" });
    expect(scope.role).toBe("food_handler");
    expect(scope.employerId).toBe("org-2");
  });

  it("resolves inspector to inspector scope with state", () => {
    const scope = resolveDashboardScope({ role: "inspector", id: "insp-1", state_id: "st-kano" });
    expect(scope.role).toBe("inspector");
    expect(scope.inspectorId).toBe("insp-1");
    expect(scope.stateId).toBe("st-kano");
  });

  it("returns empty scope for unknown roles", () => {
    const scope = resolveDashboardScope({ role: "unknown_role" });
    expect(scope.role).toBe("unknown_role");
    expect(scope.countryId).toBeUndefined();
    expect(scope.stateId).toBeUndefined();
  });
});

describe("getFieldCompatibilityReason", () => {
  it("explains why a regular dimension is incompatible with line chart", () => {
    const field = dim("state", { allowedChartTypes: ["bar", "table"] });
    const reason = getFieldCompatibilityReason(field, "line");
    expect(reason).toBeTruthy();
    expect(reason).toContain("time-based dimension");
  });

  it("explains why a regular dimension is incompatible with map chart", () => {
    const field = dim("status", { allowedChartTypes: ["bar", "table"] });
    const reason = getFieldCompatibilityReason(field, "map");
    expect(reason).toBeTruthy();
    expect(reason).toContain("geographic dimension");
  });

  it("warns about ID fields", () => {
    const field = dim("facility_id", { allowedChartTypes: ["bar", "table"] });
    const reason = getFieldCompatibilityReason(field, "bar");
    expect(reason).toContain("ID");
  });

  it("returns null for fully compatible fields", () => {
    const field = dim("state", { allowedChartTypes: ["bar", "table"] });
    const reason = getFieldCompatibilityReason(field, "bar");
    expect(reason).toBeNull();
  });
});

describe("buildAnalyticsInsightInput", () => {
  it("builds insight input from dashboard config", () => {
    const stateDim = dim("state__name", { isGeographicDimension: true });
    const totalMeas = meas("total_certificates");
    const scope = resolveDashboardScope({ role: "federal_admin" });

    const input = buildAnalyticsInsightInput({
      dimensions: [stateDim],
      measures: [totalMeas],
      filters: [{ field: "status", operator: "eq", value: "valid" }],
      chartType: "bar",
      role: "federal_admin",
      scope,
      aggregatedData: [{ "state__name": "Lagos", total_certificates: 500 }],
      timePeriod: "Q1 2026",
    });

    expect(input.dimensions).toHaveLength(1);
    expect(input.dimensions[0].fieldName).toBe("state__name");
    expect(input.measures).toHaveLength(1);
    expect(input.measures[0].defaultAggregation).toBe("sum");
    expect(input.chartType).toBe("bar");
    expect(input.role).toBe("federal_admin");
    expect(input.scope.countryId).toBe("ng");
    expect(input.filters).toHaveLength(1);
    expect(input.aggregatedData).toHaveLength(1);
    expect(input.timePeriod).toBe("Q1 2026");
  });

  it("includes comparison period when provided", () => {
    const scope = resolveDashboardScope({ role: "state_admin", state_id: "st-lagos" });

    const input = buildAnalyticsInsightInput({
      dimensions: [],
      measures: [meas("total")],
      filters: [],
      chartType: "kpi",
      role: "state_admin",
      scope,
      aggregatedData: [],
      comparisonPeriod: "Q1 2025",
    });

    expect(input.comparisonPeriod).toBe("Q1 2025");
  });
});
