# PRD: State Ministry of Health Account Flow & Stakeholder Management

**Application:** FoodCert / National Food Handlers Medical Test Platform  
**Module:** State Ministry of Health Account, Facility Oversight, Policy Adoption, Compliance, M&E, Stakeholder Management  
**Primary Users:** State Super Admin, Programme Manager, Director/Department Head, Facility Accreditation Officer, Inspector/EHO, M&E Officer, Finance/Pricing Officer, Public Awareness Officer, Compliance Officer, Viewer/Auditor  
**Purpose:** Define the step-by-step State Ministry of Health flow, including internal stakeholder/team management, Federal policy adoption, facility accreditation, package pricing, oversight, compliance enforcement, and reporting to the Federal Ministry.

---

## 1. Product Objective

The State Ministry of Health account should act as the **State-level implementation and oversight layer** between the Federal Ministry and all approved medical facilities, food businesses, and food handlers operating within the State.

The State account must enable the State Ministry to:

- Adopt Federal standards and policy configurations.
- Extend Federal templates where permitted.
- Manage State internal users, roles, and permissions.
- Review, approve, suspend, and renew medical facilities.
- Configure State-approved package pricing.
- Monitor assessments, certificates, reports, and compliance.
- Submit periodic M&E reports to the Federal Ministry.
- Publish public notices and awareness campaigns.

The State account must preserve Federal policy authority while allowing State-level operational flexibility.

---

## 2. State Ministry Account Position in the Platform

```text
Federal Ministry of Health and Social Welfare
        ↓
State Ministry of Health / FCT
        ↓
Approved Medical Facilities
        ↓
Food Businesses / Employers
        ↓
Food Handlers
```

The Federal level defines national policy and minimum standards. The State level adopts and implements those policies, manages approved facilities, monitors compliance, and reports implementation data back to Federal.

---

## 3. Step-by-Step State Account Onboarding Flow

```text
Federal Account creates or approves State Ministry account
        ↓
State Ministry receives onboarding invite
        ↓
State Admin completes State profile
        ↓
State configures departments, officers, and approval workflow
        ↓
State adopts Federal standards and templates
        ↓
State configures allowed State-level settings
        ↓
State begins implementation
```

### 3.1 State Profile Fields

| Field | Description |
|---|---|
| State name | Example: Lagos State |
| State Ministry name | State Ministry of Health |
| Responsible department | Food Safety, Public Health, Environmental Health, etc. |
| State focal person | Main programme contact |
| Official email | State programme email |
| Official phone | Programme contact number |
| State logo/seal | Optional branding for official reports/certificates where permitted |
| Implementation status | Not started, in progress, active, suspended |
| Reporting frequency | Monthly, quarterly, annual |
| Linked Federal policy version | Active Federal policy adopted by State |
| Created by | Federal or State admin |
| Created at | Timestamp |

### 3.2 State Account Statuses

```text
Pending Onboarding
Profile Incomplete
Policy Adoption Pending
Implementation In Progress
Active
Suspended
Archived
```

---

## 4. State Stakeholder / Team Management Tool

The State Ministry account must include a **Stakeholder Management** or **Team Management** section where the State Admin can manage internal officers, reviewers, inspectors, M&E users, compliance officers, and approvers.

```text
State Admin opens Stakeholder Management
        ↓
Creates or selects State roles
        ↓
Defines permissions for each role
        ↓
Invites State officers/team members
        ↓
Assigns departments and permissions
        ↓
Team member accepts invite
        ↓
Team member operates based on assigned role
```

---

## 5. Default State Roles

| Role | Main Responsibility |
|---|---|
| State Super Admin | Full State account control |
| State Programme Manager | Oversees implementation of food handler medical test programme |
| Director / Department Head | Approves State implementation decisions |
| Facility Accreditation Officer | Reviews and recommends medical facility approvals |
| Facility Inspector | Conducts facility inspections and monitoring |
| Environmental Health Officer | Conducts food business and food handler compliance inspections |
| Medical Review Officer | Reviews clinical compliance trends, with restricted access to private records |
| M&E Officer | Tracks indicators, reports, compliance trends, and submits M&E reports |
| Data / Records Officer | Manages State records and submissions |
| Finance / Pricing Officer | Manages State-approved package pricing |
| Public Awareness Officer | Manages campaigns and public notices |
| Compliance / Enforcement Officer | Handles sanctions, suspensions, and escalations |
| Viewer / Auditor | Read-only access for audits |

---

## 6. State Role and Permission Builder

The State should be able to create custom roles while remaining within Federal platform boundaries.

Example custom roles:

```text
Senior Facility Accreditation Reviewer
LGA Food Safety Officer
State M&E Supervisor
Regional Compliance Inspector
Public Health Surveillance Officer
```

