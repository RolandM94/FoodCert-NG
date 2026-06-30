# PRD: Federal Ministry of Health Account Flow, National Policy Configuration & Oversight

**Application:** FoodCert / National Food Handlers Medical Test Platform  
**Module:** Federal Ministry of Health Account  
**Primary User:** Federal Ministry of Health and Social Welfare  
**Supporting Users:** State Ministries of Health, Medical Facilities, Food Businesses, Food Handlers  
**Guideline Basis:** National Guidelines for Food Handlers’ Medical Test 2024. The guideline requires national coordination, approved medical facilities, medical assessment, vaccination, documentation, digitally verifiable certificates, central certificate storage, compliance oversight, and periodic reporting.

---

## 1. Product Objective

Develop the **Federal Ministry of Health account** as the national control centre for the FoodCert platform.

The Federal account should enable the Federal Ministry to:

```text
1. Configure national standards and policies.
2. Create and publish national health declaration templates.
3. Configure medical test packages and vaccination rules.
4. Define facility accreditation criteria.
5. Define certificate templates and QR verification rules.
6. Manage State onboarding and policy adoption.
7. Monitor State, facility, employer, and food handler compliance.
8. Maintain the central certificate registry.
9. Review State M&E reports.
10. Use national analytics for public health policy decisions.
```

The Federal account does **not** conduct day-to-day medical testing. Testing is handled by approved medical facilities, while State Ministries manage facility approval and local implementation.

---

## 2. Federal Ministry Role on the Platform

| Federal Function | Platform Responsibility |
|---|---|
| National policy authority | Create and publish standards/policies |
| Standards owner | Define tests, vaccines, certificates, declaration forms |
| National coordinator | Monitor State adoption and implementation |
| Certificate registry owner | Maintain central QR-verifiable certificate database |
| M&E authority | Review State reports and national indicators |
| Compliance oversight body | Monitor escalations and national compliance risks |
| Public health intelligence body | Use data for food safety policy decisions |

---

## 3. Federal Account Setup Flow

```text
Federal Ministry account is created
    ↓
Federal Super Admin completes Ministry/programme profile
    ↓
Federal departments and units are configured
    ↓
Federal roles and permissions are created
    ↓
Federal users are invited
    ↓
National policy workspace is activated
    ↓
Federal begins standards and oversight configuration
```

### Federal Profile Fields

| Field | Description |
|---|---|
| Ministry name | Federal Ministry of Health and Social Welfare |
| Department | Food and Drug Services / Food Safety and Quality Programme |
| Programme name | National Food Handlers Medical Test Programme |
| National coordinator | Programme lead |
| Official email | Ministry/programme email |
| Official phone | Official contact |
| Logo/seal | For official certificates/reports |
| Active guideline version | National Guidelines for Food Handlers’ Medical Test 2024 |
| Reporting cycle | Monthly, quarterly, annual |
| Central portal status | Active/inactive |

---

## 4. Federal Stakeholder Management

The Federal account should include a **Stakeholder Management** tool for managing internal Federal users, departments, roles, permissions, reviewers, approvers, M&E officers, and auditors.

```text
Federal Admin opens Stakeholder Management
    ↓
Creates Federal departments/units
    ↓
Creates or selects Federal roles
    ↓
Defines role permissions
    ↓
Invites Federal team members
    ↓
Assigns role and department
    ↓
Team member accepts invite
    ↓
Team member receives permission-based access
```

### Default Federal Roles

| Role | Main Responsibility |
|---|---|
| Federal Super Admin | Full Federal account control |
| National Programme Manager | Oversees national programme implementation |
| Director / Department Head | Approves policies, templates, reports |
| Policy Configuration Officer | Drafts national policies and rules |
| Standards Officer | Configures test, vaccine, certificate and facility standards |
| Legal / Regulatory Reviewer | Reviews legal basis and compliance |
| Medical / Clinical Reviewer | Reviews clinical and lab standards |
| M&E Officer | Tracks national indicators and State reports |
| Data Analyst | Reviews analytics and trends |
| State Coordination Officer | Coordinates State adoption and implementation |
| Facility Oversight Officer | Monitors facility performance nationally |
| Certificate Registry Officer | Oversees central certificate database |
| Public Awareness Officer | Publishes national notices/campaigns |
| Compliance / Enforcement Officer | Reviews escalated compliance cases |
| Viewer / Auditor | Read-only audit access |

