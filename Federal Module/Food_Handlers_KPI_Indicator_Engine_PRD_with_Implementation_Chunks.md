# Food Handlers Application – KPI Indicator Engine PRD

## 1. Product Overview

### 1.1 Purpose

The **KPI Indicator Engine** is a configurable performance tracking engine for the **National Food Handlers Medical Test Application**. It enables authorized federal, state, LGA, facility, and administrative users to define, calculate, track, and report KPIs related to food handler registration, medical testing, certification, compliance, renewals, coverage, and operational performance.

This PRD replaces the generic indicator PRD structure and removes elements that are not relevant to the Food Handlers application, including project/logframe linking, activity linking, and document/report module dependencies. The goal is to keep the feature focused on the **indicator engine itself**: creating KPIs, linking them to operational data sources, calculating values, tracking progress over time, and displaying performance insights.

### 1.2 Product Context

The Food Handlers platform will manage core operational data such as:

- Food handler registration records
- Medical test records
- Test result outcomes
- Certificate issuance and expiry records
- Facility / employer records
- State, LGA, ward, and geographic hierarchy
- Training or orientation records, where applicable
- Inspection and compliance records, where applicable
- Payment or fee records, where applicable
- User, role, and approval workflow records

The KPI Indicator Engine should sit above these operational modules and convert their data into measurable performance metrics.

### 1.3 Scope

#### Included

- KPI creation and configuration
- Quantitative and qualitative indicator support
- Manual and automated KPI data capture
- Linking KPIs to Food Handlers system data sources
- KPI calculation methods: count, unique count, sum, average, percentage, ratio, and custom formula
- Baselines, targets, reporting periods, and thresholds
- Progress and cumulative tracking rules
- Disaggregation by administrative, demographic, facility, test, and certification dimensions
- KPI dashboards, trend views, and performance cards
- KPI history, audit trail, and versioning
- Role-based access control for KPI configuration and viewing
- Export of KPI data to Excel/CSV/PDF
- Implementation chunks for Codex execution

#### Excluded

- Linking indicators to projects, project activities, logframes, plans, goals, outcomes, outputs, or project workplans
- Linking KPI values to document/report approval workflows
- Managing evidence documents as the official source of KPI values
- Machine learning, NLP, predictive analytics, or advanced BI tooling
- Full reporting module replacement
- Full form-builder replacement
- Financial accounting logic, unless a payment-related KPI is intentionally configured from available payment records

## 2. Goals and Success Metrics

### 2.1 Product Goals

1. Allow government administrators to configure KPIs without engineering support.
2. Enable real-time or near-real-time monitoring of Food Handler compliance performance.
3. Support federal oversight across states, LGAs, facilities, test centers, and certificate issuance pipelines.
4. Ensure KPI calculations are consistent, auditable, and protected against duplicate counting.
5. Allow KPI values to be disaggregated for better policy and operational decision-making.
6. Provide dashboards that show current performance, trends, targets, and areas requiring attention.

### 2.2 Success Metrics

- Authorized users can create a KPI in under 5 minutes.
- KPI dashboard values update within acceptable load time for normal data volume.
- KPI calculations return accurate results based on the selected calculation method.
- KPI audit trail captures who changed configuration or values and when.
- Users can filter and disaggregate KPIs by state, LGA, facility, gender, age group, test status, certificate status, and reporting period.
- Federal users can compare KPI performance across states.

## 3. User Roles and Access

### 3.1 Role Categories

The exact role names may follow the wider Food Handlers RBAC model, but the KPI Engine should support these permission groups:

| Permission Group | Description |
|---|---|
| Federal System Administrator | Can configure national KPI templates, calculation rules, thresholds, and visibility. |
| Federal Oversight User | Can view national KPI dashboards, compare state performance, export reports, and review trends. |
| State Administrator | Can view state-level KPIs, configure state-specific KPI targets if permitted, and monitor LGAs/facilities. |
| LGA / Local Authority User | Can view KPI performance for their assigned jurisdiction. |
| Facility / Employer User | Can view facility-specific KPIs, where permitted. |
| Test Center / Laboratory User | Can view operational KPIs related to submitted tests, processed tests, pending tests, and turnaround time. |
| Data Entry / Operations User | Can manually submit KPI values only for KPIs configured to allow manual entry. |
| Auditor / Reviewer | Can view KPI configuration, history, and audit logs but cannot edit. |

### 3.2 Permission Matrix

| Action | Federal Admin | Federal Viewer | State Admin | LGA User | Facility User | Test Center User | Data Entry | Auditor |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Create national KPI | Yes | No | No | No | No | No | No | No |
| Edit national KPI | Yes | No | No | No | No | No | No | No |
| Create state KPI | Optional | No | Optional | No | No | No | No | No |
| Configure calculation rules | Yes | No | Optional | No | No | No | No | No |
| Configure targets | Yes | No | Optional | No | No | No | No | No |
| View assigned KPI dashboard | Yes | Yes | Yes | Yes | Limited | Limited | Limited | Yes |
| Export KPI data | Yes | Yes | Yes | Optional | No | Optional | No | Yes |
| Manual KPI entry | Optional | No | Optional | Optional | Optional | Optional | Yes | No |
| View audit logs | Yes | Optional | Optional | No | No | No | No | Yes |
| Delete KPI | Yes | No | No | No | No | No | No | No |

## 4. Core Concepts

### 4.1 KPI / Indicator

A KPI is a measurable performance metric used to track the effectiveness, coverage, compliance, or operational status of the Food Handlers programme.