### 6.1 State Permission Categories

| Permission Category | Example Permissions |
|---|---|
| State Profile | View/edit State profile |
| Stakeholder Management | Invite officers, assign roles, suspend users |
| Policy Adoption | Adopt Federal policy, view Federal updates |
| Form Templates | Adopt Federal declaration form, add State-specific fields |
| Facility Management | Review applications, approve, suspend, renew facilities |
| Facility Inspection | Create inspection, submit inspection report |
| Medical Assessment Oversight | View assessment statistics and status |
| Certificate Oversight | View certificates issued in State |
| Compliance Enforcement | Issue warning, suspend facility, flag non-compliance |
| Pricing | Set State-approved package price |
| Reporting & M&E | Configure reports, generate reports, submit reports to Federal |
| Public Awareness | Publish State notices/campaigns |
| Audit Logs | View State-level audit logs |

---

## 7. Recommended State Permission Matrix

| Action | Super Admin | Programme Manager | Director | Accreditation Officer | Inspector/EHO | M&E Officer | Finance | Compliance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Manage State profile | Yes | Yes | View | No | No | No | No | No |
| Invite State team members | Yes | Optional | No | No | No | No | No | No |
| Create State roles | Yes | Optional | No | No | No | No | No | No |
| Adopt Federal policy | Yes | Yes | Approve | View | View | View | No | View |
| Add State form fields | Yes | Yes | Approve | No | Input | View | No | View |
| Approve State form version | Yes | Recommend | Yes | No | No | No | No | No |
| Review facility application | Yes | Yes | Approve | Yes | View | View | No | View |
| Approve facility | Yes | Recommend | Yes | Recommend | No | No | No | View |
| Suspend facility | Yes | Recommend | Yes | No | Input | No | No | Yes |
| Inspect facility | No | View | View | Yes | Yes | No | No | Yes |
| Set package price | Yes | Recommend | Approve | No | No | View | Yes | View |
| View certificates | Yes | Yes | Yes | Yes | Limited | Aggregate | No | Yes |
| View medical details | Restricted | Restricted | Restricted | No | No | Aggregate only | No | Restricted |
| Submit M&E report | Yes | Yes | View | Input | Input | Yes | No | View |
| View audit logs | Yes | Yes | Yes | Limited | Limited | Limited | No | Yes |

### 7.1 Critical Privacy Rule

State users should primarily see **oversight and compliance information**, not private patient-level medical details, unless they have a specific authorized role and lawful reason.

The State can see:

```text
Certificate status
Facility performance
Assessment counts
Compliance status
Expired certificates
Temporarily unfit counts
Aggregated risk trends
```

The State should not automatically see:

```text
Detailed lab diagnosis
Private doctor notes
Sensitive food handler medical history
```

---

## 8. Federal Policy Adoption by State

The State should not create the national standard from scratch. It should **adopt Federal policy versions** and configure permitted State-level implementation details.

```text
Federal publishes policy/template
        ↓
State receives notification
        ↓
State reviews policy
        ↓
State adopts policy
        ↓
State configures allowed State-level settings
        ↓
State publishes State implementation version
        ↓
Facilities in State are notified
```

### 8.1 State Can Configure

| Configuration | Example |
|---|---|
| State implementation start date | 1 January 2027 |
| State-approved package price | ₦X per food handler |
| Approved facilities | List of facilities in State |
| Local reporting officers | Assigned State officers |
| State-specific declaration questions | Outbreak-related questions |
| Inspection schedule | Quarterly facility inspections |
| Public awareness notices | State public health announcement |
| Local enforcement workflow | Warning → correction request → suspension → escalation |

### 8.2 State Cannot Configure

| Restriction | Reason |
|---|---|
| Remove Federal required tests | Would weaken national standard |
| Delete Federal declaration questions | Would weaken national standard |
| Extend certificate validity beyond Federal rule | Would weaken compliance |
| Approve non-accredited facility reports | Violates facility approval logic |
| Remove QR verification requirement | Violates certificate standard |

---

## 9. State Health Declaration Form Adoption Flow

The State adopts the Federal Health Declaration Form and may add State-specific questions.

```text
State opens Federal Health Declaration Template
        ↓
Clicks “Adopt Template”
        ↓
System creates State extension
        ↓
Federal fields appear locked
        ↓
State adds optional/mandatory State questions
        ↓
State submits for internal approval
        ↓
Director/authorized approver approves
        ↓
State publishes active State declaration version
        ↓
Medical facilities are notified to adopt
```

### 9.1 Example State Additions

