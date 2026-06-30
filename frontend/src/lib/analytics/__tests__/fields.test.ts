import { describe, it, expect } from "vitest";
import {
  inferFieldType,
  buildDatasetAnalyticsFields,
  getDimensions,
  getMeasures,
  isDimension,
  isMeasure,
  isTimeDimension,
  isGeographicDimension,
  canAggregate,
  type AnalyticsField,
} from "@/lib/analytics/fields";
import type { AnalyticsDataset } from "@/lib/api/analytics";

describe("inferFieldType", () => {
  it("classifies food_handler_id as dimension", () => {
    expect(inferFieldType("food_handler_id")).toBe("dimension");
  });

  it("classifies certificate_id as dimension", () => {
    expect(inferFieldType("certificate_id")).toBe("dimension");
  });

  it("classifies facility_id as dimension", () => {
    expect(inferFieldType("facility_id")).toBe("dimension");
  });

  it("classifies inspection_id as dimension", () => {
    expect(inferFieldType("inspection_id")).toBe("dimension");
  });

  it("classifies medical_test_id as dimension", () => {
    expect(inferFieldType("medical_test_id")).toBe("dimension");
  });

  it("classifies numeric IDs as dimensions, not measures", () => {
    const ids = [
      "food_handler_id",
      "certificate_id",
      "facility_id",
      "inspection_id",
      "medical_test_id",
      "employer_id",
      "laboratory_id",
      "identifier",
      "system_identifier",
      "registration_number",
      "certificate_code",
    ];
    for (const id of ids) {
      expect(inferFieldType(id)).toBe("dimension");
    }
  });

  it("classifies state as dimension", () => {
    expect(inferFieldType("state")).toBe("dimension");
  });

  it("classifies status as dimension", () => {
    expect(inferFieldType("status")).toBe("dimension");
    expect(inferFieldType("certificate_status")).toBe("dimension");
  });

  it("classifies category as dimension", () => {
    expect(inferFieldType("category")).toBe("dimension");
  });

  it("classifies numeric-only fields as measures when not matching dimension keywords", () => {
    expect(inferFieldType("total_records", "number_whole")).toBe("measure");
    expect(inferFieldType("amount", "number_decimal")).toBe("measure");
    expect(inferFieldType("score", "number_whole")).toBe("measure");
  });

  it("classifies total counts as measures when numeric", () => {
    expect(inferFieldType("total_certificates", "number_whole")).toBe("measure");
  });

  it("classifies string fields as dimensions", () => {
    expect(inferFieldType("full_name", "string")).toBe("dimension");
  });

  it("classifies boolean fields as dimensions", () => {
    expect(inferFieldType("is_active", "boolean")).toBe("dimension");
  });

  it("classifies date fields as dimensions", () => {
    expect(inferFieldType("created_at", "date")).toBe("dimension");
    expect(inferFieldType("expiry_date", "date")).toBe("dimension");
  });

  it("classifies time-related fields as dimensions", () => {
    expect(inferFieldType("month")).toBe("dimension");
    expect(inferFieldType("quarter")).toBe("dimension");
    expect(inferFieldType("year")).toBe("dimension");
    expect(inferFieldType("reporting_period")).toBe("dimension");
  });

  it("classifies FOODCERT compliance fields as dimensions", () => {
    expect(inferFieldType("compliance_status")).toBe("dimension");
    expect(inferFieldType("violation_type")).toBe("dimension");
    expect(inferFieldType("inspection_type")).toBe("dimension");
    expect(inferFieldType("inspection_status")).toBe("dimension");
  });

  it("classifies FOODCERT medical fields as dimensions", () => {
    expect(inferFieldType("test_type")).toBe("dimension");
    expect(inferFieldType("test_status")).toBe("dimension");
    expect(inferFieldType("fitness_status")).toBe("dimension");
    expect(inferFieldType("disease_category")).toBe("dimension");
  });

  it("classifies FOODCERT certificate fields as dimensions", () => {
    expect(inferFieldType("certificate_type")).toBe("dimension");
    expect(inferFieldType("renewal_status")).toBe("dimension");
    expect(inferFieldType("revocation_status")).toBe("dimension");
  });

  it("classifies FOODCERT payment fields as dimensions", () => {
    expect(inferFieldType("payment_status")).toBe("dimension");
    expect(inferFieldType("ownership_type")).toBe("dimension");
  });
});

