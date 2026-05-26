# PRD: Reports, Dashboards & M&E Module — FoodCert NG

## 1. Module Name

**Reports, Dashboards & M&E Module**

## 2. Product Context

The Reports, Dashboards & Monitoring & Evaluation (M&E) Module is the intelligence, accountability, and performance management layer of **FoodCert NG**. It consolidates operational data from food handlers, employers, medical facilities, assessments, certificates, payments, inspections, illness reports, and enforcement workflows into structured dashboards, reports, exports, and M&E indicators.

This module supports different stakeholder needs:

- **Food Handlers** need visibility into their own certification, renewal, vaccination, and assessment status.
- **Employers/FBOs** need compliance monitoring across staff, branches, certificates, vaccinations, inspections, and notices.
- **Medical Facilities** need assessment, appointment, lab, doctor decision, certificate submission, and settlement performance reports.
- **State Ministries of Health** need implementation, certification, accreditation, inspection, enforcement, revenue, illness, and compliance reports.
- **Federal Ministry of Health and Social Welfare** needs national oversight, state comparison, M&E monitoring, national compliance analytics, policy reports, and data quality oversight.
- **Platform/Super Admins** need system-wide operational, technical, financial, and adoption reports.

The module must enforce privacy. Dashboards and reports must show only the fields permitted for each role. Sensitive medical data must not be exposed to employers, public users, finance users, inspectors, or federal aggregate users unless explicit permission is granted.

---

# 3. Product Goal

To provide accurate, role-based, privacy-safe, exportable, and actionable reporting and analytics that help every FoodCert NG stakeholder monitor compliance, improve public health outcomes, manage operations, and support policy decisions.

---

# 4. Core Objectives

The Reports, Dashboards & M&E Module must:

1. Provide dashboards for each user category.
2. Provide state-level and national-level M&E indicators.
3. Provide compliance analytics for food handlers, employers, facilities, states, and sectors.
4. Provide operational reports for appointments, assessments, certificates, payments, settlements, inspections, and enforcement.
5. Provide public health indicators for illness, exclusion, return-to-work, and vaccination coverage.
6. Provide state reporting submission workflow to Federal Ministry.
7. Provide federal national reporting and state comparison.
8. Provide exportable reports in PDF, Excel, and CSV.
9. Provide role-safe report serializers that protect sensitive medical data.
10. Provide scheduled reports and automated report generation.
11. Provide data quality monitoring and anomaly detection.
12. Provide audit logs for report generation, export, and sensitive report access.
13. Provide dashboard filters and drill-downs.
14. Provide M&E indicator configuration.
15. Provide a shared analytics layer for all modules.

---

# 5. Key Actors

## 5.1 Food Handler

Can:

- View personal certification dashboard.
- View current certificate status.
- View assessment status.
- View vaccination due/valid/expired status.
- View renewal reminders.
- Download own certificate/report where permitted.

Cannot:

- View employer-wide reports.
- View other food handlers.
- View facility performance analytics.
- View state/federal reports.

## 5.2 Employer Admin / Compliance Officer

Can:

- View organization compliance dashboard.
- View branch compliance dashboards.
- View food handler certificate status.
- View vaccination compliance status.
- View inspection notices and corrective action status.
- Export employer-safe compliance reports.
- View subscription status summary.

Cannot:

- View lab results.
- View diagnosis.
- View doctor notes.
- View declaration answers.
- View full NIN.
- View other employers’ records.

## 5.3 Branch Manager

Can:

- View branch-specific compliance reports.
- View linked food handlers for assigned branch.
- View certificate and vaccination operational statuses.
- View inspection notices for assigned branch.

Cannot:

- View other branches unless permitted.
- View medical details.
- View finance reports unless assigned.

## 5.4 Medical Facility Admin

Can:

- View facility operational dashboard.
- View appointments and assessment volume.
- View lab turnaround reports.
- View doctor decision reports.
- View certificate submission outcomes.
- View settlement summaries.
- Export facility reports.

Cannot:

- View other facilities.
- View employer subscription reports.
- View state-wide regulatory reports unless permitted.

## 5.5 Doctor

Can:

- View assigned assessment workload.
- View decision history for assigned assessments.
- View lab result review pending reports.
- View return-to-work pending tasks.

Cannot:

- View facility finance reports unless authorized.
- View unrelated doctors’ cases unless facility policy permits.

## 5.6 Lab Staff

Can:

- View lab request dashboard.
- View pending sample collection.
- View pending result upload.
- View lab turnaround time for assigned lab/unit.

Cannot:

- View doctor notes.
- View final certificate registry unless permitted.
- View finance or employer compliance reports.

## 5.7 Inspector / Environmental Health Officer

Can:

- View inspection task dashboard.
- View assigned inspections.
- View certificate verification reports for inspections.
- View enforcement notice status.
- View inspector-safe compliance reports.

Cannot:

- View lab results.
- View diagnosis.
- View doctor notes.
- View declaration answers.
- View payment/settlement details.

## 5.8 State Ministry Users

Can:

- View state implementation dashboard.
- View certificate issuance reports.
- View facility accreditation reports.
- View employer compliance reports.
- View inspection/enforcement reports.
- View illness and return-to-work trends.
- View vaccination coverage.
- View revenue and settlement summary where permitted.
- Generate and submit state reports to Federal Ministry.

Access must be state-scoped and role-scoped.

## 5.9 Federal Ministry Users

Can:

- View national dashboard.
- View state comparison dashboard.
- View national M&E indicators.
- View national certificate registry summaries.
- View national facility, employer, inspection, illness, and vaccination summaries.
- Review state reports.
- Generate national reports.

