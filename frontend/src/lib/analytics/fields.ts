import type { AnalyticsDataset } from "@/lib/api/analytics";
import type { UserRole } from "@/types/auth";

export type AnalyticsFieldType = "dimension" | "measure";
export type AnalyticsDataType = "string" | "number" | "date" | "boolean" | "percentage" | "currency";
export type AnalyticsEntity =
  | "food_handler"
  | "certificate"
  | "medical_test"
  | "laboratory"
  | "inspection"
  | "employer"
  | "facility"
  | "policy"
  | "payment"
  | "geography"
  | "time"
  | "report"
  | "indicator"
  | "organization";
export type AnalyticsAggregation =
  | "sum"
  | "count"
  | "count_distinct"
  | "avg"
  | "min"
  | "max"
  | "percentage"
  | "rate"
  | "ratio"
  | "variance";
export type AnalyticsChartType =
  | "kpi"
  | "bar"
  | "grouped_bar"
  | "line"
  | "pie"
  | "donut"
  | "table"
  | "map";

export type AnalyticsField = {
  id: string;
  label: string;
  description?: string;
  fieldName: string;
  fieldType: AnalyticsFieldType;
  dataType: AnalyticsDataType;
  entity: AnalyticsEntity;
  allowedAggregations?: AnalyticsAggregation[];
  defaultAggregation?: AnalyticsAggregation;
  allowedChartTypes: AnalyticsChartType[];
  isFilterable: boolean;
  isGroupable: boolean;
  isTimeDimension?: boolean;
  isGeographicDimension?: boolean;
  requiredRoleAccess?: UserRole[];
  sourceDatasets?: string[];
  disabledReason?: string;
};

const DIMENSION_CHARTS: AnalyticsChartType[] = ["bar", "grouped_bar", "line", "pie", "donut", "table", "map"];
const MEASURE_CHARTS: AnalyticsChartType[] = ["kpi", "bar", "grouped_bar", "line", "pie", "donut", "table", "map"];
const ALL_AGGREGATIONS: AnalyticsAggregation[] = ["sum", "count", "count_distinct", "avg", "min", "max", "percentage", "rate", "ratio", "variance"];

