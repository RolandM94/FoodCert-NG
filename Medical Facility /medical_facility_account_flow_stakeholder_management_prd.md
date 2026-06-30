# PRD: Medical Facility Account Flow & Stakeholder Management

**Application:** FoodCert / National Food Handlers Medical Test Platform  
**Module:** Medical Facility Operations, Stakeholder Management, Role-Based Permissions, Assessment Processing  
**Primary Users:** Medical Facility Admin, Doctors, Lab Technicians, Front Desk Officers, Finance Officers, Records Officers, Compliance Officers, State Account, Federal Account  

---

## 1. Product Objective

Develop a full **Medical Facility Account workflow** that allows approved facilities to manage their internal team members, roles, permissions, appointments, check-ins, medical assessments, lab result input, doctor reviews, certificate/report generation, audit logs, and facility-level compliance.

The Medical Facility account should operate as a regulated service provider account. It should not only upload test results; it should manage the entire facility-side process from booking receipt to final doctor-reviewed decision.

Core facility-side flow:

```text
Facility approved by State
    ↓
Facility Admin configures team and roles
    ↓
Facility invites doctors, lab technicians, front desk, finance, records, and compliance users
    ↓
Food handler/employer books appointment
    ↓
Facility receives booking
    ↓
Front desk verifies identity and checks in food handler
    ↓
Doctor validates declaration
    ↓
Doctor conducts physical examination
    ↓
Lab technician enters lab results
    ↓
Doctor reviews lab results
    ↓
System recommends decision
    ↓
Doctor confirms Fit / Temporarily Unfit / Further Review
    ↓
System generates certificate or report
    ↓
Facility, food handler, employer, State, and Federal dashboards update
```

---

## 2. Facility Onboarding and Approval Flow

Before a medical facility can receive bookings or process food handler assessments, it must be approved by the relevant State account.

```text
Medical Facility registers or is created by State
        ↓
Facility submits profile and accreditation documents
        ↓
State reviews and approves facility
        ↓
Facility is mapped to State / LGA
        ↓
Facility becomes visible in food handler directory
        ↓
Facility can receive bookings
```

### 2.1 Facility Profile Fields

| Field | Description |
|---|---|
| Facility name | Legal facility name |
| Facility type | Hospital, clinic, diagnostic centre, PHC, mobile unit |
| State | Jurisdiction mapping |
| LGA | Local government mapping |
| Address | Physical location |
| GPS coordinates | For “near me” search |
| Accreditation status | Pending, approved, suspended, expired |
| Accreditation expiry | Annual renewal date |
| Contact officer | Facility representative |
| Available services | Food Handler Medical Test Package |
| Package price | State-approved price |
| Operating hours | Appointment availability |
| Licence / registration documents | Uploaded evidence |

### 2.2 Business Rules

| Rule | Logic |
|---|---|
| Only approved facilities can receive bookings | Yes |
| Suspended facilities cannot accept new appointments | Yes |
| Expired facilities cannot issue certificates | Yes |
| Facility must be mapped to a State | Yes |
| Facility can only operate under approved jurisdiction | Yes |
| Facility cannot remove mandatory Federal/State tests | Yes |

---

## 3. Facility Stakeholder / Team Management Tool

Each medical facility account must have a **Stakeholder Management** or **Team Management** section where the facility can manage its internal users and permissions.

```text
Facility Admin opens Stakeholder Management
        ↓
Creates or selects facility roles
        ↓
Defines permissions for each role
        ↓
Invites team members
        ↓
Assigns role to each team member
        ↓
Team member accepts invite
        ↓
Team member completes professional profile where required
        ↓
Team member gets access based on assigned permissions
```

## 3.1 Default Facility Roles

The system should provide default roles, while allowing facility admins to create custom roles within protected permission limits.