Federal dashboards should be aggregate by default.

## 5.10 Platform / Super Admin

Can:

- View system-wide adoption and operational dashboards.
- Monitor technical performance.
- Monitor failed jobs/report generation.
- Configure report templates.
- Configure global M&E indicator definitions.
- Manage scheduled reports.

---

# 6. Module Scope

## 6.1 In Scope

The module includes:

- Role-based dashboards
- Food handler dashboard
- Employer dashboard
- Branch dashboard
- Medical facility dashboard
- Doctor dashboard
- Lab dashboard
- Inspector dashboard
- State Ministry dashboard
- Federal Ministry dashboard
- Platform admin dashboard
- M&E indicator framework
- Report builder
- Report template management
- Scheduled reports
- Report exports
- Report submission workflow
- Data quality dashboard
- KPI cards and charts
- Drill-down analytics
- Filters and saved views
- Privacy-safe serializers
- Audit logs
- Analytics aggregation jobs

## 6.2 Out of Scope for MVP

The following may be deferred:

- Advanced BI drag-and-drop custom dashboard builder
- Predictive analytics
- AI-generated policy recommendations
- GIS heatmap analytics beyond simple state/LGA filters
- Public open data portal
- Third-party BI embedding
- Advanced statistical modelling
- Real-time streaming analytics
- Data warehouse separate from application database

---

# 7. Reporting Principles

## 7.1 Single Source of Truth

Dashboards and reports must not calculate core compliance logic independently in the frontend. Backend services should calculate shared metrics.

Recommended shared services:

```txt
ComplianceStatusService
CertificateAnalyticsService
AssessmentAnalyticsService
FacilityAnalyticsService
EmployerAnalyticsService
InspectionAnalyticsService
PaymentAnalyticsService
MEIndicatorService
ReportGenerationService
DataQualityService
```

## 7.2 Role-Safe Reporting

Every report must use serializers appropriate to the viewer’s role.

Example serializers:

```txt
FoodHandlerReportSerializer
EmployerSafeComplianceSerializer
FacilityOperationalReportSerializer
StateRegulatoryReportSerializer
FederalAggregateReportSerializer
FinanceReportSerializer
InspectorSafeReportSerializer
```

## 7.3 Drill-Down with Permission Checks

Users may drill from aggregate to detail only if they have permission.

Example:

```txt
Federal national dashboard
→ State summary
→ LGA summary
→ Facility/employer summary, if permitted
→ Individual record, only if authorized
```

## 7.4 Export Privacy

Exported files must follow the same privacy rules as screen views.

No export should accidentally include:

- Full NIN
- Lab results
- Doctor notes
- Diagnosis
- Declaration answers
- Treatment notes
- Sensitive public health notes

unless the user has explicit permission and the export is audit logged.

---

# 8. Dashboard Framework

## 8.1 Dashboard Structure

Each dashboard should support:

- KPI cards
- Charts
- Tables
- Filters
- Drill-downs
- Export buttons
- Saved views, future
- Date range selector
- Last updated timestamp
- Data quality warning, where applicable

## 8.2 Standard Dashboard Filters

Common filters:

- Date range
- State
- LGA
- Employer
- Branch
- Medical facility
- Certificate status
- Assessment status
- Vaccination status
- Inspection status
- Establishment category
- Facility type
- User role
- Report period

## 8.3 Standard Chart Types

Supported chart types:

- KPI cards
- Line chart
- Bar chart
- Stacked bar chart
- Pie/donut chart
- Table
- Matrix table
- Heatmap/map, future
- Trend cards

---

# 9. Food Handler Dashboard

## 9.1 Purpose

Give each food handler a simple personal view of their certification journey.

## 9.2 KPI Cards

Show:

- Current certificate status
- Certificate expiry date
- Days to expiry
- Assessment status
- Vaccination status
- Renewal status
- Return-to-work status, where applicable

## 9.3 Sections

- My certificate
- My assessment
- My vaccination records
- Renewal reminders
- Reports/downloads
- Illness/return-to-work status

## 9.4 Privacy

Food handler can view their own medical/report outputs where permitted by policy, but cannot view internal doctor notes unless explicitly allowed.

---

# 10. Employer Dashboard

## 10.1 Purpose

Help employers and food business operators monitor food handler compliance across their organization and branches.

## 10.2 KPI Cards

Show:

- Total food handlers
- Certified food handlers
- Active certificates
- Expired certificates
- Certificates expiring in 30 days
- Uncertified food handlers
- Temporarily not fit
- Return-to-work pending
- Vaccination due
- Branches compliant
- Branches non-compliant
- Open inspection notices
- Corrective actions pending
- Subscription status

## 10.3 Charts

- Certificate status distribution
- Compliance trend over time
- Branch compliance comparison
- Vaccination compliance by branch
- Expiring certificates by month
- Inspection notices by status
- Corrective action completion rate

## 10.4 Tables

### Food Handler Compliance Table

Columns:

- Food handler name
- Branch
- Role/category
- Certificate status
- Expiry date
- Vaccination status
- Fitness status
- Renewal status
- Action

### Branch Compliance Table

Columns:

- Branch
- Total food handlers
- Active certificates
- Expired certificates
- Vaccination due
- Inspection notices
- Compliance score

## 10.5 Reports

Employer can generate:

- Organization compliance report
- Branch compliance report
- Certificate expiry report
- Vaccination due report
- Inspection notice report
- Corrective action report
- Subscription/billing summary, if permitted

## 10.6 Privacy

Employer reports must not include:

- Lab results
- Diagnosis
- Doctor notes
- Health declaration answers
- Full NIN

---

# 11. Medical Facility Dashboard

