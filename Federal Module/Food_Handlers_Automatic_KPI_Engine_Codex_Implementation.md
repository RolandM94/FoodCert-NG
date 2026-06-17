# Food Handlers Application — Automatic KPI Engine Update

## Codex Implementation Brief

The KPI Indicator Engine already exists. Do **not** rebuild it from scratch.

Update the existing KPI configuration, backend calculation logic, UI actions, seed data, and policy-rule integration so that Food Handlers KPIs generated from system activities are calculated automatically instead of requiring manual entry.

Current issue: the KPI table shows several operational KPIs with `Input Mode = Manual`, including:

- Data Completeness Score
- Expired Certificate Rate
- Facility Accreditation Compliance
- Food Handler Certification Rate
- QR Verification Failure Rate
- Return-to-Work Clearance Rate

This is incorrect for most Food Handlers KPIs because their source data is already generated inside the application through food handler registration, medical assessment, certificate issuance, QR verification, facility accreditation, illness reporting, return-to-work clearance, and state reporting workflows.

---

# 1. Objective

## 1.1 Goal

Make system-derived Food Handlers KPIs automatic by default while preserving manual, imported, and hybrid KPI support for exceptional cases.

## 1.2 Expected Outcome

After implementation:

- Automatic KPIs calculate directly from system records.
- Manual entry is hidden for automatic KPIs.
- Automatic KPIs show calculation, source records, and recalculation actions.
- Certificate, assessment, facility accreditation, QR verification, and return-to-work KPI calculations read from active policy standards instead of hardcoded values.
- Existing Food Handlers KPI seed data is updated so operational KPIs are no longer created as manual by default.

---

# 2. Required KPI Input Modes

Update the KPI engine to support the following input modes.

## 2.1 Automatic

The KPI value is calculated from system records.

Rules:

- Users must not manually enter values for fully automatic KPIs.
- Users can view calculation logic.
- Users can view source records.
- Authorized users can trigger recalculation.
- Latest value should update from calculation results.

## 2.2 Manual

The KPI value is entered manually by an authorized user.

Use only when:

- The source data does not exist in the system.
- The KPI depends on an external/offline process.

## 2.3 Imported

The KPI value is uploaded through CSV/Excel.

Use only for:

- Legacy KPI data.
- Offline datasets.
- Bulk historical records.

## 2.4 Hybrid / Semi-Automatic

The system calculates the KPI value, but authorized users can override or adjust it with a mandatory reason.

Rules:

- The system must always preserve the original calculated value.
- Override reason is required.
- Override action must be logged.
- Hybrid KPIs should show both calculated and overridden values where applicable.

---

# 3. KPI UI Behaviour Requirements

## 3.1 KPI List/Table Page

Update the KPI table to display these columns:

| Column | Description |
|---|---|
| KPI | KPI name |
| Code | KPI code |
| KPI Type | Quantitative / Qualitative |
| Input Mode | Automatic / Manual / Imported / Hybrid |
| Frequency | Monthly / Quarterly / Annually / etc. |
| Latest Value | Latest calculated, entered, or imported value |
| Target | KPI target value |
| Achievement | Performance against target |
| Status | Active / Draft / Retired |
| Last Updated | Last calculated, entered, or imported date |
| Actions | Context-aware actions |

## 3.2 Actions for Automatic KPIs

For KPIs with `input_mode = automatic`, hide or disable:

- Enter Data
- Import

Show instead:

- Edit KPI
- View Calculation
- View Source Records
- Recalculate

## 3.3 Actions for Manual KPIs

For KPIs with `input_mode = manual`, show:

- Edit KPI
- Enter Data
- Import, if imports are allowed

## 3.4 Actions for Imported KPIs

For KPIs with `input_mode = imported`, show:

- Edit KPI
- Import
- View Imported Records

## 3.5 Actions for Hybrid KPIs

For KPIs with `input_mode = hybrid`, show:

- Edit KPI
- View Calculation
- View Source Records
- Recalculate
- Override Value

## 3.6 Empty or Not Calculated State

For automatic KPIs that have never been calculated:

```text
Latest Value: Not calculated yet
Last Updated: —
Actions: View Calculation, View Source Records, Recalculate
```

---

# 4. Existing KPI Seed Updates

