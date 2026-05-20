# Chunk 09 — Dashboards, Reports, and Analytics

## Goal

Implement dashboards and M&E reporting for employers, facilities, State Ministries, and the Federal Ministry.

## Employer Dashboard

Cards:
- Total food handlers
- Valid certificates
- Expired certificates
- Expiring soon
- Not certified
- Temporarily not fit
- Cleared to return
- Typhoid vaccination valid
- Typhoid vaccination expired
- Hepatitis A dose 1 completed
- Hepatitis A dose 2 pending
- Compliance percentage

Filters:
- Branch/location
- Certificate status
- Fitness category
- Food handler category
- Expiry period

Reports:
- Employer compliance report
- Expired certificate list
- Vaccination due list
- Illness/exclusion list

## Medical Facility Dashboard

Cards:
- Assessments conducted
- Certificates issued
- Not-fit reports
- Pending lab results
- Pending doctor review
- Average turnaround time
- Accreditation status
- Re-accreditation countdown
- Pending settlements
- Settled amount

Reports:
- Facility assessment report
- Lab turnaround report
- Settlement report
- Accreditation compliance report

## State Ministry Dashboard

Cards:
- Registered food handlers
- Certified food handlers
- Food businesses registered
- Approved facilities
- Suspended facilities
- Facilities due for re-accreditation
- Certificates issued this month
- Expired certificates
- Illness reports
- Inspections conducted
- Compliance by LGA
- Vaccination coverage

Reports:
- Monthly state compliance report
- Facility performance report
- Employer compliance report
- Inspection outcome report
- State revenue/fee report
- Illness trend report

## Federal Ministry Dashboard

Cards/charts:
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

Reports:
- National implementation report
- State comparison report
- National facility accreditation report
- National vaccination coverage report
- National illness trend report
- M&E report

## M&E Indicators

- Number of registered food handlers
- Number of certified food handlers
- Percentage of valid certificates
- Percentage of expired certificates
- Vaccination coverage for typhoid
- Vaccination coverage for Hepatitis A
- Number of approved facilities
- Number of facilities re-accredited
- Number of illness reports
- Number of inspections
- Employer compliance rate
- Average assessment completion time
- Average certificate issuance time

## Report Requirements

- Export PDF
- Export Excel/CSV
- Date range filters
- State/LGA filters
- Facility filters
- Employer filters
- Schedule monthly reports
- Submit state reports to federal dashboard

## API Endpoints

```txt
GET /api/dashboard/employer
GET /api/dashboard/facility
GET /api/dashboard/state
GET /api/dashboard/federal

GET /api/reports/employer-compliance
GET /api/reports/facility-performance
GET /api/reports/state-monthly
GET /api/reports/national
GET /api/reports/vaccination-coverage
GET /api/reports/illness-trends
GET /api/reports/inspection-outcomes

POST /api/reports/schedule
GET  /api/reports/generated
GET  /api/reports/generated/:id/download
```

## Acceptance Criteria

- Each role sees a relevant dashboard.
- State users see only their state.
- Federal users see national aggregates.
- Employer users see only their business.
- Medical facility users see only their facility.
- Reports can be exported.
- M&E indicators are calculated correctly.