| Role | Main Responsibility |
|---|---|
| Facility Owner / Super Admin | Full control of facility account |
| Facility Administrator | Manages bookings, team, facility settings |
| Front Desk / Reception Officer | Handles appointments, check-in, identity verification |
| Medical Doctor | Validates declaration, conducts physical exam, confirms final decision |
| Lab Technician / Lab Scientist | Records lab samples and inputs test results |
| Lab Supervisor | Reviews or validates lab result entries where enabled |
| Finance / Billing Officer | Confirms payments, manages invoices and receipts |
| Records Officer | Manages documentation and assessment records |
| Compliance Officer | Ensures facility follows policy and reporting rules |
| Viewer / Auditor | Read-only access for audits |

---

## 4. Facility Role and Permission Builder

The facility should be able to create custom roles, but permissions must be restricted by professional category and Federal/State system rules.

Example custom roles:

```text
Senior Doctor
Junior Doctor
Lab Data Entry Officer
Lab Reviewer
Front Desk Supervisor
Facility Compliance Officer
Assessment Coordinator
```

## 4.1 Permission Categories

| Permission Category | Example Permissions |
|---|---|
| Facility Profile | View profile, edit profile, upload documents |
| Team Management | Invite user, remove user, create role, assign role |
| Appointment Management | View bookings, confirm appointments, cancel appointment |
| Check-In | Verify identity, check in food handler, flag identity mismatch |
| Health Declaration | View declaration, request correction, validate declaration |
| Physical Examination | Create exam record, edit own exam record, submit exam |
| Lab Tests | View lab requests, enter results, upload result file, submit lab result |
| Doctor Review | View full assessment, review lab results, confirm final decision |
| Certificate | View generated certificates |
| Temporary Unfit Report | Generate/view report according to permissions |
| Finance | View payments, confirm pay-at-facility, issue receipt |
| Compliance | View facility compliance dashboard, view audit logs |
| Reporting | Export facility reports, submit facility reports |
| Audit | View activity logs |

## 4.2 Protected Permissions

Some permissions must be locked by professional category. A facility admin can create roles, but cannot assign doctor-only permissions to non-doctors.

| Protected Permission | Requirement |
|---|---|
| `declaration.validate` | Professional category must be doctor |
| `physical_exam.create` | Professional category must be doctor |
| `doctor_review.final_decision` | Professional category must be doctor |
| `lab_results.create` | Professional category must be lab technician/scientist/supervisor |
| `lab_results.submit` | Professional category must be lab technician/scientist/supervisor |
| `facility.roles.assign_permissions` | Facility Admin / Owner only |
| `certificate.generate` | System-triggered after doctor Fit decision |

## 4.3 Recommended Default Facility Permission Matrix

| Action | Facility Admin | Front Desk | Doctor | Lab Technician | Lab Supervisor | Finance | Records | Compliance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Manage facility profile | Yes | No | No | No | No | No | No | View |
| Invite team members | Yes | No | No | No | No | No | No | No |
| Create custom roles | Yes | No | No | No | No | No | No | No |
| Assign permissions | Yes | No | No | No | No | No | No | No |
| View appointments | Yes | Yes | Yes | Limited | Limited | Yes | Yes | Yes |
| Confirm appointments | Yes | Yes | No | No | No | No | No | No |
| Check in food handler | Yes | Yes | Optional | No | No | No | Optional | No |
| Verify identity | Yes | Yes | Optional | No | No | No | Optional | No |
| View health declaration | Yes | Limited | Yes | No | No | No | Limited | Limited |
| Validate declaration | No | No | Yes | No | No | No | No | No |
| Conduct physical exam | No | No | Yes | No | No | No | No | No |
| View lab requests | Yes | No | Yes | Yes | Yes | No | Yes | Yes |
| Enter lab result | No | No | No | Yes | Yes | No | No | No |
| Submit lab result | No | No | No | Yes | Yes | No | No | No |
| Review lab result | No | No | Yes | No | Optional | No | No | No |
| Confirm final decision | No | No | Yes | No | No | No | No | No |
| View certificate | Yes | No | Yes | No | No | No | Yes | View |
| View unfit report | Yes | No | Yes | No | No | No | Limited | View |
| View payments | Yes | No | No | No | No | Yes | No | No |
| Confirm pay-at-facility | Yes | No | No | No | No | Yes | No | No |
| View audit logs | Yes | No | No | No | No | No | No | Yes |