Examples:

- Number of registered food handlers
- Percentage of registered food handlers medically tested
- Number of certified food handlers
- Percentage of certificates expiring within 30 days
- Average test processing turnaround time
- Number of facilities with at least one certified handler
- Percentage of failed medical tests followed up
- Number of duplicate registrations detected

### 4.2 KPI Type

| Type | Description | Example |
|---|---|---|
| Quantitative | Numeric value calculated from records or entered manually. | Number of certified food handlers. |
| Qualitative | Descriptive or rating-based input. | State compliance narrative or inspection quality rating. |

The Food Handlers platform should primarily use quantitative KPIs. Qualitative KPIs should be supported only where administrators need narrative or rating-based assessment.

### 4.3 Data Source

A data source is an internal table, module, or dataset from the Food Handlers application that can be used to calculate a KPI.

Supported data source categories:

- Food handler records
- Medical test records
- Certificate records
- Facility/employer records
- Test center/laboratory records
- Training/orientation records, where applicable
- Inspection/compliance records, where applicable
- Payment records, where applicable
- Manual KPI entry table

### 4.4 Uniqueness / Unicity Field

A uniqueness field prevents duplicate counting.

Examples:

- Food Handler ID
- National Identification Number, where applicable
- Registration Number
- Certificate Number
- Test Record ID
- Facility ID

### 4.5 Disaggregation

Disaggregation breaks down KPI values by specific dimensions.

Examples:

- State
- LGA
- Ward
- Facility type
- Food business category
- Gender
- Age group
- Test status
- Certificate status
- Test center
- Reporting period

### 4.6 Reporting Period

The reporting period defines how often KPI values are tracked and displayed.

Supported frequencies:

- Daily
- Weekly
- Monthly
- Quarterly
- Biannual
- Annual
- Custom date range

## 5. Functional Requirements

## 5.1 KPI Creation and Configuration

### Requirement

Authorized users must be able to create and manage KPIs from a guided configuration interface.

### KPI Fields

| Field | Required | Description |
|---|---:|---|
| KPI Name | Yes | Full name of the KPI. |
| KPI Code | Yes | Short unique code, e.g., `FH_CERT_RATE`. |
| Description | Yes | Explains what the KPI measures. |
| KPI Type | Yes | Quantitative or qualitative. |
| Unit of Measurement | Conditional | Count, percentage, days, ratio, score, text, etc. |
| Data Source Type | Yes | Automated, manual, or hybrid. |
| Primary Data Source | Conditional | System module/table used for automated calculation. |
| Calculation Method | Conditional | Count, unique count, sum, average, percentage, ratio, formula. |
| Reporting Frequency | Yes | Daily, weekly, monthly, quarterly, annual, etc. |
| Baseline Value | Optional | Starting value. |
| Target Value | Optional | Expected performance level. |
| Target Direction | Yes | Higher is better, lower is better, or target band. |
| Thresholds | Optional | Green/amber/red ranges. |
| Disaggregation Fields | Optional | State, LGA, gender, facility type, etc. |
| Visibility Scope | Yes | National, state, LGA, facility, test center, role-based. |
| Status | Yes | Draft, active, inactive, archived. |

### Validation Rules

- KPI code must be unique.
- Quantitative KPIs must have a numeric unit and calculation method.
- Percentage KPIs must define numerator and denominator.
- Automated KPIs must define a data source.
- Manual KPIs must define who can submit values.
- Archived KPIs must remain visible in historical reports but should not calculate new values.

## 5.2 KPI Input Mode

### Requirement

The system must define how KPI values are entered or generated.

| Input Mode | Description | Food Handlers Example |
|---|---|---|
| Manual Only | User enters values directly. | Manual quality rating for state data completeness. |
| Automated Only | KPI is calculated from system records. | Number of certified food handlers. |
| Hybrid | System calculates value but authorized user can adjust or override with reason. | Corrected compliance value after data reconciliation. |

### Manual Entry Rules

Manual KPI entry must capture:

- KPI
- Reporting period
- Jurisdiction or entity scope
- Value
- Comment or explanation
- Submitted by
- Submitted at
- Approval status, if review is enabled

### Override Rules

If an automated KPI is overridden:

- Original system-calculated value must be preserved.
- Override value must require a reason.
- Override must be shown in audit logs.
- Dashboard should indicate that the value was manually adjusted.

## 5.3 Record Input Type

The engine must support the following record input options for KPI values:

| Record Input Type | Meaning | Example |
|---|---|---|
| Progress Only | User/system records only the value achieved within the current reporting period. | Food handlers tested this month. |
| Cumulative Only | User/system records the total achieved up to the current reporting period. | Total certified handlers to date. |
| Progress or Cumulative | User/system may provide either value, and the engine derives the other where valid. | Monthly registrations and total registrations. |

## 5.4 Progress and Cumulative Relationship

### Requirement

The system must define how progress values relate to cumulative values.

| Relationship | Description | Food Handlers Example |
|---|---|---|
| Dependent | Cumulative equals the sum of progress values to date. If cumulative is entered, period progress can be derived by comparing with the previous cumulative value. | Total food handlers registered to date. |
| Same | Progress and cumulative are the same because each current value already represents the full current state. | Current percentage of valid certificates. |
| Independent | Each value stands alone and should not be summed over time. | Monthly average test turnaround time. |

### Validation Rules