---

## 5. Federal Permission Categories

| Permission Category | Example Permissions |
|---|---|
| Federal Profile | View/edit programme profile |
| Stakeholder Management | Invite users, create roles, assign permissions |
| Policy Configuration | Create, edit, review, approve, publish policies |
| Standards Management | Configure tests, vaccines, certificates, accreditation rules |
| Form Templates | Create national declaration forms |
| State Management | Create/approve State accounts, monitor adoption |
| Facility Oversight | View approved facilities nationally |
| Certificate Registry | View, search, verify, revoke certificates |
| Compliance Oversight | View escalated cases and national alerts |
| Reporting & M&E | Configure indicators and review State reports |
| Public Awareness | Publish national notices |
| Audit Logs | View/export Federal audit logs |

---

## 6. Federal Policy and Standards Configuration Flow

```text
Federal Policy Officer creates national standard
    ↓
Adds policy title, description, scope and legal basis
    ↓
Defines affected entities
    ↓
Configures machine-readable rules
    ↓
Submits for technical/legal/clinical review
    ↓
Director or authorized approver approves
    ↓
Policy is published as active version
    ↓
System cascades policy to States
    ↓
States adopt and implement
```

### Policy Categories

| Policy Category | Purpose |
|---|---|
| Food Handler Eligibility Standard | Defines categories of food handlers covered |
| Food Establishment Coverage Standard | Defines affected establishment types |
| Medical Test Standard | Defines required tests and assessment frequency |
| Laboratory Investigation Standard | Defines lab tests and result rules |
| Vaccination Standard | Defines Typhoid and Hepatitis A requirements |
| Health Declaration Standard | Defines mandatory declaration questions |
| Facility Accreditation Standard | Defines facility prequalification criteria |
| Certificate Standard | Defines QR certificate format and identifiers |
| Reporting Standard | Defines State reporting obligations |
| Compliance and Enforcement Standard | Defines compliance rules and escalation logic |
| M&E Indicator Standard | Defines national indicators and dashboard metrics |

---

## 7. Federal Policy Versioning Flow

```text
Draft
    ↓
Technical Review
    ↓
Legal / Regulatory Review
    ↓
Medical / Clinical Review, where applicable
    ↓
Director / Department Approval
    ↓
Published
    ↓
Active
    ↓
Superseded / Archived
```

### Versioning Business Rules

| Rule | Logic |
|---|---|
| Published policies are immutable | Yes |
| Editing a published policy creates a new draft version | Yes |
| States are notified when a new policy version is published | Yes |
| Old assessments retain the policy version used at booking | Yes |
| Federal can supersede outdated versions | Yes |
| Every policy action is audit logged | Yes |

---

## 8. Federal Health Declaration Template Flow

The Federal Ministry creates the base Health Declaration Form using the Forms Tool.

```text
Federal opens Forms Tool
    ↓
Creates National Health Declaration Form Template
    ↓
Adds mandatory Federal fields
    ↓
Marks risk-triggering fields
    ↓
Submits template for approval
    ↓
Publishes active Federal template
    ↓
States receive notification to adopt
```

### Federal Base Form Sections

| Section | Example Fields |
|---|---|
| Identity Information | Full name, NIN, DOB, gender, passport photo |
| Food Handler Information | Category, employer if applicable |
| Recent Illness Declaration | Fever, jaundice, diarrhoea, vomiting, cough/flu, sore throat |
| Communicable Disease History | Typhoid, cholera, Hepatitis A, dysentery, gastrointestinal infection |
| Skin and Infection Declaration | Skin infection, boils, cuts, lesions, discharge |
| Vaccination History | Typhoid certificate, Hepatitis A certificate |
| Consent | Consent for assessment and certificate processing |
| Declaration Statement | Food handler confirms information is true |

### Governance Rule

```text
Federal fields are locked.
States and facilities may add fields.
States and facilities cannot delete, hide, rename, weaken, or make Federal fields optional.
```

---

## 9. Federal Medical Test Package Configuration

