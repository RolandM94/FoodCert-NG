# FOODCERT Dashboards: Tableau-Style Dimensions & Measures Implementation Prompt

## Codex Instruction

You are working on the **FOODCERT Dashboard module**.

The goal is to implement Tableau-style analytics logic for dashboard building by clearly separating fields into **Dimensions** and **Measures**. This should apply across FOODCERT dashboards for Federal, State, Employer, Medical Facility, Laboratory, Inspector, and Admin users.

The implementation should support configurable dashboards, AI-assisted insights, dynamic charts, and role-based access to analytics.

---

# 1. Core Concept

## 1.1 Dimensions

Dimensions are descriptive or categorical fields used to answer:

- By what?
- For which category?
- For which location?
- For which organisation?
- For which time period?
- For which status?
- For which policy version?

Dimensions should be used for:

- Filters
- Grouping
- Drilldowns
- Chart categories
- Table columns
- Segmentation
- Dashboard slicers

## 1.2 Measures

Measures are numerical fields used to answer:

- How many?
- How much?
- What percentage?
- What total?
- What average?
- What rate?
- What variance?
- What trend?

Measures should support aggregation using:

- SUM
- COUNT
- COUNT DISTINCT
- AVG
- MIN
- MAX
- PERCENTAGE
- RATE
- RATIO
- VARIANCE

---

# 2. Implementation Chunk 1: Analytics Field Metadata Registry

## Objective

Create a metadata-driven analytics field registry that defines all available dashboard fields and classifies them as either **dimensions** or **measures**.

## Suggested Type Definition

```ts
type AnalyticsField = {
  id: string;
  label: string;
  description?: string;
  fieldName: string;
  fieldType: "dimension" | "measure";
  dataType: "string" | "number" | "date" | "boolean" | "percentage" | "currency";
  entity:
    | "food_handler"
    | "certificate"
    | "medical_test"
    | "laboratory"
    | "inspection"
    | "employer"
    | "facility"
    | "policy"
    | "payment";
  allowedAggregations?: Array<
    | "sum"
    | "count"
    | "count_distinct"
    | "avg"
    | "min"
    | "max"
    | "percentage"
    | "rate"
    | "ratio"
    | "variance"
  >;
  defaultAggregation?:
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
  allowedChartTypes: Array<
    | "kpi"
    | "bar"
    | "grouped_bar"
    | "line"
    | "pie"
    | "donut"
    | "table"
    | "map"
  >;
  isFilterable: boolean;
  isGroupable: boolean;
  isTimeDimension?: boolean;
  isGeographicDimension?: boolean;
  requiredRoleAccess?: Array<
    | "federal_admin"
    | "state_admin"
    | "employer_admin"
    | "medical_facility_admin"
    | "laboratory_admin"
    | "inspector"
    | "system_admin"
  >;
};
```

## Deliverables

- Create a central analytics field registry file, for example:
  - `lib/analytics/fields.ts`
  - `src/analytics/fields.ts`
  - or the equivalent location used in the project.
- Define every FOODCERT dashboard field in this registry.
- Ensure every field has:
  - ID
  - Label
  - Description
  - Entity
  - Field type
  - Data type
  - Chart compatibility
  - Filter and grouping rules
  - Aggregation rules, where applicable

## Acceptance Criteria

- All dashboard fields are metadata-driven.
- The dashboard builder reads from the field registry instead of hardcoded field lists.
- Dimensions and measures are clearly separated in the registry.

---

# 3. Implementation Chunk 2: Define FOODCERT Dimensions

## Objective

Implement all major FOODCERT dimensions for filtering, grouping, drilldown, segmentation, and chart category axes.

## Organisation Dimensions

- Federal Ministry / Regulator
- State
- LGA
- Ward
- Employer
- Food Business Operator
- Medical Facility
- Laboratory
- Inspection Agency
- Department / Unit
- Facility Type
- Organisation Type
- Ownership Type: Public, Private, NGO, Donor-supported

## Food Handler Dimensions

- Food Handler ID
- Gender
- Age Band
- Employment Type
- Food Handler Category
- Risk Category
- Job Role
- Employer
- Work Location
- Registration Status
- Certificate Status
- Renewal Status

