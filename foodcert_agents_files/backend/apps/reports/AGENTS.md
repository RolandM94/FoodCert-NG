# reports/AGENTS.md — Dashboards, Reporting, and Analytics Instructions

## Scope

This app manages:
- Employer dashboards
- Medical facility dashboards
- State Ministry dashboards
- Federal Ministry dashboards
- M&E reports
- Compliance reports
- Exports

## Reporting Principles

- Reports should respect role and organization permissions.
- Employers see only their own compliance records.
- Medical facilities see only their own assessment and settlement data.
- State Ministries see only their state data.
- Federal Ministry sees national and aggregate data.
- Public users do not access dashboards.

## Employer Dashboard Metrics

Show:
- Total food handlers
- Certified food handlers
- Uncertified food handlers
- Expired certificates
- Expiring certificates
- Temporarily not fit
- Excluded from food handling
- Vaccination due
- Overall compliance percentage

Do not show:
- Lab result details
- Diagnosis
- Doctor notes
- Declaration answers

## Facility Dashboard Metrics

Show:
- Assessments paid for
- Assessments completed
- Certificates issued
- Not-fit reports
- Pending lab results
- Pending doctor review
- Average turnaround time
- Accreditation status
- Re-accreditation countdown
- Pending settlements
- Settled amount

## State Dashboard Metrics

Show:
- Total registered food handlers
- Total certified food handlers
- Food businesses registered
- Approved facilities
- Facilities due for re-accreditation
- Certificates issued this month
- Expired certificates
- Illness reports
- Compliance by LGA
- Compliance by establishment type
- Vaccination coverage
- Inspection outcomes

## Federal Dashboard Metrics

Show:
- National certification coverage
- Compliance by state
- Approved facilities by state
- Food handler categories
- Establishment categories
- Vaccination coverage nationally
- Illness trends
- Certificate issuance trends
- Inspection trends
- State report submission status

## Export Rules

Support:
- CSV
- Excel
- PDF summary reports

Do not export sensitive medical details unless user role is authorized.

## Performance Rules

- Use database aggregation for dashboard metrics.
- Avoid loading all rows into memory.
- Cache expensive national dashboard queries where appropriate.
- Use background jobs for large report generation.

## Do Not Do

- Do not leak cross-state data to State Ministry users.
- Do not leak medical details into employer reports.
- Do not expose individual medical details in national aggregate dashboards unless authorized.
