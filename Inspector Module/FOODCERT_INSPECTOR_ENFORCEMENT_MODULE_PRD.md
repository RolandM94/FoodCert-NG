# PRD: Inspector & Enforcement Module — FoodCert NG

## 1. Module Name

**Inspector & Enforcement Module**

## 2. Product Context

The Inspector & Enforcement Module is the field compliance and regulatory enforcement layer of **FoodCert NG**. It enables authorized State Ministry inspectors, Environmental Health Officers, LGA officers, and supervisory users to inspect food businesses, verify food handler certificates, record compliance findings, issue notices, track corrective actions, and escalate enforcement cases.

This module depends on the certificate system, employer/branch records, food handler compliance records, and shared audit logging. It can be built in parallel with the Payments, Subscriptions & Settlements Module only if both teams agree on the shared contracts listed in this PRD.

The module must protect medical privacy. Inspectors may verify whether a food handler is certified, expired, suspended, revoked, or excluded from food handling, but must not see private clinical records such as lab results, doctor notes, diagnosis, full health declaration answers, or full NIN.

---

# 3. Product Goal

To provide State Ministries of Health with a structured digital inspection and enforcement workflow for ensuring that food businesses employ medically fit food handlers and comply with food safety certification requirements.

---

# 4. Core Objectives

The Inspector & Enforcement Module must allow authorized users to:

1. Assign inspections to inspectors.
2. Conduct scheduled and unscheduled inspections.
3. Inspect employers and business branches.
4. Scan QR codes on food handler certificates.
5. Verify certificates by QR token or certificate number.
6. View public/inspector-safe certificate results.
7. Check employer and branch compliance.
8. Review linked food handlers and certificate statuses.
9. Record inspection checklist findings.
10. Upload photos, documents, and evidence.
11. Issue advisory, warning, compliance, or enforcement notices.
12. Track corrective actions.
13. Schedule follow-up inspections.
14. Escalate serious non-compliance cases.
15. Record inspection outcomes.
16. Generate inspection reports.
17. Maintain audit logs.
18. Provide state and federal dashboards with enforcement analytics.

---

# 5. Key Actors

## 5.1 Inspector / Environmental Health Officer

Field officer who conducts inspections.

Can:

- View assigned inspections.
- Start inspection.
- Scan certificate QR codes.
- Verify certificates manually.
- View employer and branch profile.
- View inspector-safe food handler compliance status.
- Complete inspection checklist.
- Upload evidence.
- Issue notices where authorized.
- Recommend enforcement action.
- Submit inspection report.
- Schedule follow-up where permitted.

Cannot:

- View lab results.
- View diagnosis.
- View doctor notes.
- View declaration answers.
- View full NIN.
- Change certificate status.
- Change payment/subscription status.
- Mark a food handler medically fit.

## 5.2 Inspectorate Coordinator

State Ministry user responsible for assigning and supervising inspectors.

Can:

- Create inspection assignments.
- Assign inspectors.
- View inspection dashboard.
- Review inspection reports.
- Return inspection reports for correction.
- Approve notices.
- Escalate cases.
- Close inspection cases.
- Reassign inspections.
- Track inspector performance.

## 5.3 State Ministry Admin

Senior state user with regulatory authority.

Can:

- View all inspections within the state.
- Manage inspection teams.
- Approve serious enforcement actions.
- Suspend or recommend certificate review through certificate module.
- Escalate non-compliant employers.
- Generate state enforcement reports.
- Configure inspection templates/checklists, where permitted.

## 5.4 LGA Office Officer

Local government implementation officer.

Can:

- View inspections within assigned LGA.
- Conduct or support inspections.
- View local employer and branch compliance.
- Submit inspection findings.
- Track local corrective actions.

## 5.5 Employer / Branch Manager

The regulated business being inspected.

Can:

- View notices issued to their business/branch.
- Respond to corrective action requests.
- Upload evidence of compliance.
- View inspection outcome summary.
- View follow-up deadlines.

Cannot:

- Edit inspection findings.
- Delete notices.
- View inspector internal notes.
- View other employers’ inspection records.
- Override enforcement decision.

## 5.6 Food Handler

Can:

- Present certificate QR code.
- View own certificate status.
- Receive notification if employer/inspection flags their certificate issue.

Cannot:

- Edit inspection result.
- Edit certificate status.
- Access employer inspection notes.

## 5.7 Federal Ministry User

National oversight user.

Can:

- View aggregate enforcement dashboards.
- Compare inspection activity by state.
- View state inspection performance.
- Monitor serious enforcement trends.
- View non-sensitive national enforcement reports.

Cannot by default:

- Conduct state inspection.
- Edit state inspection findings.
- View sensitive medical data.
- Override state enforcement unless explicit policy allows.

---

# 6. Module Scope

## 6.1 In Scope

- Inspector role and permissions
- Inspectorate team management
- Inspection assignment
- Scheduled inspection
- Unscheduled inspection
- Employer inspection
- Branch inspection
- Food handler certificate verification
- QR scanning
- Manual certificate verification
- Inspection checklist
- Evidence upload
- Inspection findings
- Notices and corrective actions
- Follow-up inspection
- Enforcement escalation
- Case closure
- Inspector dashboard
- State enforcement dashboard
- Federal enforcement summary
- Inspection reports
- Audit logging

## 6.2 Out of Scope for MVP

- Court/legal prosecution management
- Fine payment processing
- Offline-first mobile app
- GPS geofencing enforcement
- Biometric verification
- AI fraud detection
- Drone/photo analytics
- Inter-agency enforcement integration
- Police/court workflow
- Full sanctions payment module

---

# 7. Inspection Types

The system should support multiple inspection types.

## 7.1 Routine Inspection

Standard periodic inspection of a food business or branch.

## 7.2 Follow-Up Inspection

Inspection conducted after a previous notice or corrective action deadline.

## 7.3 Complaint-Based Inspection

Inspection triggered by public complaint, illness report, employer report, or regulatory concern.

## 7.4 Certificate Verification Sweep

Inspection focused mainly on confirming that food handlers have valid certificates.

## 7.5 Illness / Public Health Risk Inspection

Inspection triggered by reported illness, outbreak concern, or return-to-work issue.

## 7.6 Facility-Linked Verification

Inspection or field verification related to certificate authenticity, suspicious issuance, or suspected fraud.