## Medical Test Dimensions

- Medical Test Type
- Laboratory Investigation Type
- Medical Facility
- Laboratory
- Test Status
- Result Status
- Fitness Status
- Disease Category
- Clearance Status
- Referral Status
- Retest Required: Yes / No

## Certificate Dimensions

- Certificate ID
- Certificate Type
- Certificate Status
- Issue Date
- Expiry Date
- Renewal Period
- Revocation Status
- Verification Status

## Policy and Standards Dimensions

- Policy Version
- Standard Type
- Food Handler Eligibility Standard
- Medical Test Standard
- Laboratory Investigation Standard
- Certificate Validity Standard
- State Adoption Status
- Policy Effective Date
- Policy Review Cycle

## Inspection and Compliance Dimensions

- Inspection Type
- Inspection Status
- Compliance Status
- Compliance Category
- Violation Type
- Risk Level
- Corrective Action Status
- Enforcement Action Type
- Inspection Officer
- Inspection Date

## Geography and Time Dimensions

- Country
- State
- LGA
- Ward
- Facility Location
- Year
- Quarter
- Month
- Week
- Day
- Reporting Period

## Important Classification Rule

Numeric IDs such as:

- `food_handler_id`
- `certificate_id`
- `facility_id`
- `inspection_id`
- `medical_test_id`

must be treated as **Dimensions**, not Measures, because they identify records and should not be summed or averaged.

## Deliverables

- Add all listed dimensions to the analytics field registry.
- Mark dimensions as:
  - `fieldType: "dimension"`
  - `isFilterable: true` where applicable
  - `isGroupable: true` where applicable
- Mark date-related dimensions with:
  - `isTimeDimension: true`
- Mark geography-related dimensions with:
  - `isGeographicDimension: true`

## Acceptance Criteria

- Dashboard users can select dimensions for filters, groupings, breakdowns, drilldowns, and chart categories.
- Numeric IDs are not treated as aggregatable measures.

---

# 4. Implementation Chunk 3: Define FOODCERT Measures

## Objective

Implement all major FOODCERT measures for KPIs, chart values, totals, percentages, rates, averages, trends, and comparisons.

## Food Handler Measures

- Total Food Handlers
- Registered Food Handlers
- Approved Food Handlers
- Rejected Food Handlers
- Active Food Handlers
- Suspended Food Handlers
- Food Handlers Due for Renewal
- Food Handlers with Valid Certificates
- Food Handlers with Expired Certificates

## Medical Test Measures

- Total Medical Tests Conducted
- Pending Medical Tests
- Completed Medical Tests
- Failed Medical Tests
- Passed Medical Tests
- Retests Required
- Average Medical Test Completion Time
- Test Positivity Rate
- Medical Clearance Rate
- Disease Detection Count

## Certificate Measures

- Total Certificates Issued
- Valid Certificates
- Expired Certificates
- Revoked Certificates
- Certificates Due for Renewal
- Certificate Renewal Rate
- Certificate Verification Count
- Failed Verification Count

## Compliance Measures

- Total Inspections Conducted
- Passed Inspections
- Failed Inspections
- Open Violations
- Closed Violations
- Compliance Rate
- Non-Compliance Rate
- Corrective Action Completion Rate
- Average Time to Close Violation
- Enforcement Action Count

## Facility and Employer Measures

- Total Employers
- Total Food Businesses
- Total Medical Facilities
- Total Laboratories
- Active Facilities
- Suspended Facilities
- Accredited Laboratories
- Non-Accredited Laboratories
- Facility Compliance Rate

## Policy Adoption Measures

- Number of States that Adopted Policy
- Number of States Pending Adoption
- Policy Adoption Rate
- Number of Facilities Operating Under Current Policy
- Number of Certificates Issued Under Policy Version
- Number of Medical Tests Conducted Under Policy Version

## Financial / Payment Measures, if Applicable

- Total Fees Collected
- Certificate Fee Revenue
- Medical Test Fee Revenue
- Renewal Fee Revenue
- Outstanding Payments
- Failed Payments
- Average Revenue per Facility

## Deliverables