---

## 5. Facility Team Member Invitation Flow

```text
Facility Admin opens Team Management
        ↓
Clicks “Invite Team Member”
        ↓
Enters name, email/phone, professional category
        ↓
Selects role
        ↓
System validates role requirements
        ↓
Invite is sent
        ↓
Team member accepts invite
        ↓
Team member completes profile
        ↓
If doctor/lab user, professional licence details are required
        ↓
Facility Admin activates member
```

### 5.1 Required Team Member Fields

| Field | Required |
|---|---|
| Full name | Yes |
| Email / phone | Yes |
| Role | Yes |
| Professional category | Yes |
| Licence number | Required for doctors/lab users |
| Licence issuing body | Required for clinical users |
| Licence document | Required for clinical users |
| Department / unit | Optional |
| Status | Invited, active, suspended, removed |

### 5.2 Team Member Statuses

```text
Invited
Pending Profile Completion
Pending Licence Verification
Active
Suspended
Removed
Deactivated
```

---

## 6. Facility Appointment Management Flow

Once approved, a facility receives bookings from food handlers and employers.

```text
Facility receives booking notification
        ↓
Facility dashboard shows new appointment
        ↓
Facility views food handler profile summary
        ↓
Facility views declaration status
        ↓
Facility confirms appointment slot where required
        ↓
Food handler arrives
        ↓
Front desk checks in food handler
```

### 6.1 Appointment List Fields

| Field | Description |
|---|---|
| Appointment ID | Unique booking number |
| Assessment ID | Linked medical assessment |
| Food handler name | Linked profile |
| Employer | If applicable |
| Appointment date/time | Booking slot |
| Payment status | Paid, unpaid, pay-at-facility |
| Declaration status | Missing, submitted, validated |
| Assessment status | Current workflow stage |
| Assigned doctor | Optional |
| Assigned lab unit/technician | Optional |
| Action buttons | Based on user permissions |

---

## 7. Facility Check-In and Identity Verification Flow

```text
Front Desk opens appointment
        ↓
Verifies food handler identity
        ↓
Checks NIN / DOB / passport photo
        ↓
Confirms attendance
        ↓
System marks assessment as Checked In
        ↓
Doctor can begin declaration validation
```

### 7.1 Identity Verification Checks

| Check | Logic |
|---|---|
| Passport photo match | Required |
| NIN match | Required |
| DOB match | Required |
| Appointment ownership | Food handler must match assessment |
| Employer link | Optional but visible if employer initiated |

### 7.2 Identity Mismatch Flow

```text
Identity mismatch detected
        ↓
Assessment is paused
        ↓
Facility flags case
        ↓
State/Federal audit log is updated
        ↓
No test or certificate can proceed
```

---

## 8. Doctor Workflow Inside Facility Account

The doctor should have a dedicated assessment queue.

```text
Doctor logs in
        ↓
Views assigned assessments
        ↓
Opens food handler case
        ↓
Reviews health declaration
        ↓
Validates / rejects / requests correction
        ↓
Conducts physical examination
        ↓
Requests lab tests
        ↓
Reviews lab results
        ↓
Confirms final decision
```

### 8.1 Doctor Dashboard Queues

| Queue | Description |
|---|---|
| Pending declaration validation | Declarations awaiting doctor review |
| Pending physical examination | Checked-in food handlers |
| Awaiting lab results | Cases waiting for lab |
| Lab results submitted | Cases ready for doctor review |
| Further review required | Cases needing follow-up |
| Completed today | Finalized assessments |

### 8.2 Doctor Actions

| Action | Rule |
|---|---|
| View assigned assessment | Doctor must belong to facility and be assigned or have override permission |
| Validate declaration | Doctor-only permission |
| Request correction | Doctor-only permission |
| Conduct physical examination | Doctor-only permission |
| Request lab tests | Doctor-only permission |
| Review lab result | Doctor-only permission or permitted lab supervisor review |
| Confirm final decision | Doctor-only permission |