| State Addition | Example |
|---|---|
| Local outbreak question | “Have you recently been exposed to cholera in this LGA?” |
| Market exposure question | “Have you worked in a market with a recent reported outbreak?” |
| State consent | Consent for State public health surveillance |
| State administrative field | State food handler registration number |

### 9.2 State Restrictions

The State cannot:

```text
Delete Federal fields
Hide Federal fields
Rename Federal fields
Make Federal required fields optional
Change Federal risk logic
Change Federal validation rules
Change Federal display meaning
```

---

## 10. Medical Facility Accreditation and Management Flow

This is one of the most important State functions.

```text
Medical facility applies for approval
        ↓
State Accreditation Officer reviews application
        ↓
State schedules inspection if required
        ↓
Inspector submits inspection checklist
        ↓
State reviews facility eligibility
        ↓
Director/authorized approver approves or rejects
        ↓
Approved facility is mapped to State/LGA
        ↓
Facility becomes visible in Food Handler directory
        ↓
State monitors facility performance
        ↓
Facility undergoes annual re-accreditation
```

### 10.1 Facility Accreditation Data

| Field | Description |
|---|---|
| Facility name | Legal name |
| Facility type | Hospital, clinic, diagnostic centre, PHC, mobile unit |
| CAC/registration details | Business/legal registration |
| State/LGA | Jurisdiction |
| Licence documents | Facility licence |
| Medical record capacity | Computers, operators, internet access |
| Certificate capability | QR certificate support |
| Staff profile | Doctors/lab staff |
| Inspection result | Pass/fail/conditional |
| Approval status | Pending, approved, suspended, rejected, expired |
| Accreditation expiry | Annual renewal date |

### 10.2 Facility Application Statuses

```text
Draft
Submitted
Under Review
Correction Requested
Inspection Required
Inspection Scheduled
Inspection Completed
Recommended for Approval
Approved
Rejected
Suspended
Expired
Renewal Due
Renewed
```

---

## 11. State Facility Directory Management

The State manages the list of approved facilities visible to food handlers.

```text
State approves facility
        ↓
Facility status becomes Active
        ↓
Facility appears in public directory
        ↓
Food handlers can book facility
```

### 11.1 State Facility Actions

| Action | Description |
|---|---|
| Approve facility | Allows facility to receive bookings |
| Suspend facility | Temporarily removes booking ability |
| Revoke approval | Removes facility from programme |
| Renew accreditation | Extends facility approval |
| Request correction | Facility must update documents |
| Assign inspection | Sends facility to inspection officer |
| View facility dashboard | Monitor facility performance |

---

## 12. State Package Pricing Flow

The State should be able to configure a standardized price for the Food Handler Medical Test Package for all approved facilities in the State.

```text
State Finance/Pricing Officer opens Package Pricing
        ↓
Views Federal-approved test package
        ↓
Enters State-approved package price
        ↓
Submits for approval
        ↓
Director/authorized approver approves
        ↓
Price becomes active for all facilities in State
```

### 12.1 Pricing Rules

| Rule | Logic |
|---|---|
| Price applies to all approved facilities in the State | Yes |
| Facility cannot override mandatory State price | Recommended |
| Price version should be tracked | Yes |
| Effective date required | Yes |
| Price changes notify facilities | Yes |
| Old assessments keep old price | Yes |

---

## 13. State Oversight of Medical Assessments

State users should monitor assessment activity across all approved facilities in the State.

```text
Food handler completes assessment at facility
        ↓
Certificate/report generated
        ↓
State dashboard updates
        ↓
State monitors facility compliance and trends
```

### 13.1 State Assessment Metrics

| Metric | Description |
|---|---|
| Total assessments booked | Across State |
| Assessments completed | Completed by facilities |
| Certificates issued | Fit certificates |
| Temporary unfit reports | Count and trend |
| Pending lab results | By facility |
| Overdue doctor review | By facility |
| Expired certificates | By LGA/employer |
| Facility performance | Speed, volume, compliance |
| High-risk declarations | Aggregated trend |
| Non-compliant facilities | Suspended, expired, delayed reporting |

---

## 14. State Compliance and Enforcement Flow

```text
System detects non-compliance or officer creates case
        ↓
Compliance Officer reviews issue
        ↓
State sends warning / correction notice
        ↓
Facility or business responds
        ↓
State reviews response
        ↓
State closes case or escalates
        ↓
Possible suspension/sanction
        ↓
Federal dashboard receives compliance update
```

### 14.1 Compliance Triggers

| Trigger | Example |
|---|---|
| Facility accreditation expired | Facility not renewed |
| Facility delayed lab result submissions | Repeated overdue results |
| Facility enters incomplete records | Missing required fields |
| Facility attempts invalid certificate generation | Rule violation |
| Food business has uncertified handlers | Employer non-compliance |
| Certificates expired | Food handlers still active without renewal |
| State report overdue | State has not submitted periodic report |