Update the current KPI seed/configuration so the following KPIs are automatic or hybrid.

---

## 4.1 Data Completeness Score

```json
{
  "name": "Data Completeness Score",
  "code": "ME-DATA-COMPLETE",
  "kpi_type": "quantitative",
  "input_mode": "automatic",
  "calculation_type": "percentage",
  "calculation_source": "system_required_fields",
  "frequency": "quarterly",
  "status": "active"
}
```

### Calculation

```text
Data Completeness Score = (Completed Required Fields / Total Required Fields) × 100
```

### Suggested Source Records

- Food handler profile records
- Medical assessment records
- Certificate records
- Medical facility records
- State reporting records, if applicable

### Required Fields

Suggested required fields include:

- Full name
- Date of birth
- Gender
- NIN
- Passport photograph
- State
- LGA
- Food handler category
- Linked food business or establishment
- Medical assessment status
- Certificate status
- Certificate issue date
- Certificate expiry date

---

## 4.2 Expired Certificate Rate

```json
{
  "name": "Expired Certificate Rate",
  "code": "ME-EXPIRED-RATE",
  "kpi_type": "quantitative",
  "input_mode": "automatic",
  "calculation_type": "percentage",
  "calculation_source": "certificates",
  "frequency": "monthly",
  "linked_policy_standard_code": "FH-VALIDITY-2024-001",
  "status": "active"
}
```

### Calculation

```text
Expired Certificate Rate = (Number of expired certificates / Total issued certificates) × 100
```

### Source Records

- Certificates table
- Food handler certification records

### Policy Dependency

Use active policy standard:

```text
FH-VALIDITY-2024-001
```

Required policy parameter:

```json
{
  "certificate_validity_months": 6
}
```

### Expiry Rule

A certificate is expired when:

```text
current_date > certificate_expiry_date
```

---

## 4.3 Facility Accreditation Compliance

```json
{
  "name": "Facility Accreditation Compliance",
  "code": "ME-FACILITY-ACCRED",
  "kpi_type": "quantitative",
  "input_mode": "automatic",
  "calculation_type": "percentage",
  "calculation_source": "medical_facilities",
  "frequency": "quarterly",
  "linked_policy_standard_code": "FH-FAC-2024-001",
  "status": "active"
}
```

### Calculation

```text
Facility Accreditation Compliance = (Number of approved facilities with valid accreditation / Total registered medical facilities) × 100
```

### Source Records

- Medical facilities
- Facility accreditation records
- State facility mapping records

### Policy Dependency

Use active policy standard:

```text
FH-FAC-2024-001
```

Required policy parameter:

```json
{
  "reaccreditation_interval_months": 12
}
```

### Facility Compliance Rule

A facility is compliant when:

- Facility status is approved/accredited.
- Accreditation has not expired.
- Facility is mapped to a state/FCT.
- Facility is authorized to conduct food handler assessments.

---

## 4.4 Food Handler Certification Rate

```json
{
  "name": "Food Handler Certification Rate",
  "code": "ME-CERT-RATE",
  "kpi_type": "quantitative",
  "input_mode": "automatic",
  "calculation_type": "percentage",
  "calculation_source": "certificates",
  "frequency": "quarterly",
  "linked_policy_standard_code": "FH-VALIDITY-2024-001",
  "status": "active"
}
```

### Calculation

```text
Food Handler Certification Rate = (Number of food handlers with valid certificates / Total registered food handlers) × 100
```

### Source Records

- Food handlers table
- Certificates table
- Medical assessment table

### Policy Dependency

Use active policy standard:

```text
FH-VALIDITY-2024-001
```

Required policy parameter:

```json
{
  "certificate_validity_months": 6
}
```

### Food Handler Compliance Rule

A food handler is certified/compliant when:

- The handler has a certificate.
- Certificate status is valid/active.
- Certificate is within the 6-month validity period.
- Certificate has not expired.
- Certificate has not been revoked.

---

## 4.5 QR Verification Failure Rate

```json
{
  "name": "QR Verification Failure Rate",
  "code": "ME-QR-FAIL",
  "kpi_type": "quantitative",
  "input_mode": "automatic",
  "calculation_type": "percentage",
  "calculation_source": "qr_verification_logs",
  "frequency": "monthly",
  "linked_policy_standard_code": "FH-CERT-2024-001",
  "status": "active"
}
```