- If input type is `Progress or Cumulative`, the `Independent` relationship is invalid.
- If relationship is `Dependent`, cumulative cannot decrease unless the KPI is explicitly configured to allow correction/reversal.
- If relationship is `Same`, the system should copy progress value into cumulative value and vice versa.
- If relationship is `Independent`, trend charts should show period-by-period values only.

## 5.5 Quantitative Calculation Methods

### Supported Methods

| Method | Description | Example |
|---|---|---|
| Count | Counts matching records. | Number of medical tests submitted. |
| Unique Count | Counts unique records using a unicity field. | Number of unique food handlers tested. |
| Sum | Adds numeric values. | Total fees collected, if payment module exists. |
| Average | Computes mean value. | Average test processing time. |
| Percentage | Numerator divided by denominator × 100. | Certified handlers / registered handlers × 100. |
| Ratio | Compares two values. | Certified handlers per facility. |
| Formula | Custom calculation based on multiple fields/KPIs. | Compliance score combining registration, testing, and certification rates. |

### Calculation Configuration Fields

| Field | Applies To | Description |
|---|---|---|
| Data Source | All automated methods | Table/module to query. |
| Value Field | Sum, average | Numeric field used for calculation. |
| Numerator Source | Percentage, ratio | Data source for numerator. |
| Denominator Source | Percentage, ratio | Data source for denominator. |
| Filter Rules | All automated methods | Conditions that records must satisfy. |
| Unicity Field | Count, unique count, percentage | Field used to avoid duplicates. |
| Date Field | All automated methods | Field used to assign record to reporting period. |
| Scope Field | All automated methods | Field used for state, LGA, facility, etc. |

### Filter Examples

- Count only handlers where `registration_status = active`
- Count only tests where `test_status = completed`
- Count only certificates where `certificate_status = valid`
- Count only certificates expiring within 30 days
- Count only handlers in selected state or LGA
- Count only test results where `result = failed`

## 5.6 Qualitative KPI Input

### Requirement

The system may support qualitative KPI values for operational narratives or ratings.

Supported input types:

- Short text
- Long text/narrative
- Dropdown category
- Rating scale, e.g., 1–5
- Compliance rating, e.g., High / Medium / Low

### Food Handlers Use Cases

- State-level narrative on implementation progress
- Facility compliance observations
- Data quality review comments
- Inspection quality rating
- Operational bottleneck notes

### Rules

- Qualitative KPI values should not be mathematically aggregated unless a rating scale is selected.
- Narrative entries should be searchable and exportable.
- Qualitative KPIs should be optional and not the default KPI type.

## 5.7 Linking KPIs to Food Handlers Data Sources

### Requirement

The engine must allow KPIs to pull values from Food Handlers application records.

### Supported Internal Data Sources

| Data Source | Example KPI |
|---|---|
| Food Handler Registry | Number of registered food handlers. |
| Medical Test Records | Number of tested food handlers. |
| Test Results | Percentage of handlers with passed medical tests. |
| Certificate Records | Number of valid certificates issued. |
| Facility Records | Number of registered food businesses/facilities. |
| Facility-Handler Mapping | Facilities with at least one certified handler. |
| Test Centers/Labs | Average processing turnaround time by lab. |
| Inspections | Number of non-compliant facilities identified. |
| Training/Orientation | Number of trained food handlers. |
| Payments | Payment completion rate, if relevant. |

### Removed from Original PRD

The following links are intentionally removed because they are not relevant to the Food Handlers KPI Engine:

- Link to Projects
- Link to Plans / Logframes
- Link to Goals, Outcomes, Outputs, or Activities
- Link to Documents as an official KPI data source
- Draft-to-approved document workflow for official indicator values

## 5.8 KPI-to-KPI Formulas

### Requirement

A KPI may use another KPI as part of its calculation where useful.

### Example

`Certification Rate = (Number of Certified Food Handlers / Number of Registered Food Handlers) × 100`

### Rules

- KPI dependency loops must be prevented.
- If KPI A depends on KPI B, KPI B must calculate first.
- If a dependent KPI fails, the system should show the formula KPI as unavailable for that period and log the reason.
- Aggregation should support sum, average, percentage, ratio, and formula-based calculation.

## 5.9 Disaggregation

### Requirement

The engine must calculate and display KPI values across selected dimensions.

### Required Disaggregation Fields

| Category | Fields |
|---|---|
| Geography | State, LGA, ward, location. |
| Facility | Facility, facility type, food business category. |
| Person | Gender, age group, occupation category, handler category. |
| Medical Testing | Test type, test status, result status, test center/lab. |
| Certification | Certificate status, issue period, expiry period, renewal status. |
| Operations | Registration channel, approval status, data source, user office. |

### Multi-Level Disaggregation

The system should support two-level and optional three-level breakdowns, such as:

- State × LGA
- State × certificate status
- Facility type × certificate status
- Gender × age group
- Test center × turnaround time band

### Rules

- Disaggregation must use fields that exist in the selected data source.
- Disaggregation should not materially slow the dashboard.
- Empty groups should display as zero only when appropriate.

## 5.10 Targets, Thresholds, and Performance Status

### Requirement

Each KPI may define target values and performance thresholds.

### Target Configuration

| Field | Description |
|---|---|
| Target Value | Expected value for a period. |
| Target Period | Month, quarter, year, or custom date range. |
| Target Direction | Higher is better, lower is better, exact target, or target range. |
| Scope | National, state, LGA, facility, lab, etc. |

### Threshold Configuration