const STATIC_FIELDS: AnalyticsField[] = [
  {
    id: "state",
    label: "State",
    description: "State-level grouping and dashboard filtering.",
    fieldName: "state__name",
    fieldType: "dimension",
    dataType: "string",
    entity: "geography",
    allowedChartTypes: DIMENSION_CHARTS,
    isFilterable: true,
    isGroupable: true,
    isGeographicDimension: true,
  },
  {
    id: "lga",
    label: "LGA",
    description: "Local government area grouping and drilldown.",
    fieldName: "lga__name",
    fieldType: "dimension",
    dataType: "string",
    entity: "geography",
    allowedChartTypes: DIMENSION_CHARTS,
    isFilterable: true,
    isGroupable: true,
    isGeographicDimension: true,
  },
  {
    id: "ward",
    label: "Ward",
    description: "Ward-level segmentation where available.",
    fieldName: "ward",
    fieldType: "dimension",
    dataType: "string",
    entity: "geography",
    allowedChartTypes: DIMENSION_CHARTS,
    isFilterable: true,
    isGroupable: true,
    isGeographicDimension: true,
  },
  {
    id: "year",
    label: "Year",
    description: "Year-based time breakdown.",
    fieldName: "year",
    fieldType: "dimension",
    dataType: "date",
    entity: "time",
    allowedChartTypes: ["line", "bar", "grouped_bar", "table"],
    isFilterable: true,
    isGroupable: true,
    isTimeDimension: true,
  },
  {
    id: "quarter",
    label: "Quarter",
    description: "Quarter-based reporting period breakdown.",
    fieldName: "quarter",
    fieldType: "dimension",
    dataType: "date",
    entity: "time",
    allowedChartTypes: ["line", "bar", "grouped_bar", "table"],
    isFilterable: true,
    isGroupable: true,
    isTimeDimension: true,
  },
  {
    id: "month",
    label: "Month",
    description: "Month-based trend analysis.",
    fieldName: "month",
    fieldType: "dimension",
    dataType: "date",
    entity: "time",
    allowedChartTypes: ["line", "bar", "grouped_bar", "table"],
    isFilterable: true,
    isGroupable: true,
    isTimeDimension: true,
  },
  {
    id: "reporting_period",
    label: "Reporting Period",
    description: "Configured reporting period dimension.",
    fieldName: "reporting_period",
    fieldType: "dimension",
    dataType: "date",
    entity: "report",
    allowedChartTypes: ["line", "bar", "table"],
    isFilterable: true,
    isGroupable: true,
    isTimeDimension: true,
  },
  {
    id: "certificate_status",
    label: "Certificate Status",
    description: "Certificate lifecycle status: valid, expired, revoked, pending renewal.",
    fieldName: "status",
    fieldType: "dimension",
    dataType: "string",
    entity: "certificate",
    allowedChartTypes: DIMENSION_CHARTS,
    isFilterable: true,
    isGroupable: true,
    sourceDatasets: ["certificates"],
  },
  {
    id: "certificate_type",
    label: "Certificate Type",
    description: "Type of certificate issued (e.g., food handler, facility, renewal).",
    fieldName: "certificate_type",
    fieldType: "dimension",
    dataType: "string",
    entity: "certificate",
    allowedChartTypes: DIMENSION_CHARTS,
    isFilterable: true,
    isGroupable: true,
    sourceDatasets: ["certificates"],
  },
  {
    id: "food_handler_category",
    label: "Food Handler Category",
    description: "Category of food handler (e.g., street vendor, restaurant staff, caterer).",
    fieldName: "category",
    fieldType: "dimension",
    dataType: "string",
    entity: "food_handler",
    allowedChartTypes: DIMENSION_CHARTS,
    isFilterable: true,
    isGroupable: true,
    sourceDatasets: ["food_handlers"],
  },
  {
    id: "food_handler_risk",
    label: "Risk Category",
    description: "Risk classification of food handler: high, medium, low.",
    fieldName: "risk_category",
    fieldType: "dimension",
    dataType: "string",
    entity: "food_handler",
    allowedChartTypes: DIMENSION_CHARTS,
    isFilterable: true,
    isGroupable: true,
    sourceDatasets: ["food_handlers"],
  },
  {
    id: "medical_test_type",
    label: "Medical Test Type",
    description: "Type of medical investigation or screening.",
    fieldName: "test_type",
    fieldType: "dimension",
    dataType: "string",
    entity: "medical_test",
    allowedChartTypes: DIMENSION_CHARTS,
    isFilterable: true,
    isGroupable: true,
    sourceDatasets: ["medical_tests"],
  },
  {
    id: "medical_test_status",
    label: "Medical Test Status",
    description: "Status of medical test: pending, completed, failed, passed.",
    fieldName: "test_status",
    fieldType: "dimension",
    dataType: "string",
    entity: "medical_test",
    allowedChartTypes: DIMENSION_CHARTS,
    isFilterable: true,
    isGroupable: true,
    sourceDatasets: ["medical_tests"],
  },
  {
    id: "fitness_status",
    label: "Fitness Status",
    description: "Medical fitness determination: fit, unfit, pending review.",
    fieldName: "fitness_status",
    fieldType: "dimension",
    dataType: "string",
    entity: "medical_test",
    allowedChartTypes: DIMENSION_CHARTS,
    isFilterable: true,
    isGroupable: true,
    sourceDatasets: ["medical_tests"],
  },
  {
    id: "inspection_type",
    label: "Inspection Type",
    description: "Type of inspection conducted: routine, follow-up, complaint-driven.",
    fieldName: "inspection_type",
    fieldType: "dimension",
    dataType: "string",
    entity: "inspection",
    allowedChartTypes: DIMENSION_CHARTS,
    isFilterable: true,
    isGroupable: true,
    sourceDatasets: ["inspections"],
  },
  {
    id: "inspection_status",
    label: "Inspection Status",
    description: "Status of inspection: scheduled, in-progress, completed, on-hold.",
    fieldName: "inspection_status",
    fieldType: "dimension",
    dataType: "string",
    entity: "inspection",
    allowedChartTypes: DIMENSION_CHARTS,
    isFilterable: true,
    isGroupable: true,
    sourceDatasets: ["inspections"],
  },
  {
    id: "compliance_status",
    label: "Compliance Status",
    description: "Compliance determination: compliant, non-compliant, partial.",
    fieldName: "compliance_status",
    fieldType: "dimension",
    dataType: "string",
    entity: "inspection",
    allowedChartTypes: DIMENSION_CHARTS,
    isFilterable: true,
    isGroupable: true,
    sourceDatasets: ["inspections"],
  },
  {
    id: "violation_type",
    label: "Violation Type",
    description: "Category of violation identified during inspection.",
    fieldName: "violation_type",
    fieldType: "dimension",
    dataType: "string",
    entity: "inspection",
    allowedChartTypes: DIMENSION_CHARTS,
    isFilterable: true,
    isGroupable: true,
    sourceDatasets: ["inspections"],
  },
  {
    id: "facility_type",
    label: "Facility Type",
    description: "Type of facility: medical, laboratory, food business, etc.",
    fieldName: "facility_type",
    fieldType: "dimension",
    dataType: "string",
    entity: "facility",
    allowedChartTypes: DIMENSION_CHARTS,
    isFilterable: true,
    isGroupable: true,
    sourceDatasets: ["facilities"],
  },
  {
    id: "policy_version",
    label: "Policy Version",
    description: "Version of food safety policy or standard.",
    fieldName: "policy_version",
    fieldType: "dimension",
    dataType: "string",
    entity: "policy",
    allowedChartTypes: DIMENSION_CHARTS,
    isFilterable: true,
    isGroupable: true,
    sourceDatasets: ["policies"],
  },
  {
    id: "policy_adoption",
    label: "Policy Adoption Status",
    description: "Whether a state has adopted the current policy version.",
    fieldName: "adoption_status",
    fieldType: "dimension",
    dataType: "string",
    entity: "policy",
    allowedChartTypes: DIMENSION_CHARTS,
    isFilterable: true,
    isGroupable: true,
    sourceDatasets: ["policies"],
  },
  {
    id: "payment_status",
    label: "Payment Status",
    description: "Payment status: paid, pending, failed, refunded.",
    fieldName: "payment_status",
    fieldType: "dimension",
    dataType: "string",
    entity: "payment",
    allowedChartTypes: DIMENSION_CHARTS,
    isFilterable: true,
    isGroupable: true,
    sourceDatasets: ["payment_transactions"],
  },
  {
    id: "organisation_type",
    label: "Organisation Type",
    description: "Type of organisation: public, private, NGO, donor-supported.",
    fieldName: "organisation_type",
    fieldType: "dimension",
    dataType: "string",
    entity: "organization",
    allowedChartTypes: DIMENSION_CHARTS,
    isFilterable: true,
    isGroupable: true,
    sourceDatasets: ["employers", "facilities"],
  },
];