### Calculation

```text
QR Verification Failure Rate = (Failed QR verification attempts / Total QR verification attempts) × 100
```

### Source Records

- QR verification logs
- Certificate verification attempts

### Failure Conditions

A verification attempt should be counted as failed if the failure reason is one of the following:

- Invalid QR code
- Expired certificate
- Revoked certificate
- Certificate not found
- Identity mismatch
- Malformed verification token

### Policy Dependency

Use active policy standard:

```text
FH-CERT-2024-001
```

Required policy parameters:

```json
{
  "requires_qr_code": true,
  "certificate_must_be_digitally_verifiable": true
}
```

---

## 4.6 Return-to-Work Clearance Rate

Use `automatic` if the illness and return-to-work clearance workflows are fully inside the system.

Use `hybrid` if some clearances happen offline and require manual override or adjustment.

```json
{
  "name": "Return-to-Work Clearance Rate",
  "code": "ME-RTW-RATE",
  "kpi_type": "quantitative",
  "input_mode": "hybrid",
  "calculation_type": "percentage",
  "calculation_source": "return_to_work_clearances",
  "frequency": "quarterly",
  "linked_policy_standard_code": "FH-RTW-2024-001",
  "allow_manual_override": true,
  "override_requires_reason": true,
  "status": "active"
}
```

### Calculation

```text
Return-to-Work Clearance Rate = (Number of excluded food handlers cleared to return to work / Total excluded food handlers requiring clearance) × 100
```

### Source Records

- Illness reports
- Exclusion records
- Medical reassessment records
- Return-to-work clearance records

### Policy Dependency

Use active policy standard:

```text
FH-RTW-2024-001
```

### Valid Return-to-Work Clearance Rule

A return-to-work clearance is valid when:

- The excluded handler has completed the required exclusion period.
- Medical clearance has been recorded, where required.
- Clearance status is approved.
- Clearance was issued by an authorized medical practitioner or health authority, depending on condition.

---

# 5. Backend Model / Configuration Updates

Add or update the KPI model/configuration with the fields below if they do not already exist.

If equivalent fields already exist, reuse them instead of duplicating.

```text
input_mode: enum
Allowed values: automatic, manual, imported, hybrid

calculation_type: enum
Suggested values: percentage, count, ratio, average, sum, score

calculation_source: string or enum
Examples: food_handlers, certificates, medical_assessments, medical_facilities, qr_verification_logs, illness_reports, return_to_work_clearances, state_reports

numerator_definition: text/json
denominator_definition: text/json
policy_version_id: nullable FK
policy_standard_id: nullable FK
rule_parameter_key: nullable string
allow_manual_override: boolean
override_requires_reason: boolean
last_calculated_at: datetime
latest_value: decimal/float
target_value: decimal/float nullable
achievement_value: decimal/float nullable
```

---

# 6. KPI Calculation Service Requirements

Create or update a KPI calculation service with methods similar to:

```text
calculateKpi(kpiId, filters)
calculateDataCompletenessScore(filters)
calculateExpiredCertificateRate(filters)
calculateFacilityAccreditationCompliance(filters)
calculateFoodHandlerCertificationRate(filters)
calculateQrVerificationFailureRate(filters)
calculateReturnToWorkClearanceRate(filters)
recalculateAutomaticKpis()
getKpiSourceRecords(kpiId, filters)
```

## 6.1 Calculation Service Rules

The service must:

- Only calculate `automatic` and `hybrid` KPIs.
- Reject calculation for purely `manual` KPIs.
- Store latest calculated value.
- Store calculation timestamp.
- Support calculation filters.
- Create a calculation log for every recalculation.

## 6.2 Required Filters

The calculation service should support filters by:

- Date range
- State
- LGA
- Facility
- Food handler category
- Establishment type
- Certificate status
- Policy version, where applicable

---

# 7. Policy Rule Integration Requirements

Do **not** hardcode certificate validity, assessment validity, facility reaccreditation, QR verification requirements, or return-to-work exclusion rules directly inside KPI calculation code.

The KPI engine must read policy-dependent values from the active Policy Version tool.

## 7.1 Required Active Policy Standards