## 11.1 Purpose

Help facilities monitor operational performance, assessment throughput, lab workflows, certificate submission outcomes, and settlement status.

## 11.2 KPI Cards

Show:

- Accreditation status
- Re-accreditation due date
- Appointments today
- Pending appointments
- Assessments in progress
- Lab requests pending
- Lab results pending review
- Doctor decisions pending
- Submitted to State
- Certificates issued
- State clarification requests
- Settlement pending
- Settlement paid

## 11.3 Charts

- Assessment volume over time
- Appointment status distribution
- Lab turnaround time
- Doctor decision distribution
- Certificate approval rate
- Clarification request trend
- Settlement trend
- Department workload

## 11.4 Tables

- Appointment report table
- Assessment queue table
- Lab requests table
- Doctor decision table
- State submission table
- Settlement table

## 11.5 Facility Reports

- Assessment volume report
- Appointment report
- Lab turnaround report
- Doctor decision report
- Certificate submission report
- Clarification request report
- Department workload report
- Settlement report
- Re-accreditation readiness report

---

# 12. Doctor Dashboard

## 12.1 Purpose

Give doctors a focused workflow dashboard for assigned assessments.

## 12.2 KPI Cards

Show:

- Assigned assessments
- Declaration reviews pending
- Physical exams pending
- Lab results pending review
- Vaccination reviews pending
- Decisions pending
- Temporarily not-fit cases
- Return-to-work reviews pending

## 12.3 Reports

- Doctor workload report
- Doctor decision report
- Lab review pending report
- Return-to-work review report

---

# 13. Lab Dashboard

## 13.1 Purpose

Help lab staff manage lab requests and turnaround time.

## 13.2 KPI Cards

Show:

- Lab requests pending
- Samples pending collection
- Results pending upload
- Results submitted today
- Repeat tests required
- Average turnaround time

## 13.3 Reports

- Lab request report
- Lab result report
- Turnaround time report
- Repeat test report

---

# 14. Inspector and Enforcement Dashboard

## 14.1 Purpose

Support field inspection monitoring and enforcement tracking.

## 14.2 Inspector KPI Cards

Show:

- Assigned inspections
- Due today
- Overdue inspections
- In-progress inspections
- Submitted inspections
- Notices issued
- Corrective actions pending
- Follow-ups due

## 14.3 State Enforcement Dashboard Cards

Show:

- Total inspections
- Inspections by LGA
- Open enforcement cases
- Notices issued
- Overdue corrective actions
- Critical findings
- Suspicious certificates flagged
- Follow-up inspections pending
- Employer compliance rate

## 14.4 Reports

- Inspection summary report
- Certificate verification report
- Enforcement notice report
- Corrective action report
- Critical findings report
- Inspector performance report
- Suspicious certificate report

---

# 15. State Ministry Dashboard

## 15.1 Purpose

Provide the State Ministry of Health with a complete state-level implementation dashboard.

## 15.2 KPI Cards

Show:

- Total registered food handlers
- Certified food handlers
- Active certificates
- Expired certificates
- Certificates issued this month
- Certificates expiring soon
- Registered employers
- Registered branches
- Approved medical facilities
- Facilities pending accreditation
- Facilities due for re-accreditation
- Suspended facilities
- Assessments completed
- Pending State validations
- Inspections conducted
- Notices issued
- Illness reports
- Return-to-work pending
- Vaccination compliance rate
- State compliance percentage
- State revenue summary, permission-based

## 15.3 Charts

- Certification trend over time
- Compliance by LGA
- Certificate status distribution
- Facility accreditation status
- Employer compliance by establishment category
- Inspection outcomes by LGA
- Vaccination coverage trend
- Illness report trend
- Assessment volume by facility
- Revenue trend, permission-based

## 15.4 State Reports

State users can generate:

- State implementation report
- Food handler certification report
- Certificate registry report
- Employer compliance report
- Branch compliance report
- Medical facility accreditation report
- Assessment volume report
- Inspection/enforcement report
- Illness and return-to-work report
- Vaccination coverage report
- State revenue and settlement report
- Data quality report
- Monthly state report to Federal Ministry

---

# 16. Federal Ministry Dashboard

## 16.1 Purpose

Provide the Federal Ministry of Health and Social Welfare with national oversight across all 36 States and the FCT.

## 16.2 KPI Cards

Show:

- Total registered food handlers nationally
- Certified food handlers nationally
- National certification coverage rate
- Active certificates nationally
- Expired certificates nationally
- Certificates issued this month
- Registered employers nationally
- Registered branches nationally
- Approved facilities nationally
- States with active implementation
- States with overdue reports
- National vaccination coverage
- National inspection count
- National illness reports
- National return-to-work pending
- National compliance rate

## 16.3 State Performance Table

Columns:

- State
- Registered food handlers
- Certified food handlers
- Certification coverage
- Approved facilities
- Pending facility applications
- Certificates issued
- Expired certificates
- Registered employers
- Inspections conducted
- Notices issued
- Illness reports
- Vaccination coverage
- Last report submitted
- Report status
- Overall performance rating

## 16.4 Federal Charts

- Certification coverage by state
- Certificate issuance trend
- Facility accreditation by state
- Employer compliance by state
- Vaccination coverage by state
- Inspection activity by state
- Illness trends by state
- State report submission status
- Data quality score by state

## 16.5 Federal Reports

Federal users can generate:

- National implementation report
- State comparison report
- National certificate registry summary
- Facility accreditation report
- Employer compliance report
- National vaccination coverage report
- National inspection/enforcement report
- National illness and return-to-work report
- State report submission report
- Data quality report
- Policy compliance report
- National M&E report

