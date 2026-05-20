# PRD: State Ministry of Health Module & Federal Ministry of Health Module — FoodCert NG

## 1. Module Names

**A. State Ministry of Health Module**  
Used by each State Ministry of Health and the FCT Health authority to manage state-level implementation of food handler medical certification.

**B. Federal Ministry of Health Module**  
Used by the Federal Ministry of Health and Social Welfare for national oversight, policy monitoring, data aggregation, M&E, national reporting, and central certificate registry governance.

---

# 2. Product Context

FoodCert NG is a national platform for automating food handler medical fitness certification in line with the **National Guidelines for Food Handlers’ Medical Test 2024**. The guideline assigns major implementation responsibilities to State Ministries of Health, including medical facility pre-qualification, food handler certification, vaccination oversight, compliance monitoring, and enforcement. It also requires a central digitally verifiable certificate system and data-driven monitoring for policy decisions.

The Federal Ministry of Health and Social Welfare provides national-level oversight, ensuring uniform implementation across all 36 States and the FCT, maintaining national policy direction, monitoring compliance trends, supporting national analytics, and overseeing the central certificate verification infrastructure.

This PRD also incorporates the stakeholder management supplement, which requires ministries to support internal units such as Food Safety Directorates, Verification Desks, Accreditation Units, Policy and Finance Units, Inspectorates, and LGA offices.

---

# 3. High-Level Product Goal

To provide State Ministries of Health and the Federal Ministry of Health with a digital regulatory workspace for implementing, supervising, monitoring, and improving food handler medical certification across Nigeria.

The system must allow:

- State-level certificate issuance
- State-level facility accreditation
- State-level fee configuration
- State-level inspection and enforcement
- National oversight by the Federal Ministry
- National certificate registry monitoring
- Cross-state compliance analytics
- Public health reporting
- Policy and M&E dashboards

---

# 4. Governance Model

## 4.1 State Ministry Role

Each State Ministry of Health is responsible for implementation within its jurisdiction.

State Ministry responsibilities include:

1. Approving and monitoring medical facilities.
2. Mapping approved facilities to the state.
3. Setting state-approved assessment fees.
4. Validating certificate eligibility.
5. Issuing food handler fitness certificates under state authority.
6. Managing inspectors and inspection workflows.
7. Monitoring food businesses and food handlers.
8. Reviewing illness/exclusion reports.
9. Generating state reports.
10. Submitting periodic reports to the Federal Ministry.
11. Enforcing compliance within the state.

## 4.2 Federal Ministry Role

The Federal Ministry of Health and Social Welfare has national oversight.

Federal responsibilities include:

1. Monitoring implementation across all states and FCT.
2. Managing national policy configuration.
3. Overseeing the central certificate registry.
4. Monitoring state compliance and report submission.
5. Reviewing national food handler certification coverage.
6. Monitoring vaccination coverage nationally.
7. Tracking illness and foodborne disease risk trends.
8. Comparing state performance.
9. Supporting data-driven public health decisions.
10. Managing national M&E indicators.
11. Ensuring uniform digital certification standards.

---

# 5. User Roles

## 5.1 State Ministry Users

### A. State Ministry Super Admin

Usually the senior state-level platform administrator.

Can:

- Manage state users.
- Manage state units/offices.
- Approve medical facilities.
- Configure state assessment fees.
- Review certificate validation queues.
- Manage inspectors.
- View state dashboards.
- Generate state reports.
- Submit reports to Federal Ministry.
- Suspend/revoke certificates within state.
- Suspend facilities within state.

### B. Food Safety Directorate Officer

Responsible for food safety oversight.

Can:

- View state compliance.
- Review facility performance.
- Review food business compliance.
- View inspections.
- View reports.
- Monitor state-level public health indicators.

### C. Certificate Verification Desk Officer

Responsible for validating and approving certificate issuance.

Can:

- View certificate validation queue.
- Review assessment eligibility.
- Approve or reject certificate issuance.
- Request clarification from facilities.
- View certificate registry.
- Suspend or recommend revocation where authorized.

### D. Facility Accreditation Officer

Responsible for reviewing and approving medical facility applications.

Can:

- Review facility applications.
- Approve/reject facility accreditation.
- Request more information.
- Track re-accreditation.
- Suspend facilities where authorized.
- View facility performance.

### E. Policy and Finance Officer

Responsible for fees, revenue, and settlement oversight.

Can:

- Configure state assessment fees.
- View payment/revenue reports.
- View facility settlement reports.
- View state fee collections.
- Reconcile state financial reports.

### F. Inspectorate Coordinator

Responsible for managing inspectors and inspection assignments.

Can:

- Assign inspections.
- Review inspection reports.
- Issue or review notices.
- Track follow-up actions.
- Monitor inspector performance.