---

# 8. Inspection Lifecycle

## 8.1 High-Level Flow

```txt
Inspection assignment created
→ Inspector receives assignment
→ Inspector visits employer/branch
→ Inspector starts inspection
→ Inspector verifies business/branch details
→ Inspector scans food handler certificates
→ Inspector completes compliance checklist
→ Inspector uploads evidence
→ Inspector records findings
→ Inspector issues or recommends notice
→ Inspector submits report
→ Coordinator reviews report
→ Employer responds to corrective actions
→ Follow-up inspection conducted if required
→ Case closed or escalated
```

## 8.2 Inspection Statuses

- Draft
- Assigned
- Accepted
- Scheduled
- In Progress
- Submitted
- Under Review
- Returned for Correction
- Notice Issued
- Corrective Action Pending
- Corrective Action Submitted
- Follow-Up Required
- Follow-Up Scheduled
- Resolved
- Escalated
- Closed
- Cancelled

## 8.3 Status Transition Rules

| From | To | Trigger |
|---|---|---|
| Draft | Assigned | Coordinator assigns inspector |
| Assigned | Accepted | Inspector accepts assignment |
| Accepted | Scheduled | Visit date confirmed |
| Scheduled | In Progress | Inspector starts inspection |
| In Progress | Submitted | Inspector submits report |
| Submitted | Under Review | Coordinator begins review |
| Under Review | Returned for Correction | Coordinator requests correction |
| Under Review | Notice Issued | Notice approved/issued |
| Notice Issued | Corrective Action Pending | Employer notified |
| Corrective Action Pending | Corrective Action Submitted | Employer uploads response |
| Corrective Action Submitted | Follow-Up Required | Coordinator requests follow-up |
| Follow-Up Required | Follow-Up Scheduled | Follow-up assigned |
| Corrective Action Submitted | Resolved | Coordinator accepts response |
| Resolved | Closed | Case closed |
| Any active stage | Escalated | Serious non-compliance |
| Any active stage | Cancelled | Authorized cancellation |

---

# 9. Inspection Assignment

## 9.1 Purpose

Inspectorate coordinators and authorized State Ministry users assign inspections to field officers.

## 9.2 Assignment Fields

- Inspection type
- Employer
- Branch
- State
- LGA
- Address
- Assigned inspector
- Supervising officer
- Scheduled date/time
- Priority
- Reason for inspection
- Linked complaint, optional
- Linked illness report, optional
- Linked previous inspection, optional
- Notes

## 9.3 Assignment Priority

- Low
- Medium
- High
- Critical

## 9.4 Assignment Rules

- Inspector must belong to the State Ministry or authorized LGA office.
- Inspector must be scoped to the correct state/LGA unless permitted otherwise.
- Branch inspections must be linked to an employer and branch.
- Complaint or illness-triggered inspections should carry the linked reference.
- Assignment creation must be audit logged.

---

# 10. Inspector Dashboard

## 10.1 Dashboard Cards

Show:

- Assigned inspections
- Inspections due today
- Overdue inspections
- In-progress inspections
- Submitted inspections
- Notices issued
- Corrective actions pending
- Follow-up inspections
- High-priority cases
- Closed inspections this month

## 10.2 Inspector Task List

Columns:

- Inspection reference
- Employer
- Branch
- LGA
- Inspection type
- Scheduled date
- Priority
- Status
- Actions

## 10.3 Inspector Actions

- Accept assignment
- Start inspection
- Reschedule request
- View employer/branch
- Scan certificate
- Complete checklist
- Upload evidence
- Submit report

---

# 11. Employer and Branch Inspection

## 11.1 Purpose

The inspection must be tied to a real employer and branch where applicable.

## 11.2 Employer/Branch Context

Inspector should see:

- Employer name
- Registration/profile status
- Establishment category
- Branch name
- Branch address
- LGA
- Contact person
- Number of linked food handlers
- Certificate compliance summary
- Last inspection date
- Open notices
- Previous enforcement history
- Subscription status, read-only if exposed

## 11.3 Employer/Branch Compliance Summary

Show:

- Total linked food handlers
- Active certificates
- Expired certificates
- Expiring soon certificates
- Suspended certificates
- Revoked certificates
- Uncertified food handlers
- Temporarily not fit handlers
- Return-to-work pending handlers
- Vaccination due handlers

## 11.4 Privacy Rule

This view must not show:

- Lab results
- Diagnosis
- Doctor notes
- Health declaration answers
- Full NIN
- Payment details beyond read-only subscription/payment status indicators

---

# 12. Certificate QR Verification During Inspection

## 12.1 Purpose

Inspectors must verify certificate authenticity in the field.

## 12.2 QR Verification Flow

```txt
Inspector opens scanner
→ Scans certificate QR code
→ System calls certificate verification API
→ System returns inspector-safe result
→ Inspector confirms identity match
→ Verification result is saved to inspection
```

## 12.3 Manual Verification Flow

```txt
Inspector enters certificate number
→ System verifies certificate
→ Inspector views verification result
→ Inspector saves result to inspection
```

## 12.4 Inspector-Safe Verification Result

Show:

- Certificate status
- Certificate number
- Food handler name
- Passport photo
- Issuing State Ministry
- Medical facility
- Issue date
- Expiry date
- Fitness status
- Verification timestamp

Do not show:

- Full NIN
- Lab results
- Diagnosis
- Doctor notes
- Declaration answers
- Medical report

## 12.5 Verification Outcomes

- Valid
- Expired
- Suspended
- Revoked
- Replaced
- Not Found
- Invalid QR
- Tamper Suspected
- Verification Service Error

## 12.6 Verification Log Requirements

Each verification attempt must log:

- Certificate, if found
- Certificate number/token attempted
- Inspector user
- Inspection ID
- Employer/branch
- Result
- Timestamp
- IP/device details
- Optional location coordinates, if user permits

---

# 13. Food Handler Verification List

## 13.1 Purpose

During inspection, inspectors should be able to review expected food handlers for the branch and mark who was verified.

## 13.2 Food Handler List Columns

- Name
- Passport photo
- Role/category
- Certificate status
- Expiry date
- Vaccination status
- Fitness status
- Present during inspection
- Verified by QR
- Issue found
- Action

## 13.3 Inspector Actions