| Status | Example Logic for Higher-is-Better KPI |
|---|---|
| On Track | Actual is at least 90% of target. |
| Watch | Actual is 70%–89% of target. |
| Off Track | Actual is below 70% of target. |
| Exceeded | Actual is above target. |

### Food Handlers Examples

- Target: 95% of registered handlers medically tested.
- Target: 90% of certificates renewed before expiry.
- Target: Average test turnaround time below 72 hours.
- Target: 100% of LGAs submitting monthly compliance data.

## 5.11 KPI History and Audit Trail

### Requirement

The system must maintain a full history of KPI configuration changes and KPI value changes.

### Audit Events

- KPI created
- KPI edited
- KPI activated/deactivated
- Calculation rule changed
- Target changed
- Threshold changed
- Manual value submitted
- Manual value approved/rejected
- Automated calculation executed
- Override submitted
- Export generated

### Audit Fields

- Event type
- KPI ID
- User ID
- Role
- Previous value/configuration
- New value/configuration
- Timestamp
- IP/device metadata, where available
- Reason/comment, where applicable

## 5.12 Dashboards and Visualization

### Requirement

KPI values must be displayed in dashboards suitable for operational monitoring and federal oversight.

### Dashboard Components

| Component | Description |
|---|---|
| KPI Summary Cards | Current value, target, status, trend direction. |
| Trend Chart | Value over time by reporting period. |
| Geographic Comparison | State/LGA ranking and comparison. |
| Disaggregation Table | Breakdown by selected dimensions. |
| Threshold Status View | Green/amber/red status. |
| Drilldown View | Click from national → state → LGA → facility where permitted. |
| Data Quality Flags | Missing values, stale data, calculation error, override notice. |

### Suggested Core National KPIs

| KPI Code | KPI Name | Calculation |
|---|---|---|
| `FH_REGISTERED_TOTAL` | Total Registered Food Handlers | Unique count of active food handler IDs. |
| `FH_TESTED_TOTAL` | Total Food Handlers Tested | Unique count of handlers with completed medical test. |
| `FH_TEST_COVERAGE_RATE` | Medical Test Coverage Rate | Tested handlers / registered handlers × 100. |
| `FH_CERTIFIED_TOTAL` | Total Certified Food Handlers | Unique count of handlers with valid certificate. |
| `FH_CERTIFICATION_RATE` | Certification Rate | Certified handlers / registered handlers × 100. |
| `FH_CERT_EXPIRING_30D` | Certificates Expiring Within 30 Days | Count of valid certificates expiring within next 30 days. |
| `FH_RENEWAL_RATE` | Certificate Renewal Rate | Renewed certificates / certificates due for renewal × 100. |
| `FH_FAILED_TEST_RATE` | Failed Medical Test Rate | Failed tests / completed tests × 100. |
| `FH_AVG_TEST_TAT` | Average Test Turnaround Time | Average time from test submission to result approval. |
| `FH_FACILITY_CERT_COVERAGE` | Facility Certification Coverage | Facilities with certified handlers / registered facilities × 100. |
| `FH_PENDING_APPROVALS` | Pending Approvals | Count of records awaiting administrative approval. |
| `FH_DATA_COMPLETENESS_RATE` | Data Completeness Rate | Complete handler records / total handler records × 100. |

## 5.13 Export and Reporting

### Requirement

Users must be able to export KPI views and underlying values.

### Export Formats

- Excel
- CSV
- PDF summary

### Export Types

- KPI list
- KPI configuration
- KPI values by period
- KPI disaggregation table
- KPI dashboard summary
- KPI audit log, for authorized users

### Rules

- Export must respect user access scope.
- Export must show applied filters.
- Export must show generation date, user, and reporting period.
- Exported values must identify whether they are system-calculated, manually entered, or overridden.

## 5.14 Notifications and Alerts

### Requirement

The system should alert users when KPIs require attention.

### Alert Triggers

- KPI below threshold
- KPI has missing reporting period value
- KPI calculation failed
- KPI target period is ending soon
- Certificate expiry KPI exceeds risk threshold
- Test processing turnaround time exceeds threshold
- Manual override submitted for review

### Notification Channels

- In-app notification
- Email, if notification system exists
- Dashboard alert badge

## 6. Non-Functional Requirements

### 6.1 Performance

- KPI dashboard should load within acceptable time for normal operational volume.
- Common KPI calculations should use optimized queries and cached aggregates.
- Large disaggregation queries should be paginated or pre-aggregated.

### 6.2 Scalability

- Must support hundreds of KPIs across national, state, LGA, facility, and lab scopes.
- Must support large food handler registries without significant performance degradation.
- KPI values should be stored as period snapshots to avoid recalculating all historical values on every dashboard load.

### 6.3 Security

- Role-based access must be enforced at API and UI level.
- Sensitive KPI configurations must be editable only by authorized administrators.
- Manual overrides must require permission and audit logging.
- Export access must respect jurisdiction and role.

### 6.4 Reliability

- Failed KPI calculations must not break the full dashboard.
- Each calculation run should log success/failure status.
- The system should retry scheduled calculations where appropriate.

### 6.5 Data Integrity

- Use stable identifiers for unicity fields.
- Prevent duplicate KPI codes.
- Prevent circular KPI dependencies.
- Preserve historical values after KPI configuration changes.

## 7. Recommended Data Model