### G. Inspector / Environmental Health Officer

Responsible for field verification and enforcement.

Can:

- Scan certificates.
- Inspect food businesses.
- Record findings.
- Upload evidence.
- Issue notices.
- Submit inspection reports.

### H. LGA Office Officer

Responsible for local implementation.

Can:

- View local food businesses.
- View local inspections.
- View local facility activity.
- Support local enforcement workflows.

---

## 5.2 Federal Ministry Users

### A. Federal Ministry Super Admin

Can:

- View national dashboard.
- Manage national users.
- Configure national policy defaults.
- View state performance.
- View national certificate registry.
- View national M&E reports.
- Manage federal-level templates and settings.
- Oversee all states.

### B. National Food Safety Programme Officer

Can:

- Monitor implementation nationally.
- View food safety compliance indicators.
- Review state trends.
- View public health analytics.
- Generate national food safety reports.

### C. National M&E Officer

Can:

- Monitor M&E indicators.
- Track state report submission.
- Generate national M&E reports.
- Compare state performance.
- Export aggregate datasets.

### D. National Policy Officer

Can:

- Manage policy settings.
- Review state-level deviations.
- Configure national certificate validity defaults.
- Review fee policy summaries.
- Monitor implementation gaps.

### E. National Finance/Oversight Officer

Can:

- View national revenue summaries.
- View state fee summaries.
- View platform transaction summaries.
- View settlement summaries.
- Export finance reports.

### F. Federal Viewer / Executive Viewer

Can:

- View read-only national dashboards.
- View aggregate reports.
- Export approved reports.

---

# 6. State Ministry of Health Module

## 6.1 State Ministry Dashboard

### Purpose

The State Ministry Dashboard provides a real-time view of food handler certification, medical facility readiness, employer compliance, inspections, illness reports, and state-level implementation performance.

### Dashboard Cards

Show:

- Total registered food handlers in the state
- Total certified food handlers
- Active certificates
- Expired certificates
- Certificates expiring in 30 days
- Certificates issued this month
- Food businesses registered
- Approved medical facilities
- Facilities pending accreditation
- Facilities due for re-accreditation
- Suspended facilities
- Total inspections conducted
- Open inspection notices
- Illness reports
- Vaccination compliance rate
- State compliance percentage
- Pending certificate validations

### Charts

Suggested charts:

- Certification trend over time
- Compliance by LGA
- Certificates by status
- Facility accreditation status distribution
- Vaccination coverage
- Inspection outcomes
- Illness report trends
- Food business compliance by establishment category
- Assessment volume by facility

### Filters

- Date range
- State, locked to user’s state
- LGA
- Facility
- Employer
- Branch
- Food handler category
- Establishment category
- Certificate status
- Inspection status
- Ministry unit/office

---

## 6.2 State Organization Unit Management

### Purpose

State Ministries should be able to model internal structures such as Food Safety Directorate, Verification Desk, Accreditation Unit, Inspectorate, Policy and Finance Unit, and LGA offices.

### Core Features

- Create unit
- Edit unit
- Deactivate unit
- Add child unit
- Assign users to unit
- View members
- View unit workload
- Route queues to unit
- Apply unit-based dashboard defaults

### Example Units

| Unit | Function |
|---|---|
| Food Safety Directorate | State food safety oversight |
| Certificate Verification Desk | Certificate approval queue |
| Facility Accreditation Unit | Medical facility approval |
| Policy and Finance Unit | State fees and revenue |
| Inspectorate | Inspections and enforcement |
| LGA Office | Local compliance monitoring |

### Acceptance Criteria

- State Ministry can create multiple units.
- Units can be nested.
- Users can be assigned to units.
- Unit-restricted users only see records within their assigned scope.
- Dashboards default to the user’s unit where applicable.

---

## 6.3 State User and Role Management

### Purpose

The State Ministry must manage users responsible for different parts of implementation.

### Features

- Invite user
- Assign role
- Assign unit
- Set unit restriction
- Suspend user
- Reactivate user
- View user activity
- View audit trail

### Invite Fields

- Name
- Email
- Phone
- Role
- Unit
- Message
- Expiry date

### Invite Workflow

```txt
State Admin sends invite
→ Officer receives invite
→ Officer registers/logs in
→ Officer accepts invite
→ User is assigned to State Ministry, role, and unit
→ User lands on role-specific state dashboard
```

---

## 6.4 Medical Facility Accreditation Management

### Purpose

State Ministries must pre-qualify and monitor medical facilities that are eligible to conduct food handler assessments.

### Facility Application Statuses

- Draft
- Submitted
- Under Review
- More Information Required
- Approved
- Rejected
- Suspended
- Expired
- Re-accreditation Due