- Mark present
- Mark absent
- Scan certificate
- Flag no certificate
- Flag expired certificate
- Flag certificate mismatch
- Flag unfit handler working
- Add note
- Add evidence

## 13.4 Food Handler Issue Types

- No certificate presented
- Certificate expired
- Certificate suspended
- Certificate revoked
- Certificate belongs to another person
- Certificate photo mismatch
- QR invalid
- Food handler not linked to employer
- Temporarily not fit but working
- Return-to-work clearance pending
- Vaccination due
- Suspicious certificate

---

# 14. Inspection Checklist

## 14.1 Purpose

The checklist standardizes inspection findings across states and LGAs.

## 14.2 Core Checklist Categories

### A. Food Handler Certification

- Are all food handlers registered on FoodCert NG?
- Do all active food handlers have valid certificates?
- Are expired certificates being used?
- Are suspended or revoked certificates being used?
- Are certificates available for verification?
- Are uncertified persons handling food?

### B. Fitness and Exclusion Compliance

- Are temporarily not-fit handlers excluded from food handling?
- Are sick handlers present in food handling areas?
- Are return-to-work clearances respected?
- Has employer reported illness where required?

### C. Vaccination Compliance

- Are required vaccination statuses up to date?
- Are food handlers with vaccination due flagged for renewal?
- Are vaccination compliance records maintained?

### D. Employer Records

- Does employer maintain food handler records?
- Are branch records up to date?
- Are linked food handlers correctly assigned to branch?
- Are compliance records available?

### E. Hygiene and Food Safety Practices

- Handwashing facilities available
- Soap/sanitizer available
- PPE available
- Clean food handling area
- Waste disposal adequate
- Food handlers observe hygiene rules
- No visible unsafe food handling practice

### F. Certificate Authenticity

- QR codes verified successfully
- No fake certificates identified
- No certificate-person mismatch
- No repeated suspicious certificate use

### G. Corrective Action Compliance

- Previous notices addressed
- Evidence of correction available
- Outstanding corrective actions remain

## 14.3 Checklist Response Types

- Yes
- No
- Not Applicable
- Not Observed
- Needs Follow-Up

## 14.4 Severity

Each failed item should support severity:

- Minor
- Major
- Critical

## 14.5 Checklist Rules

- Critical issues should trigger enforcement recommendation.
- Repeated major issues should trigger escalation.
- Checklist completion is required before submission unless inspection is cancelled.
- Photos/evidence may be required for major or critical findings.

---

# 15. Evidence Upload

## 15.1 Purpose

Inspectors must be able to attach evidence to findings and notices.

## 15.2 Evidence Types

- Photo
- Video, optional/future
- Document
- Certificate screenshot
- Signed notice
- Employer response document
- Inspector note
- GPS/location metadata, optional

## 15.3 Evidence Fields

- Inspection
- Finding
- Evidence type
- File URL
- Caption
- Uploaded by
- Timestamp
- Location metadata, optional

## 15.4 Evidence Rules

- Evidence must be linked to inspection.
- Sensitive evidence must be access-controlled.
- Employer should see only evidence shared with notice.
- Evidence upload must be audit logged.
- Files must be scanned/validated by storage policy.

---

# 16. Inspection Findings

## 16.1 Purpose

Findings are structured records of non-compliance, observations, or verified compliance.

## 16.2 Finding Fields

- Inspection
- Checklist item
- Category
- Finding type
- Severity
- Description
- Evidence
- Recommended action
- Food handler, optional
- Certificate, optional
- Employer/branch
- Status

## 16.3 Finding Statuses

- Open
- Under Review
- Notice Issued
- Corrective Action Pending
- Corrected
- Not Corrected
- Escalated
- Closed

## 16.4 Finding Types

- Compliance confirmed
- Minor non-compliance
- Major non-compliance
- Critical non-compliance
- Suspicious certificate
- Public health risk
- Documentation gap
- Repeat violation

---

# 17. Notices and Enforcement Actions

## 17.1 Notice Types

- Advisory Notice
- Warning Notice
- Compliance Notice
- Corrective Action Notice
- Follow-Up Notice
- Suspension Recommendation
- Closure Recommendation
- Public Health Escalation
- Certificate Review Recommendation
- Facility Review Recommendation

## 17.2 Notice Fields

- Notice reference
- Inspection
- Employer
- Branch
- Notice type
- Findings included
- Description
- Required corrective actions
- Deadline
- Issued by
- Approved by, where required
- Status
- Employer response
- Evidence submitted
- Closure decision

## 17.3 Notice Statuses

- Draft
- Pending Approval
- Issued
- Acknowledged
- Corrective Action Pending
- Response Submitted
- Under Review
- Accepted
- Rejected
- Follow-Up Required
- Escalated
- Closed

## 17.4 Notice Rules

- Minor issues may generate advisory notice.
- Major issues may generate warning or compliance notice.
- Critical issues may require immediate escalation.
- Certain notices may require supervisor approval.
- Employer should be notified when notice is issued.
- Notice actions must be audit logged.

---

# 18. Corrective Action Workflow

## 18.1 Purpose

Employers must be able to respond to notices and provide evidence of corrective action.

## 18.2 Corrective Action Flow

```txt
Notice issued
→ Employer receives notice
→ Employer acknowledges notice
→ Employer uploads corrective action evidence
→ Inspector/coordinator reviews response
→ Response accepted, rejected, or follow-up required
→ Case closed or escalated
```

## 18.3 Employer Response Fields

- Response note
- Corrective action taken
- Evidence upload
- Submitted by
- Submitted at

## 18.4 Review Actions

Inspector/coordinator can:

- Accept response
- Reject response
- Request more evidence
- Schedule follow-up inspection
- Escalate case
- Close notice

## 18.5 Deadline Rules

- Notice deadline must be visible to employer.
- Overdue notices should trigger reminders.
- Overdue critical notices should trigger escalation.
- Deadline extensions require authorization and reason.

---

# 19. Escalation Workflow

## 19.1 Purpose

Serious or repeated non-compliance must be escalated to higher regulatory authority.

## 19.2 Escalation Triggers

- Critical public health risk
- Repeated expired certificates
- Revoked/suspended certificate in use
- Unfit food handler working
- Fraudulent certificate
- Employer ignores notice
- Corrective action overdue
- Facility suspected of improper certification
- Illness cluster
- Inspector safety concern