### 14.2 Compliance Case Statuses

```text
Open
Under Review
Warning Issued
Correction Requested
Escalated
Suspended
Resolved
Closed
```

---

## 15. State Reporting and M&E Flow

The State should prepare periodic reports to the Federal Ministry.

```text
System generates State report draft
        ↓
M&E Officer reviews indicators
        ↓
Programme Manager reviews report
        ↓
Director approves report
        ↓
State submits report to Federal
        ↓
Federal dashboard updates
```

### 15.1 State M&E Indicators

| Indicator | Example |
|---|---|
| Number of approved facilities | By LGA |
| Number of food handlers assessed | Monthly/quarterly |
| Number of certificates issued | Fit outcomes |
| Number temporarily unfit | Trend |
| Number of expired certificates | Compliance issue |
| Average assessment completion time | Facility performance |
| Pending lab result rate | Facility performance |
| Facility accreditation status | Active/suspended/expired |
| Food business compliance rate | Employer oversight |
| Public awareness activities | Campaign count |
| Report submission status | On-time/late |

### 15.2 Report Statuses

```text
Draft
Under Review
Approved
Submitted
Returned
Closed
```

---

## 16. Public Awareness and Notifications Flow

State should be able to send public notices to facilities, businesses, and food handlers.

```text
State creates public notice
        ↓
Selects audience
        ↓
Submits notice for approval
        ↓
Notice is published
        ↓
Target users receive notification
```

### 16.1 Notice Audience

| Audience | Example |
|---|---|
| Medical facilities | New policy adoption required |
| Food businesses | Ensure staff certification |
| Food handlers | Certificate renewal reminder |
| Inspectors | Updated inspection checklist |
| Public | Awareness campaign |

### 16.2 Notice Statuses

```text
Draft
Submitted
Approved
Published
Archived
```

---

## 17. State Dashboard

### 17.1 Main Dashboard Widgets

| Widget | Description |
|---|---|
| Active Federal policies adopted | Shows policy adoption status |
| Facilities approved | Active facilities in State |
| Facilities pending approval | Applications awaiting review |
| Facilities expiring soon | Accreditation renewal alerts |
| Assessments completed | Total completed assessments |
| Certificates issued | Total fit certificates |
| Temporary unfit reports | Count and trend |
| Pending lab results | Facility-level backlog |
| Employer compliance | Food businesses with certified handlers |
| LGA performance | Assessments/certificates by LGA |
| M&E report status | Due/submitted/late |
| Public awareness campaigns | Active notices |
| Enforcement cases | Open/closed cases |

### 17.2 Dashboard Filters

| Filter | Purpose |
|---|---|
| Date range | Review period |
| LGA | Local performance |
| Facility | Facility-specific metrics |
| Food handler category | Segment analysis |
| Certificate status | Active, expired, revoked |
| Assessment status | Pending, completed, unfit, etc. |

---

## 18. State Audit Logs

Every State-level action must be audit logged.

| Action | Actor |
|---|---|
| State officer invited | State Admin |
| Role created/updated | State Admin |
| Federal policy adopted | Programme Manager/Director |
| State form field added | State authorized user |
| State form published | Director/Approver |
| Facility application reviewed | Accreditation Officer |
| Facility approved/rejected/suspended | Director/Approver |
| Facility inspection submitted | Inspector |
| Package price updated | Finance/Pricing Officer |
| Compliance case opened | Compliance Officer |
| Enforcement action taken | Compliance/Director |
| M&E report submitted | M&E Officer |
| Public notice published | Public Awareness Officer |

### 18.1 Audit Log Fields

```text
id
actor_user_id
actor_role
state_id
entity_type
entity_id
action
old_value
new_value
reason
ip_address
user_agent
timestamp
```

---

# 19. Data Model Requirements

## 19.1 `state_profiles`

| Field | Type |
|---|---|
| id | UUID |
| state_name | String |
| ministry_name | String |
| responsible_department | String |
| focal_person_name | String |
| official_email | String |
| official_phone | String |
| logo_url | String nullable |
| implementation_status | Enum |
| reporting_frequency | Enum |
| active_federal_policy_version_id | UUID nullable |
| created_at | Timestamp |
| updated_at | Timestamp |

## 19.2 `state_team_members`

| Field | Type |
|---|---|
| id | UUID |
| state_id | UUID |
| user_id | UUID |
| role_id | UUID |
| department_id | UUID nullable |
| officer_type | String |
| status | Enum |
| invited_by | UUID |
| accepted_at | Timestamp nullable |
| created_at | Timestamp |
| updated_at | Timestamp |

## 19.3 `state_roles`