---

## 9. Lab Technician / Lab Scientist Flow

```text
Lab technician logs in
        ↓
Views assigned lab requests
        ↓
Collects sample
        ↓
Records sample collection details
        ↓
Conducts test
        ↓
Inputs structured result
        ↓
Uploads supporting lab document
        ↓
Submits result
        ↓
Doctor is notified
```

### 9.1 Lab Result Fields

| Field | Description |
|---|---|
| Test name | Auto-generated from package |
| Sample type | Stool, blood, etc. |
| Sample collection date/time | Required |
| Result date/time | Required |
| Result status | Normal, abnormal, positive, negative, inconclusive |
| Organism detected | Conditional |
| Sensitivity result | Conditional |
| Lab notes | Optional |
| Result file upload | Required or optional by policy |
| Lab officer | Auto-recorded |
| Licence number | Required |
| Submission timestamp | Auto |

### 9.2 Lab Rules

| Rule | Logic |
|---|---|
| Lab technician cannot validate declaration | Yes |
| Lab technician cannot conduct physical examination | Yes |
| Lab technician cannot confirm fit/unfit decision | Yes |
| Lab technician cannot issue certificate | Yes |
| Lab technician can only enter assigned lab result | Yes |
| Lab result edit after submission requires correction workflow | Yes |

---

## 10. Medical Facility Assessment Workflow

Full facility-side flow:

```text
1. Facility is approved by State.

2. Facility admin configures team roles and permissions.

3. Facility admin invites doctors, lab technicians, front desk officers, finance officers, records officers, and compliance officers.

4. Food handler/employer books appointment with facility.

5. Facility receives booking.

6. Facility confirms or manages appointment.

7. Food handler submits declaration before appointment.

8. Food handler arrives at facility.

9. Front desk verifies identity and checks in food handler.

10. Doctor validates health declaration.

11. Doctor conducts physical examination.

12. Doctor requests required lab tests.

13. Lab technician collects samples and inputs structured results.

14. Lab technician submits lab results.

15. Doctor reviews lab results.

16. System recommends Fit, Temporarily Unfit, or Further Review.

17. Doctor confirms final decision.

18. If Fit, system generates QR-coded Certificate of Fitness.

19. If Temporarily Unfit, system generates Temporary Unfit Report.

20. Certificate/report is stored in central database.

21. Facility dashboard updates.

22. Food handler, employer, State, and Federal dashboards update.
```

---

## 11. Facility Internal Case Assignment

The facility should be able to assign cases internally.

```text
Facility receives appointment
        ↓
Facility Admin assigns doctor
        ↓
Doctor validates declaration and performs exam
        ↓
Facility Admin or Doctor assigns lab unit/lab technician
        ↓
Lab technician enters result
        ↓
Doctor reviews final case
```

### 11.1 Assignment Rules

| Rule | Logic |
|---|---|
| Facility Admin can assign cases | Yes |
| Doctor can self-claim unassigned cases | Optional |
| Lab Supervisor can assign lab requests | Optional |
| Only assigned users can edit case sections | Recommended |
| Facility Admin can reassign cases | Yes, with audit log |
| Reassignment after submission requires reason | Yes |

---

## 12. Facility Account Settings

Medical facilities should have settings for:

| Setting | Description |
|---|---|
| Facility profile | Basic facility information |
| Accreditation details | Approval status, expiry, documents |
| Team management | Users and roles |
| Appointment availability | Working hours, slots, capacity |
| Package settings | View approved package and price |
| Payment settings | Online payment/pay-at-facility if enabled |
| Notification settings | Email, SMS, in-app |
| Report settings | Facility operational reports |
| Audit logs | All account actions |

The facility should be able to **view** the approved test package and price, but should not be able to remove mandatory tests defined by Federal/State policy.

---

## 13. Facility Dashboard

### 13.1 Dashboard Widgets