## 19.3 Escalation Levels

- Inspectorate Coordinator
- State Ministry Admin
- State Food Safety Directorate
- Federal Ministry Oversight, aggregate or serious cases
- Other regulatory body, future integration

## 19.4 Escalation Actions

- Escalate case
- Add escalation note
- Attach evidence
- Recommend enforcement action
- Recommend certificate suspension/revocation
- Recommend facility review
- Notify state authority
- Track resolution

---

# 20. Follow-Up Inspection

## 20.1 Purpose

Follow-up inspections confirm whether corrective actions were completed.

## 20.2 Follow-Up Rules

- Follow-up inspection should link to original inspection.
- Follow-up checklist should focus on unresolved findings.
- Follow-up can close notice or escalate case.
- Follow-up outcome must be audit logged.

## 20.3 Follow-Up Outcomes

- Corrected
- Partially corrected
- Not corrected
- New violation found
- Escalated
- Closed

---

# 21. Enforcement Case Management

## 21.1 Purpose

A case groups inspections, findings, notices, corrective actions, and escalations.

## 21.2 Case Creation

Cases may be created when:

- Notice is issued.
- Critical finding is recorded.
- Corrective action is required.
- Serious issue is escalated.
- Repeated violations are identified.

## 21.3 Case Statuses

- Open
- Under Review
- Awaiting Employer Response
- Follow-Up Required
- Escalated
- Resolved
- Closed

## 21.4 Case Timeline

The system should show:

- Inspection assignment
- Inspection submission
- Findings
- Notice issuance
- Employer responses
- Evidence uploads
- Follow-up inspections
- Escalations
- Closure decision

---

# 22. State Enforcement Dashboard

## 22.1 Dashboard Cards

Show:

- Total inspections
- Inspections this month
- Inspections by LGA
- Open enforcement cases
- Notices issued
- Overdue corrective actions
- Critical findings
- Suspicious certificates flagged
- Follow-up inspections pending
- Employer compliance rate
- Branches inspected
- Inspectors active

## 22.2 Charts

Suggested charts:

- Inspections over time
- Findings by severity
- Notices by type
- Compliance by LGA
- Compliance by establishment category
- Certificate issues detected
- Corrective action completion rate
- Inspector workload
- Repeat violations by employer

## 22.3 Filters

- Date range
- State
- LGA
- Inspector
- Employer
- Branch
- Inspection type
- Notice status
- Finding severity
- Certificate issue type
- Establishment category

---

# 23. Federal Enforcement Oversight

## 23.1 Purpose

Federal users need national aggregate visibility into inspection and enforcement trends.

## 23.2 Federal Dashboard Metrics

Show:

- Total inspections nationally
- Inspections by state
- Notices by state
- Critical findings by state
- Overdue corrective actions by state
- Suspicious certificates flagged
- Employer compliance trends
- Inspection coverage by state
- Repeat violation patterns
- Public health risk escalations

## 23.3 Federal Rules

- Federal dashboard is aggregate by default.
- Federal users may drill into state summaries where permitted.
- Sensitive medical data remains hidden.
- Federal users do not conduct routine state inspections by default.

---

# 24. Reports and Exports

## 24.1 Inspector Reports

- My inspections report
- Inspection outcome report
- Certificate verification report
- Follow-up report

## 24.2 State Reports

- State inspection summary
- Enforcement notice report
- Corrective action report
- Critical findings report
- Employer compliance report
- LGA inspection report
- Inspector performance report
- Suspicious certificate report

## 24.3 Federal Reports

- National enforcement summary
- State comparison report
- Inspection coverage report
- Critical risk report
- Suspicious certificate trend report
- Corrective action performance report

## 24.4 Export Formats

- PDF
- Excel
- CSV

## 24.5 Export Privacy

Exports must respect the user’s role and must not include sensitive medical data unless explicitly authorized.

---

# 25. Notifications

## 25.1 Inspector Notifications

Notify when:

- New inspection assigned
- Inspection rescheduled
- Inspection due today
- Inspection overdue
- Report returned for correction
- Follow-up assigned
- Notice approved/rejected

## 25.2 Coordinator Notifications

Notify when:

- Inspection submitted
- Critical finding recorded
- Notice pending approval
- Corrective action submitted
- Notice overdue
- Follow-up due
- Case escalated

## 25.3 Employer Notifications

Notify when:

- Inspection scheduled, where applicable
- Notice issued
- Corrective action deadline approaching
- Corrective action overdue
- Response accepted/rejected
- Follow-up inspection scheduled
- Case closed

## 25.4 State Ministry Notifications

Notify when:

- Critical case escalated
- Suspicious certificate flagged
- High-risk employer identified
- Repeated violations detected
- LGA inspection performance below threshold

## 25.5 Federal Ministry Notifications

Notify when:

- State has abnormal critical finding rate
- Suspicious certificate trend detected
- State enforcement report overdue
- Major public health escalation recorded

---

# 26. Data Model Requirements

## 26.1 Inspection

```python
class Inspection(models.Model):
    id = models.UUIDField(primary_key=True)
    reference = models.CharField(max_length=100, unique=True)
    inspection_type = models.CharField(max_length=80)
    state = models.ForeignKey("geography.State", on_delete=models.PROTECT)
    lga = models.ForeignKey("geography.LGA", null=True, blank=True, on_delete=models.SET_NULL)
    employer = models.ForeignKey("employers.Employer", on_delete=models.PROTECT)
    branch = models.ForeignKey("organizations.OrganizationUnit", null=True, blank=True, on_delete=models.SET_NULL)
    assigned_inspector = models.ForeignKey("accounts.User", related_name="assigned_inspections", on_delete=models.PROTECT)
    assigned_by = models.ForeignKey("accounts.User", related_name="created_inspection_assignments", null=True, on_delete=models.SET_NULL)
    supervising_officer = models.ForeignKey("accounts.User", related_name="supervised_inspections", null=True, blank=True, on_delete=models.SET_NULL)
    priority = models.CharField(max_length=50)
    status = models.CharField(max_length=80)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    linked_complaint_id = models.UUIDField(null=True, blank=True)
    linked_illness_report_id = models.UUIDField(null=True, blank=True)
    parent_inspection = models.ForeignKey("self", null=True, blank=True, related_name="follow_up_inspections", on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 26.2 InspectionChecklistItem

```python
class InspectionChecklistItem(models.Model):
    id = models.UUIDField(primary_key=True)
    category = models.CharField(max_length=100)
    question = models.TextField()
    severity_if_failed = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 26.3 InspectionChecklistResponse