| Field | Type |
|---|---|
| id | UUID |
| state_id | UUID |
| name | String |
| description | Text |
| is_system_default | Boolean |
| is_custom | Boolean |
| created_by | UUID |
| created_at | Timestamp |
| updated_at | Timestamp |

## 19.4 `state_role_permissions`

| Field | Type |
|---|---|
| id | UUID |
| role_id | UUID |
| permission_key | String |
| allowed | Boolean |

## 19.5 `state_departments`

| Field | Type |
|---|---|
| id | UUID |
| state_id | UUID |
| name | String |
| description | Text |
| created_at | Timestamp |
| updated_at | Timestamp |

## 19.6 `state_policy_adoptions`

| Field | Type |
|---|---|
| id | UUID |
| state_id | UUID |
| federal_policy_version_id | UUID |
| adoption_status | Enum |
| implementation_start_date | Date |
| local_notes | Text nullable |
| adopted_by | UUID |
| approved_by | UUID nullable |
| adopted_at | Timestamp |
| activated_at | Timestamp nullable |

## 19.7 `facility_accreditation_applications`

| Field | Type |
|---|---|
| id | UUID |
| facility_id | UUID |
| state_id | UUID |
| status | Enum |
| submitted_by | UUID |
| reviewed_by | UUID nullable |
| inspection_required | Boolean |
| approval_decision | Enum nullable |
| decision_notes | Text nullable |
| accreditation_expiry | Date nullable |
| created_at | Timestamp |
| updated_at | Timestamp |

## 19.8 `state_package_prices`

| Field | Type |
|---|---|
| id | UUID |
| state_id | UUID |
| package_id | UUID |
| amount | Decimal |
| currency | String |
| effective_date | Date |
| status | Enum |
| approved_by | UUID nullable |
| created_at | Timestamp |
| updated_at | Timestamp |

## 19.9 `state_compliance_cases`

| Field | Type |
|---|---|
| id | UUID |
| state_id | UUID |
| case_type | Enum |
| related_entity_type | String |
| related_entity_id | UUID |
| status | Enum |
| severity | Enum |
| description | Text |
| opened_by | UUID |
| assigned_to | UUID nullable |
| resolution_notes | Text nullable |
| created_at | Timestamp |
| updated_at | Timestamp |

## 19.10 `state_me_reports`

| Field | Type |
|---|---|
| id | UUID |
| state_id | UUID |
| reporting_period_start | Date |
| reporting_period_end | Date |
| report_payload | JSON |
| status | Enum |
| prepared_by | UUID |
| reviewed_by | UUID nullable |
| approved_by | UUID nullable |
| submitted_to_federal_at | Timestamp nullable |
| created_at | Timestamp |
| updated_at | Timestamp |

---

# 20. API Requirements

## 20.1 State Profile APIs

```http
GET /api/state/profile
PATCH /api/state/profile
GET /api/state/dashboard
```

## 20.2 State Team APIs

```http
GET /api/state/team
POST /api/state/team/invite
PATCH /api/state/team/:memberId
POST /api/state/team/:memberId/suspend
POST /api/state/team/:memberId/remove
POST /api/state/team/:memberId/assign-role
```

## 20.3 State Role APIs

```http
GET /api/state/roles
POST /api/state/roles
GET /api/state/roles/:roleId
PATCH /api/state/roles/:roleId
POST /api/state/roles/:roleId/permissions
```

## 20.4 State Policy Adoption APIs

```http
GET /api/state/federal-policies
POST /api/state/policies/:policyVersionId/adopt
PATCH /api/state/policy-adoptions/:adoptionId
POST /api/state/policy-adoptions/:adoptionId/activate
```

## 20.5 State Form Template APIs

```http
GET /api/state/forms/federal-templates
POST /api/state/forms/:templateId/adopt
PATCH /api/state/forms/:stateTemplateId
POST /api/state/forms/:stateTemplateId/publish
```

## 20.6 Facility Accreditation APIs

```http
GET /api/state/facilities
GET /api/state/facilities/applications
GET /api/state/facilities/:facilityId
POST /api/state/facilities/:facilityId/request-correction
POST /api/state/facilities/:facilityId/assign-inspection
POST /api/state/facilities/:facilityId/approve
POST /api/state/facilities/:facilityId/reject
POST /api/state/facilities/:facilityId/suspend
POST /api/state/facilities/:facilityId/renew
```

## 20.7 Pricing APIs

```http
GET /api/state/package-prices
POST /api/state/package-prices
POST /api/state/package-prices/:priceId/approve
GET /api/state/package-prices/history
```

## 20.8 Oversight APIs

```http
GET /api/state/assessments
GET /api/state/certificates
GET /api/state/analytics
GET /api/state/facility-performance
```