```text
Federal Standards Officer opens Test Package Configuration
    ↓
Creates Food Handler Medical Test Package
    ↓
Adds mandatory assessment components
    ↓
Adds required laboratory tests
    ↓
Adds vaccination review rules
    ↓
Adds certificate/report generation rules
    ↓
Publishes package version
    ↓
States adopt package and configure State price
```

### Default Federal Test Package

| Component | Rule |
|---|---|
| Health Declaration Form | Mandatory |
| Doctor Declaration Validation | Mandatory |
| Physical Examination | Mandatory |
| Vaccination Certificate Review | Mandatory |
| Stool microscopy, culture and sensitivity | Mandatory |
| Hepatitis A Antigen | Mandatory |
| Additional tests | Conditional if clinically indicated |
| Doctor Final Review | Mandatory |
| Certificate of Fitness / Temporary Unfit Report | Mandatory |

---

## 10. Federal Vaccination Standard

```text
Federal creates Vaccination Standard
    ↓
Adds vaccine requirements
    ↓
Defines validity and dose schedule
    ↓
Defines missing/invalid certificate action
    ↓
Publishes standard
    ↓
States and facilities enforce it
```

### Default Vaccine Rules

| Vaccine | Rule |
|---|---|
| Typhoid | Required; one dose every 3 years |
| Hepatitis A | Required; two doses at 0 and 6 months |
| Other vaccines | May be added by Federal when required |

---

## 11. Federal Facility Accreditation Criteria

Federal defines the minimum criteria that States must use when approving medical facilities.

### Accreditation Criteria

| Criteria | Description |
|---|---|
| Facility type | Hospital, clinic, diagnostic centre, PHC, mobile unit |
| Required documents | Licences, registration documents, operating permits |
| Medical records capacity | Computers, trained staff, records policy |
| Internet access | Required for portal use and certificate upload |
| Doctor availability | Registered medical doctor access |
| Lab capacity | Ability to perform required tests |
| QR certificate capability | Facility must support digital certificate process |
| Documentation policy | Standard reporting and record-keeping process |
| Re-accreditation cycle | Annual renewal |

### Business Rules

| Rule | Logic |
|---|---|
| State must use Federal criteria as minimum | Yes |
| State may add additional criteria | Yes |
| State cannot remove Federal criteria | Yes |
| Facility approval appears in Federal registry | Yes |
| Federal can monitor but not necessarily approve every facility | Yes |

---

## 12. Federal Certificate Template and Central Registry

```text
Federal creates certificate template
    ↓
Defines required certificate fields
    ↓
Defines QR verification rules
    ↓
Publishes certificate template
    ↓
Facilities generate certificates using active template
    ↓
Certificates are stored in Federal central registry
    ↓
QR verification becomes publicly accessible
```

### Required Certificate Fields

| Field | Required |
|---|---|
| Certificate number | Yes |
| QR code | Yes |
| Verification token/URL | Yes |
| Full name | Yes |
| Date of birth | Yes |
| Gender | Yes |
| Passport photograph | Yes |
| NIN | Yes |
| Food handler category | Yes |
| Issuing State | Yes |
| Approved medical facility | Yes |
| Medical doctor | Yes |
| Assessment date | Yes |
| Issue date | Yes |
| Expiry date | Yes |
| Certificate status | Yes |

### Registry Features

| Feature | Description |
|---|---|
| Certificate search | Search by number, NIN, State, facility |
| QR verification | Public verification page |
| Expiry monitoring | Active, expiring, expired |
| Revocation | Authorized revocation with reason |
| Duplicate detection | Detect multiple active certificates for same NIN |
| Audit trail | Track generation, verification, revocation |

---

## 13. Federal State Management Flow

```text
Federal creates or approves State account
    ↓
State receives onboarding invite
    ↓
State completes profile
    ↓
State adopts Federal policies/templates
    ↓
Federal monitors State adoption
    ↓
Federal follows up on pending/late States
```

### Federal Monitors

| Indicator | Description |
|---|---|
| State onboarding status | Not started, active, delayed |
| Policy adoption status | Whether State adopted active Federal policy |
| Declaration template adoption | Whether State uses latest form |
| Approved facilities | Number of approved facilities |
| Assessment volume | Number of tests conducted |
| Certificates issued | Certification output |
| Expired certificates | Compliance risk |
| M&E report status | Submitted, late, pending |
| Enforcement cases | Open/escalated cases |
| Public awareness activities | State campaigns/notices |