---

# 17. Platform Admin Dashboard

## 17.1 Purpose

Help super admins monitor platform health, adoption, and operations.

## 17.2 KPI Cards

Show:

- Total users
- Active organizations
- Active employers
- Active facilities
- Active State Ministry accounts
- Active Federal users
- API errors
- Failed payments
- Failed certificate generation
- Failed report jobs
- Background job health
- Storage usage
- Notification delivery status

## 17.3 Reports

- Platform adoption report
- System usage report
- Failed job report
- Notification delivery report
- Data quality report
- Audit activity report

---

# 18. M&E Framework

## 18.1 Purpose

The M&E framework tracks implementation, output, outcome, compliance, and public health indicators.

## 18.2 Indicator Categories

### A. Registration and Coverage Indicators

- Number of registered food handlers
- Number of registered employers
- Number of registered branches
- Number of registered medical facilities
- Number of approved medical facilities
- Number of active states/FCT implementing

### B. Certification Indicators

- Number of certificates issued
- Number of active certificates
- Number of expired certificates
- Number of suspended certificates
- Number of revoked certificates
- Certification coverage rate
- Certificate renewal rate
- Average certificate issuance time
- Average State validation time

### C. Medical Assessment Indicators

- Number of assessments initiated
- Number of assessments completed
- Number of fit decisions
- Number of temporarily not-fit decisions
- Number of not-fit decisions
- Average assessment completion time
- Lab test completion rate
- Lab turnaround time
- Clarification request rate

### D. Vaccination Indicators

- Typhoid vaccination coverage
- Hepatitis A dose 1 coverage
- Hepatitis A dose 2 completion rate
- Vaccination expired rate
- Vaccination due rate

### E. Facility Indicators

- Approved facilities by state
- Facilities due for re-accreditation
- Suspended facilities
- Facility assessment volume
- Facility average turnaround time
- Facility clarification rate

### F. Employer Compliance Indicators

- Employer compliance rate
- Branch compliance rate
- Food handlers with valid certificates
- Food handlers with expired certificates
- Food handlers with vaccination due
- Branches with open inspection notices

### G. Inspection and Enforcement Indicators

- Number of inspections conducted
- Inspection coverage rate
- Number of notices issued
- Corrective action completion rate
- Overdue corrective actions
- Critical findings rate
- Suspicious certificates detected
- Follow-up inspection completion rate

### H. Illness and Return-to-Work Indicators

- Number of illness reports
- Number of temporary exclusions
- Return-to-work clearances issued
- Return-to-work pending cases
- Illness cluster flags
- Average exclusion duration

### I. Finance Indicators

Access controlled.

- Assessment payment volume
- Assessment revenue
- Facility settlement amount
- State fee amount
- Platform fee amount
- Employer subscription revenue
- Failed payment rate
- Refund volume

### J. Data Quality Indicators

- Duplicate NIN flags
- Duplicate certificate flags
- Missing profile data
- Missing vaccination records
- Expired facility conducting assessments
- Incomplete assessment records
- Unusual certificate issuance patterns
- Failed verification attempts

## 18.3 Indicator Metadata

Each indicator should have:

- Indicator code
- Indicator name
- Description
- Numerator
- Denominator
- Calculation formula
- Data source
- Reporting frequency
- Responsible role
- Disaggregation fields
- Target value, optional
- Thresholds
- Visualization type
- Privacy level

---

# 19. M&E Indicator Examples

## 19.1 Certification Coverage Rate

```txt
Indicator: Certification Coverage Rate
Formula: Certified food handlers / Registered food handlers * 100
Disaggregation: State, LGA, employer, branch, establishment category, gender where permitted
Frequency: Daily/monthly
Privacy: Aggregate
```

## 19.2 State Report Submission Rate

```txt
Indicator: State Report Submission Rate
Formula: Reports submitted on time / Expected reports * 100
Disaggregation: State, report type, period
Frequency: Monthly
Privacy: State/Federal
```

## 19.3 Facility Re-Accreditation Compliance

```txt
Indicator: Facility Re-Accreditation Compliance
Formula: Facilities with active accreditation / Total approved facilities * 100
Disaggregation: State, LGA, facility type
Frequency: Monthly
Privacy: State/Federal
```

## 19.4 Employer Compliance Rate

```txt
Indicator: Employer Compliance Rate
Formula: Food handlers with active certificates / Total linked food handlers * 100
Disaggregation: Employer, branch, state, LGA, establishment category
Frequency: Daily/monthly
Privacy: Employer/State/Federal aggregate
```

---

# 20. Report Builder

## 20.1 Purpose

Authorized users should be able to generate structured reports from approved templates.

## 20.2 Report Builder Features

- Select report type
- Select period
- Apply filters
- Preview report
- Generate report
- Export report
- Schedule report
- Submit report, where applicable
- Archive report

## 20.3 Report Parameters

Common parameters:

- Report type
- Start date
- End date
- State
- LGA
- Employer
- Branch
- Facility
- Status
- Establishment category
- Output format

## 20.4 Report Output Formats

- PDF
- Excel
- CSV
- JSON, internal/API only

## 20.5 Report Statuses

- Draft
- Generating
- Generated
- Failed
- Submitted
- Returned for Correction
- Accepted
- Archived

---

# 21. State-to-Federal Reporting Workflow

## 21.1 Purpose

State Ministries must submit periodic implementation reports to the Federal Ministry.

## 21.2 Workflow

```txt
State user selects report type
→ Applies reporting period
→ Generates report
→ Reviews report
→ Submits to Federal Ministry
→ Federal user reviews
→ Federal accepts or returns for correction
→ State corrects and resubmits if required
```