## 20.9 Compliance APIs

```http
GET /api/state/compliance-cases
POST /api/state/compliance-cases
GET /api/state/compliance-cases/:caseId
PATCH /api/state/compliance-cases/:caseId
POST /api/state/compliance-cases/:caseId/issue-warning
POST /api/state/compliance-cases/:caseId/request-correction
POST /api/state/compliance-cases/:caseId/escalate
POST /api/state/compliance-cases/:caseId/close
```

## 20.10 M&E Reporting APIs

```http
GET /api/state/me-reports
POST /api/state/me-reports/generate-draft
GET /api/state/me-reports/:reportId
PATCH /api/state/me-reports/:reportId
POST /api/state/me-reports/:reportId/submit
```

## 20.11 Public Notice APIs

```http
GET /api/state/public-notices
POST /api/state/public-notices
PATCH /api/state/public-notices/:noticeId
POST /api/state/public-notices/:noticeId/publish
```

## 20.12 Audit APIs

```http
GET /api/state/audit-logs
```

---

# 21. UI/UX Pages to Build

## 21.1 State Account Pages

```text
/state/dashboard
/state/profile
/state/team
/state/team/invite
/state/team/:memberId
/state/roles
/state/roles/new
/state/roles/:roleId/edit
/state/departments
```

## 21.2 Policy and Forms Pages

```text
/state/policies
/state/policies/federal
/state/policies/adoptions
/state/forms
/state/forms/federal-templates
/state/forms/:templateId/adopt
/state/forms/:stateTemplateId/edit
```

## 21.3 Facility Management Pages

```text
/state/facilities
/state/facilities/applications
/state/facilities/:facilityId
/state/facilities/:facilityId/inspections
/state/facilities/:facilityId/performance
```

## 21.4 Pricing Pages

```text
/state/pricing
/state/pricing/history
```

## 21.5 Oversight and Compliance Pages

```text
/state/assessments
/state/certificates
/state/analytics
/state/compliance
/state/compliance/:caseId
```

## 21.6 Reporting and Public Notice Pages

```text
/state/me-reports
/state/me-reports/:reportId
/state/public-notices
/state/public-notices/new
/state/public-notices/:noticeId
/state/audit-logs
```

---

# 22. Implementation Chunks for Codex

## Chunk 1: State Team and Role Models

```text
Implement State Ministry stakeholder/team management models.

Create or extend:
- state_team_members
- state_roles
- state_role_permissions
- state_invitations
- state_departments

state_team_members fields:
- id
- state_id
- user_id
- role_id
- department_id
- professional_category or officer_type
- status: invited, pending_profile, active, suspended, removed
- invited_by
- accepted_at
- created_at
- updated_at

state_roles fields:
- id
- state_id
- name
- description
- is_system_default
- is_custom
- created_by
- created_at
- updated_at

state_role_permissions fields:
- id
- role_id
- permission_key
- allowed

state_departments fields:
- id
- state_id
- name
- description
- created_at
- updated_at
```

---

## Chunk 2: Seed Default State Roles and Permissions

```text
Seed default State Ministry roles and permissions.

Default roles:
1. State Super Admin
2. State Programme Manager
3. Director / Department Head
4. Facility Accreditation Officer
5. Facility Inspector
6. Environmental Health Officer
7. Medical Review Officer
8. M&E Officer
9. Data / Records Officer
10. Finance / Pricing Officer
11. Public Awareness Officer
12. Compliance / Enforcement Officer
13. Viewer / Auditor

Create permission keys:
- state.profile.view
- state.profile.edit
- state.team.invite
- state.team.remove
- state.roles.create
- state.roles.edit
- state.roles.assign_permissions
- policy.view_federal
- policy.adopt
- policy.publish_state_extension
- forms.view_federal_template
- forms.adopt_template
- forms.add_state_fields
- facilities.view
- facilities.review_application
- facilities.approve
- facilities.reject
- facilities.suspend
- facilities.renew
- facilities.inspect
- pricing.view
- pricing.configure
- pricing.approve
- assessments.view_state
- certificates.view_state
- compliance.view
- compliance.create_case
- compliance.issue_warning
- compliance.suspend_entity
- reports.view
- reports.generate
- reports.submit_to_federal
- public_notices.create
- public_notices.publish
- audit_logs.view
```

---

## Chunk 3: State Stakeholder Management UI

```text
Build State Ministry Stakeholder Management UI.

Pages:
- /state/team
- /state/team/invite
- /state/team/:memberId
- /state/roles
- /state/roles/new
- /state/roles/:roleId/edit
- /state/departments

Features:
1. State Admin can invite officers by email/phone.
2. State Admin selects role and department.
3. Team member accepts invite and completes profile.
4. State Admin can activate, suspend, remove, or reassign user.
5. State Admin can create custom roles.
6. State Admin can assign permissions to custom roles.
7. Permissions must be scoped to the State.
8. All team and role changes must be audit logged.
```