---

## 14. Federal National Facility Registry

```text
State approves facility
    ↓
Facility enters State directory
    ↓
Federal national facility registry updates
    ↓
Federal monitors distribution, status and performance
```

### Federal Facility Metrics

| Metric | Description |
|---|---|
| Total approved facilities | National count |
| Facilities by State/LGA | Geographic coverage |
| Suspended facilities | Compliance risk |
| Expired accreditation | Renewal issue |
| Assessment volume | Facility workload |
| Pending lab results | Operational delay |
| Doctor review delay | Operational delay |
| Certificates generated | Facility output |
| Temporary unfit reports | Public health signal |

---

## 15. Federal M&E Reporting Flow

```text
State submits periodic report
    ↓
Federal M&E Officer receives report
    ↓
Federal reviews indicators and comments
    ↓
Report is accepted or returned for clarification
    ↓
Federal dashboard updates
    ↓
Insights inform national policy updates
```

### Federal M&E Indicators

| Indicator | Example |
|---|---|
| Number of States onboarded | National adoption |
| Number of States using latest policy | Policy compliance |
| Number of approved facilities | National capacity |
| Number of registered food handlers | Programme coverage |
| Number of assessments conducted | Implementation activity |
| Number of certificates issued | Certification output |
| Number temporarily unfit | Public health signal |
| Number of expired certificates | Compliance issue |
| Facility performance | Timeliness and quality |
| State report submission rate | Governance compliance |
| Public awareness campaigns | Outreach activity |

---

## 16. Federal Compliance and Escalation Flow

```text
System detects compliance issue or State escalates case
    ↓
Federal Compliance Officer reviews case
    ↓
Federal requests clarification from State
    ↓
State responds or takes corrective action
    ↓
Federal tracks resolution
    ↓
Issue is closed or escalated further
```

### Federal Compliance Triggers

| Trigger | Example |
|---|---|
| State has not adopted active policy | Adoption delay |
| State report overdue | Governance non-compliance |
| Unusual certificate generation pattern | Possible fraud |
| Duplicate active certificates for same NIN | Data integrity risk |
| High facility suspension rate | Implementation issue |
| High pending lab result rate | Facility performance risk |
| High expired certificate count | Compliance issue |
| Certificate verification failure | Registry issue |

---

## 17. Federal Public Awareness Notices

```text
Federal creates notice/campaign
    ↓
Selects target audience
    ↓
Submits notice for approval
    ↓
Publishes notice
    ↓
States, facilities, employers, and food handlers receive notification
```

### Audience Options

| Audience | Example Notice |
|---|---|
| States | Adopt new national policy version |
| Medical facilities | Updated test package requirements |
| Food businesses | Ensure staff certification |
| Food handlers | Renew certificates before expiry |
| General public | National food safety awareness campaign |

---

## 18. Federal Dashboard

### Dashboard Widgets

| Widget | Description |
|---|---|
| States onboarded | Active States/FCT |
| States using latest policy | Policy adoption status |
| States using latest declaration template | Template adoption status |
| Approved facilities nationally | Facility coverage |
| Registered food handlers | National food handler count |
| Assessments completed | National testing volume |
| Certificates issued | Certificate output |
| Active certificates | Current valid certificates |
| Expired certificates | Compliance risk |
| Temporary unfit reports | Public health trend |
| State report submissions | Submitted/late/pending |
| Facility performance | National facility analytics |
| Compliance alerts | High-risk cases |
| QR verification activity | Certificate verification scans |
| Public awareness campaigns | Active national campaigns |

---

## 19. Data Model Requirements

### `federal_profiles`

| Field | Type |
|---|---|
| id | UUID |
| ministry_name | String |
| department_name | String |
| programme_name | String |
| national_coordinator | String |
| official_email | String |
| official_phone | String |
| logo_url | String |
| active_guideline_version | String |
| reporting_cycle | String |
| central_portal_status | active/inactive |
| created_at | Timestamp |
| updated_at | Timestamp |

### `federal_departments`

| Field | Type |
|---|---|
| id | UUID |
| name | String |
| description | Text |
| created_at | Timestamp |

### `federal_team_members`