### Facility Review Checklist

The state reviewer should verify:

- Facility license
- Facility type
- Facility address
- Public/private ownership
- Medical records capacity
- Internet access
- Availability of standard forms
- Availability of computers/computer operators
- Availability of trained clinical staff
- Availability of trained lab staff
- Availability of trained records staff
- QR certificate capability
- Patient file/documentation policy
- Laboratory capability
- Doctor credentials
- Lab staff credentials

### State Facility Actions

- View application
- Approve facility
- Reject facility
- Request more information
- Suspend facility
- Reinstate facility
- Trigger re-accreditation
- View facility performance
- View assessment volume
- View complaint/inspection history

### Acceptance Criteria

- Only State Ministry users with accreditation permissions can approve facilities.
- Approved facilities become available for food handler appointments.
- Suspended or expired facilities cannot conduct assessments.
- Re-accreditation must occur annually.
- Facility approval/rejection creates audit log.

---

## 6.5 State Assessment Fee Configuration

### Purpose

Each state should be able to set standardized food handler assessment fees for approved medical facilities in that state.

### Fee Configuration Fields

- State
- Facility type
- Gross assessment fee
- Facility share
- State share
- Platform share
- Currency
- Effective start date
- Effective end date
- Status
- Created by
- Approved by

### Fee Rules

- Fees are state-specific.
- Historical fees used in completed payments must not be edited.
- New fee changes should create a new effective record.
- Fee changes must be auditable.
- Only authorized state policy/finance users can configure fees.

### Fee Workflow

```txt
Policy/Finance Officer creates fee schedule
→ State Admin reviews/approves
→ Fee becomes active from effective date
→ Food handlers see active fee when selecting facility
→ Payment and settlement calculations use active fee
```

---

## 6.6 Certificate Validation and Issuance

### Purpose

Certificates are issued by the State Ministry of Health. The state must validate that all requirements are met before certificate generation.

### Certificate Validation Queue

Columns:

- Food handler name
- NIN status
- Employer
- Branch
- Facility
- Doctor
- Assessment date
- Payment status
- Lab status
- Vaccination status
- Doctor decision
- Validation status
- Submitted date
- Actions

### Validation Checklist

Before approval, the system should confirm:

- Food handler profile is complete
- NIN verified or override approved
- Payment confirmed
- Facility approved
- Doctor authorized
- Declaration validated
- Physical examination completed
- Required lab tests completed/reviewed
- Vaccination reviewed
- Doctor decision is `fit`
- No unresolved illness report
- Certificate validity policy applied

### State Actions

- Approve certificate issuance
- Reject certificate issuance
- Request clarification from facility
- Escalate to supervisor
- View assessment summary
- View audit log

### Certificate Statuses

- Pending State Validation
- Approved
- Issued
- Rejected
- Clarification Requested
- Suspended
- Revoked
- Expired

### Acceptance Criteria

- Certificate is not generated until state validation is approved.
- Certificate shows State Ministry as issuing authority.
- Certificate is stored in central registry.
- QR code is generated after issuance.
- Certificate is publicly verifiable.
- Certificate validation action is audit logged.

---

## 6.7 State Certificate Registry

### Purpose

The State Certificate Registry allows authorized state users to search, review, suspend, revoke, and monitor certificates issued under the state.

### Search Filters

- Certificate number
- Food handler name
- NIN, authorized users only
- Employer
- Branch
- Facility
- Doctor
- Status
- Issue date
- Expiry date
- LGA

### Registry Actions

- View certificate
- Verify certificate
- Download certificate
- Suspend certificate
- Revoke certificate
- Replace certificate
- Export registry
- View audit history

### Suspension/Revocation Requirements

To suspend or revoke a certificate, user must provide:

- Reason
- Supporting note
- Effective date
- Approval, where required
- Confirmation

### Acceptance Criteria

- Revoked certificates show invalid on public verification page.
- Suspended certificates show suspended on public verification page.
- Revocation/suspension creates audit log.
- Certificate record remains immutable except status transitions.

---

## 6.8 Employer and Food Business Monitoring

### Purpose

State Ministry users should monitor food businesses operating in the state.

### Features

- View registered employers
- View branches in the state
- View food handler compliance by employer
- View certificate compliance
- View vaccination compliance
- View illness reports
- View inspection history
- Flag non-compliant employers
- Export employer compliance reports

### Employer Compliance Metrics

- Total food handlers
- Certified food handlers
- Expired certificates
- Certification pending
- Temporarily not fit
- Excluded from food handling
- Vaccination due
- Inspection notices
- Compliance percentage

### Acceptance Criteria

- State users can only view employers/branches operating in their state.
- Medical details are still restricted.
- State users can view regulatory compliance status.

---