```python
class InspectionChecklistResponse(models.Model):
    id = models.UUIDField(primary_key=True)
    inspection = models.ForeignKey("inspections.Inspection", on_delete=models.CASCADE)
    checklist_item = models.ForeignKey("inspections.InspectionChecklistItem", on_delete=models.PROTECT)
    response = models.CharField(max_length=50)  # yes, no, n/a, not_observed, needs_follow_up
    severity = models.CharField(max_length=50, blank=True)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey("accounts.User", null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 26.4 InspectionCertificateVerification

```python
class InspectionCertificateVerification(models.Model):
    id = models.UUIDField(primary_key=True)
    inspection = models.ForeignKey("inspections.Inspection", on_delete=models.CASCADE)
    food_handler = models.ForeignKey("food_handlers.FoodHandlerProfile", null=True, blank=True, on_delete=models.SET_NULL)
    certificate = models.ForeignKey("certificates.Certificate", null=True, blank=True, on_delete=models.SET_NULL)
    certificate_number_attempted = models.CharField(max_length=100, blank=True)
    verification_token_attempted = models.CharField(max_length=255, blank=True)
    verification_result = models.CharField(max_length=80)
    identity_match_confirmed = models.BooleanField(default=False)
    issue_found = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)
    verified_by = models.ForeignKey("accounts.User", null=True, on_delete=models.SET_NULL)
    verified_at = models.DateTimeField(auto_now_add=True)