## 21.3 State Report Types

- Monthly implementation report
- Facility accreditation report
- Certificate issuance report
- Employer compliance report
- Inspection/enforcement report
- Illness and return-to-work report
- Vaccination coverage report
- Revenue summary, permission-based
- Data quality report

## 21.4 Federal Review Actions

- Accept report
- Return for correction
- Add review comment
- Escalate overdue report
- Download report
- Compare with live dashboard

---

# 22. Scheduled Reports

## 22.1 Purpose

Allow authorized users to schedule recurring reports.

## 22.2 Schedule Options

- Daily
- Weekly
- Monthly
- Quarterly
- Custom date range

## 22.3 Delivery Channels

- In-app notification
- Email
- Secure download link

## 22.4 Scheduled Report Rules

- Reports must be generated using the viewer’s permissions.
- Report links should expire.
- Sensitive reports should require login.
- Generation failures should notify report owner.

---

# 23. Data Quality Dashboard

## 23.1 Purpose

Identify missing, inconsistent, duplicate, or suspicious data.

## 23.2 Data Quality Checks

- Duplicate NINs
- Duplicate food handler profiles
- Duplicate certificates
- Missing passport photo
- Missing employer branch assignment
- Missing vaccination records
- Expired facility conducting assessment
- Certificate generated without complete assessment
- Assessment without payment where payment is required
- Lab result pending beyond threshold
- State validation pending beyond threshold
- Suspicious certificate verification patterns
- Facilities with unusually high certificate volume
- Employers with high expired certificate burden

## 23.3 Data Quality Severity

- Low
- Medium
- High
- Critical

## 23.4 Data Quality Actions

- View issue
- Assign issue
- Mark resolved
- Add note
- Export issue list
- Escalate issue

---

# 24. Analytics Aggregation

## 24.1 Purpose

Improve dashboard performance by precomputing commonly used metrics.

## 24.2 Aggregation Levels

- Daily
- Weekly
- Monthly
- State
- LGA
- Employer
- Branch
- Facility
- Certificate status
- Assessment status
- Inspection status

## 24.3 Aggregated Metric Examples

- Daily certificates issued by state
- Monthly employer compliance by state
- Facility assessment volume by month
- Inspection findings by severity
- Vaccination coverage by LGA
- Illness reports by state

## 24.4 Aggregation Rules

- Aggregates should refresh on schedule.
- Critical dashboard cards may calculate live if needed.
- Aggregates must be recalculated if source data changes materially.
- Aggregation jobs must be monitored.

---

# 25. Data Sources

The module depends on the following source modules:

```txt
FoodHandlerProfile
Employer
OrganizationUnit / Branch
MedicalFacility
FacilityAccreditationApplication
MedicalAssessment
HealthDeclaration
PhysicalExamination
LabTest
VaccinationReview
FitnessDecision
Certificate
CertificateVerificationLog
PaymentTransaction
EmployerSubscription
Settlement
Inspection
InspectionFinding
EnforcementNotice
CorrectiveActionResponse
IllnessReport
ReturnToWorkCase
StateReport
AuditLog
```

---

# 26. Data Model Requirements

## 26.1 ReportTemplate

```python
class ReportTemplate(models.Model):
    id = models.UUIDField(primary_key=True)
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    module = models.CharField(max_length=100)
    scope = models.CharField(max_length=50)  # food_handler, employer, facility, state, federal, admin
    output_formats = models.JSONField(default=list)
    default_filters = models.JSONField(default=dict)
    required_permissions = models.JSONField(default=list)
    privacy_level = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey("accounts.User", null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 26.2 GeneratedReport

```python
class GeneratedReport(models.Model):
    id = models.UUIDField(primary_key=True)
    report_template = models.ForeignKey("reports.ReportTemplate", on_delete=models.PROTECT)
    title = models.CharField(max_length=255)
    generated_by = models.ForeignKey("accounts.User", null=True, on_delete=models.SET_NULL)
    organization = models.ForeignKey("organizations.Organization", null=True, blank=True, on_delete=models.SET_NULL)
    state = models.ForeignKey("geography.State", null=True, blank=True, on_delete=models.SET_NULL)
    reporting_period_start = models.DateField(null=True, blank=True)
    reporting_period_end = models.DateField(null=True, blank=True)
    filters = models.JSONField(default=dict)
    status = models.CharField(max_length=50)
    output_format = models.CharField(max_length=20)
    file_url = models.URLField(blank=True)
    data_snapshot = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    submitted_to_federal_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey("accounts.User", null=True, blank=True, related_name="reviewed_generated_reports", on_delete=models.SET_NULL)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_status = models.CharField(max_length=50, blank=True)
    review_comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 26.3 MEIndicator

```python
class MEIndicator(models.Model):
    id = models.UUIDField(primary_key=True)
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100)
    numerator_definition = models.TextField(blank=True)
    denominator_definition = models.TextField(blank=True)
    formula = models.TextField()
    data_sources = models.JSONField(default=list)
    reporting_frequency = models.CharField(max_length=50)
    disaggregation_fields = models.JSONField(default=list)
    target_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    warning_threshold = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    critical_threshold = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    visualization_type = models.CharField(max_length=50)
    privacy_level = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 26.4 MEIndicatorValue

```python
class MEIndicatorValue(models.Model):
    id = models.UUIDField(primary_key=True)
    indicator = models.ForeignKey("reports.MEIndicator", on_delete=models.CASCADE)
    state = models.ForeignKey("geography.State", null=True, blank=True, on_delete=models.SET_NULL)
    lga = models.ForeignKey("geography.LGA", null=True, blank=True, on_delete=models.SET_NULL)
    organization = models.ForeignKey("organizations.Organization", null=True, blank=True, on_delete=models.SET_NULL)
    period_start = models.DateField()
    period_end = models.DateField()
    numerator_value = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    denominator_value = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    calculated_value = models.DecimalField(max_digits=18, decimal_places=4)
    disaggregation = models.JSONField(default=dict)
    calculated_at = models.DateTimeField(auto_now_add=True)