| Field | Type |
|---|---|
| id | UUID |
| user_id | UUID |
| department_id | UUID |
| role_id | UUID |
| status | invited/pending/active/suspended/removed |
| invited_by | UUID |
| accepted_at | Timestamp |
| created_at | Timestamp |

### `federal_roles`

| Field | Type |
|---|---|
| id | UUID |
| name | String |
| description | Text |
| is_system_default | Boolean |
| is_custom | Boolean |
| created_by | UUID |
| created_at | Timestamp |

### `federal_role_permissions`

| Field | Type |
|---|---|
| id | UUID |
| role_id | UUID |
| permission_key | String |
| allowed | Boolean |

### `national_policies`

| Field | Type |
|---|---|
| id | UUID |
| title | String |
| policy_category | Enum |
| description | Text |
| legal_basis | Text |
| scope | Text |
| affected_entities | JSON |
| status | Enum |
| current_version_id | UUID |
| created_by | UUID |
| created_at | Timestamp |

### `policy_versions`

| Field | Type |
|---|---|
| id | UUID |
| policy_id | UUID |
| version | String |
| content | JSON/Text |
| rules | JSON |
| status | draft/review/approved/published/active/superseded/archived |
| effective_date | Date |
| review_date | Date |
| published_at | Timestamp |
| created_by | UUID |
| approved_by | UUID |

### `policy_rules`

| Field | Type |
|---|---|
| id | UUID |
| policy_version_id | UUID |
| rule_name | String |
| rule_type | String |
| applies_to | JSON |
| condition | JSON |
| action | JSON |
| severity | low/medium/high/critical |
| blocking_effect | Boolean |
| status | active/inactive |

### `state_policy_adoptions`

| Field | Type |
|---|---|
| id | UUID |
| state_id | UUID |
| policy_id | UUID |
| policy_version_id | UUID |
| status | pending/adopted/active/superseded |
| implementation_start_date | Date |
| adopted_by | UUID |
| adopted_at | Timestamp |

### `certificate_templates`

| Field | Type |
|---|---|
| id | UUID |
| name | String |
| version | String |
| template_schema | JSON |
| status | draft/published/active/superseded |
| created_by | UUID |
| published_at | Timestamp |

---

## 20. Implementation Chunks for Codex

### Chunk 1: Federal Account, Departments, Roles and Team Management

```text
Implement Federal Ministry account setup and stakeholder management.

Create or extend models for:
- federal_profiles
- federal_departments
- federal_team_members
- federal_roles
- federal_role_permissions
- federal_invitations

Federal profile fields:
- ministry_name
- department_name
- programme_name
- national_coordinator
- official_email
- official_phone
- logo_url
- active_guideline_version
- reporting_cycle
- central_portal_status

Default roles:
1. Federal Super Admin
2. National Programme Manager
3. Director / Department Head
4. Policy Configuration Officer
5. Standards Officer
6. Legal / Regulatory Reviewer
7. Medical / Clinical Reviewer
8. M&E Officer
9. Data Analyst
10. State Coordination Officer
11. Facility Oversight Officer
12. Certificate Registry Officer
13. Public Awareness Officer
14. Compliance / Enforcement Officer
15. Viewer / Auditor

Build UI pages:
- /federal/settings/profile
- /federal/team
- /federal/team/invite
- /federal/roles
- /federal/roles/new
- /federal/departments

Add permissions and audit logs for all team, role, and department actions.
```

### Chunk 2: Federal Policy Library and Versioning

```text
Build the Federal National Policy Library.

Features:
1. Federal users can create policies/standards.
2. Each policy must have:
   - title
   - policy_category
   - description
   - guideline/legal basis
   - scope
   - affected entities
   - effective date
   - review date
   - status
   - version
3. Supported policy categories:
   - Food Handler Eligibility Standard
   - Food Establishment Coverage Standard
   - Medical Test Standard
   - Laboratory Investigation Standard
   - Vaccination Standard
   - Health Declaration Standard
   - Facility Accreditation Standard
   - Certificate Standard
   - Reporting Standard
   - Compliance and Enforcement Standard
   - M&E Indicator Standard
4. Policy lifecycle:
   - draft
   - technical_review
   - legal_review
   - approved
   - published
   - active
   - superseded
   - archived
5. Published policies are immutable.
6. Editing a published policy creates a new draft version.
7. States should be notified when a new policy version is published.

Build pages:
- /federal/policies
- /federal/policies/new
- /federal/policies/:id
- /federal/policies/:id/versions
- /federal/policies/:id/review
```