### 7.1 `kpi_indicators`

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key. |
| code | string | Unique KPI code. |
| name | string | KPI display name. |
| description | text | KPI description. |
| type | enum | quantitative, qualitative. |
| unit | string | count, percentage, days, score, text, etc. |
| input_mode | enum | manual, automated, hybrid. |
| record_input_type | enum | progress_only, cumulative_only, progress_or_cumulative. |
| progress_cumulative_relationship | enum | dependent, same, independent. |
| reporting_frequency | enum | daily, weekly, monthly, quarterly, annual, custom. |
| target_direction | enum | higher_better, lower_better, exact, range. |
| visibility_scope | json | Role/jurisdiction visibility rules. |
| status | enum | draft, active, inactive, archived. |
| created_by | UUID | User ID. |
| updated_by | UUID | User ID. |
| created_at | timestamp |  |
| updated_at | timestamp |  |

### 7.2 `kpi_calculation_rules`

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key. |
| kpi_id | UUID | Foreign key. |
| method | enum | count, unique_count, sum, average, percentage, ratio, formula. |
| data_source | string | Internal module/table identifier. |
| value_field | string | Numeric field for sum/average. |
| numerator_config | json | For percentage/ratio. |
| denominator_config | json | For percentage/ratio. |
| formula_config | json | For formulas and KPI dependencies. |
| filter_rules | json | Query/filter builder config. |
| unicity_field | string | Prevent duplicate counting. |
| date_field | string | Used for reporting period. |
| scope_field | string | State/LGA/facility/lab field. |
| created_at | timestamp |  |
| updated_at | timestamp |  |

### 7.3 `kpi_targets`

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key. |
| kpi_id | UUID | Foreign key. |
| scope_type | enum | national, state, lga, facility, test_center. |
| scope_id | UUID/string | Nullable for national. |
| period_start | date |  |
| period_end | date |  |
| target_value | decimal |  |
| lower_bound | decimal | Optional range target. |
| upper_bound | decimal | Optional range target. |
| created_by | UUID |  |
| created_at | timestamp |  |

### 7.4 `kpi_thresholds`

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key. |
| kpi_id | UUID | Foreign key. |
| status | enum | exceeded, on_track, watch, off_track. |
| operator | enum | >=, >, <=, <, between. |
| value | decimal | Threshold value. |
| value_to | decimal | For between. |
| created_at | timestamp |  |

### 7.5 `kpi_values`

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key. |
| kpi_id | UUID | Foreign key. |
| scope_type | enum | national, state, lga, facility, test_center. |
| scope_id | UUID/string | Nullable for national. |
| period_start | date |  |
| period_end | date |  |
| progress_value | decimal/text | Numeric or qualitative value. |
| cumulative_value | decimal/text | Numeric or qualitative value. |
| calculated_value | decimal/text | Original system value. |
| final_value | decimal/text | Value shown after override. |
| value_source | enum | automated, manual, override. |
| status | enum | draft, submitted, approved, rejected, final. |
| calculation_run_id | UUID | Nullable. |
| submitted_by | UUID | Nullable. |
| approved_by | UUID | Nullable. |
| notes | text | Optional. |
| created_at | timestamp |  |
| updated_at | timestamp |  |

### 7.6 `kpi_disaggregation_values`

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key. |
| kpi_value_id | UUID | Foreign key. |
| dimension_1_name | string | e.g., state. |
| dimension_1_value | string | e.g., Lagos. |
| dimension_2_name | string | Optional. |
| dimension_2_value | string | Optional. |
| value | decimal/text | Disaggregated value. |
| created_at | timestamp |  |

### 7.7 `kpi_calculation_runs`

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key. |
| kpi_id | UUID | Foreign key. |
| period_start | date |  |
| period_end | date |  |
| scope_type | enum |  |
| scope_id | UUID/string |  |
| status | enum | queued, running, success, failed. |
| error_message | text | Nullable. |
| started_at | timestamp |  |
| completed_at | timestamp |  |

### 7.8 `kpi_audit_logs`

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key. |
| kpi_id | UUID | Nullable. |
| event_type | string | Created, updated, calculated, exported, etc. |
| actor_id | UUID | User ID. |
| actor_role | string |  |
| old_value | json | Nullable. |
| new_value | json | Nullable. |
| reason | text | Nullable. |
| created_at | timestamp |  |

## 8. API Requirements

### 8.1 KPI Configuration APIs

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/kpis` | List KPIs with filters. |
| POST | `/api/kpis` | Create KPI. |
| GET | `/api/kpis/{id}` | View KPI details. |
| PUT | `/api/kpis/{id}` | Update KPI. |
| DELETE | `/api/kpis/{id}` | Archive/delete KPI, depending on policy. |
| POST | `/api/kpis/{id}/activate` | Activate KPI. |
| POST | `/api/kpis/{id}/deactivate` | Deactivate KPI. |

### 8.2 Calculation Rule APIs

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/kpis/{id}/calculation-rule` | Get calculation rule. |
| PUT | `/api/kpis/{id}/calculation-rule` | Save calculation rule. |
| POST | `/api/kpis/{id}/validate-rule` | Validate rule before activation. |
| POST | `/api/kpis/{id}/calculate` | Run calculation for selected period/scope. |
| GET | `/api/kpis/{id}/calculation-runs` | View calculation run history. |