const MODULE_ENTITY_MAP: Record<string, AnalyticsEntity> = {
  food_handlers: "food_handler",
  certificates: "certificate",
  employers: "employer",
  facilities: "facility",
  medical_facilities: "facility",
  inspections: "inspection",
  payments: "payment",
  payment_transactions: "payment",
  medical_tests: "medical_test",
  lab_tests: "laboratory",
  illnesses: "medical_test",
  vaccinations: "medical_test",
  policy: "policy",
  standards: "policy",
  indicator_results: "indicator",
  indicator_performance: "indicator",
  indicator_targets: "indicator",
  indicators: "indicator",
  reports: "report",
};

const DIMENSION_KEYWORDS = [
  "state",
  "lga",
  "ward",
  "employer",
  "facility",
  "laboratory",
  "lab",
  "category",
  "type",
  "status",
  "role",
  "gender",
  "owner",
  "agency",
  "ministry",
  "location",
  "version",
  "policy",
  "country",
  "region",
  "zone",
  "national",
  "local",
  "period",
  "month",
  "quarter",
  "week",
  "day",
  "year",
  "date",
  "renewal",
  "revocation",
  "verification",
  "compliance",
  "violation",
  "corrective",
  "enforcement",
  "fitness",
  "clearance",
  "referral",
  "registration",
  "certification",
  "accreditation",
  "investigation",
  "ownership",
  "risk",
  "age",
  "band",
  "employment",
  "job",
  "work",
  "disease",
  "retest",
  "result",
  "issue",
  "expiry",
  "inspection",
  "test",
  "department",
  "unit",
  "eligibility",
  "adoption",
  "scope",
  "level",
  "priority",
  "severity",
  "source",
  "target",
  "mode",
  "channel",
];

const ID_KEYWORDS = ["_id", "identifier", "number", "code"];
const GEOGRAPHIC_KEYWORDS = ["state", "lga", "ward", "location", "country"];
const TIME_KEYWORDS = ["date", "month", "quarter", "week", "day", "year", "period"];