## 6.9 State Inspection and Enforcement Management

### Purpose

The State Ministry manages inspections conducted by inspectors and Environmental Health Officers.

### Inspection Features

- Assign inspection
- Search business
- Select branch
- Conduct checklist
- Review inspection report
- Issue notice
- Track corrective action
- Close inspection
- Escalate enforcement

### Inspection Assignment Fields

- Inspector
- Employer
- Branch, optional
- LGA
- Inspection type
- Scheduled date
- Priority
- Notes

### Inspection Checklist

- All food handlers registered
- Certificates valid
- Certificates genuine
- Vaccination records current
- Sick handlers excluded
- Handwashing facilities available
- PPE available
- Hygiene practices enforced
- Employer records up to date
- No expired certificates in use

### Enforcement Actions

- No action
- Advisory notice
- Warning notice
- Compliance notice
- Follow-up required
- Recommend sanction
- Escalate to state authority

### Acceptance Criteria

- Inspectors can scan QR codes during inspection.
- Inspections can target employer-wide or branch-specific scope.
- Inspection reports are visible to authorized state users.
- Employers can respond to notices.
- State users can close or escalate inspection cases.

---

## 6.10 State Illness and Return-to-Work Monitoring

### Purpose

The State Ministry should monitor illness reports and exclusion/return-to-work patterns for public health purposes.

### Features

- View illness reports
- Filter by LGA, employer, branch, symptom, date
- View operational status
- Monitor exclusions
- Monitor return-to-work clearances
- Identify clusters or unusual trends
- Export aggregate reports

### Privacy Rules

State medical/public health users may see more details than employers, but access should still be role-limited. Non-medical state users should see aggregate or operational status only.

### Acceptance Criteria

- State can monitor illness trends.
- Employers cannot override exclusions.
- Return-to-work clearance is medical/regulatory controlled.
- Sensitive medical details are role-restricted.

---

## 6.11 State Reporting and M&E

### Purpose

States must submit periodic reports to the Federal Ministry and use analytics to improve compliance.

### Report Types

- Monthly state compliance report
- Facility performance report
- Food handler certification report
- Employer compliance report
- Vaccination coverage report
- Illness/exclusion report
- Inspection and enforcement report
- Certificate issuance report
- Revenue and settlement report
- Re-accreditation report

### Report Workflow

```txt
State officer generates report
→ Reviews report
→ Submits to Federal Ministry
→ Federal Ministry receives report
→ Report status changes to submitted
→ Federal dashboard updates state reporting status
```

### Report Statuses

- Draft
- Generated
- Submitted
- Returned for Correction
- Accepted
- Archived

### Acceptance Criteria

- State can generate reports by date range.
- State can export PDF/Excel/CSV.
- State can submit reports to Federal Ministry.
- Federal Ministry can track report submission status.

---

## 6.12 State Revenue and Settlement Oversight

### Purpose

The State Ministry needs visibility into state-approved assessment payments and settlement flows.

### Features

- View assessment payments
- View state fee revenue
- View facility settlement status
- View platform fee breakdown
- Filter by facility, LGA, date range
- Export reconciliation report

### Metrics

- Gross assessment revenue
- State fee amount
- Facility amount
- Platform amount
- Pending settlements
- Paid settlements
- Failed settlements
- Refunds

### Acceptance Criteria

- State finance users can view state-level revenue.
- State cannot view unrelated states’ revenue.
- Settlement reports are exportable.
- Payment changes are audit logged.

---

# 7. Federal Ministry of Health Module

## 7.1 Federal National Dashboard

### Purpose

The Federal Ministry Dashboard provides national oversight across all 36 states and the FCT.

### Dashboard Cards

Show:

- Total registered food handlers nationally
- Total certified food handlers nationally
- Active certificates nationally
- Expired certificates nationally
- Certificates issued this month
- Total registered food businesses
- Total approved medical facilities
- States with active implementation
- States with overdue reports
- National vaccination coverage
- National inspection count
- National illness reports
- Overall national compliance rate

### Charts

Suggested charts:

- Certification coverage by state
- Certificate issuance trend
- Vaccination coverage by state
- Facility accreditation by state
- Compliance by establishment type
- Inspection outcome by state
- Illness report trend
- State report submission status
- Revenue trend, if authorized

### Drill-Down Path

```txt
National → State → LGA → Facility / Employer → Branch / Department
```

---

## 7.2 National State Performance Monitoring

### Purpose

Federal users must compare state performance and identify implementation gaps.

### State Performance Table

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
- Illness reports
- Vaccination coverage
- Last report submitted
- Report status
- Overall performance rating

### Performance Indicators

- Certification coverage rate
- Facility availability per LGA
- Average certificate validation time
- Average assessment completion time
- Employer compliance rate
- Inspection coverage rate
- Vaccination completion rate
- Report timeliness
- Re-accreditation compliance