### 8.3 KPI Value APIs

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/kpi-values` | List KPI values by period/scope. |
| POST | `/api/kpi-values/manual` | Submit manual KPI value. |
| POST | `/api/kpi-values/{id}/approve` | Approve manual/override value. |
| POST | `/api/kpi-values/{id}/reject` | Reject submitted value. |
| POST | `/api/kpi-values/{id}/override` | Override KPI value with reason. |
| GET | `/api/kpis/{id}/trend` | Get trend data. |
| GET | `/api/kpis/{id}/disaggregation` | Get disaggregated values. |

### 8.4 Dashboard and Export APIs

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/kpi-dashboard/summary` | KPI summary cards. |
| GET | `/api/kpi-dashboard/comparison` | State/LGA/facility comparison. |
| GET | `/api/kpi-dashboard/alerts` | KPI alerts. |
| GET | `/api/kpi-dashboard/export` | Export dashboard. |
| GET | `/api/kpis/{id}/export` | Export KPI values/configuration. |

## 9. UI/UX Requirements

## 9.1 KPI Management Screen

### Purpose

Allows authorized users to view, search, create, edit, activate, deactivate, and archive KPIs.

### Layout

- Header: `KPI Indicator Engine`
- Primary actions: `Create KPI`, `Export`, `Run Calculations`
- Filters:
  - Status
  - KPI type
  - Reporting frequency
  - Data source
  - Scope
  - Created by
- Table columns:
  - KPI code
  - KPI name
  - Type
  - Unit
  - Input mode
  - Data source
  - Frequency
  - Status
  - Last calculated
  - Actions

### Actions

- View
- Edit
- Configure calculation
- Configure targets
- View values
- View audit log
- Activate/deactivate
- Archive

## 9.2 KPI Creation Wizard

### Step 1: Basic Details

Fields:

- KPI name
- KPI code
- Description
- KPI type
- Unit of measurement
- Reporting frequency
- Visibility scope

### Step 2: Input Mode

Fields:

- Manual, automated, or hybrid
- Record input type
- Progress/cumulative relationship
- Manual submission roles, if applicable

### Step 3: Data Source and Calculation

Fields:

- Data source
- Calculation method
- Value field
- Date field
- Scope field
- Unicity field
- Numerator and denominator, if percentage/ratio
- Filter builder

### Step 4: Disaggregation

Fields:

- Select one or more dimensions
- Preview possible disaggregation output

### Step 5: Targets and Thresholds

Fields:

- Target value
- Target direction
- Target period
- Threshold rules
- Scope-specific targets

### Step 6: Review and Activate

Displays:

- Summary of KPI configuration
- Validation results
- Calculation preview using sample/latest data
- Buttons: `Save as Draft`, `Activate KPI`, `Cancel`

## 9.3 KPI Detail Screen

Sections:

- KPI summary
- Current value
- Target and status
- Trend chart
- Disaggregation breakdown
- Calculation rule
- Manual entries/overrides
- Calculation history
- Audit log

## 9.4 KPI Dashboard

### Federal Dashboard View

Should support:

- National KPI summary cards
- State ranking table
- Map or table by state
- Trends over time
- Expiring certificate risk indicators
- Test turnaround time indicators
- Data completeness indicators
- Filters by period, state, LGA, facility type, test center, and certificate status

### State Dashboard View

Should support:

- State KPI summary cards
- LGA comparison
- Facility-level drilldown
- Test center performance
- Certificate status distribution
- Monthly trend views

### Facility/Test Center View

Should support limited scope KPIs such as:

- Registered handlers in facility
- Certified handlers in facility
- Expiring certificates
- Tests submitted
- Tests pending
- Average turnaround time

## 10. Implementation Chunks for Codex

## Chunk 1: Create KPI Engine Data Models and Migrations

### Objective

Create database tables for KPI configuration, calculation rules, targets, thresholds, values, disaggregation, calculation runs, and audit logs.

### Tasks

1. Add `kpi_indicators` model/table.
2. Add `kpi_calculation_rules` model/table.
3. Add `kpi_targets` model/table.
4. Add `kpi_thresholds` model/table.
5. Add `kpi_values` model/table.
6. Add `kpi_disaggregation_values` model/table.
7. Add `kpi_calculation_runs` model/table.
8. Add `kpi_audit_logs` model/table.
9. Add enum constants for KPI type, status, input mode, calculation method, reporting frequency, scope type, value source, and progress/cumulative relationship.
10. Add indexes for:
    - KPI code
    - KPI status
    - KPI values by KPI + period + scope
    - Calculation runs by KPI + status
    - Audit logs by KPI + created date

### Acceptance Criteria

- Migrations run successfully.
- KPI code uniqueness is enforced.
- Foreign keys are defined correctly.
- Historical KPI values are not deleted when KPI is archived.

## Chunk 2: Build KPI CRUD APIs

### Objective

Implement API endpoints for creating, reading, updating, listing, activating, deactivating, and archiving KPIs.

### Tasks

1. Create KPI controller/service.
2. Implement `GET /api/kpis` with filters and pagination.
3. Implement `POST /api/kpis`.
4. Implement `GET /api/kpis/{id}`.
5. Implement `PUT /api/kpis/{id}`.
6. Implement archive/deactivate behavior instead of hard delete by default.
7. Add request validation.
8. Add audit logging for create/update/status changes.
9. Add permission checks.

### Acceptance Criteria

- Authorized users can create KPIs.
- Unauthorized users cannot create or edit KPIs.
- KPI list can be filtered by status, type, input mode, frequency, and data source.
- Audit logs are created for all configuration changes.

## Chunk 3: Build Calculation Rule Builder Backend

### Objective

Allow automated KPIs to be configured against Food Handlers data sources.

### Tasks