| Widget | Description |
|---|---|
| Today’s appointments | Bookings for current day |
| Pending declaration validation | Cases waiting for doctor |
| Checked-in food handlers | Currently at facility |
| Awaiting lab results | Tests pending lab entry |
| Doctor review pending | Results ready for doctor decision |
| Certificates generated | Fit certificates issued |
| Temporary unfit reports | Unfit reports issued |
| No-shows | Missed appointments |
| Payment pending | Unpaid/pay-at-facility cases |
| Staff activity | Actions by team members |
| Compliance alerts | Expiring accreditation, overdue lab result, etc. |

---

## 14. Facility Audit Logs

Every action must be audit logged.

| Action | Actor |
|---|---|
| Team member invited | Facility admin |
| Role created/updated | Facility admin |
| Permission changed | Facility admin |
| Appointment confirmed | Front desk/admin |
| Food handler checked in | Front desk |
| Identity mismatch flagged | Front desk/admin |
| Declaration validated | Doctor |
| Declaration reopened | Doctor |
| Physical examination submitted | Doctor |
| Lab result entered | Lab technician |
| Lab result edited | Lab technician/supervisor |
| Lab result submitted | Lab technician |
| Final decision confirmed | Doctor |
| Certificate generated | System |
| Temporary unfit report generated | System/doctor |
| Case reassigned | Facility admin |
| Payment confirmed | Finance officer |

---

# 15. Implementation Chunks for Codex

## Chunk 1: Facility Team and Role Models

```text
Implement Medical Facility stakeholder/team management models.

Create or extend tables/models for:
- facility_team_members
- facility_roles
- facility_role_permissions
- facility_invitations
- facility_user_professional_profiles

facility_team_members should include:
- id
- facility_id
- user_id
- role_id
- professional_category: doctor, lab_technician, lab_scientist, front_desk, finance, records, compliance, admin
- status: invited, pending_profile, pending_license_verification, active, suspended, removed
- invited_by
- accepted_at
- created_at
- updated_at

facility_roles should include:
- id
- facility_id
- name
- description
- is_system_default
- is_custom
- created_by
- created_at
- updated_at

facility_role_permissions should include:
- id
- role_id
- permission_key
- allowed boolean

facility_user_professional_profiles should include:
- user_id
- facility_id
- professional_category
- license_number
- license_issuing_body
- license_document_url
- verification_status
```

## Chunk 2: Facility Default Roles and Permissions

```text
Seed default medical facility roles and permissions.

Default roles:
1. Facility Owner / Super Admin
2. Facility Administrator
3. Front Desk / Reception Officer
4. Medical Doctor
5. Lab Technician / Lab Scientist
6. Lab Supervisor
7. Finance / Billing Officer
8. Records Officer
9. Compliance Officer
10. Viewer / Auditor

Create permission keys for:
- facility.profile.view
- facility.profile.edit
- facility.team.invite
- facility.team.remove
- facility.roles.create
- facility.roles.edit
- facility.roles.assign_permissions
- appointments.view
- appointments.confirm
- appointments.cancel
- assessment.check_in
- assessment.verify_identity
- declaration.view
- declaration.validate
- declaration.request_correction
- physical_exam.create
- lab_requests.view
- lab_results.create
- lab_results.submit
- lab_results.review
- doctor_review.view
- doctor_review.final_decision
- certificates.view
- unfit_reports.view
- finance.view_payments
- finance.confirm_payment
- compliance.view_dashboard
- audit_logs.view

Protect clinical permissions:
- declaration.validate requires professional_category = doctor
- physical_exam.create requires professional_category = doctor
- doctor_review.final_decision requires professional_category = doctor
- lab_results.create requires professional_category in lab_technician, lab_scientist, lab_supervisor
```

## Chunk 3: Facility Team Management UI