### Acceptance Criteria

- Federal users can compare all states.
- Federal users can drill into state-level summaries.
- Federal users can export state performance reports.
- Sensitive individual medical data remains restricted.

---

## 7.3 National Certificate Registry Oversight

### Purpose

The Federal Ministry oversees the national central certificate registry.

### Features

- Search certificates nationally
- Filter by state
- Filter by certificate status
- View certificate metadata
- View issuing state
- View issuing facility
- View public verification status
- Monitor revoked/suspended certificates
- Detect duplicate or suspicious patterns
- Export registry summary

### Federal Actions

Depending on authorization:

- View certificate metadata
- Flag certificate for review
- Recommend suspension/revocation to state
- Apply federal override suspension, if policy allows
- View certificate audit trail

### Acceptance Criteria

- Federal users can view national registry.
- Certificate remains state-issued.
- Federal oversight does not remove state issuing authority.
- Public verification status reflects current certificate state.

---

## 7.4 National Facility Registry Oversight

### Purpose

Federal Ministry should monitor approved medical facilities nationwide.

### Features

- View all facilities
- Filter by state, LGA, facility type, status
- View accreditation status
- View re-accreditation due
- View facility assessment volume
- View facility performance
- View suspended/expired facilities
- Export national facility registry

### Facility Performance Metrics

- Number of assessments conducted
- Certificates issued
- Not-fit reports
- Average assessment turnaround time
- Lab result turnaround time
- Rejection/clarification rate
- Settlement issues
- Accreditation status

### Acceptance Criteria

- Federal users can view all facility records nationally.
- Federal users cannot approve state facilities unless explicit override exists.
- State approval authority remains with State Ministry.

---

## 7.5 National Employer and Food Business Oversight

### Purpose

Federal Ministry should see national compliance trends by establishment type and state.

### Features

- View aggregate employer compliance
- Filter by state, LGA, establishment category
- View multi-state employers
- Compare compliance by sector
- Track high-risk categories
- View national branch coverage

### Metrics

- Registered employers nationally
- Registered branches nationally
- Employer compliance by state
- Compliance by establishment category
- Certificate expiry burden
- Vaccination due burden
- Inspection notices by category

### Acceptance Criteria

- Federal users see aggregate employer trends.
- Individual employer details visible only to authorized federal users.
- Sensitive medical information remains restricted.

---

## 7.6 National Policy Configuration

### Purpose

Federal Ministry should set national defaults and control policy-level configuration.

### Configurable National Rules

- Default certificate validity, default 6 months
- Renewal reminder days
- Typhoid vaccination validity years
- Hepatitis A second dose interval
- Whether NIN verification is mandatory
- Whether payment is required before assessment
- Whether state validation is required before certificate issuance
- Whether public QR verification is enabled
- Certificate template
- National certificate numbering format
- National M&E indicators
- Data retention rules
- Privacy settings

### State Override Management

Federal users should see:

- State-level overrides
- Override reason
- Approving authority
- Effective date
- Expiry date
- Audit trail

### Acceptance Criteria

- Federal can configure national policy defaults.
- State overrides are visible and auditable.
- System uses national default where state override is absent.
- Policy changes are audit logged.

---

## 7.7 National M&E Module

### Purpose

The Federal Ministry uses M&E to monitor implementation effectiveness, policy outcomes, and public health impact.

### M&E Indicators

Suggested indicators:

1. Number of registered food handlers
2. Number of certified food handlers
3. Certification coverage rate
4. Certificate renewal rate
5. Number of approved medical facilities
6. Facility distribution by state and LGA
7. Average assessment completion time
8. Average certificate validation time
9. Vaccination coverage rate
10. Typhoid vaccination compliance
11. Hepatitis A vaccination completion
12. Number of illness reports
13. Number of return-to-work clearances
14. Number of inspections conducted
15. Employer compliance rate
16. State report submission rate
17. Facility re-accreditation compliance
18. Number of revoked/suspended certificates
19. Number of non-compliant employers
20. Public verification volume

### Federal M&E Dashboard

Features:

- Indicator cards
- Trends over time
- State comparison
- Exportable reports
- Data quality checks
- Missing report alerts
- Implementation progress tracker

### Acceptance Criteria

- Federal users can generate national M&E reports.
- M&E reports can be exported.
- Reports can be filtered by state and date.
- Federal can identify states with low implementation performance.

---

## 7.8 National Reporting

### Report Types

Federal Ministry should generate:

- National implementation report
- State performance comparison report
- National certificate registry summary
- National facility accreditation report
- National vaccination coverage report
- National employer compliance report
- National inspection and enforcement report
- National illness/exclusion trend report
- National revenue and settlement summary, if authorized
- State report submission report
- Policy compliance report