The KPI engine should be able to read from:

```text
FH-VALIDITY-2024-001
FH-FAC-2024-001
FH-CERT-2024-001
FH-RTW-2024-001
```

## 7.2 Certificate KPI Policy Rules

For certificate-related KPIs, read from:

```text
FH-VALIDITY-2024-001
```

Required parameters:

```json
{
  "certificate_validity_months": 6,
  "assessment_validity_months": 6
}
```

## 7.3 Facility Accreditation KPI Policy Rules

For Facility Accreditation Compliance, read from:

```text
FH-FAC-2024-001
```

Required parameter:

```json
{
  "reaccreditation_interval_months": 12
}
```

## 7.4 QR Verification KPI Policy Rules

For QR Verification Failure Rate, read from:

```text
FH-CERT-2024-001
```

Required parameters:

```json
{
  "requires_qr_code": true,
  "certificate_must_be_digitally_verifiable": true
}
```

## 7.5 Return-to-Work KPI Policy Rules

For Return-to-Work Clearance Rate, read from:

```text
FH-RTW-2024-001
```

Required parameter:

```json
{
  "standard_exclusion_period_hours_after_symptoms_stop": 48
}
```

Also use specific infection clearance rules where applicable.

## 7.6 Missing Policy Rule Error

If active policy rules are unavailable, return a clear system error:

```text
Active policy rule not found for this KPI calculation.
```

---

# 8. Source Records View

For automatic and hybrid KPIs, implement **View Source Records**.

This page or modal should show the records used in the calculation.

## 8.1 Expired Certificate Rate Source Records

Show:

- Total issued certificates
- Expired certificates
- Certificate ID
- Food handler name
- Issue date
- Expiry date
- Status
- State
- Facility

## 8.2 QR Verification Failure Rate Source Records

Show:

- Total QR attempts
- Failed attempts
- Verification timestamp
- Certificate ID
- Failure reason
- Verifier type
- State
- Facility/inspector, if available

## 8.3 Facility Accreditation Compliance Source Records

Show:

- Total registered facilities
- Approved/accredited facilities
- Expired accreditation facilities
- Facility name
- State
- Accreditation issue date
- Accreditation expiry date
- Status

## 8.4 Food Handler Certification Rate Source Records

Show:

- Total registered food handlers
- Certified food handlers
- Food handler name
- Food handler category
- Certificate ID
- Certificate issue date
- Certificate expiry date
- Certificate status
- State
- LGA
- Facility

## 8.5 Return-to-Work Clearance Rate Source Records

Show:

- Total excluded food handlers requiring clearance
- Cleared food handlers
- Food handler name
- Illness/exclusion reason
- Exclusion start date
- Required clearance date
- Clearance date
- Clearance status
- Medical facility
- Approving practitioner/authority

---

# 9. Recalculation Requirements

For automatic and hybrid KPIs:

- Add a `Recalculate` action.
- Recalculation should update `latest_value`.
- Recalculation should update `last_calculated_at`.
- Recalculation should respect the KPI frequency and selected reporting period.
- Recalculation should create a calculation log.

## 9.1 Calculation Log Table

Create or update a calculation log table if needed.

Suggested fields:

```text
id
kpi_id
reporting_period
calculated_value
numerator_value
denominator_value
filters_used
policy_version_id
policy_standard_id
calculated_by
calculated_at
calculation_status
error_message
```

---

# 10. Manual Override Requirements for Hybrid KPIs

For hybrid KPIs:

- Allow authorized users to override calculated values.
- Override must require a reason.
- Store the original calculated value.
- Store the overridden value.
- Store override reason.
- Store override user and timestamp.

Suggested override fields:

```text
original_calculated_value
overridden_value
override_reason
overridden_by
overridden_at
```

Automatic KPIs should not allow override unless:

```text
allow_manual_override = true
```

---

# 11. Permissions

Add or enforce these permissions.

## 11.1 Federal Admin

Can:

- Create/edit KPI configuration
- Recalculate automatic KPIs
- View source records
- Approve overrides

## 11.2 Federal M&E Officer

Can:

- View KPIs
- Recalculate automatic KPIs
- View source records
- Enter manual data where permitted
- Request or perform hybrid override if allowed

## 11.3 State Admin

Can:

- View KPIs for their state
- View source records scoped to their state
- Enter manual data only for state-level manual KPIs

## 11.4 Medical Facility Admin

Can:

- View KPIs related to their facility only, if enabled
- Cannot edit KPI definitions

## 11.5 KPI Admin

Can:

- Configure KPI calculation rules
- Link KPIs to policy standards

---

# 12. Implementation Chunks for Codex

## Chunk 1: Review Existing KPI Engine Structure

### Task

Inspect the existing KPI engine models, seed files, API endpoints, list table component, action buttons, and manual entry/import workflows.

### Acceptance Criteria

- Existing KPI model/configuration fields are identified.
- Existing manual entry workflow is identified.
- Existing import workflow is identified.
- Existing KPI seed/configuration file is identified.
- No duplicate model fields are introduced where equivalent fields already exist.

---

## Chunk 2: Add or Update KPI Input Mode Support

### Task

Add support for these input modes:

```text
automatic
manual
imported
hybrid
```

### Acceptance Criteria

- KPI records can store the correct input mode.
- Existing manual KPIs continue to work.
- Automatic and hybrid modes are accepted by backend validation.
- UI displays all four modes correctly.

---

## Chunk 3: Update KPI Model/Schema Fields

### Task

Add or reuse fields required for automatic calculation and policy linking.

### Required Fields

```text
calculation_type
calculation_source
numerator_definition
denominator_definition
policy_version_id
policy_standard_id
rule_parameter_key
allow_manual_override
override_requires_reason
last_calculated_at
latest_value
target_value
achievement_value
```

### Acceptance Criteria

- Database/model supports automatic KPI configuration.
- Fields are nullable where needed to avoid breaking existing KPIs.
- Migrations run successfully.
- Existing KPI data remains intact.

---

## Chunk 4: Update Food Handlers KPI Seed Data

### Task

Update existing seed/configuration for the following KPIs:

```text
ME-DATA-COMPLETE → automatic
ME-EXPIRED-RATE → automatic
ME-FACILITY-ACCRED → automatic
ME-CERT-RATE → automatic
ME-QR-FAIL → automatic
ME-RTW-RATE → hybrid or automatic depending on implemented return-to-work workflow
```

### Acceptance Criteria

- These KPIs no longer seed as manual by default.
- Each KPI has a calculation type.
- Each KPI has a calculation source.
- Policy-dependent KPIs link to the correct policy standard code.
- Existing data is updated safely without duplicating KPI records.

---

## Chunk 5: Implement Active Policy Rule Reader

### Task

Create or reuse a service for reading active policy standard parameters.

### Required Methods

```text
getActivePolicyVersion()
getActivePolicyStandardByCode(standardCode)
getPolicyRuleParameter(standardCode, parameterKey)
```

### Acceptance Criteria

- KPI engine can fetch `FH-VALIDITY-2024-001`.
- KPI engine can fetch `FH-FAC-2024-001`.
- KPI engine can fetch `FH-CERT-2024-001`.
- KPI engine can fetch `FH-RTW-2024-001`.
- Missing active rules return a clear error.
- No policy-dependent KPI uses hardcoded policy values.

---

## Chunk 6: Build KPI Calculation Service

### Task

Create or update a central KPI calculation service.

### Required Methods

```text
calculateKpi(kpiId, filters)
calculateDataCompletenessScore(filters)
calculateExpiredCertificateRate(filters)
calculateFacilityAccreditationCompliance(filters)
calculateFoodHandlerCertificationRate(filters)
calculateQrVerificationFailureRate(filters)
calculateReturnToWorkClearanceRate(filters)
recalculateAutomaticKpis()
getKpiSourceRecords(kpiId, filters)
```

### Acceptance Criteria

- Automatic KPIs can be calculated.
- Hybrid KPIs can be calculated.
- Manual KPIs are not auto-calculated.
- Latest value is saved.
- Last calculated timestamp is saved.
- Calculation logs are created.

---

## Chunk 7: Implement Data Completeness Score Calculation

### Task

Calculate data completeness from required system fields.

### Formula

```text
Data Completeness Score = (Completed Required Fields / Total Required Fields) × 100
```

### Acceptance Criteria