```text
Build Facility Stakeholder Management UI.

Pages:
- /facility/team
- /facility/team/invite
- /facility/team/:memberId
- /facility/roles
- /facility/roles/new
- /facility/roles/:roleId/edit

Features:
1. Facility admin can view all team members.
2. Facility admin can invite team member by email/phone.
3. Facility admin selects role and professional category.
4. If professional category is doctor or lab user, require licence number and issuing body.
5. Team member accepts invite and completes profile.
6. Facility admin can activate, suspend, remove, or reassign role.
7. Facility admin can create custom roles.
8. Facility admin can assign permissions to custom roles.
9. UI should block protected permissions if role/professional type is not eligible.
10. All team actions must be audit logged.
```

## Chunk 4: Facility Appointment Dashboard

```text
Build Medical Facility appointment dashboard.

Pages:
- /facility/dashboard
- /facility/appointments
- /facility/appointments/:appointmentId
- /facility/assessments/:assessmentId

Appointment list should show:
- appointment ID
- food handler name
- employer if applicable
- appointment date/time
- payment status
- declaration status
- assessment status
- assigned doctor
- assigned lab technician
- actions allowed by user permissions

Features:
1. Facility users with appointments.view can view appointments.
2. Users with appointments.confirm can confirm appointment.
3. Users with assessment.check_in can check in food handler.
4. Dashboard widgets should show today’s appointments, pending declarations, checked-in handlers, awaiting lab results, doctor review pending, completed assessments.
```

## Chunk 5: Facility Check-In and Identity Verification

```text
Implement facility check-in and identity verification.

Requirements:
1. Only users with assessment.check_in and assessment.verify_identity can check in food handlers.
2. Display food handler profile: name, NIN, DOB, passport photo, employer if applicable.
3. Facility staff confirms identity match.
4. If verified, set assessment status to Checked In or Assessment In Progress.
5. If mismatch, allow staff to flag identity mismatch and pause assessment.
6. Identity mismatch should prevent lab result entry and certificate generation.
7. Audit log check-in and identity mismatch events.
```

## Chunk 6: Internal Case Assignment

```text
Implement facility internal case assignment.

Requirements:
1. Facility Admin can assign doctor to an assessment.
2. Facility Admin or Doctor can assign lab technician/lab unit after physical exam.
3. Assigned doctor sees assessment in their queue.
4. Assigned lab technician sees lab requests in their queue.
5. Reassignment requires reason if work has already started.
6. Only assigned clinical users can edit their respective sections unless user has admin override permission.
7. Audit log all assignments and reassignments.
```

## Chunk 7: Doctor Workspace

```text
Build Medical Doctor workspace inside facility account.

Pages:
- /facility/doctor
- /facility/doctor/declarations
- /facility/doctor/assessments/:assessmentId
- /facility/doctor/reviews

Features:
1. Doctor sees assigned cases.
2. Doctor can validate declaration if permission declaration.validate exists and professional_category = doctor.
3. Doctor can request correction or reject declaration.
4. Doctor can complete physical examination checklist.
5. Doctor can request required lab tests.
6. Doctor can view submitted lab results.
7. Doctor sees system recommendation.
8. Doctor confirms final decision: Fit, Temporarily Unfit, or Further Review.
9. Doctor notes are stored as private medical data.
10. Audit log every doctor action.
```

## Chunk 8: Lab Technician Workspace

```text
Build Lab Technician/Lab Scientist workspace.

Pages:
- /facility/lab
- /facility/lab/requests
- /facility/lab/requests/:requestId
- /facility/lab/results/:resultId

Features:
1. Lab users see assigned lab requests.
2. Lab user records sample collection date/time.
3. Lab user inputs structured results:
   - result status
   - organism detected
   - sensitivity result
   - lab notes
   - supporting result file upload
4. Lab user submits result for doctor review.
5. Lab user cannot validate declaration, conduct physical exam, confirm final decision, or generate certificate.
6. Submitted results are locked unless correction workflow is triggered.
7. Audit log result entry, upload, submission, and correction.
```

## Chunk 9: Facility Finance and Payment Confirmation