### Report Workflow

```txt
Federal user selects report
→ Applies filters
→ Generates report
→ Reviews output
→ Exports PDF/Excel/CSV
→ Archives report
```

### Acceptance Criteria

- Federal users can generate national reports.
- Federal users can export reports.
- Reports are aggregate by default.
- Sensitive medical data is excluded unless authorized.

---

## 7.9 National Data Quality and Audit Oversight

### Purpose

Federal Ministry should monitor data quality and suspicious activities.

### Data Quality Checks

- Duplicate NINs
- Duplicate certificates
- Unusual certificate issuance volumes
- Facilities issuing certificates too quickly
- Facilities with high rejection rates
- Missing vaccination records
- Expired facility issuing assessments
- State report delays
- Invalid public verification attempts

### Audit Oversight

Federal users should view:

- Certificate issuance audit trail
- Facility approval audit trail
- State policy change audit trail
- Revocation/suspension audit trail
- Payment/settlement audit summary
- User role changes

### Acceptance Criteria

- Federal users can view audit logs nationally, based on permission.
- Suspicious patterns can be flagged.
- Audit exports are restricted to authorized users.

---

## 7.10 Federal Notification and Escalation

### Notifications

Federal users should receive alerts for:

- State report overdue
- State implementation below threshold
- High certificate revocation rate
- High illness reports in a state/LGA
- Facility suspicious activity
- National policy deviation
- Payment/settlement anomalies
- Data quality issues

### Escalation Workflow

```txt
System detects issue
→ Federal user receives alert
→ Federal user reviews details
→ Federal user sends query to state
→ State responds
→ Federal user closes or escalates
```

---

# 8. Data Model Requirements

## 8.1 State Report

```python
class StateReport(models.Model):
    id = models.UUIDField(primary_key=True)
    state = models.ForeignKey("geography.State", on_delete=models.CASCADE)
    report_type = models.CharField(max_length=100)
    reporting_period_start = models.DateField()
    reporting_period_end = models.DateField()
    status = models.CharField(max_length=50)
    generated_by = models.ForeignKey("accounts.User", null=True, on_delete=models.SET_NULL)
    submitted_by = models.ForeignKey("accounts.User", null=True, related_name="submitted_state_reports", on_delete=models.SET_NULL)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey("accounts.User", null=True, related_name="reviewed_state_reports", on_delete=models.SET_NULL)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    file_url = models.URLField(blank=True)
    data_snapshot = models.JSONField(default=dict)
    review_comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 8.2 Policy Configuration

```python
class PolicyConfiguration(models.Model):
    id = models.UUIDField(primary_key=True)
    scope = models.CharField(max_length=20)  # national or state
    state = models.ForeignKey("geography.State", null=True, blank=True, on_delete=models.SET_NULL)
    certificate_validity_months = models.PositiveIntegerField(default=6)
    renewal_reminder_days = models.PositiveIntegerField(default=30)
    typhoid_validity_years = models.PositiveIntegerField(default=3)
    hepatitis_a_second_dose_interval_months = models.PositiveIntegerField(default=6)
    require_nin_verification = models.BooleanField(default=True)
    require_payment_before_assessment = models.BooleanField(default=True)
    require_state_validation_before_certificate = models.BooleanField(default=True)
    public_qr_verification_enabled = models.BooleanField(default=True)
    created_by = models.ForeignKey("accounts.User", null=True, on_delete=models.SET_NULL)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 8.3 State Assessment Fee