- Add all listed measures to the analytics field registry.
- Mark measures as:
  - `fieldType: "measure"`
  - `dataType: "number"`, `"percentage"`, or `"currency"` as applicable
  - `isFilterable: false` by default, unless the project supports numeric filters
  - `isGroupable: false`
- Add valid aggregation methods for each measure.
- Add a default aggregation for each measure.

## Acceptance Criteria

- Dashboard users can select measures for KPIs, chart values, totals, percentages, rates, averages, and trends.
- Measures cannot be used as normal grouping dimensions unless explicitly supported.

---

# 5. Implementation Chunk 4: Field Classification Rules

## Objective

Create rules that classify fields consistently as dimensions or measures.

## Dimension Rules

A field should be classified as a Dimension if it:

- Describes a record
- Categorizes data
- Groups data
- Filters data
- Identifies an entity
- Represents a status, type, category, location, organisation, or time period

Examples:

- State
- LGA
- Employer
- Medical Facility
- Laboratory
- Certificate Status
- Food Handler Category
- Policy Version
- Inspection Status
- Medical Test Type

## Measure Rules

A field should be classified as a Measure if it:

- Is numeric
- Can be aggregated
- Represents a count, total, rate, percentage, average, duration, amount, or variance
- Is used as a KPI value or chart metric

Examples:

- Total Food Handlers
- Certificate Count
- Compliance Rate
- Test Positivity Rate
- Average Test Completion Time
- Total Fees Collected
- Number of Failed Inspections

## Deliverables

- Add classification helper functions, for example:
  - `isDimension(field)`
  - `isMeasure(field)`
  - `isTimeDimension(field)`
  - `isGeographicDimension(field)`
  - `canAggregate(field, aggregation)`
- Prevent incorrect usage such as:
  - Summing dimensions
  - Averaging IDs
  - Using non-time fields for line chart time axes
  - Using non-geographic fields for map charts

## Acceptance Criteria

- The classification logic is reusable across dashboard builder, filters, chart rendering, query generation, and AI insight generation.

---

# 6. Implementation Chunk 5: Dashboard Builder UI Logic

## Objective

Update the dashboard builder so users can clearly select dimensions and measures in a Tableau-like manner.

## UI Requirements

In the dashboard builder UI, separate fields into two panels:

1. **Dimensions**
2. **Measures**

For each field, show:

- Display name
- Description
- Entity source
- Data type
- Recommended chart types
- Whether it can be used as a filter
- Whether it can be used for grouping
- Default aggregation, for measures

## Dimension Usage

Dimensions should be selectable for:

- Rows
- Columns
- Filters
- Group by
- Breakdown by
- Drilldown hierarchy
- Chart category axis
- Table grouping

## Measure Usage

Measures should be selectable for:

- KPI cards
- Chart values
- Aggregated totals
- Y-axis values
- Table numeric columns
- Trend analysis
- Scorecards

## Example Dashboard Questions

### Example 1

Question: How many food handlers have valid certificates by State?

- Dimension: State
- Measure: Food Handlers with Valid Certificates
- Filter: Certificate Status = Valid

### Example 2

Question: What is the medical test positivity rate by LGA?

- Dimension: LGA
- Measure: Test Positivity Rate
- Filter: Test Status = Completed

### Example 3

Question: What is the certificate renewal rate by employer?

- Dimension: Employer
- Measure: Certificate Renewal Rate

### Example 4

Question: What is the compliance rate by medical facility?

- Dimension: Medical Facility
- Measure: Compliance Rate

## Deliverables

- Update the dashboard builder UI to display Dimensions and Measures separately.
- Add drag-and-drop or selection controls if already supported by the application.
- Add field tooltips and descriptions.
- Disable fields that are incompatible with the selected chart type.
- Explain why incompatible fields are disabled.

## Acceptance Criteria

- Users can clearly understand what fields are dimensions and what fields are measures.
- Users can build charts by selecting compatible dimensions and measures.
- The dashboard builder behaves similarly to Tableau’s field model, adapted for FOODCERT.

---

# 7. Implementation Chunk 6: Chart Compatibility Rules

## Objective

Implement rules that determine which chart types are valid based on selected dimensions and measures.

## KPI Card

Requires:

- 1 Measure
- Optional filters

Examples:

- Total Registered Food Handlers
- Valid Certificates
- Compliance Rate