```text
Implement facility finance/payment confirmation workflow.

Requirements:
1. Users with finance.view_payments can view assessment payment status.
2. Users with finance.confirm_payment can confirm pay-at-facility payments if enabled.
3. Payment statuses: unpaid, pending, paid, failed, waived, refunded.
4. Appointment cannot move to confirmed unless payment is paid or pay-at-facility is allowed.
5. Payment confirmation should generate receipt reference.
6. Payment actions must be audit logged.
```

## Chunk 10: Facility Compliance and Audit Logs

```text
Build facility compliance and audit log pages.

Pages:
- /facility/compliance
- /facility/audit-logs

Compliance dashboard should show:
- total assessments
- certificates generated
- temporary unfit reports
- pending lab results
- overdue doctor reviews
- pending declaration validations
- staff activity
- accreditation expiry countdown
- suspended/expired status warnings

Audit logs should be filterable by:
- actor
- role
- action
- assessment ID
- date range
- entity type

Only users with audit_logs.view can access audit logs.
```

## Chunk 11: Facility Certificate and Report Access

```text
Implement facility certificate and temporary unfit report access.

Requirements:
1. Facility users with certificates.view can view certificates generated from their facility.
2. Facility users with unfit_reports.view can view temporary unfit reports subject to privacy permissions.
3. Facility cannot manually generate certificate without doctor final decision = Fit.
4. Certificate generation remains system-triggered after doctor approval.
5. Facility can download certificate/report where permissions allow.
6. Employer view remains status-only for unfit cases.
```

## Chunk 12: Permission Enforcement Middleware

```text
Implement permission enforcement middleware for facility account.

Requirements:
1. Every facility route/API must check facility membership.
2. Every sensitive action must check permission_key.
3. Protected permissions must check professional_category.
4. Users suspended or removed from facility must lose access immediately.
5. Facility users can only access records belonging to their facility.
6. Facility admins cannot override Federal/State policy rules.
7. Return clear authorization errors when permissions fail.
```

---

# 16. Acceptance Criteria

## Facility Onboarding

- Facility can only receive bookings after State approval.
- Suspended or expired facilities cannot process new appointments.
- Facility profile supports accreditation and State/LGA mapping.

## Stakeholder Management

- Facility admin can invite team members.
- Facility admin can assign default or custom roles.
- Facility admin can create custom roles.
- Protected permissions cannot be assigned to ineligible professional categories.
- Suspended/removed users lose facility access immediately.

## Appointment Management

- Facility users can view bookings based on permission.
- Facility can confirm/manage appointments.
- Facility can check in food handlers after identity verification.
- Identity mismatch pauses assessment.

## Doctor Workflow

- Doctor can validate declaration.
- Doctor can conduct physical examination.
- Doctor can review lab results.
- Doctor can confirm final decision.
- Non-doctor users cannot perform doctor-only actions.

## Lab Workflow

- Lab users can view assigned lab requests.
- Lab users can input structured results.
- Lab users can upload supporting documents.
- Lab users cannot approve fit/unfit decisions.

## Certificate / Report

- Certificate is generated only after doctor Fit decision.
- Temporary Unfit Report is generated after doctor Unfit decision.
- Facility users can view certificate/report based on permission.
- Employer sees unfit status only, not private clinical details.

## Audit and Compliance

- All sensitive actions are audit logged.
- Facility compliance dashboard shows pending and completed workflow items.
- Audit logs are role-protected.

---

# 17. Final Recommended Facility Flow

```text
Facility approved by State
    ↓
Facility Admin configures team and roles
    ↓
Facility invites doctors, lab technicians, front desk, finance, records, compliance users
    ↓
Food handler/employer books appointment
    ↓
Facility receives booking
    ↓
Front desk verifies identity and checks in food handler
    ↓
Doctor validates declaration
    ↓
Doctor conducts physical examination
    ↓
Lab technician enters lab results
    ↓
Doctor reviews lab results
    ↓
System recommends decision
    ↓
Doctor confirms Fit / Temporarily Unfit / Further Review
    ↓
System generates certificate or report
    ↓
Facility, food handler, employer, State, and Federal dashboards update
```