```python
class AssessmentFee(models.Model):
    id = models.UUIDField(primary_key=True)
    state = models.ForeignKey("geography.State", on_delete=models.CASCADE)
    facility_type = models.CharField(max_length=100)
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2)
    facility_amount = models.DecimalField(max_digits=12, decimal_places=2)
    state_amount = models.DecimalField(max_digits=12, decimal_places=2)
    platform_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="NGN")
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50)
    created_by = models.ForeignKey("accounts.User", null=True, on_delete=models.SET_NULL)
    approved_by = models.ForeignKey("accounts.User", null=True, related_name="approved_assessment_fees", on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 8.4 State Query / Federal Escalation

```python
class FederalStateQuery(models.Model):
    id = models.UUIDField(primary_key=True)
    state = models.ForeignKey("geography.State", on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    priority = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    raised_by = models.ForeignKey("accounts.User", related_name="raised_federal_queries", on_delete=models.SET_NULL, null=True)
    assigned_to = models.ForeignKey("accounts.User", related_name="assigned_federal_queries", on_delete=models.SET_NULL, null=True, blank=True)
    response = models.TextField(blank=True)
    responded_by = models.ForeignKey("accounts.User", related_name="responded_federal_queries", on_delete=models.SET_NULL, null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

---

# 9. API Requirements

## 9.1 State Ministry APIs

```txt
GET    /api/state/dashboard
GET    /api/state/units
POST   /api/state/units
PATCH  /api/state/units/:id

GET    /api/state/users
POST   /api/state/invites
GET    /api/state/invites

GET    /api/state/facilities
GET    /api/state/facilities/applications
PATCH  /api/state/facilities/:id/approve
PATCH  /api/state/facilities/:id/reject
PATCH  /api/state/facilities/:id/suspend
PATCH  /api/state/facilities/:id/reinstate

GET    /api/state/fees
POST   /api/state/fees
PATCH  /api/state/fees/:id

GET    /api/state/certificate-validation-queue
GET    /api/state/certificate-validation-queue/:id
PATCH  /api/state/certificate-validation-queue/:id/approve
PATCH  /api/state/certificate-validation-queue/:id/reject
PATCH  /api/state/certificate-validation-queue/:id/request-clarification

GET    /api/state/certificates
GET    /api/state/certificates/:id
PATCH  /api/state/certificates/:id/suspend
PATCH  /api/state/certificates/:id/revoke

GET    /api/state/employers
GET    /api/state/food-handlers
GET    /api/state/inspections
POST   /api/state/inspections/assign
PATCH  /api/state/inspections/:id/review
PATCH  /api/state/inspections/:id/close

GET    /api/state/illness-reports
GET    /api/state/reports
POST   /api/state/reports/generate
PATCH  /api/state/reports/:id/submit

GET    /api/state/revenue
GET    /api/state/settlements
```

## 9.2 Federal Ministry APIs

```txt
GET    /api/federal/dashboard
GET    /api/federal/states/performance
GET    /api/federal/states/:state_id/summary

GET    /api/federal/certificates
GET    /api/federal/certificates/:id
PATCH  /api/federal/certificates/:id/flag

GET    /api/federal/facilities
GET    /api/federal/employers
GET    /api/federal/food-handlers/summary

GET    /api/federal/policy
POST   /api/federal/policy
PATCH  /api/federal/policy/:id

GET    /api/federal/state-overrides
GET    /api/federal/reports
POST   /api/federal/reports/generate
GET    /api/federal/state-reports
PATCH  /api/federal/state-reports/:id/review
PATCH  /api/federal/state-reports/:id/return-for-correction
PATCH  /api/federal/state-reports/:id/accept

GET    /api/federal/m-and-e/indicators
GET    /api/federal/data-quality
GET    /api/federal/audit-logs

POST   /api/federal/queries
GET    /api/federal/queries
PATCH  /api/federal/queries/:id/respond
PATCH  /api/federal/queries/:id/close
```

---

# 10. Frontend Routes

## 10.1 State Ministry Routes

```txt
/app/state/dashboard
/app/state/units
/app/state/users
/app/state/invites
/app/state/facilities
/app/state/facilities/applications
/app/state/facilities/[id]
/app/state/fees
/app/state/certificate-validation
/app/state/certificate-validation/[id]
/app/state/certificates
/app/state/certificates/[id]
/app/state/employers
/app/state/food-handlers
/app/state/inspectors
/app/state/inspections
/app/state/inspections/[id]
/app/state/illness-reports
/app/state/reports
/app/state/revenue
/app/state/settings
```

## 10.2 Federal Ministry Routes

```txt
/app/federal/dashboard
/app/federal/states
/app/federal/states/[id]
/app/federal/certificates
/app/federal/facilities
/app/federal/employers
/app/federal/m-and-e
/app/federal/reports
/app/federal/state-reports
/app/federal/policy
/app/federal/data-quality
/app/federal/audit
/app/federal/queries
/app/federal/settings
```

---

# 11. UI Components

## 11.1 Shared Ministry Components

- MinistryDashboardCards
- StatePerformanceTable
- CertificateValidationQueueTable
- FacilityAccreditationReviewPanel
- AssessmentFeeConfigForm
- CertificateRegistryTable
- InspectionAssignmentForm
- InspectionReviewPanel
- StateReportBuilder
- FederalReportBuilder
- PolicyConfigurationForm
- MAndEIndicatorCard
- StateComparisonChart
- NationalMap
- UnitTree
- UnitMemberTable
- QueryEscalationPanel
- DataQualityAlertCard
- AuditLogTable

---

# 12. Permissions and Access Control

## 12.1 State Ministry Access

State Ministry users can only access records within their state unless given federal/super admin permissions.

Unit scoping rules:

- Verification Desk users default to certificate validation queue.
- Accreditation Unit users default to facility applications.
- Policy and Finance users default to fees/revenue.
- Inspectorate users default to inspections.
- LGA Office users default to LGA-specific views.

## 12.2 Federal Ministry Access

Federal Ministry users have national oversight, but access should still be permission-based.

Federal users can:

- View national aggregates.
- View state summaries.
- View national registries.
- Generate national reports.
- Configure national policy, if authorized.
- Review state reports.

Federal users should not automatically see sensitive individual medical details unless explicitly authorized.

---

# 13. Privacy Requirements

## 13.1 State Ministry Privacy

State users may require access to more sensitive data for regulatory or public health purposes, but access should be role-limited.

Rules:

- Certificate Verification Desk can view assessment summary but not unnecessary full clinical notes unless authorized.
- Public health/medical users may view illness details where needed.
- Policy/Finance users should not view medical details.
- Inspectorate users should see operational compliance, not full medical records.
- All sensitive medical access must be audit logged.

## 13.2 Federal Ministry Privacy

Federal users should primarily see aggregate data.

Rules:

- National dashboards are aggregate by default.
- Individual medical details are restricted.
- Full NIN should be masked unless authorized.
- Report exports must exclude sensitive medical records unless explicitly permitted.
- Public certificate verification remains limited.

---

# 14. Audit Logs

Audit logs are required for:

- State user invite
- State user role change
- Unit creation/update
- Facility approval/rejection/suspension
- Fee configuration
- Certificate validation approval/rejection
- Certificate issuance
- Certificate suspension/revocation
- Inspection assignment/review
- State report submission
- Federal report review
- National policy configuration
- State override approval
- Federal query/escalation
- Sensitive medical data access

---

# 15. Acceptance Criteria

## 15.1 State Ministry Module

- State users can view state dashboard.
- State users can manage internal units.
- State users can invite users and assign them to units.
- State users can approve/reject medical facilities.
- State users can configure state assessment fees.
- State users can validate certificate issuance.
- Certificates are issued under State Ministry authority.
- State users can view certificate registry.
- State users can suspend/revoke certificates.
- State users can manage inspections.
- State users can monitor employer compliance.
- State users can generate and submit reports to Federal Ministry.
- State finance users can view revenue/settlement reports.
- State users cannot access records outside their state unless authorized.

## 15.2 Federal Ministry Module

- Federal users can view national dashboard.
- Federal users can compare state performance.
- Federal users can view national certificate registry.
- Federal users can view national facility registry.
- Federal users can view national employer compliance trends.
- Federal users can configure national policy defaults.
- Federal users can monitor state policy overrides.
- Federal users can generate national reports.
- Federal users can review state reports.
- Federal users can monitor M&E indicators.
- Federal users can view data quality alerts.
- Federal users can raise queries to states.
- Federal users have national oversight but not unrestricted medical record access by default.

---

# 16. Codex Implementation Instructions

Use this prompt for Codex:

```txt
Implement the State Ministry of Health Module and Federal Ministry of Health Module for FoodCert NG.

The State Ministry Module must support state dashboards, organization units, state users and invites, medical facility accreditation, assessment fee configuration, certificate validation and issuance, certificate registry, employer/food business monitoring, inspections, illness monitoring, state reports, revenue and settlement oversight.

The Federal Ministry Module must support national oversight, national dashboard, state performance monitoring, national certificate registry oversight, national facility registry oversight, employer compliance analytics, policy configuration, national M&E, national reports, data quality monitoring, audit oversight, and state escalation/query workflows.

Important rules:
- Certificates are issued by the State Ministry of Health.
- Federal Ministry has national oversight but does not replace state issuing authority.
- State users are scoped to their state.
- Federal users see national dashboards and state comparisons.
- Sensitive medical data must remain restricted and audit logged.
- OrganizationUnit must support State Ministry units such as Verification Desk, Accreditation Unit, Policy and Finance Unit, Inspectorate, and LGA Offices.
- State reports must be submitted to Federal Ministry.
- National dashboards should be aggregate by default.
- Public certificate verification remains limited and privacy-safe.

Build backend models, serializers, permissions, services, endpoints, tests, and frontend pages for both modules.
```

---

# 17. MVP Build Order

## State Ministry MVP

1. State dashboard shell
2. State users and unit management
3. Facility accreditation review
4. Assessment fee configuration
5. Certificate validation queue
6. Certificate issuance approval
7. Certificate registry
8. Inspection management
9. Employer compliance monitoring
10. State reports
11. Revenue/settlement summary
12. State permissions and tests

## Federal Ministry MVP

1. Federal dashboard shell
2. State performance table
3. National certificate registry
4. National facility registry
5. National policy configuration
6. State report monitoring
7. National M&E dashboard
8. National reports
9. Data quality alerts
10. Federal query/escalation workflow
11. Federal permissions and tests