## Bar Chart

Requires:

- 1 Dimension
- 1 or more Measures

Examples:

- Certificates Issued by State
- Food Handlers by Employer
- Failed Inspections by Facility

## Grouped Bar Chart

Requires:

- 1 primary Dimension
- 1 secondary Dimension
- 1 Measure

Examples:

- Certificate Status by State
- Medical Test Result by LGA
- Compliance Status by Facility Type

## Line Chart

Requires:

- 1 Time Dimension
- 1 or more Measures

Examples:

- Monthly Certificate Issuance Trend
- Weekly Medical Tests Conducted
- Quarterly Compliance Rate

## Pie / Donut Chart

Requires:

- 1 Dimension
- 1 Measure

Best for low-cardinality categories only.

Examples:

- Certificate Status Distribution
- Food Handler Risk Category Distribution
- Inspection Status Distribution

## Table

Supports:

- Multiple Dimensions
- Multiple Measures

Examples:

- Employer performance table
- State compliance table
- Medical facility testing table

## Map

Requires:

- Geographic Dimension
- 1 Measure

Examples:

- Food Handlers by State
- Compliance Rate by LGA
- Certificates Issued by State

## Deliverables

Create chart validation helpers, for example:

```ts
type ChartType =
  | "kpi"
  | "bar"
  | "grouped_bar"
  | "line"
  | "pie"
  | "donut"
  | "table"
  | "map";

function validateChartConfig(config: {
  chartType: ChartType;
  dimensions: AnalyticsField[];
  measures: AnalyticsField[];
  filters?: unknown[];
}): {
  valid: boolean;
  errors: string[];
  warnings: string[];
};
```

## Validation Messages

Use plain-language validation messages such as:

- “Line charts require a time-based dimension such as Month, Quarter, Year, Issue Date, Test Date, or Inspection Date.”
- “Map charts require a geographic dimension such as State, LGA, Ward, or Facility Location.”
- “Pie charts are best used with low-cardinality dimensions such as Certificate Status, Test Result, Risk Category, or Compliance Status.”
- “KPI cards should use one primary measure.”

## Acceptance Criteria

- Invalid chart combinations are blocked before rendering.
- Users receive understandable validation feedback.
- Chart type suggestions are based on selected fields.

---

# 8. Implementation Chunk 7: Dashboard Filters

## Objective

Implement dashboard filters using dimensions.

## Supported Filters

Dashboards should allow filtering by dimensions such as:

- State
- LGA
- Employer
- Medical Facility
- Laboratory
- Food Handler Category
- Certificate Status
- Medical Test Status
- Inspection Status
- Compliance Status
- Policy Version
- Date Range
- Reporting Period

## Filter Behaviour

- Filters should be built from dimensions.
- Filters should respect role-based access.
- Filters should not expose values outside the user’s data scope.
- Date filters should support common reporting periods:
  - Today
  - This week
  - This month
  - This quarter
  - This year
  - Custom date range

## Deliverables

- Implement dimension-based dashboard filters.
- Add dependent filters where useful, for example:
  - Selecting State limits available LGAs.
  - Selecting Medical Facility limits available tests.
  - Selecting Employer limits available food handlers.
- Ensure filters are applied before data aggregation.

## Acceptance Criteria

- Users can filter dashboards by allowed dimensions.
- Filter values are scoped to the user’s role and permissions.
- Filters cannot be used to infer restricted data.

---

# 9. Implementation Chunk 8: Role-Based Dashboard Scope

## Objective

Implement role-based data scoping for all dimensions, measures, filters, and aggregations.

## Federal Dashboard

Federal users can view national-level analytics:

- All states
- All LGAs
- All employers
- All medical facilities
- All laboratories
- All food handlers
- National policy adoption
- National compliance performance

## State Dashboard

State users can view state-level analytics:

- LGAs within the state
- Employers within the state
- Facilities within the state
- Food handlers within the state
- State policy adoption
- State compliance performance

## Employer Dashboard

Employer users can view employer-level analytics:

- Own food handlers
- Own certificate status
- Own renewal compliance
- Own inspection performance
- Own violations and corrective actions

## Medical Facility Dashboard