---

## Chunk 4: State Policy Adoption

```text
Implement State adoption of Federal policies.

Requirements:
1. State users with policy.view_federal can view active Federal policies.
2. State users with policy.adopt can adopt a Federal policy version.
3. Adoption creates a state_policy_adoption record.
4. State can set implementation start date and local implementation notes.
5. State cannot alter locked Federal requirements.
6. State users with approval permission can publish State implementation version.
7. Notify facilities when State adopts or updates a policy.
8. Track adoption status: pending, adopted, active, superseded.
```

---

## Chunk 5: State Health Declaration Extension

```text
Implement State extension of Federal Health Declaration Form.

Requirements:
1. State users can adopt active Federal declaration template.
2. Federal fields must appear locked.
3. State users can add State-specific fields.
4. State cannot delete, hide, rename, reorder, or weaken Federal fields.
5. State extension must go through draft, review, approved, published, active statuses.
6. Facilities in the State are notified when the State extension is published.
7. New food handler assessments in the State should use Federal + active State extension.
```

---

## Chunk 6: Medical Facility Application and Accreditation

```text
Implement State medical facility accreditation workflow.

Requirements:
1. Facilities can submit application for approval or State can create facility profile.
2. State Accreditation Officer can review applications.
3. State can request corrections.
4. State can assign inspection officer.
5. Inspector submits inspection checklist/report.
6. Director/authorized approver can approve or reject facility.
7. Approved facility is mapped to State and LGA.
8. Approved facility becomes visible in Food Handler directory.
9. Statuses: draft, submitted, under_review, correction_requested, inspection_required, approved, rejected, suspended, expired.
10. Accreditation expiry should support annual renewal.
11. Audit log all review, approval, rejection, suspension, and renewal actions.
```

---

## Chunk 7: State Facility Management Dashboard

```text
Build State facility management dashboard.

Pages:
- /state/facilities
- /state/facilities/applications
- /state/facilities/:facilityId
- /state/facilities/:facilityId/inspections
- /state/facilities/:facilityId/performance

Features:
1. View all facilities in the State.
2. Filter by LGA, approval status, accreditation expiry, facility type.
3. View facility application documents.
4. Approve, reject, suspend, renew facility based on permissions.
5. View facility performance metrics:
   - assessments completed
   - pending lab results
   - doctor review delays
   - certificates generated
   - temporary unfit reports
6. Show accreditation expiry alerts.
```

---

## Chunk 8: State Package Pricing

```text
Implement State package pricing configuration.

Requirements:
1. State users with pricing.configure can configure State-approved Food Handler Medical Test Package price.
2. Price applies to all approved facilities in the State.
3. Price record should include:
   - state_id
   - package_id
   - amount
   - currency
   - effective_date
   - status
   - approved_by
4. Price changes should be versioned.
5. Old assessments retain the price active at time of booking.
6. Facilities should be notified when package price changes.
7. Facility users can view price but cannot override mandatory State price unless policy allows.
```

---

## Chunk 9: State Assessment and Certificate Oversight

```text
Implement State-level assessment and certificate oversight.

Pages:
- /state/assessments
- /state/certificates
- /state/analytics

Features:
1. State users can view assessments conducted within their State.
2. Display assessment status, facility, LGA, certificate status, and timestamps.
3. Hide detailed lab results and doctor notes unless user has restricted medical oversight permission.
4. State can filter by facility, LGA, status, date range.
5. State can view certificate counts, active/expired/revoked certificates.
6. State can monitor pending lab results and overdue doctor reviews.
```

---

## Chunk 10: State Compliance and Enforcement

```text
Implement State compliance and enforcement workflow.

Requirements:
1. System can create compliance alerts automatically.
2. State Compliance Officer can open compliance cases manually.
3. Case types:
   - facility non-compliance
   - expired accreditation
   - delayed lab results
   - invalid records
   - employer non-compliance
   - expired food handler certificates
4. Case statuses:
   - open
   - under_review
   - warning_issued
   - correction_requested
   - escalated
   - resolved
   - closed
5. State can issue warning, request correction, suspend facility, or escalate to Federal.
6. All enforcement actions must be audit logged.
```

---

## Chunk 11: State M&E Reporting to Federal