### Chunk 3: Federal Policy Approval Workflow

```text
Implement Federal policy approval workflow.

Workflow:
1. Policy Configuration Officer creates draft policy.
2. Technical Reviewer reviews content.
3. Legal / Regulatory Reviewer reviews legal basis.
4. Medical / Clinical Reviewer reviews clinical rules where applicable.
5. Director / Department Head approves.
6. Authorized Federal user publishes policy.
7. Published policy becomes active based on effective date.

Requirements:
- Track reviewer comments.
- Allow approve, reject, return for correction.
- Keep full version history.
- Lock policy after publication.
- Audit log every workflow action.
- Notify next reviewer when action is required.
```

### Chunk 4: Federal Standards Configuration Engine

```text
Build Federal Standards Configuration Engine.

The engine should allow Federal users to configure machine-readable rules for:
- food handler categories
- food establishment types
- required medical tests
- lab result rules
- vaccination requirements
- certificate validity
- re-examination triggers
- facility accreditation criteria
- reporting requirements
- compliance flags

Each rule should include:
- rule_name
- rule_type
- applies_to
- condition
- action
- severity
- blocking_effect
- policy_version_id
- effective_date
- status

Example rule:
If required lab test result is missing, block certificate generation.

Example rule:
If certificate expiry date has passed, mark food handler as non-compliant.

Build APIs and UI for creating, editing, previewing, publishing, and testing rules.
```

### Chunk 5: Federal Health Declaration Template Builder

```text
Build Federal Health Declaration Form Template Builder using the existing Forms Tool.

Requirements:
1. Federal users can create the National Food Handler Health Declaration Form Template.
2. Template must support:
   - sections
   - field ownership
   - required fields
   - locked fields
   - risk flags
   - validation rules
   - versioning
3. Default sections:
   - Identity Information
   - Food Handler Information
   - Recent Illness Declaration
   - Communicable Disease History
   - Skin and Infection Declaration
   - Vaccination History
   - Consent
   - Declaration Statement
4. Default fields:
   - fever
   - jaundice
   - diarrhoea
   - vomiting
   - cough or flu
   - sore throat
   - skin infection
   - boils/cuts/lesions
   - discharge from eyes/nose/ears/mouth
   - known typhoid carrier history
   - recent cholera/dysentery/gastrointestinal infection
   - Hepatitis A history
   - current medication
   - Typhoid vaccination certificate upload/date
   - Hepatitis A vaccination certificate upload/date
   - consent checkbox
   - declaration certification checkbox
5. Published Federal fields must be locked for State and Facility users.
6. Editing a published template creates a new version.
7. Notify States when a new Federal declaration template is published.
```

### Chunk 6: Federal Medical Test Package Configuration

```text
Build Federal Medical Test Package Configuration.

Federal users should be able to create and publish the national minimum Food Handler Medical Test Package.

Default package components:
- Health Declaration Form
- Doctor Declaration Validation
- Physical Examination
- Vaccination Certificate Review
- Stool microscopy, culture and sensitivity
- Hepatitis A Antigen
- Additional tests if clinically indicated
- Doctor Final Review
- Certificate of Fitness or Temporary Unfit Report

Rules:
1. Federal mandatory package items cannot be removed by States or facilities.
2. States can configure price and implementation details only.
3. Facilities can view package requirements but cannot remove mandatory items.
4. Certificate generation should check that all required package components are completed.
5. Package versions must be tracked.
6. Old assessments must retain the package version used at booking.
```

### Chunk 7: Federal Vaccination Standard Configuration

```text
Build Federal Vaccination Standard Configuration.

Requirements:
1. Federal users can configure required vaccines.
2. Default vaccine rules:
   - Typhoid: required, one dose every 3 years.
   - Hepatitis A: required, two doses at 0 and 6 months.
3. Each vaccine rule should include:
   - vaccine_name
   - required
   - dose_schedule
   - validity_period
   - missing_certificate_action
   - certificate_blocking_rule
   - applies_to
   - policy_version_id
4. Facilities must apply active vaccine rules during assessment.
5. Missing or invalid vaccine certificate should trigger doctor review and vaccine action.
6. States and facilities cannot weaken Federal vaccine rules.
```