```

## 26.5 InspectionFinding

```python
class InspectionFinding(models.Model):
    id = models.UUIDField(primary_key=True)
    inspection = models.ForeignKey("inspections.Inspection", on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    finding_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=50)
    description = models.TextField()
    recommended_action = models.TextField(blank=True)
    food_handler = models.ForeignKey("food_handlers.FoodHandlerProfile", null=True, blank=True, on_delete=models.SET_NULL)
    certificate = models.ForeignKey("certificates.Certificate", null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=50)
    created_by = models.ForeignKey("accounts.User", null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 26.6 InspectionEvidence

```python
class InspectionEvidence(models.Model):
    id = models.UUIDField(primary_key=True)
    inspection = models.ForeignKey("inspections.Inspection", on_delete=models.CASCADE)
    finding = models.ForeignKey("inspections.InspectionFinding", null=True, blank=True, on_delete=models.CASCADE)
    evidence_type = models.CharField(max_length=50)
    file_url = models.URLField()
    caption = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey("accounts.User", null=True, on_delete=models.SET_NULL)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 26.7 EnforcementNotice

```python
class EnforcementNotice(models.Model):
    id = models.UUIDField(primary_key=True)
    notice_reference = models.CharField(max_length=100, unique=True)
    inspection = models.ForeignKey("inspections.Inspection", on_delete=models.CASCADE)
    employer = models.ForeignKey("employers.Employer", on_delete=models.PROTECT)
    branch = models.ForeignKey("organizations.OrganizationUnit", null=True, blank=True, on_delete=models.SET_NULL)
    notice_type = models.CharField(max_length=100)
    status = models.CharField(max_length=80)
    description = models.TextField()
    required_corrective_actions = models.TextField()
    deadline = models.DateField(null=True, blank=True)
    issued_by = models.ForeignKey("accounts.User", related_name="notices_issued", null=True, on_delete=models.SET_NULL)
    approved_by = models.ForeignKey("accounts.User", related_name="notices_approved", null=True, blank=True, on_delete=models.SET_NULL)
    issued_at = models.DateTimeField(null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    closure_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 26.8 CorrectiveActionResponse

```python
class CorrectiveActionResponse(models.Model):
    id = models.UUIDField(primary_key=True)
    notice = models.ForeignKey("inspections.EnforcementNotice", on_delete=models.CASCADE)
    submitted_by = models.ForeignKey("accounts.User", null=True, on_delete=models.SET_NULL)
    response_note = models.TextField()
    action_taken = models.TextField()
    status = models.CharField(max_length=80)
    reviewed_by = models.ForeignKey("accounts.User", related_name="corrective_actions_reviewed", null=True, blank=True, on_delete=models.SET_NULL)
    review_note = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
```

## 26.9 EnforcementCase

```python
class EnforcementCase(models.Model):
    id = models.UUIDField(primary_key=True)
    case_reference = models.CharField(max_length=100, unique=True)
    state = models.ForeignKey("geography.State", on_delete=models.PROTECT)
    employer = models.ForeignKey("employers.Employer", on_delete=models.PROTECT)
    branch = models.ForeignKey("organizations.OrganizationUnit", null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=80)
    severity = models.CharField(max_length=50)
    summary = models.TextField()
    opened_by = models.ForeignKey("accounts.User", related_name="enforcement_cases_opened", null=True, on_delete=models.SET_NULL)
    assigned_to = models.ForeignKey("accounts.User", related_name="enforcement_cases_assigned", null=True, blank=True, on_delete=models.SET_NULL)
    escalated_to = models.CharField(max_length=100, blank=True)
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    closure_note = models.TextField(blank=True)
```

---

# 27. API Requirements

## 27.1 Inspector Dashboard

```txt
GET /api/inspector/dashboard
GET /api/inspector/tasks
```

## 27.2 Inspection Assignment

```txt
GET    /api/inspections
POST   /api/inspections
GET    /api/inspections/:id
PATCH  /api/inspections/:id
POST   /api/inspections/:id/assign
POST   /api/inspections/:id/accept
POST   /api/inspections/:id/reschedule-request
POST   /api/inspections/:id/start
POST   /api/inspections/:id/submit
POST   /api/inspections/:id/return-for-correction
POST   /api/inspections/:id/close
POST   /api/inspections/:id/cancel
```

## 27.3 Employer/Branch Inspection Context

```txt
GET /api/inspections/:id/employer-context
GET /api/inspections/:id/branch-context
GET /api/inspections/:id/food-handlers
GET /api/inspections/:id/compliance-summary
```

## 27.4 Certificate Verification

```txt
POST /api/inspections/:id/certificate-verifications/scan
POST /api/inspections/:id/certificate-verifications/verify-by-number
GET  /api/inspections/:id/certificate-verifications
POST /api/inspections/:id/certificate-verifications/:verification_id/confirm-identity-match
POST /api/inspections/:id/certificate-verifications/:verification_id/flag-issue
```

## 27.5 Checklist

```txt
GET   /api/inspection-checklist-items
POST  /api/inspections/:id/checklist-responses
GET   /api/inspections/:id/checklist-responses
PATCH /api/inspections/:id/checklist-responses/:response_id
```

## 27.6 Findings and Evidence

```txt
GET    /api/inspections/:id/findings
POST   /api/inspections/:id/findings
GET    /api/inspections/:id/findings/:finding_id
PATCH  /api/inspections/:id/findings/:finding_id
POST   /api/inspections/:id/evidence
GET    /api/inspections/:id/evidence
DELETE /api/inspections/:id/evidence/:evidence_id
```

## 27.7 Notices

```txt
GET   /api/enforcement-notices
POST  /api/inspections/:id/notices
GET   /api/enforcement-notices/:id
PATCH /api/enforcement-notices/:id
POST  /api/enforcement-notices/:id/submit-for-approval
POST  /api/enforcement-notices/:id/approve
POST  /api/enforcement-notices/:id/issue
POST  /api/enforcement-notices/:id/acknowledge
POST  /api/enforcement-notices/:id/close
```

## 27.8 Corrective Actions

```txt
GET  /api/enforcement-notices/:id/corrective-actions
POST /api/enforcement-notices/:id/corrective-actions
POST /api/corrective-actions/:id/review
POST /api/corrective-actions/:id/accept
POST /api/corrective-actions/:id/reject
POST /api/corrective-actions/:id/request-more-evidence
```

## 27.9 Follow-Up and Escalation

```txt
POST /api/inspections/:id/create-follow-up
POST /api/inspections/:id/escalate
GET  /api/enforcement-cases
POST /api/enforcement-cases
GET  /api/enforcement-cases/:id
PATCH /api/enforcement-cases/:id
POST /api/enforcement-cases/:id/close
```

## 27.10 Dashboards and Reports

```txt
GET /api/state/enforcement/dashboard
GET /api/state/enforcement/reports/inspections
GET /api/state/enforcement/reports/notices
GET /api/state/enforcement/reports/corrective-actions
GET /api/state/enforcement/reports/critical-findings
GET /api/federal/enforcement/dashboard
GET /api/federal/enforcement/reports/summary
```

---

# 28. Frontend Routes

## 28.1 Inspector Routes

```txt
/app/inspector/dashboard
/app/inspector/tasks
/app/inspector/inspections
/app/inspector/inspections/[id]
/app/inspector/inspections/[id]/start
/app/inspector/inspections/[id]/scan
/app/inspector/inspections/[id]/food-handlers
/app/inspector/inspections/[id]/checklist
/app/inspector/inspections/[id]/findings
/app/inspector/inspections/[id]/evidence
/app/inspector/inspections/[id]/submit
```

## 28.2 Inspectorate Coordinator Routes

```txt
/app/state/inspectorate/dashboard
/app/state/inspectorate/assignments
/app/state/inspectorate/inspections
/app/state/inspectorate/inspections/[id]
/app/state/inspectorate/notices
/app/state/inspectorate/notices/[id]
/app/state/inspectorate/cases
/app/state/inspectorate/cases/[id]
/app/state/inspectorate/reports
```

## 28.3 Employer Routes

```txt
/app/employer/inspections
/app/employer/inspections/[id]
/app/employer/notices
/app/employer/notices/[id]
/app/employer/notices/[id]/respond
```

## 28.4 State Ministry Routes

```txt
/app/state/enforcement/dashboard
/app/state/enforcement/inspections
/app/state/enforcement/notices
/app/state/enforcement/corrective-actions
/app/state/enforcement/cases
/app/state/enforcement/reports
/app/state/enforcement/checklist-settings
```

## 28.5 Federal Ministry Routes

```txt
/app/federal/enforcement/dashboard
/app/federal/enforcement/states
/app/federal/enforcement/reports
```

---

# 29. Core Frontend Components

- InspectorDashboardCards
- InspectionTaskTable
- InspectionAssignmentForm
- InspectionStatusBadge
- EmployerBranchInspectionContext
- InspectorQRScanner
- ManualCertificateVerificationForm
- InspectorVerificationResultCard
- FoodHandlerInspectionList
- InspectionChecklistForm
- ChecklistSeverityBadge
- FindingForm
- FindingList
- EvidenceUploadPanel
- EvidenceGallery
- NoticeBuilder
- NoticeStatusBadge
- CorrectiveActionResponseForm
- CorrectiveActionReviewPanel
- EnforcementCaseTimeline
- FollowUpInspectionPanel
- EscalationModal
- StateEnforcementDashboardCards
- FederalEnforcementSummaryCards
- InspectionReportBuilder

---

# 30. Permissions and Access Control

## 30.1 Inspector

Can:

- View assigned inspections.
- Conduct assigned inspections.
- Scan certificates.
- Complete checklist.
- Add findings and evidence.
- Submit reports.
- Recommend notices/enforcement.

Cannot:

- View medical details.
- Change certificate status.
- Change payment/subscription status.
- Close escalated cases unless authorized.

## 30.2 Inspectorate Coordinator

Can:

- Assign inspections.
- Review reports.
- Approve or return reports.
- Issue/approve notices.
- Create follow-ups.
- Escalate cases.
- Close cases where permitted.

## 30.3 State Ministry Admin

Can:

- View all state inspections.
- Manage enforcement cases.
- Approve serious enforcement actions.
- Configure checklist templates.
- Generate state reports.

## 30.4 LGA Officer

Can:

- View and conduct inspections within assigned LGA.
- Submit findings.
- Track local corrective actions.

## 30.5 Employer

Can:

- View own inspections and notices.
- Respond to corrective actions.
- Upload evidence.

Cannot:

- Edit findings.
- See inspector internal notes unless shared.
- See other employers’ cases.

## 30.6 Federal Ministry

Can:

- View national aggregate enforcement metrics.
- View state summaries.
- Generate national reports.

Cannot:

- View medical details by default.
- Edit state inspection findings by default.

---

# 31. Privacy and Data Protection

## 31.1 Inspector Privacy Rules

Inspectors can see:

- Certificate status
- Food handler name
- Passport photo
- Certificate number
- Issue/expiry dates
- Employer/branch assignment
- Operational fitness status
- Return-to-work status

Inspectors cannot see:

- Lab results
- Doctor notes
- Diagnosis
- Declaration answers
- Full NIN
- Treatment details
- Payment details beyond high-level status where needed

## 31.2 Employer Privacy Rules

Employers can see:

- Inspection summary
- Notices
- Required corrective actions
- Deadlines
- Shared evidence
- Case status

Employers cannot see:

- Internal inspector review notes
- Other employers’ inspection records
- Sensitive medical data

## 31.3 Federal Privacy Rules

Federal views should be aggregate by default. Individual enforcement case access should depend on permission and should still exclude medical details.

---

# 32. Audit Logs

Create audit logs for:

- Inspection assignment created
- Inspector assigned/reassigned
- Inspection accepted
- Inspection started
- Certificate scanned
- Manual certificate verification
- Identity match confirmed
- Certificate issue flagged
- Checklist response created/updated
- Finding created/updated
- Evidence uploaded/deleted
- Inspection submitted
- Inspection returned for correction
- Notice drafted
- Notice approved
- Notice issued
- Notice acknowledged
- Employer response submitted
- Corrective action reviewed
- Follow-up inspection created
- Case escalated
- Case closed
- Sensitive enforcement record viewed

---

# 33. Background Jobs

## 33.1 Inspection Reminder Job

Runs daily/hourly.

Tasks:

- Notify inspectors of inspections due today.
- Notify inspectors of overdue inspections.
- Notify coordinators of overdue assignments.

## 33.2 Notice Deadline Job

Runs daily.

Tasks:

- Notify employers of upcoming corrective action deadlines.
- Mark overdue notices.
- Notify coordinators of overdue corrective actions.
- Escalate overdue critical notices based on policy.

## 33.3 Follow-Up Reminder Job

Runs daily.

Tasks:

- Notify coordinators of follow-up inspections due.
- Notify inspectors of assigned follow-ups.

## 33.4 Enforcement Analytics Job

Runs daily.

Tasks:

- Recalculate state inspection metrics.
- Recalculate employer compliance trends.
- Identify repeated violations.
- Identify suspicious certificate patterns.

---

# 34. Acceptance Criteria

## 34.1 Inspection Assignment

- Coordinator can create inspection assignment.
- Inspector receives assigned inspection.
- Inspector can accept/start inspection.
- Assignment respects state/LGA scope.
- Assignment creation is audit logged.

## 34.2 Certificate Verification

- Inspector can scan QR code.
- Inspector can verify certificate by number.
- Verification returns inspector-safe result.
- Verification result can be saved to inspection.
- Invalid/expired/suspended/revoked certificates can be flagged.
- Verification does not expose medical data.
- Verification attempt is logged.

## 34.3 Checklist and Findings

- Inspector can complete checklist.
- Failed checklist items can create findings.
- Findings can be assigned severity.
- Evidence can be attached to findings.
- Checklist and findings are saved to inspection record.

## 34.4 Notices and Corrective Actions

- Inspector/coordinator can create notice from findings.
- Notice can require approval.
- Employer can view notice.
- Employer can submit corrective action response.
- Coordinator can accept/reject/request more evidence.
- Overdue corrective actions are flagged.

## 34.5 Follow-Up and Escalation

- Follow-up inspections can be created from open findings/notices.
- Follow-up links to original inspection.
- Serious cases can be escalated.
- Enforcement case timeline shows all related actions.

## 34.6 Dashboards and Reports

- Inspector can view personal task dashboard.
- State can view enforcement dashboard.
- Federal can view aggregate enforcement dashboard.
- Reports can be exported.
- Exports respect privacy rules.

## 34.7 Privacy

- Inspectors cannot see lab results, doctor notes, diagnosis, declaration answers, or full NIN.
- Employers cannot edit inspection findings.
- Federal dashboards are aggregate by default.
- Sensitive access is audit logged.

---

# 35. Shared Dependencies With Payments Module and Other Modules

This section should be shared with both the Payments team and Inspector & Enforcement team before simultaneous development begins.

## 35.1 Dependency Summary

The Inspector & Enforcement Module can be built alongside the Payments, Subscriptions & Settlements Module, but both teams must agree on shared contracts.

The Inspector module should **consume** payment and subscription statuses but should **not own or update** financial logic.

## 35.2 Shared Data Models

The following models must be stable or have agreed interfaces:

```txt
Employer
OrganizationUnit as Branch
FoodHandlerProfile
Certificate
MedicalAssessment
EmployerSubscription
PaymentTransaction
AuditLog
User
Role/Permission
State
LGA
```

## 35.3 Employer and Branch Contract

Both modules must use the same employer/branch references.

Required shared fields:

```txt
employer.id
employer.name
employer.status
employer.establishment_category
branch.id
branch.name
branch.unit_type = branch
branch.state
branch.lga
branch.address
branch.status
```

Rule:

- Payments owns employer subscription and billing status.
- Inspector module reads subscription status as compliance context only.
- Inspector module must not update subscription records.

## 35.4 Food Handler Compliance Contract

Inspector module needs read-only access to operational compliance fields.

Required shared fields:

```txt
food_handler.id
food_handler.full_name
food_handler.passport_photo_url
food_handler.employer_id
food_handler.branch_id
food_handler.certificate_status
food_handler.fitness_status
food_handler.vaccination_status
food_handler.return_to_work_status
```

Inspector module must not expose:

```txt
lab_results
doctor_notes
diagnosis
health_declaration_answers
full_nin
```

## 35.5 Certificate Verification API Contract

The Certificate module must provide inspector-safe verification endpoints.

Required endpoint:

```txt
GET /api/inspector/certificates/verify/:verification_token
POST /api/inspector/certificates/verify-by-number
```

Required response shape:

```json
{
  "verification_result": "valid | expired | suspended | revoked | not_found | invalid | tamper_suspected",
  "certificate_id": "uuid-or-null",
  "certificate_number": "string-or-null",
  "food_handler": {
    "id": "uuid-or-null",
    "full_name": "string",
    "passport_photo_url": "url"
  },
  "issuing_state": "string",
  "facility_name": "string",
  "issue_date": "date",
  "expiry_date": "date",
  "fitness_status": "fit_to_work | expired | suspended | revoked | unknown",
  "privacy_level": "inspector_safe"
}
```

This response must not include medical details.

## 35.6 Subscription Status Contract

The Payments module owns subscription data.

Inspector module may read:

```txt
subscription_status = active | trial | past_due | expired | suspended | cancelled | unknown
billing_status = current | overdue | unpaid | not_required | unknown
```

Inspector module must not update:

```txt
subscription_plan
payment_status
invoice_status
settlement_status
billing_cycle
amount_paid
gateway_reference
```

## 35.7 Assessment Payment Status Contract

Inspectors usually do not need payment details, but may need to know whether a certificate or assessment is legitimate.

Allowed read-only status:

```txt
assessment_payment_status = confirmed | pending | failed | refunded | not_required
```

Inspector module must not display transaction amounts by default and must not allow financial actions.

## 35.8 Compliance Status Contract

Create a unified compliance status service used by employer dashboards, inspector workflows, and reports.

Recommended service:

```txt
ComplianceStatusService.get_branch_compliance_summary(branch_id)
ComplianceStatusService.get_employer_compliance_summary(employer_id)
ComplianceStatusService.get_food_handler_operational_status(food_handler_id)
```

Recommended branch summary response:

```json
{
  "employer_id": "uuid",
  "branch_id": "uuid",
  "total_food_handlers": 0,
  "active_certificates": 0,
  "expired_certificates": 0,
  "suspended_certificates": 0,
  "revoked_certificates": 0,
  "uncertified_food_handlers": 0,
  "temporarily_not_fit": 0,
  "return_to_work_pending": 0,
  "vaccination_due": 0,
  "subscription_status": "active",
  "overall_compliance_status": "compliant | partially_compliant | non_compliant | high_risk"
}
```

## 35.9 Audit Log Contract

Both modules must use a shared audit log format.

Recommended fields:

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

Recommended module names:

```txt
payments
subscriptions
settlements
inspections
enforcement
certificates
assessments
employers
```

## 35.10 Notification Contract

Both modules should use the shared notification system.

Shared notification channels:

```txt
in_app
email
sms
whatsapp
```

Inspector module notification events:

```txt
inspection_assigned
inspection_due
notice_issued
corrective_action_due
corrective_action_overdue
case_escalated
```

Payments module notification events:

```txt
payment_successful
payment_failed
subscription_expiring
subscription_expired
settlement_paid
settlement_failed
```

## 35.11 Permissions Contract

Shared roles and permission naming should be consistent.

Inspector permissions:

```txt
inspection.view
inspection.create
inspection.assign
inspection.conduct
inspection.submit
inspection.review
inspection.close
inspection.escalate
notice.create
notice.approve
notice.issue
notice.close
corrective_action.review
certificate.verify
```

Payments permissions:

```txt
payment.view
payment.initiate
payment.refund
subscription.view
subscription.manage
settlement.view
settlement.reconcile
```

Rule:

- Inspector role should have `certificate.verify`.
- Inspector role should not have payment mutation permissions.
- Finance users should not have inspection mutation permissions unless separately assigned.

## 35.12 Parallel Build Recommendation

### Payments Team Should Build

- PaymentTransaction model
- Assessment payment workflow
- EmployerSubscription model
- SubscriptionPlan model
- Payment gateway abstraction
- Webhook handler
- Receipt generation
- Settlement ledger
- Subscription status API

### Inspector Team Should Build

- Inspection model
- Inspection assignment workflow
- Inspector dashboard
- QR verification integration
- Branch compliance view
- Checklist and findings
- Evidence upload
- Notices and corrective actions
- Enforcement case workflow
- State/Federal enforcement dashboards

### Integration Checkpoints

Before merging both modules, run integration tests for:

1. Inspector can read employer subscription status but cannot update it.
2. Inspector can verify certificate using certificate API.
3. Inspector can view branch compliance summary.
4. Inspector cannot view medical details.
5. Inspector cannot view payment amounts or settlement details by default.
6. Employer can respond to notice.
7. Payment webhook cannot affect inspection records directly.
8. Enforcement notice cannot change subscription status directly.
9. Shared audit logs are created correctly.
10. Dashboards use the same compliance summary service.

---

# 36. Codex Implementation Instructions

Use this prompt for Codex:

```txt
Implement the Inspector & Enforcement Module for FoodCert NG.

The module must support inspection assignments, inspector dashboard, employer and branch inspection context, QR certificate scanning, manual certificate verification, inspector-safe verification results, food handler verification list, inspection checklist, inspection findings, evidence upload, enforcement notices, corrective action workflow, follow-up inspections, escalation workflow, enforcement case management, state enforcement dashboard, federal enforcement summary, reports, notifications, permissions, privacy controls, and audit logs.

Important rules:
- Inspectors must not see lab results, diagnosis, doctor notes, declaration answers, or full NIN.
- Inspectors can verify certificate authenticity using the Certificate module.
- Inspectors can read employer subscription status but must not update payment/subscription records.
- Employer/branch data must use existing Employer and OrganizationUnit branch models.
- Food handler operational statuses must come from shared compliance status service.
- Certificate verification response must be inspector-safe.
- Notices and corrective actions must be linked to inspections and employers/branches.
- Serious non-compliance can create enforcement cases and follow-up inspections.
- All verification attempts and enforcement actions must be audit logged.

Build backend models, serializers, permissions, services, API endpoints, background jobs, tests, and frontend pages for the module.
```

---

# 37. MVP Build Order

1. Inspection model
2. Inspection assignment API
3. Inspector dashboard
4. Employer/branch inspection context
5. Certificate verification integration
6. Inspection certificate verification log
7. Food handler verification list
8. Inspection checklist items
9. Checklist response workflow
10. Findings workflow
11. Evidence upload
12. Submit inspection report
13. Coordinator review workflow
14. Notice builder
15. Notice issuance workflow
16. Employer notice view and response
17. Corrective action review
18. Follow-up inspection creation
19. Enforcement case creation
20. State enforcement dashboard
21. Federal enforcement summary
22. Background reminder jobs
23. Shared dependency integration tests
24. Privacy and permission tests
25. Audit log tests