```text
Implement State M&E reporting workflow.

Requirements:
1. System generates draft periodic State report from platform data.
2. M&E Officer can review and add comments.
3. Programme Manager can review.
4. Director/authorized approver can approve submission.
5. Report is submitted to Federal account.
6. Report should include:
   - approved facilities
   - assessments completed
   - certificates issued
   - temporary unfit reports
   - expired certificates
   - facility compliance status
   - food business compliance status
   - enforcement cases
   - public awareness activities
7. Report statuses:
   - draft
   - under_review
   - approved
   - submitted
   - returned
8. Federal dashboard updates after submission.
```

---

## Chunk 12: Public Notices and Awareness

```text
Implement State public awareness notice tool.

Requirements:
1. State users can create notices/campaigns.
2. Audience can be:
   - medical facilities
   - food businesses
   - food handlers
   - inspectors
   - general public
3. Notices can be draft, submitted, approved, published, archived.
4. Published notices trigger in-app notifications.
5. Notices should be visible on relevant dashboards.
6. Audit log notice creation and publication.
```

---

## Chunk 13: State Dashboard and Analytics

```text
Build State dashboard and analytics.

Dashboard widgets:
- Federal policies adopted
- State implementation status
- approved facilities
- pending facility applications
- facilities expiring soon
- assessments completed
- certificates issued
- temporary unfit reports
- pending lab results
- overdue doctor reviews
- expired certificates
- compliance cases
- M&E report status
- public awareness campaigns
- LGA performance map/table

Filters:
- date range
- LGA
- facility
- food handler category
- certificate status
```

---

## Chunk 14: State Audit Logs

```text
Implement State audit logs.

Audit events:
- State officer invited
- State role created/updated
- Federal policy adopted
- State form template adopted
- State form field added
- State form published
- Facility application reviewed
- Facility approved/rejected/suspended/renewed
- Facility inspection submitted
- Package price configured/approved
- Compliance case opened
- Enforcement action taken
- M&E report submitted
- Public notice published

Audit logs should be filterable by:
- actor
- role
- action
- entity
- date range
- LGA/facility where applicable
```

---

## Chunk 15: State Permission Enforcement Middleware

```text
Implement permission enforcement middleware for State account.

Requirements:
1. Every State route/API must check State membership.
2. Every sensitive action must check permission_key.
3. Users suspended or removed from State account must lose access immediately.
4. State users can only access records belonging to their State unless Federal-level access is granted.
5. State users cannot override Federal locked rules.
6. State users cannot access detailed medical data unless role has restricted medical oversight permission.
7. Return clear authorization errors when permissions fail.
```

---

# 23. Acceptance Criteria

## State Onboarding

- Federal can create/approve State account.
- State Admin can complete profile.
- State can configure departments and internal users.

## Stakeholder Management

- State Admin can invite officers.
- State Admin can create roles and assign permissions.
- Users can be activated, suspended, removed, and reassigned.
- All stakeholder actions are audit logged.

## Policy Adoption

- State can view and adopt Federal policy versions.
- State cannot modify Federal locked requirements.
- Facilities are notified when State publishes implementation updates.

## Form Extension

- State can adopt Federal Health Declaration Form.
- State can add State-specific fields.
- State cannot delete or weaken Federal fields.

## Facility Accreditation

- Facilities can apply or be created by State.
- State can review, inspect, approve, reject, suspend, and renew facilities.
- Approved facilities appear in the public facility directory.

## Pricing

- State can configure package price.
- Price applies to all approved facilities in the State.
- Price changes are versioned and audited.

## Oversight

- State can view assessment and certificate activity within the State.
- State sees aggregate medical trends but not private medical notes by default.

## Compliance

- State can open compliance cases.
- State can issue warnings, request correction, suspend facilities, or escalate cases.
- Enforcement actions are audit logged.

## M&E Reporting

- System generates State report drafts.
- M&E Officer reviews.
- Programme Manager and Director approve.
- State submits report to Federal.

---

# 24. Final State Ministry Flow

```text
1. Federal creates/approves State Ministry account.

2. State Admin completes State profile.

3. State Admin configures departments, team members, roles, and permissions.

4. State adopts Federal policies and Federal declaration templates.

5. State adds State-specific declaration requirements without deleting Federal fields.

6. State configures implementation start date and State package price.

7. State reviews and approves medical facilities.

8. Approved facilities become visible in the food handler facility directory.

9. State monitors assessments, lab result timelines, doctor review timelines, certificates, and reports.

10. State manages facility renewals, suspensions, inspections, and compliance cases.

11. State publishes public notices and awareness campaigns.

12. State M&E Officer prepares periodic report.

13. Programme Manager and Director review/approve report.

14. State submits periodic report to Federal.

15. Federal dashboard updates with State implementation and compliance data.
```

This State Ministry flow gives the State full operational control over implementation while preserving Federal policy authority and ensuring medical facilities operate only within approved standards.