- Required fields are counted correctly.
- Missing fields are counted correctly.
- Calculation can be filtered by state, LGA, facility, date range, and food handler category.
- Latest value updates after recalculation.

---

## Chunk 8: Implement Expired Certificate Rate Calculation

### Task

Calculate expired certificate rate from certificate records.

### Formula

```text
Expired Certificate Rate = (Number of expired certificates / Total issued certificates) × 100
```

### Acceptance Criteria

- Total issued certificates are counted correctly.
- Expired certificates are counted correctly.
- Expiry uses certificate expiry date.
- Certificate validity is based on active policy rule `certificate_validity_months = 6`.
- Revoked/cancelled certificates are handled according to existing system status rules.

---

## Chunk 9: Implement Facility Accreditation Compliance Calculation

### Task

Calculate facility accreditation compliance.

### Formula

```text
Facility Accreditation Compliance = (Number of approved facilities with valid accreditation / Total registered medical facilities) × 100
```

### Acceptance Criteria

- Total registered medical facilities are counted correctly.
- Approved/accredited facilities are counted correctly.
- Expired accreditation is excluded from compliant count.
- Facility must be mapped to a state/FCT to count as compliant.
- Reaccreditation interval is read from `FH-FAC-2024-001` as 12 months.

---

## Chunk 10: Implement Food Handler Certification Rate Calculation

### Task

Calculate certification rate from food handler and certificate records.

### Formula

```text
Food Handler Certification Rate = (Number of food handlers with valid certificates / Total registered food handlers) × 100
```

### Acceptance Criteria

- Total registered food handlers are counted correctly.
- Food handlers with valid certificates are counted correctly.
- Expired/revoked certificates are excluded.
- Certificate validity is read from `FH-VALIDITY-2024-001`.
- Certificate validity is 6 months.

---

## Chunk 11: Implement QR Verification Failure Rate Calculation

### Task

Calculate QR verification failure rate from QR verification logs.

### Formula

```text
QR Verification Failure Rate = (Failed QR verification attempts / Total QR verification attempts) × 100
```

### Acceptance Criteria

- Total QR verification attempts are counted correctly.
- Failed attempts are counted correctly.
- Failure reasons are stored and displayed.
- Failure rate supports filtering by date range, state, facility, and verifier type.
- QR policy rules are read from `FH-CERT-2024-001`.

---

## Chunk 12: Implement Return-to-Work Clearance Rate Calculation

### Task

Calculate return-to-work clearance rate from illness/exclusion/clearance records.

### Formula

```text
Return-to-Work Clearance Rate = (Number of excluded food handlers cleared to return to work / Total excluded food handlers requiring clearance) × 100
```

### Acceptance Criteria

- Total excluded handlers requiring clearance are counted correctly.
- Cleared handlers are counted correctly.
- Clearance status must be approved to count.
- Return-to-work rules are read from `FH-RTW-2024-001`.
- If offline clearances exist, KPI remains hybrid and supports override with reason.

---

## Chunk 13: Add Calculation Log Support

### Task

Create or update KPI calculation logs.

### Suggested Fields

```text
id
kpi_id
reporting_period
calculated_value
numerator_value
denominator_value
filters_used
policy_version_id
policy_standard_id
calculated_by
calculated_at
calculation_status
error_message
```

### Acceptance Criteria

- Every recalculation creates a log.
- Failed calculations create logs with error message.
- Logs are viewable from KPI detail or calculation view.
- Logs include policy version/standard used.

---

## Chunk 14: Implement View Calculation UI

### Task

Add `View Calculation` for automatic and hybrid KPIs.

### Acceptance Criteria

- Shows formula.
- Shows numerator definition.
- Shows denominator definition.
- Shows linked policy standard.
- Shows policy rule parameter used.
- Shows last calculation timestamp.
- Shows latest calculated value.

---

## Chunk 15: Implement View Source Records UI

### Task

Add `View Source Records` for automatic and hybrid KPIs.

### Acceptance Criteria

- Source records are shown in a table/modal/page.
- Records are scoped by user permissions.
- Records support filtering.
- Records support pagination.
- Data shown matches the records used in calculation.

---

## Chunk 16: Update KPI List Actions

### Task

Make KPI action buttons conditional based on input mode.

### Acceptance Criteria