function titleize(value: string) {
  return value.replaceAll("__", " / ").replaceAll("_", " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

function normalizeFieldType(datasetType: string | undefined) {
  const value = String(datasetType || "").toLowerCase();
  if (value.includes("currency") || value.includes("amount")) return "currency" as const;
  if (value.includes("percentage") || value.includes("rate") || value.includes("ratio")) return "percentage" as const;
  if (value.includes("date") && value.includes("time")) return "date" as const;
  if (value.includes("date")) return "date" as const;
  if (value.includes("bool")) return "boolean" as const;
  if (value.includes("number") || value.includes("integer") || value.includes("decimal") || value.includes("float")) return "number" as const;
  return "string" as const;
}

function looksLikeIdentifier(fieldName: string) {
  const lower = fieldName.toLowerCase();
  return ID_KEYWORDS.some((token) => lower.endsWith(token) || lower.includes(token));
}

export function inferFieldType(fieldName: string, datasetType?: string): AnalyticsFieldType {
  const lower = fieldName.toLowerCase();
  if (looksLikeIdentifier(lower)) return "dimension";
  const dataType = normalizeFieldType(datasetType);
  if (dataType === "number") {
    const isDimensionByName = DIMENSION_KEYWORDS.some((token) => lower.includes(token));
    return isDimensionByName ? "dimension" : "measure";
  }
  return "dimension";
}

export function buildDatasetAnalyticsFields(dataset: AnalyticsDataset, role?: UserRole): AnalyticsField[] {
  const staticFields = STATIC_FIELDS.filter((field) =>
    dataset.available_fields.includes(field.fieldName) || (field.sourceDatasets || []).includes(dataset.code),
  );

  const dynamicFields = dataset.available_fields.map((fieldName) => {
    const metadata = dataset.field_type_metadata?.[fieldName];
    const normalizedDataType = normalizeFieldType(metadata?.type || dataset.field_types?.[fieldName]);
    const inferredKind = inferFieldType(fieldName, metadata?.type || dataset.field_types?.[fieldName]);
    const fieldType: AnalyticsFieldType = inferredKind;
    const lower = fieldName.toLowerCase();
    const isTimeDimension = fieldType === "dimension" && TIME_KEYWORDS.some((token) => lower.includes(token));
    const isGeographicDimension = fieldType === "dimension" && GEOGRAPHIC_KEYWORDS.some((token) => lower.includes(token));
    const label = dataset.field_labels?.[fieldName] || titleize(fieldName);
    const description =
      fieldType === "measure"
        ? `${label} is available as an aggregated analytic measure.`
        : `${label} is available for grouping, filtering, drilldown, and segmentation.`;
    const allowedAggregations: AnalyticsAggregation[] | undefined =
      fieldType === "measure"
        ? normalizedDataType === "currency"
          ? ["sum", "avg", "min", "max", "count"]
          : normalizedDataType === "percentage"
            ? ["avg", "min", "max", "percentage", "rate", "ratio", "variance"]
            : ["sum", "count", "count_distinct", "avg", "min", "max", "variance"]
        : undefined;
    const defaultAggregation =
      fieldType === "measure"
        ? normalizedDataType === "currency"
          ? "sum"
          : normalizedDataType === "percentage"
            ? "avg"
            : "sum"
        : undefined;

    const item: AnalyticsField = {
      id: `${dataset.code}:${fieldName}`,
      label,
      description,
      fieldName,
      fieldType,
      dataType: normalizedDataType,
      entity: MODULE_ENTITY_MAP[dataset.code] || MODULE_ENTITY_MAP[dataset.module_source] || "organization",
      allowedAggregations,
      defaultAggregation,
      allowedChartTypes:
        fieldType === "measure"
          ? MEASURE_CHARTS
          : isTimeDimension
            ? ["line", "bar", "grouped_bar", "table"]
            : isGeographicDimension
              ? ["bar", "grouped_bar", "table", "map"]
              : DIMENSION_CHARTS,
      isFilterable: fieldType === "dimension",
      isGroupable: fieldType === "dimension",
      isTimeDimension,
      isGeographicDimension,
      requiredRoleAccess: role ? [role] : undefined,
      sourceDatasets: [dataset.code],
    };

    if (fieldType === "dimension" && looksLikeIdentifier(fieldName)) {
      item.description = `${label} identifies records and is treated as a dimension, not an aggregatable measure.`;
    }
    return item;
  });

  const merged = [...staticFields, ...dynamicFields].reduce<AnalyticsField[]>((acc, field) => {
    if (!acc.find((item) => item.fieldName === field.fieldName)) {
      acc.push(field);
    }
    return acc;
  }, []);

  return merged;
}

export function getDimensions(fields: AnalyticsField[]) {
  return fields.filter((field) => field.fieldType === "dimension");
}

export function getMeasures(fields: AnalyticsField[]) {
  return fields.filter((field) => field.fieldType === "measure");
}

export function isDimension(field: AnalyticsField) {
  return field.fieldType === "dimension";
}

export function isMeasure(field: AnalyticsField) {
  return field.fieldType === "measure";
}

export function isTimeDimension(field: AnalyticsField) {
  return field.fieldType === "dimension" && Boolean(field.isTimeDimension);
}

export function isGeographicDimension(field: AnalyticsField) {
  return field.fieldType === "dimension" && Boolean(field.isGeographicDimension);
}

export function canAggregate(field: AnalyticsField, aggregation: AnalyticsAggregation) {
  return isMeasure(field) && Boolean(field.allowedAggregations?.includes(aggregation));
}