Medical facility users can view facility-level analytics:

- Medical tests conducted by the facility
- Pending tests
- Completed tests
- Fitness decisions
- Clearance rates
- Certificate recommendations

## Laboratory Dashboard

Laboratory users can view laboratory-level analytics:

- Laboratory investigations
- Pending investigations
- Completed investigations
- Positive findings
- Turnaround time
- Result submission performance

## Inspector Dashboard

Inspector users can view inspection-level analytics:

- Assigned inspections
- Completed inspections
- Failed inspections
- Violations identified
- Corrective actions
- Enforcement recommendations

## Deliverables

- Implement a role scope resolver, for example:

```ts
type DashboardScope = {
  role: string;
  countryId?: string;
  stateId?: string;
  lgaIds?: string[];
  employerId?: string;
  facilityId?: string;
  laboratoryId?: string;
  inspectorId?: string;
};

function resolveDashboardScope(user: User): DashboardScope;
```

- Apply resolved scope before aggregation.
- Apply resolved scope before returning filter options.
- Apply resolved scope before AI insight generation.

## Acceptance Criteria

- Federal users see national analytics.
- State users see only their state analytics.
- Employer users see only their organisation’s analytics.
- Medical facilities see only their facility analytics.
- Laboratories see only their laboratory analytics.
- Inspectors see only assigned inspection analytics.
- No role can query or infer data outside its permission scope.

---

# 10. Implementation Chunk 9: Aggregation and Query Generation

## Objective

Implement aggregation logic for measures and grouped queries based on selected dimensions.

## Aggregation Requirements

Measures must support the following aggregation methods where applicable:

- SUM
- COUNT
- COUNT DISTINCT
- AVG
- MIN
- MAX
- PERCENTAGE
- RATE
- RATIO
- VARIANCE

## Query Logic

The query builder should:

1. Resolve user scope.
2. Apply role-based scope.
3. Apply selected filters.
4. Group by selected dimensions.
5. Aggregate selected measures.
6. Return chart-ready data.

## Deliverables

- Create or update analytics query builder.
- Ensure dimensions are used in `GROUP BY` clauses or ORM equivalents.
- Ensure measures use valid aggregations.
- Ensure calculated measures such as rates and percentages are computed correctly.

## Examples

### Compliance Rate

```text
Compliance Rate = Passed Inspections / Total Inspections Conducted * 100
```

### Non-Compliance Rate

```text
Non-Compliance Rate = Failed Inspections / Total Inspections Conducted * 100
```

### Test Positivity Rate

```text
Test Positivity Rate = Positive Test Results / Completed Medical Tests * 100
```

### Certificate Renewal Rate

```text
Certificate Renewal Rate = Renewed Certificates / Certificates Due for Renewal * 100
```

### Corrective Action Completion Rate

```text
Corrective Action Completion Rate = Closed Corrective Actions / Total Corrective Actions * 100
```

## Acceptance Criteria

- Measures aggregate correctly.
- Calculated rates and percentages are accurate.
- Dimensions group results correctly.
- Role-based scope is applied before aggregation.

---

# 11. Implementation Chunk 10: AI Insight Layer

## Objective

Add support for AI-assisted dashboard interpretation based on selected dimensions, measures, filters, chart type, and user role.

## AI Insight Inputs

The AI insight layer should receive:

- Selected dimensions
- Selected measures
- Applied filters
- Time period
- User role
- Data scope
- Current chart type
- Comparison period, where available
- Aggregated chart data

## AI Insight Outputs

The AI insight layer should return:

- Summary
- Key findings
- Possible risk areas
- Recommended follow-up actions
- Data caveats

## Example AI Insights

- “Compliance rate dropped in Kano because failed inspections increased among high-risk food businesses.”
- “Lagos has the highest number of certificates issued, but also the highest renewal backlog.”
- “Medical test positivity is increasing in selected LGAs and should be reviewed by state regulators.”
- “This employer has a high number of expired certificates and should be flagged for follow-up.”

## Deliverables

- Create an AI insight input schema.
- Create an AI insight response schema.
- Ensure AI insights only use data available within the user’s permission scope.
- Add AI insight summary to dashboard widgets or dashboard detail pages.

## Acceptance Criteria