### Chunk 8: Federal Facility Accreditation Criteria

```text
Build Federal Facility Accreditation Criteria Configuration.

Federal users should define the national minimum criteria for approved medical facilities.

Criteria should include:
- allowed facility types
- required documents
- medical record capacity
- computers and internet access
- trained records staff
- doctor availability
- lab capacity
- QR certificate capability
- reporting/documentation policy
- annual re-accreditation requirement

Rules:
1. State accreditation workflows must use Federal criteria as minimum standard.
2. State can add additional criteria but cannot remove Federal criteria.
3. Facilities that do not meet Federal minimum criteria cannot be approved.
4. Accreditation expiry should default to one year unless policy changes.
5. Facility approval/suspension/renewal should be visible to Federal.
```

### Chunk 9: Federal Certificate Template and Central Registry

```text
Build Federal Certificate Template and Central Certificate Registry.

Certificate template requirements:
- certificate_number
- QR code
- verification token/URL
- full name
- date of birth
- gender
- passport photograph
- NIN
- food handler category
- issuing state
- approved medical facility
- medical doctor
- assessment date
- issue date
- expiry date
- certificate status

Registry features:
1. Store every generated certificate centrally.
2. Search by certificate number, NIN, food handler, State, facility, status.
3. Verify certificate by QR token.
4. Track active, expired, revoked, suspended certificates.
5. Detect duplicate active certificates for same NIN where applicable.
6. Allow authorized certificate revocation with reason.
7. Do not expose lab results or private medical notes on public verification page.
8. Audit log certificate generation, verification, revocation, and status changes.
```

### Chunk 10: Federal State Management and Adoption Monitoring

```text
Build Federal State Management module.

Features:
1. Federal can create or approve State Ministry accounts.
2. Federal can view all States/FCT.
3. Federal can monitor:
   - onboarding status
   - policy adoption status
   - declaration template adoption
   - facility approval count
   - assessment volume
   - certificate issuance
   - expired certificate rate
   - M&E report submission status
   - compliance cases
4. Federal can send reminders to States that have not adopted active policies/templates.
5. Federal can view State implementation notes.
6. Federal can compare adoption by policy version.
```

### Chunk 11: National Facility Registry

```text
Build National Facility Registry for Federal oversight.

Requirements:
1. When a State approves a medical facility, it appears in the Federal facility registry.
2. Federal can view all facilities nationally.
3. Filters:
   - State
   - LGA
   - approval status
   - accreditation expiry
   - facility type
   - assessment volume
4. Federal can view facility performance:
   - assessments completed
   - pending lab results
   - doctor review delays
   - certificates generated
   - temporary unfit reports
   - suspension history
5. Federal cannot normally approve State facilities unless given special override permission.
6. Federal can flag facility-level risks and request State review.
```

### Chunk 12: Federal M&E Reporting

```text
Build Federal M&E reporting module.

Requirements:
1. States submit periodic reports to Federal.
2. Federal M&E Officer can review submitted reports.
3. Federal can accept, return for clarification, or escalate report.
4. Reports should include:
   - approved facilities
   - assessments completed
   - certificates issued
   - temporary unfit reports
   - expired certificates
   - facility compliance status
   - food business compliance status
   - enforcement cases
   - public awareness activities
5. Federal dashboard should update after report acceptance.
6. Federal should also have auto-generated analytics from platform data, independent of submitted report narratives.
```

### Chunk 13: Federal Compliance and Escalation

```text
Build Federal Compliance and Escalation module.

Requirements:
1. Federal can view escalated cases from States.
2. Federal can create national compliance alerts.
3. System should auto-flag:
   - State has not adopted active policy
   - State M&E report is overdue
   - unusual certificate generation pattern
   - duplicate active certificates for same NIN
   - high facility suspension rate
   - high pending lab result rate
   - high expired certificate count
4. Federal Compliance Officer can:
   - request clarification from State
   - return issue to State for action
   - escalate internally
   - close case
5. Audit log all compliance actions.
```

### Chunk 14: Federal Public Awareness Notices