```

## 26.5 DashboardWidget

```python
class DashboardWidget(models.Model):
    id = models.UUIDField(primary_key=True)
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    dashboard_scope = models.CharField(max_length=50)
    widget_type = models.CharField(max_length=50)
    metric_code = models.CharField(max_length=100, blank=True)
    configuration = models.JSONField(default=dict)
    required_permissions = models.JSONField(default=list)
    privacy_level = models.CharField(max_length=50)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 26.6 ScheduledReport

```python
class ScheduledReport(models.Model):
    id = models.UUIDField(primary_key=True)
    report_template = models.ForeignKey("reports.ReportTemplate", on_delete=models.PROTECT)
    owner = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    schedule_frequency = models.CharField(max_length=50)
    filters = models.JSONField(default=dict)
    output_format = models.CharField(max_length=20)
    delivery_channels = models.JSONField(default=list)
    recipients = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    next_run_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 26.7 DataQualityIssue

```python
class DataQualityIssue(models.Model):
    id = models.UUIDField(primary_key=True)
    issue_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=50)
    module = models.CharField(max_length=100)
    target_type = models.CharField(max_length=100)
    target_id = models.UUIDField(null=True, blank=True)
    state = models.ForeignKey("geography.State", null=True, blank=True, on_delete=models.SET_NULL)
    organization = models.ForeignKey("organizations.Organization", null=True, blank=True, on_delete=models.SET_NULL)
    description = models.TextField()
    status = models.CharField(max_length=50)
    assigned_to = models.ForeignKey("accounts.User", null=True, blank=True, on_delete=models.SET_NULL)
    resolved_by = models.ForeignKey("accounts.User", null=True, blank=True, related_name="resolved_data_quality_issues", on_delete=models.SET_NULL)
    resolved_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

---

# 27. API Requirements

## 27.1 Dashboard APIs

```txt
GET /api/dashboards/food-handler
GET /api/dashboards/employer
GET /api/dashboards/employer/branches/:branch_id
GET /api/dashboards/facility
GET /api/dashboards/doctor
GET /api/dashboards/lab
GET /api/dashboards/inspector
GET /api/dashboards/state
GET /api/dashboards/federal
GET /api/dashboards/admin
```

## 27.2 Analytics APIs

```txt
GET /api/analytics/certificates
GET /api/analytics/assessments
GET /api/analytics/vaccinations
GET /api/analytics/facilities
GET /api/analytics/employers
GET /api/analytics/inspections
GET /api/analytics/enforcement
GET /api/analytics/illness
GET /api/analytics/payments
GET /api/analytics/settlements
GET /api/analytics/data-quality
```

## 27.3 M&E APIs

```txt
GET    /api/m-and-e/indicators
POST   /api/m-and-e/indicators
GET    /api/m-and-e/indicators/:id
PATCH  /api/m-and-e/indicators/:id
GET    /api/m-and-e/indicators/:id/values
POST   /api/m-and-e/calculate
GET    /api/m-and-e/dashboard
GET    /api/m-and-e/state-performance
GET    /api/m-and-e/national-summary
```

## 27.4 Report Template APIs

```txt
GET    /api/report-templates
POST   /api/report-templates
GET    /api/report-templates/:id
PATCH  /api/report-templates/:id
DELETE /api/report-templates/:id
```

## 27.5 Report Generation APIs

```txt
GET  /api/reports
POST /api/reports/generate
GET  /api/reports/:id
GET  /api/reports/:id/download
POST /api/reports/:id/submit-to-federal
POST /api/reports/:id/archive
POST /api/reports/:id/regenerate
```

## 27.6 Federal Report Review APIs

```txt
GET  /api/federal/state-reports
GET  /api/federal/state-reports/:id
POST /api/federal/state-reports/:id/accept
POST /api/federal/state-reports/:id/return-for-correction
POST /api/federal/state-reports/:id/escalate
```

## 27.7 Scheduled Report APIs

```txt
GET    /api/scheduled-reports
POST   /api/scheduled-reports
GET    /api/scheduled-reports/:id
PATCH  /api/scheduled-reports/:id
DELETE /api/scheduled-reports/:id
POST   /api/scheduled-reports/:id/run-now
```

## 27.8 Data Quality APIs

```txt
GET   /api/data-quality/issues
GET   /api/data-quality/issues/:id
PATCH /api/data-quality/issues/:id
POST  /api/data-quality/issues/:id/assign
POST  /api/data-quality/issues/:id/resolve
POST  /api/data-quality/issues/:id/escalate
GET   /api/data-quality/dashboard
```

---

# 28. Frontend Routes

## 28.1 Shared Report Routes

```txt
/app/reports
/app/reports/generate
/app/reports/[id]
/app/reports/scheduled
/app/reports/templates
```

## 28.2 Food Handler Routes

```txt
/app/food-handler/dashboard
/app/food-handler/reports
```

## 28.3 Employer Routes

```txt
/app/employer/dashboard
/app/employer/reports
/app/employer/reports/compliance
/app/employer/reports/certificates
/app/employer/reports/vaccinations
/app/employer/reports/inspections
```

## 28.4 Facility Routes