- Automatic KPIs show Edit KPI, View Calculation, View Source Records, Recalculate.
- Automatic KPIs do not show Enter Data or Import.
- Manual KPIs show Enter Data.
- Imported KPIs show Import.
- Hybrid KPIs show Override Value.
- Action visibility respects permissions.

---

## Chunk 17: Implement Recalculate Action

### Task

Add recalculation action for automatic and hybrid KPIs.

### Acceptance Criteria

- Recalculate triggers backend calculation.
- Latest value updates.
- Last calculated timestamp updates.
- Calculation log is created.
- UI displays success or error message.
- Missing policy rules return clear error.

---

## Chunk 18: Implement Hybrid Override Workflow

### Task

Allow authorized overrides for hybrid KPIs.

### Acceptance Criteria

- Override requires reason.
- Original calculated value is preserved.
- Overridden value is stored.
- Override user and timestamp are stored.
- Audit log is created.
- Unauthorized users cannot override.

---

## Chunk 19: Enforce Permissions and Scoping

### Task

Enforce role-based permissions for KPI calculation, source records, manual entry, and overrides.

### Acceptance Criteria

- Federal Admin has full KPI management access.
- Federal M&E Officer can recalculate and view source records.
- State Admin can only see state-scoped data.
- Medical Facility Admin can only see facility-scoped data, where enabled.
- KPI Admin can configure KPI calculation rules and policy links.

---

## Chunk 20: Testing

### Task

Write backend, frontend, and integration tests.

### Required Tests

```text
- KPI input modes validate correctly.
- Automatic KPIs do not show Enter Data.
- Manual KPIs still show Enter Data.
- Imported KPIs show Import.
- Hybrid KPIs show Override Value.
- Data Completeness Score calculates correctly.
- Expired Certificate Rate calculates correctly.
- Facility Accreditation Compliance calculates correctly.
- Food Handler Certification Rate calculates correctly.
- QR Verification Failure Rate calculates correctly.
- Return-to-Work Clearance Rate calculates correctly.
- Certificate validity is read from active policy standard.
- Facility reaccreditation interval is read from active policy standard.
- Missing policy rule returns clear error.
- Recalculate updates latest value and timestamp.
- Calculation log is created.
- Hybrid override requires reason.
- Source records are permission-scoped.
```

---

# 13. Acceptance Criteria

The implementation is complete when:

1. The KPI engine supports Automatic, Manual, Imported, and Hybrid input modes.
2. Existing Food Handlers operational KPIs are updated from Manual to Automatic/Hybrid as appropriate.
3. Automatic KPIs no longer show Enter Data or Import actions.
4. Automatic KPIs show View Calculation, View Source Records, and Recalculate.
5. Expired Certificate Rate calculates from certificate records.
6. Food Handler Certification Rate calculates from food handler and certificate records.
7. Facility Accreditation Compliance calculates from facility accreditation records.
8. QR Verification Failure Rate calculates from QR verification logs.
9. Data Completeness Score calculates from required system fields.
10. Return-to-Work Clearance Rate calculates from illness and clearance records where available.
11. Certificate validity is read from active policy standard `FH-VALIDITY-2024-001` and is 6 months.
12. Facility reaccreditation interval is read from active policy standard `FH-FAC-2024-001` and is 12 months.
13. QR verification rules are read from active policy standard `FH-CERT-2024-001`.
14. Return-to-work rules are read from active policy standard `FH-RTW-2024-001`.
15. Recalculate updates `latest_value` and `last_calculated_at`.
16. Source records can be viewed for automatic KPIs.
17. Hybrid KPI override requires a reason and creates an audit log.
18. Manual entry remains available only for Manual or Hybrid KPIs where allowed.
19. Permissions are enforced based on user role.
20. Tests cover the calculation logic and UI action visibility.

---

# 14. Important Implementation Notes

```text
Do not hardcode Food Handlers policy values directly into KPI calculation code.

Always fetch policy-dependent values from the active Policy Version tool.

Do not remove manual KPI support entirely. Manual KPIs are still needed for indicators where system data does not exist.

Do not remove import support entirely. Imported KPIs are still needed for legacy/offline data.

The goal is to make system-derived Food Handlers KPIs automatic by default, while preserving manual/imported/hybrid options for exceptional cases.
```