```text
Build Federal Public Awareness and Notice module.

Requirements:
1. Federal users can create notices/campaigns.
2. Audience options:
   - States
   - Medical facilities
   - Food businesses
   - Food handlers
   - Inspectors
   - General public
3. Notices should support:
   - title
   - body
   - attachments
   - target audience
   - effective date
   - expiry date
   - status
4. Workflow:
   - draft
   - submitted
   - approved
   - published
   - archived
5. Published notices trigger in-app notifications.
6. Audit log notice creation, approval, and publication.
```

### Chunk 15: Federal Dashboard and Analytics

```text
Build Federal dashboard and analytics.

Dashboard widgets:
- States onboarded
- States using latest policy version
- States using latest declaration template
- approved facilities nationally
- registered food handlers
- assessments completed
- certificates issued
- active certificates
- expired certificates
- temporary unfit reports
- State report submissions
- facility performance
- compliance alerts
- QR verification activity
- public awareness campaigns

Filters:
- date range
- State
- LGA
- facility
- food handler category
- certificate status
- policy version

Add charts/tables for:
- State-by-State adoption
- assessment volume over time
- certificate issuance over time
- expired certificates by State
- facility performance ranking
- temporary unfit trends
```

### Chunk 16: Federal Audit Logs

```text
Implement Federal audit logs.

Audit events:
- Federal user invited
- Federal role created/updated
- Department created/updated
- National policy created
- Policy reviewed
- Policy approved
- Policy published
- Policy superseded
- Health declaration template created/published
- Medical test package updated
- Vaccination standard updated
- Facility accreditation criteria updated
- Certificate template published
- State account created
- State adoption reminder sent
- State report accepted/returned
- Compliance case escalated/closed
- Public notice published
- Certificate revoked
- Audit log exported

Audit logs should be filterable by:
- actor
- role
- department
- action
- entity type
- entity ID
- date range
- State
```

---

## 21. Acceptance Criteria

### Federal Account Setup

- Federal profile can be created and edited.
- Federal departments can be created.
- Federal users can be invited and assigned roles.
- Federal permissions are enforced.

### Policy Configuration

- Federal can create national policies.
- Policies support versioning.
- Published policies are immutable.
- States are notified when new policies are published.

### Standards Configuration

- Federal can configure food handler categories, tests, vaccines, certificates, accreditation criteria, reporting rules, and compliance rules.
- Rules are machine-readable and enforceable by operational modules.

### Health Declaration Template

- Federal can create the national health declaration template.
- Federal fields are locked for States and facilities.
- States can adopt and extend but cannot weaken Federal fields.

### Certificate Registry

- Certificates generated by facilities are stored centrally.
- QR verification works.
- Federal can search, monitor, and revoke certificates where authorized.
- Public verification does not reveal medical details.

### State Monitoring

- Federal can monitor State onboarding, policy adoption, report submission, facility approval, assessments, certificates, and compliance.

### M&E and Compliance

- Federal can review State reports.
- Federal can monitor national indicators.
- Federal can handle escalated compliance cases.
- Federal dashboards update from live data and submitted reports.

---

## 22. Final Federal Ministry Flow

```text
1. Federal Ministry account is created.

2. Federal Super Admin completes Ministry/programme profile.

3. Federal Admin configures departments, roles, permissions, and team members.

4. Federal Policy Officer creates national standards and policies.

5. Federal uses Forms Tool to create the national Health Declaration Form template.

6. Federal configures medical test package, lab requirements, vaccination rules, facility accreditation criteria, certificate rules, and M&E indicators.

7. Federal submits policies/templates for technical, legal, clinical, and director-level approval.

8. Federal publishes active policy and template versions.

9. System notifies State Ministries to adopt Federal policies/templates.

10. States adopt and configure State-level implementation details.

11. Federal monitors State adoption and implementation readiness.

12. States approve medical facilities; Federal national facility registry updates.

13. Food handlers complete tests through approved facilities.

14. Facilities generate doctor-approved certificates/reports.

15. Certificates are stored in the Federal central certificate database.

16. Federal monitors certificates, facilities, assessments, expired records, State reports, and compliance trends.

17. States submit periodic M&E reports to Federal.

18. Federal reviews reports, accepts or returns them, and uses data for policy decisions.

19. Federal handles escalated compliance issues and publishes national notices.

20. Federal updates policies and standards through new versions when required.
```