1. Define allowed data source registry for Food Handlers modules.
2. Define allowed fields per data source.
3. Implement validation for calculation methods.
4. Implement filter rule schema.
5. Implement unicity field validation.
6. Implement numerator/denominator validation for percentages and ratios.
7. Implement formula dependency validation.
8. Prevent circular KPI dependencies.
9. Implement `PUT /api/kpis/{id}/calculation-rule`.
10. Implement `POST /api/kpis/{id}/validate-rule`.

### Acceptance Criteria

- Users can only select valid fields for the selected data source.
- Percentage KPIs cannot be saved without numerator and denominator.
- Formula KPIs cannot reference themselves directly or indirectly.
- Invalid rules return useful error messages.

## Chunk 4: Implement KPI Calculation Engine

### Objective

Calculate KPI values using configured calculation rules.

### Tasks

1. Create `KpiCalculationService`.
2. Implement count calculation.
3. Implement unique count calculation.
4. Implement sum calculation.
5. Implement average calculation.
6. Implement percentage calculation.
7. Implement ratio calculation.
8. Implement formula calculation.
9. Apply filter rules.
10. Apply date period filtering.
11. Apply scope filtering.
12. Store calculation results in `kpi_values`.
13. Store calculation run status in `kpi_calculation_runs`.
14. Log calculation errors without breaking dashboard.

### Acceptance Criteria

- Calculation results are stored per KPI, period, and scope.
- Failed calculations are logged.
- Dashboard can continue loading if one KPI fails.
- Unique count prevents double counting based on configured unicity field.

## Chunk 5: Implement Progress and Cumulative Logic

### Objective

Support progress-only, cumulative-only, and progress-or-cumulative values with valid relationships.

### Tasks

1. Add validation for record input type and relationship combinations.
2. Implement dependent calculation logic.
3. Implement same-value logic.
4. Implement independent-value logic.
5. Handle cumulative derivation from progress.
6. Handle progress derivation from cumulative where valid.
7. Add tests for edge cases.

### Acceptance Criteria

- Independent relationship is rejected for progress-or-cumulative input.
- Dependent cumulative values are correctly summed from progress values.
- Same relationship mirrors progress and cumulative.
- Independent values are not summed over time.

## Chunk 6: Implement Manual KPI Entry and Override Workflow

### Objective

Allow manual KPI values and controlled overrides.

### Tasks

1. Implement `POST /api/kpi-values/manual`.
2. Implement draft/submitted/approved/rejected/final statuses.
3. Implement override endpoint.
4. Require reason for overrides.
5. Preserve calculated value and final displayed value separately.
6. Add permission checks.
7. Add audit logs.
8. Add UI indicators for overridden values.

### Acceptance Criteria

- Manual entries require valid KPI, period, scope, and value.
- Overrides require reason.
- Original calculated value is never lost.
- Audit logs show who entered or overrode values.

## Chunk 7: Implement Targets and Thresholds

### Objective

Allow users to configure targets and performance status logic.

### Tasks

1. Implement target CRUD endpoints.
2. Implement threshold CRUD endpoints.
3. Add target direction support.
4. Add scope-specific targets.
5. Implement status evaluation service.
6. Display status as exceeded/on-track/watch/off-track.
7. Add validation for threshold overlaps.

### Acceptance Criteria

- KPI can have different targets by period and scope.
- KPI status is calculated correctly based on target direction.
- Threshold rules cannot conflict.
- Dashboard cards show target, actual, and status.

## Chunk 8: Implement Disaggregation Engine

### Objective

Calculate KPI breakdowns by selected dimensions.

### Tasks

1. Add disaggregation field registry per data source.
2. Implement one-level disaggregation.
3. Implement two-level disaggregation.
4. Store disaggregation snapshots.
5. Implement `GET /api/kpis/{id}/disaggregation`.
6. Add pagination for large breakdowns.
7. Add filter support.

### Acceptance Criteria

- KPI can be broken down by state, LGA, facility type, gender, age group, test status, certificate status, and test center where available.
- Disaggregation fields must exist in selected data source.
- Dashboard can display disaggregation table and charts.

## Chunk 9: Build KPI Management UI

### Objective

Create the interface for listing and managing KPIs.

### Tasks

1. Build KPI management page.
2. Add KPI table with filters.
3. Add create KPI button.
4. Add action menu.
5. Add status badges.
6. Add last calculated display.
7. Add permissions-aware buttons.

### Acceptance Criteria

- Users can search and filter KPIs.
- Authorized users see create/edit actions.
- Unauthorized users see view-only experience.
- UI clearly distinguishes draft, active, inactive, and archived KPIs.

## Chunk 10: Build KPI Creation Wizard UI

### Objective

Create the step-by-step KPI configuration wizard.

### Tasks

1. Build Step 1: Basic Details.
2. Build Step 2: Input Mode.
3. Build Step 3: Data Source and Calculation.
4. Build Step 4: Disaggregation.
5. Build Step 5: Targets and Thresholds.
6. Build Step 6: Review and Activate.
7. Add form validation.
8. Add calculation rule preview.
9. Add save draft behavior.

### Acceptance Criteria

- Users can complete KPI setup without seeing irrelevant project/document fields.
- Wizard only shows Food Handlers data sources.
- Invalid calculation rules are blocked before activation.
- KPI can be saved as draft or activated.

## Chunk 11: Build KPI Detail and Trend Views

### Objective

Show KPI values, trend, targets, calculation configuration, and audit information.

### Tasks

1. Build KPI detail page.
2. Add current value summary.
3. Add target/status card.
4. Add trend chart.
5. Add disaggregation section.
6. Add calculation history tab.
7. Add manual values/overrides tab.
8. Add audit log tab.