- AI insights explain dashboard results using selected dimensions and measures.
- AI insights respect role-based access.
- AI outputs include summary, findings, risks, recommendations, and caveats.

---

# 12. Implementation Chunk 11: UI/UX Behaviour and Validation

## Objective

Ensure the dashboard builder is understandable and prevents invalid configurations.

## UI Behaviour

When a user selects a chart type:

- Show only compatible dimensions and measures.
- Disable incompatible fields.
- Explain why a field is disabled.
- Suggest the best chart type based on selected dimensions and measures.
- Show validation errors in plain language.

## Required User Feedback

Examples of validation messages:

- “Line charts require a time-based dimension such as Month, Quarter, Year, Issue Date, Test Date, or Inspection Date.”
- “Map charts require a geographic dimension such as State, LGA, Ward, or Facility Location.”
- “Pie charts are best used with low-cardinality dimensions such as Certificate Status, Test Result, Risk Category, or Compliance Status.”
- “This field is an ID and cannot be summed or averaged.”
- “This filter is not available for your current role.”

## Deliverables

- Add validation messages.
- Add chart suggestions.
- Add disabled-state explanations.
- Add tooltips for dimensions and measures.
- Add empty states when no compatible fields are available.

## Acceptance Criteria

- Users understand why a chart configuration is valid or invalid.
- Incompatible fields are not silently hidden without explanation.
- Dashboard configuration errors are prevented before chart rendering.

---

# 13. Implementation Chunk 12: Testing Requirements

## Objective

Add tests to validate the analytics field model, chart compatibility, aggregation, role scoping, and filters.

## Required Tests

Add tests for:

1. Dimension classification
2. Measure classification
3. Numeric ID classification as dimensions
4. Aggregation validation
5. Chart compatibility
6. KPI validation
7. Bar chart validation
8. Grouped bar chart validation
9. Line chart validation with time dimensions
10. Map chart validation with geographic dimensions
11. Pie and donut chart validation
12. Role-based data scoping
13. Filter permission enforcement
14. Scope application before aggregation
15. AI insight input scoping

## Example Test Cases

- `food_handler_id` should be classified as a dimension.
- `total_food_handlers` should be classified as a measure.
- A line chart without a time dimension should fail validation.
- A map chart without a geographic dimension should fail validation.
- A federal user should access national data.
- A state user should only access data within their state.
- An employer user should only access food handlers linked to their employer account.
- A medical facility user should only access medical tests linked to their facility.
- A laboratory user should only access investigations linked to their laboratory.
- A restricted filter value should not be returned to an unauthorized user.

## Acceptance Criteria

- All tests pass.
- Validation logic prevents invalid dashboard configurations.
- Role scoping is enforced consistently across filters, charts, tables, KPIs, and AI insights.

---

# 14. Final Acceptance Criteria

The implementation is complete when:

- Users can clearly distinguish Dimensions from Measures in the dashboard builder.
- Users can select dimensions for grouping, filtering, and drilldowns.
- Users can select measures for KPIs, charts, totals, percentages, rates, and trends.
- Invalid chart combinations are prevented.
- Role-based access is enforced before analytics aggregation.
- Federal users see national analytics.
- State users see only their state analytics.
- Employers see only their organisation’s analytics.
- Medical facilities see only their facility analytics.
- Laboratories see only their laboratory analytics.
- Inspectors see only assigned inspection analytics.
- AI insights can interpret dashboards using selected dimensions, measures, filters, chart type, and scoped data.
- The dashboard builder behaves similarly to Tableau’s model of Dimensions and Measures, adapted specifically for the FOODCERT platform.

---

# 15. Implementation Order

Use this sequence:

1. Create analytics field metadata registry.
2. Add FOODCERT dimensions.
3. Add FOODCERT measures.
4. Add field classification helpers.
5. Add chart compatibility validation.
6. Add role-based dashboard scope resolver.
7. Add filter generation and filter permission logic.
8. Add analytics query builder and aggregation logic.
9. Update dashboard builder UI to separate Dimensions and Measures.
10. Add AI insight input/output schemas.
11. Add AI insight rendering to dashboard widgets.
12. Add tests.
13. Confirm all acceptance criteria.