describe("isDimension / isMeasure / isTimeDimension / isGeographicDimension / canAggregate", () => {
  const dimensionField: AnalyticsField = {
    id: "test:state",
    label: "State",
    fieldName: "state",
    fieldType: "dimension",
    dataType: "string",
    entity: "geography",
    allowedChartTypes: ["bar", "table"],
    isFilterable: true,
    isGroupable: true,
    isGeographicDimension: true,
  };

  const measureField: AnalyticsField = {
    id: "test:total",
    label: "Total",
    fieldName: "total",
    fieldType: "measure",
    dataType: "number",
    entity: "food_handler",
    allowedChartTypes: ["bar", "kpi", "table"],
    isFilterable: false,
    isGroupable: false,
    allowedAggregations: ["sum", "count", "avg"],
    defaultAggregation: "sum",
  };

  const timeField: AnalyticsField = {
    id: "test:month",
    label: "Month",
    fieldName: "month",
    fieldType: "dimension",
    dataType: "date",
    entity: "time",
    allowedChartTypes: ["line", "bar", "table"],
    isFilterable: true,
    isGroupable: true,
    isTimeDimension: true,
  };

  const idField: AnalyticsField = {
    id: "test:id",
    label: "ID",
    description: "Identifies records and is treated as a dimension, not an aggregatable measure.",
    fieldName: "food_handler_id",
    fieldType: "dimension",
    dataType: "number",
    entity: "food_handler",
    allowedChartTypes: ["bar", "table"],
    isFilterable: true,
    isGroupable: true,
  };

  it("isDimension returns true for dimensions", () => {
    expect(isDimension(dimensionField)).toBe(true);
    expect(isDimension(measureField)).toBe(false);
  });

  it("isMeasure returns true for measures", () => {
    expect(isMeasure(measureField)).toBe(true);
    expect(isMeasure(dimensionField)).toBe(false);
  });

  it("isTimeDimension returns true only for time dimensions", () => {
    expect(isTimeDimension(timeField)).toBe(true);
    expect(isTimeDimension(dimensionField)).toBe(false);
    expect(isTimeDimension(measureField)).toBe(false);
  });

  it("isGeographicDimension returns true only for geographic dimensions", () => {
    expect(isGeographicDimension(dimensionField)).toBe(true);
    expect(isGeographicDimension(measureField)).toBe(false);
  });

  it("canAggregate returns true only for measures with the aggregation", () => {
    expect(canAggregate(measureField, "sum")).toBe(true);
    expect(canAggregate(measureField, "percentage")).toBe(false);
    expect(canAggregate(dimensionField, "sum")).toBe(false);
    expect(canAggregate(idField, "sum")).toBe(false);
    expect(canAggregate(idField, "avg")).toBe(false);
  });

  it("numeric IDs cannot be aggregated", () => {
    expect(canAggregate(idField, "sum")).toBe(false);
    expect(canAggregate(idField, "count")).toBe(false);
    expect(canAggregate(idField, "avg")).toBe(false);
    expect(canAggregate(idField, "min")).toBe(false);
    expect(canAggregate(idField, "max")).toBe(false);
  });
});