### Acceptance Criteria

- KPI detail page shows current and historical values.
- Users can inspect how KPI was calculated.
- Overrides and manual entries are visible to authorized users.
- Audit trail is accessible to authorized users.

## Chunk 12: Build KPI Dashboard

### Objective

Create dashboard views for federal, state, LGA, facility, and test center users.

### Tasks

1. Build dashboard summary API.
2. Build summary cards.
3. Build trend chart component.
4. Build comparison table.
5. Build disaggregation chart/table component.
6. Add filters for period, geography, facility type, test center, certificate status, and test status.
7. Add drilldown behavior based on access scope.
8. Add alert indicators.

### Acceptance Criteria

- Federal users can see national and state comparison.
- State users can see state and LGA comparison.
- Facility/test center users see only assigned scope.
- Filters update dashboard values correctly.

## Chunk 13: Implement Scheduled Calculation Jobs

### Objective

Automatically calculate active KPIs based on reporting frequency.

### Tasks

1. Create scheduled job for active KPIs.
2. Determine due KPIs by reporting frequency.
3. Calculate KPIs by configured scope.
4. Save run logs.
5. Retry failed jobs where appropriate.
6. Add manual “Run Calculation” action.

### Acceptance Criteria

- Active KPIs are calculated automatically.
- Failed runs are logged with reasons.
- Authorized users can trigger calculation manually.
- Duplicate runs for same KPI/period/scope are prevented or safely updated.

## Chunk 14: Implement Alerts and Notifications

### Objective

Notify users when KPI values require attention.

### Tasks

1. Define alert rules.
2. Generate alerts after KPI calculation.
3. Add dashboard alert list.
4. Add in-app notifications.
5. Add email notifications if notification system exists.
6. Add alert read/resolve status.

### Acceptance Criteria

- Off-track KPIs generate alerts.
- Missing or failed KPI calculations generate alerts.
- Alerts respect user scope and role.

## Chunk 15: Implement Exports

### Objective

Allow KPI data and dashboard views to be exported.

### Tasks

1. Implement Excel export.
2. Implement CSV export.
3. Implement PDF dashboard summary export.
4. Include applied filters and metadata.
5. Enforce access scope.
6. Add export audit logs.

### Acceptance Criteria

- Users can export allowed KPI data.
- Exported data reflects applied filters.
- Unauthorized data is not included.
- Export action is logged.

## Chunk 16: Testing and QA

### Objective

Ensure the KPI Engine is accurate, secure, and production-ready.

### Test Categories

1. Unit tests for calculation methods.
2. Unit tests for progress/cumulative logic.
3. Unit tests for threshold evaluation.
4. Unit tests for formula dependencies and circular dependency prevention.
5. API tests for permissions.
6. API tests for KPI CRUD.
7. API tests for manual entry and override.
8. Dashboard tests for scoped data visibility.
9. Export tests.
10. Performance tests for large datasets.

### Acceptance Criteria

- All calculation methods return expected values.
- RBAC prevents unauthorized access.
- Dashboard values match stored KPI values.
- Exports match filtered dashboard results.
- Failed calculation jobs do not crash the dashboard.

## 11. Acceptance Criteria

### Functional Acceptance Criteria

1. Users can create KPI indicators specifically for Food Handlers operations.
2. Users cannot configure irrelevant links to projects, logframes, plans, activities, or documents.
3. Automated KPIs can calculate from Food Handlers data sources.
4. Manual and hybrid KPI values are supported with audit trails.
5. Count, unique count, sum, average, percentage, ratio, and formula methods work correctly.
6. KPI values can be filtered and disaggregated by relevant Food Handlers dimensions.
7. Dashboards display KPI values, trends, targets, thresholds, and alerts.
8. KPI values can be exported according to user access scope.
9. Configuration and value changes are audit logged.
10. Sensitive or national KPI configuration is protected by RBAC.

### Technical Acceptance Criteria

1. KPI calculations complete within acceptable load time for normal query sizes.
2. Large historical values are retrieved from snapshots rather than recalculated every time.
3. Failed KPI calculations are logged and do not crash the dashboard.
4. API endpoints enforce scope-based permissions.
5. Database indexes support common KPI queries.
6. Calculation rules are validated before activation.
7. Circular KPI dependencies are prevented.

## 12. Out of Scope

The following should not be implemented as part of this KPI Engine:

- Project management module
- Logframe or plan hierarchy
- Activity management
- Document evidence workflow
- Document approval workflow
- Report-builder replacement
- Machine learning prediction
- NLP analysis of qualitative text
- External BI dashboard embedding, unless separately scoped

## 13. Codex Implementation Prompt

Use the following prompt to guide implementation:

> Implement the Food Handlers KPI Indicator Engine using the attached PRD. This engine should allow authorized users to configure, calculate, track, disaggregate, dashboard, audit, and export KPIs for the National Food Handlers Medical Test Application. Do not include project, logframe, activity, or document-linking logic. KPI data sources must be internal Food Handlers modules such as food handler registry, medical tests, certificates, facilities, test centers, inspections, training, and payments where available. Implement in chunks: models/migrations, CRUD APIs, calculation rule builder, calculation engine, progress/cumulative logic, manual/override workflow, targets/thresholds, disaggregation engine, KPI management UI, KPI wizard UI, KPI detail/trend views, dashboards, scheduled calculations, alerts, exports, and tests. Enforce RBAC, audit logging, scope-based visibility, and validation for calculation rules.