```txt
/app/facility/dashboard
/app/facility/reports
/app/facility/reports/assessments
/app/facility/reports/lab
/app/facility/reports/doctor-decisions
/app/facility/reports/settlements
```

## 28.5 State Routes

```txt
/app/state/dashboard
/app/state/reports
/app/state/reports/generate
/app/state/reports/submissions
/app/state/m-and-e
/app/state/data-quality
/app/state/analytics/certificates
/app/state/analytics/employers
/app/state/analytics/facilities
/app/state/analytics/inspections
```

## 28.6 Federal Routes

```txt
/app/federal/dashboard
/app/federal/reports
/app/federal/state-reports
/app/federal/m-and-e
/app/federal/state-performance
/app/federal/data-quality
/app/federal/analytics/certificates
/app/federal/analytics/facilities
/app/federal/analytics/employers
/app/federal/analytics/enforcement
```

## 28.7 Admin Routes

```txt
/app/admin/dashboards
/app/admin/report-templates
/app/admin/m-and-e/indicators
/app/admin/data-quality
/app/admin/system-reports
```

---

# 29. Core Frontend Components

- DashboardLayout
- DashboardFilterBar
- DateRangePicker
- KPICard
- TrendCard
- ChartCard
- DataTableCard
- DrillDownBreadcrumb
- ExportButton
- ReportBuilder
- ReportTemplateSelector
- ReportPreview
- ReportStatusBadge
- ScheduledReportForm
- MEIndicatorCard
- MEIndicatorTable
- StatePerformanceTable
- ComplianceSummaryCard
- CertificateAnalyticsChart
- FacilityPerformanceChart
- EmployerComplianceTable
- InspectionAnalyticsChart
- DataQualityIssueTable
- DataQualitySeverityBadge
- StateReportSubmissionTable
- FederalReportReviewPanel
- PrivacyWarningBanner

---

# 30. Permissions and Access Control

## 30.1 Permission Groups

Recommended permissions:

```txt
report.view
report.generate
report.export
report.schedule
report.submit_to_federal
report.review_state_report
report.manage_templates

dashboard.view_food_handler
dashboard.view_employer
dashboard.view_facility
dashboard.view_state
dashboard.view_federal
dashboard.view_admin

m_and_e.view
m_and_e.manage_indicators
m_and_e.calculate
m_and_e.export

data_quality.view
data_quality.assign
data_quality.resolve
data_quality.escalate
```

## 30.2 Access Rules

- Food handler sees only own dashboard and reports.
- Employer sees only own organization and branches.
- Branch manager sees only assigned branch.
- Facility user sees only assigned facility.
- State user sees only assigned state unless federal/super admin.
- Federal user sees national aggregate and permitted state summaries.
- Finance reports require finance permission.
- Sensitive medical reports require medical/regulatory permission.

---

# 31. Privacy Requirements

## 31.1 Sensitive Fields

Sensitive fields include:

- Full NIN
- Lab results
- Doctor notes
- Diagnosis
- Declaration answers
- Treatment notes
- Public health clearance notes
- Medical report internals
- Payment gateway secrets
- Settlement bank details

## 31.2 Privacy Rules

- Public users cannot access reports.
- Employers cannot access medical details.
- Inspectors cannot access medical details.
- Finance users cannot access clinical details.
- Federal dashboards are aggregate by default.
- Exports must apply role-safe serializers.
- Sensitive report generation must be audit logged.
- Download links must expire where reports are sensitive.

---

# 32. Audit Logs

Create audit logs for:

- Dashboard viewed, for sensitive dashboards
- Report generated
- Report exported
- Report downloaded
- Scheduled report created/updated/deleted
- State report submitted to Federal Ministry
- Federal report accepted
- Federal report returned for correction
- M&E indicator created/updated
- Data quality issue assigned/resolved/escalated
- Sensitive report accessed
- Finance report exported
- Medical report exported
- Report generation failed

---

# 33. Background Jobs

## 33.1 Dashboard Aggregation Job

Runs hourly/daily depending on metric.

Tasks:

- Calculate dashboard aggregates.
- Refresh KPI summaries.
- Update chart datasets.

## 33.2 M&E Calculation Job

Runs daily/monthly.

Tasks:

- Calculate indicator values.
- Store indicator snapshots.
- Compare against thresholds.
- Generate alerts where needed.

## 33.3 Scheduled Report Job

Runs according to schedule.

Tasks:

- Generate scheduled reports.
- Store files.
- Notify recipients.
- Log failures.

## 33.4 Data Quality Scan Job

Runs daily.

Tasks:

- Scan for duplicate/missing/suspicious data.
- Create/update data quality issues.
- Notify responsible users.

## 33.5 State Report Reminder Job

Runs daily.

Tasks:

- Notify states of upcoming report deadlines.
- Notify states of overdue reports.
- Notify Federal users of states overdue.

---

# 34. Error Handling

## 34.1 Report Generation Errors

Possible errors:

- Missing required filters
- User lacks permission
- Data source unavailable
- Export generation failed
- Report template misconfigured
- File storage failed

Handling:

- Set report status to `Failed`.
- Save error message for authorized admins.
- Show user-friendly message.
- Allow retry.
- Audit log error.

## 34.2 Dashboard Errors

If a widget fails:

- Show fallback widget error state.
- Do not break entire dashboard.
- Log error.
- Allow retry.

---

# 35. Acceptance Criteria

## 35.1 Dashboards

- Each major role has an appropriate dashboard.
- Dashboards show role-safe data.
- Dashboards support date filtering.
- Dashboard metrics come from backend services.
- Users cannot access dashboards outside their scope.

## 35.2 Reports