function makeDataset(overrides: Partial<AnalyticsDataset> = {}): AnalyticsDataset {
  return {
    id: "d1",
    code: "food_handlers",
    name: "Food Handlers",
    description: "Registered food handlers",
    module_source: "food_handlers",
    allowed_account_types: ["federal", "state", "employer"],
    allowed_roles: ["federal_admin", "state_admin", "employer"],
    available_fields: [
      "system_identifier",
      "full_name",
      "gender",
      "category",
      "status",
      "risk_category",
      "state__name",
      "lga__name",
      "certificate_count",
    ],
    field_labels: {
      system_identifier: "System ID",
      full_name: "Full Name",
      gender: "Gender",
      category: "Category",
      status: "Status",
      risk_category: "Risk Category",
      "state__name": "State",
      "lga__name": "LGA",
      certificate_count: "Certificate Count",
    },
    field_types: {
      system_identifier: "string",
      full_name: "string",
      gender: "string",
      category: "string",
      status: "string",
      risk_category: "string",
      "state__name": "string",
      "lga__name": "string",
      certificate_count: "number_whole",
    },
    field_type_metadata: {},
    sensitive_fields: [],
    default_filters: {},
    joinable_datasets: [],
    aggregation_rules: {},
    required_permissions: [],
    privacy_level: "internal",
    is_active: true,
    ...overrides,
  };
}

describe("buildDatasetAnalyticsFields", () => {
  it("separates dimensions from measures", () => {
    const dataset = makeDataset();
    const fields = buildDatasetAnalyticsFields(dataset);
    const dims = getDimensions(fields);
    const meas = getMeasures(fields);

    expect(dims.length).toBeGreaterThan(0);
    expect(meas.length).toBeGreaterThan(0);

    const statusField = dims.find((f) => f.fieldName === "status");
    expect(statusField).toBeDefined();
    expect(statusField?.fieldType).toBe("dimension");

    const countField = meas.find((f) => f.fieldName === "certificate_count");
    expect(countField).toBeDefined();
    expect(countField?.fieldType).toBe("measure");
  });

  it("marks state, lga as geographic dimensions", () => {
    const dataset = makeDataset();
    const fields = buildDatasetAnalyticsFields(dataset);
    const stateField = fields.find((f) => f.fieldName === "state__name");
    const lgaField = fields.find((f) => f.fieldName === "lga__name");

    expect(stateField?.isGeographicDimension).toBe(true);
    expect(lgaField?.isGeographicDimension).toBe(true);
  });

  it("marks IDs as dimensions with descriptive text", () => {
    const dataset = makeDataset();
    const fields = buildDatasetAnalyticsFields(dataset);
    const idField = fields.find((f) => f.fieldName === "system_identifier");

    expect(idField?.fieldType).toBe("dimension");
    expect(idField?.description).toContain("identifies records");
  });

  it("adds measures with proper aggregation options", () => {
    const dataset = makeDataset();
    const fields = buildDatasetAnalyticsFields(dataset);
    const measureFields = getMeasures(fields);

    for (const measure of measureFields) {
      expect(measure.allowedAggregations).toBeDefined();
      expect(measure.allowedAggregations!.length).toBeGreaterThan(0);
      expect(measure.defaultAggregation).toBeDefined();
    }
  });

  it("filters static fields to only those available in dataset", () => {
    const dataset = makeDataset({ available_fields: ["state__name", "gender"] });
    const fields = buildDatasetAnalyticsFields(dataset);

    const stateField = fields.find((f) => f.fieldName === "state__name");
    expect(stateField?.isGeographicDimension).toBe(true);

    const lgaField = fields.find((f) => f.fieldName === "lga__name");
    expect(lgaField).toBeUndefined();
  });

  it("dimensions are filterable and groupable", () => {
    const dataset = makeDataset();
    const fields = buildDatasetAnalyticsFields(dataset);
    const dims = getDimensions(fields);

    for (const dim of dims) {
      expect(dim.isFilterable).toBe(true);
      expect(dim.isGroupable).toBe(true);
    }
  });

  it("measures are not filterable by default", () => {
    const dataset = makeDataset();
    const fields = buildDatasetAnalyticsFields(dataset);
    const measures = getMeasures(fields);

    for (const measure of measures) {
      expect(measure.isFilterable).toBe(false);
    }
  });
});