- Authorized users can generate reports.
- Reports can be exported in PDF, Excel, and CSV.
- Reports respect role permissions.
- Sensitive fields are excluded unless explicitly authorized.
- Report generation is audit logged.

## 35.3 M&E

- M&E indicators can be configured.
- Indicator values can be calculated.
- Federal users can view national M&E dashboard.
- State users can view state M&E dashboard.
- Indicators support disaggregation.

## 35.4 State-to-Federal Reporting

- State users can generate periodic reports.
- State users can submit reports to Federal Ministry.
- Federal users can accept or return reports.
- Report status is tracked.
- Overdue report reminders are sent.

## 35.5 Data Quality

- Data quality issues are detected.
- Issues can be assigned and resolved.
- Data quality dashboard shows severity and trends.
- Critical issues can trigger alerts.

## 35.6 Privacy

- Employer reports do not expose medical details.
- Public users cannot access reports.
- Federal dashboards are aggregate by default.
- Sensitive report access is audit logged.

---

# 36. Shared Dependencies With Other Modules

## 36.1 Dependency Summary

The Reports, Dashboards & M&E Module depends on all major operational modules. It should not own source transactional data; it should consume and aggregate validated data from domain modules.

## 36.2 Required Module Contracts

### Food Handler Module

Must expose:

```txt
food_handler_id
full_name
state
lga
employer_id
branch_id
profile_status
certificate_status
vaccination_status
fitness_status
return_to_work_status
```

### Employer Module

Must expose:

```txt
employer_id
organization_name
establishment_category
state
lga
branch_count
subscription_status
compliance_status
```

### Medical Facility Module

Must expose:

```txt
facility_id
facility_name
facility_type
state
lga
accreditation_status
accreditation_expiry_date
assessment_volume
```

### Assessment Module

Must expose:

```txt
assessment_id
food_handler_id
facility_id
doctor_id
state
status
final_decision
created_at
completed_at
submitted_to_state_at
```

### Certificate Module

Must expose:

```txt
certificate_id
certificate_number
food_handler_id
issuing_state
facility_id
status
issue_date
expiry_date
verification_count
```

### Payments Module

Must expose finance-safe metrics:

```txt
payment_status
payment_type
amount
state_fee_amount
facility_amount
platform_amount
settlement_status
subscription_status
```

Finance data must require finance permission.

### Inspector & Enforcement Module

Must expose:

```txt
inspection_id
state
lga
employer_id
branch_id
inspection_type
status
finding_count
critical_finding_count
notice_count
corrective_action_status
```

### Illness / Return-to-Work Module

Must expose:

```txt
illness_report_id
state
lga
employer_id
branch_id
status
exclusion_status
return_to_work_status
reported_at
cleared_at
```

## 36.3 Shared Compliance Status Service

Reports module should use a shared compliance service rather than duplicating logic.

Recommended methods:

```txt
ComplianceStatusService.get_food_handler_operational_status(food_handler_id)
ComplianceStatusService.get_branch_compliance_summary(branch_id)
ComplianceStatusService.get_employer_compliance_summary(employer_id)
ComplianceStatusService.get_state_compliance_summary(state_id)
ComplianceStatusService.get_national_compliance_summary()
```

## 36.4 Shared Audit Log Contract

All modules should log using the same structure:

```txt
actor
action_type
module
target_type
target_id
organization_id
state_id
metadata
ip_address
user_agent
created_at
```

## 36.5 Shared Privacy Contract

Every analytics endpoint must declare its privacy level:

```txt
public_safe
employer_safe
inspector_safe
facility_operational
state_regulatory
federal_aggregate
finance_restricted
medical_restricted
admin_restricted
```

---

# 37. Codex Implementation Instructions

Use this prompt for Codex:

```txt
Implement the Reports, Dashboards & M&E Module for FoodCert NG.

The module must support role-based dashboards, report generation, report templates, scheduled reports, M&E indicators, M&E calculation, state-to-federal report submission, federal report review, data quality monitoring, analytics aggregation, export to PDF/Excel/CSV, privacy-safe serializers, permission enforcement, audit logging, and background jobs.

Important rules:
- Dashboards and reports must use backend services as the source of truth.
- Frontend must not independently calculate core compliance metrics.
- Reports must be role-safe and privacy-safe.
- Employers must not see lab results, diagnosis, doctor notes, declaration answers, or full NIN.
- Federal dashboards must be aggregate by default.
- Finance reports require finance permissions.
- Medical reports require medical/regulatory permissions.
- State reports must support submission to Federal Ministry.
- Federal users must be able to accept or return state reports.
- M&E indicators must support numerator, denominator, formula, disaggregation, frequency, and thresholds.
- Data quality issues must be detectable, assignable, resolvable, and exportable.
- Report generation, export, sensitive access, and M&E changes must be audit logged.

Build backend models, services, serializers, permissions, API endpoints, background jobs, tests, and frontend pages for the module.
```

---

# 38. MVP Build Order

1. ReportTemplate model
2. GeneratedReport model
3. Basic report generation service
4. PDF/Excel/CSV export service
5. Employer dashboard
6. Facility dashboard
7. State dashboard
8. Federal dashboard
9. Shared analytics service layer
10. Compliance summary service integration
11. M&E Indicator model
12. M&E calculation service
13. State performance dashboard
14. State report generation
15. State-to-Federal report submission
16. Federal report review workflow
17. Data quality issue model
18. Data quality scan job
19. Scheduled report model
20. Scheduled report job
21. Dashboard aggregation job
22. Privacy-safe serializers
23. Report permissions
24. Audit logs
25. Export privacy tests
26. Dashboard permission tests
27. M&E calculation tests
28. Data quality tests
