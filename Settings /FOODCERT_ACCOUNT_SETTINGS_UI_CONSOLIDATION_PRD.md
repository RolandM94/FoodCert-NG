# PRD: Account Settings & System Configuration UI Consolidation — FoodCert NG

## 1. Document Purpose

This PRD defines the introduction of dedicated **Account Settings** areas across FoodCert NG account types, with special focus on the **State Ministry Account Settings**.

The immediate product decision is:

> Configuration items such as **Assessment Fees** and **Certificate Templates** should be moved out of scattered operational modules and placed inside the relevant account/system settings area.

For example:

```txt
State Ministry
└── Account Settings
    ├── Fees & Payments
    └── Certificate Settings
```

Operational modules should use these settings, but should not own configuration screens.

---

# 2. Product Decision

## 2.1 Create Account Settings for Each Account Type

Each major account type should have its own Account Settings area:

```txt
State Ministry Account Settings
Federal Ministry Account Settings
Medical Facility Account Settings
Employer Account Settings
Platform Admin System Settings
```

Each settings area should only expose settings relevant to that account type and the user’s permissions.

## 2.2 Move Fees to State Account Settings

Assessment fee configuration should move to:

```txt
State Ministry → Account Settings → Fees & Payments
```

The State Ministry sets official assessment fees for the state. Medical facilities should not set their own food handler assessment fees.

## 2.3 Move Certificate Template to State Account Settings

Certificate template configuration should move to:

```txt
State Ministry → Account Settings → Certificate Settings
```

Certificate Registry and Certificate Validation should not configure certificate templates. They should only use issued certificate data and verification rules.

## 2.4 Core Rule

Use this rule across the platform:

> **Operational modules run workflows. Account Settings configure rules, templates, fees, defaults, and account-level policies.**

---

# 3. Why This Update Is Needed

Currently, configuration pages can become scattered across the platform.

Examples of scattered configuration include:

```txt
Fees as a standalone menu
Certificate Template as a standalone menu
Inspection defaults inside Inspections
Medical facility rules inside Medical Facilities
Notification rules scattered across modules
```

This creates a confusing experience because users may not know where to configure rules versus where to run daily operations.

The cleaner structure is:

```txt
Account Settings = Configure the rules
Operational Modules = Use the rules
Reports/Revenue = Monitor the results
```

Examples:

```txt
Account Settings → Fees & Payments = Configure assessment fees
Payments & Revenue = View collections, transactions, settlements, reconciliation
```

```txt
Account Settings → Certificate Settings = Configure certificate template and validity
Certificates = Issue, search, validate, suspend, revoke, renew certificates
```

---

# 4. Recommended State Ministry Navigation

## 4.1 State Ministry Sidebar

Recommended State Ministry sidebar:

```txt
Dashboard
Stakeholder Management
Medical Facilities
Directory & Registry
Forms Tool
Inspections & Enforcement
Certificates
Payments & Revenue
Reports
Account Settings
```

Do not show these as separate top-level modules:

```txt
Fees
Assessment Fees
Certificate Template
Certificate Branding
Certificate Rules
Inspection Settings
Notification Settings
```

These should be under Account Settings.

---

# 5. State Ministry Account Settings Structure

## 5.1 Parent Module

```txt
Account Settings
```

## 5.2 Recommended Tabs / Sections

```txt
Account Settings
├── State Profile
├── Fees & Payments
├── Certificate Settings
├── Medical Facility Settings
├── Inspection Settings
├── Forms Settings
├── Notification Settings
├── Security & Access
└── Audit Logs
```

## 5.3 Tab Summary

| Section | Purpose |
|---|---|
| State Profile | Configure state name, logo, ministry details, contact information, official addresses |
| Fees & Payments | Configure assessment fees, certificate fees, accreditation fees, re-accreditation fees, settlement rules, effective dates |
| Certificate Settings | Configure certificate template, branding, authorized signatory, validity period, QR display, numbering rules |
| Medical Facility Settings | Configure accreditation rules, required documents, review timelines, re-accreditation reminders |
| Inspection Settings | Configure inspection defaults, inspection categories, severity levels, notice timelines, escalation rules |
| Forms Settings | Configure form defaults, default templates, response rules, retention rules |
| Notification Settings | Configure state-level notification templates and reminder schedules |
| Security & Access | View security policies and account-level access settings; operational roles remain in Stakeholder Management |
| Audit Logs | View changes made to account settings |

---

# 6. Fees & Payments Settings

## 6.1 Purpose

The Fees & Payments section allows authorized State Ministry users to configure official fees that apply within their state.

## 6.2 Location

```txt
State Ministry → Account Settings → Fees & Payments
```

## 6.3 Fee Types

Supported fee types:

```txt
Food Handler Assessment Fee
Certificate Fee, if applicable
Medical Facility Accreditation Fee
Medical Facility Re-accreditation Fee
Late Renewal Fee, if applicable
Replacement Certificate Fee, if applicable
Inspection Revisit Fee, if applicable
```

## 6.4 Fee Scope

Fee scope should support:

```txt
State-wide
Facility type, if policy allows
Assessment type, if policy allows
Certificate type, if policy allows
Effective date range
```

MVP recommendation:

```txt
State-wide standard assessment fee
```

This avoids each medical facility charging different assessment fees.

## 6.5 Fee Configuration Fields

Recommended fields:

```txt
Fee Name
Fee Type
Amount
Currency
Applies To
Effective Start Date
Effective End Date
Status
Created By
Approved By
Approval Date
Notes
```

## 6.6 Fee Statuses

```txt
Draft
Pending Approval
Active
Scheduled
Expired
Archived
Rejected
```

## 6.7 Fee Approval Workflow

Recommended workflow:

```txt
Finance/Policy Officer creates fee draft
→ Authorized approver reviews
→ Fee is approved and scheduled
→ Fee becomes active on effective date
→ Payment workflows use active fee
→ Old fee is retained in history
```

## 6.8 Fee History

The system must keep fee history.

Fee history is important because a food handler payment should always be linked to the fee amount active at the time of payment.

Do not overwrite old fees.

## 6.9 Settlement Rules

Fees & Payments settings may also include settlement split configuration.

Examples:

```txt
State Share
Medical Facility Share
Platform Service Charge
Gateway Charge
Tax/VAT, if applicable
```

Settlement rules should be permission-controlled and audit logged.

## 6.10 What Should Not Be in Fees Settings

Do not place transaction monitoring here.

The following belong in Payments & Revenue:

```txt
Transactions
Collections
Receipts
Settlements
Reconciliation
Refunds
Revenue Reports
Payment Failures
```

---

# 7. Certificate Settings

## 7.1 Purpose

Certificate Settings allows the State Ministry to configure how food handler certificates issued in the state should look and behave.

## 7.2 Location

```txt
State Ministry → Account Settings → Certificate Settings
```

## 7.3 Certificate Settings Sections

Recommended sub-sections:

```txt
Certificate Template
Certificate Branding
Authorized Signatory
Validity Rules
QR Verification Display
Certificate Numbering
Footer Notes / Legal Text
Renewal Rules
Preview & Test Certificate
Version History
```

## 7.4 Certificate Template

The certificate template should define:

```txt
Layout
State logo placement
Ministry name
Certificate title
Food handler photo placement
Food handler identity fields
NIN display rule
Certificate number placement
Issue date
Expiry date
QR code placement
Authorized signatory block
Footer text
Verification URL text
Watermark, if applicable
```

## 7.5 Certificate Branding

Configurable branding:

```txt
State logo
Ministry logo, if different
Primary color
Secondary color
Seal / stamp image, if allowed
Watermark
Header text
Footer text
```

## 7.6 Authorized Signatory

Fields:

```txt
Signatory Name
Designation
Department
Signature Image
Effective Start Date
Effective End Date
Status
```

Only authorized users should configure signatories.

## 7.7 Certificate Validity Rules

Certificate validity should be configurable by policy.

Recommended fields:

```txt
Validity Duration
Validity Unit
Renewal Window
Expiry Reminder Schedule
Grace Period, if policy allows
```

Example:

```txt
Validity Duration = 6
Validity Unit = Months
Renewal Reminder = 30 days before expiry
```

## 7.8 QR Verification Display Rules

Configure what public QR verification should show.

Recommended public-safe fields:

```txt
Certificate Status
Food Handler Name
Photo, if policy allows
Certificate Number
Issuing State
Issue Date
Expiry Date
Fitness Status
Verification Timestamp
```

Do not show:

```txt
Medical test results
Diagnosis
Doctor notes
Lab results
Health declaration answers
Private medical data
```

## 7.9 Certificate Number Format

The State Ministry should be able to configure certificate numbering format within allowed system constraints.

Example:

```txt
FCNG-{STATE_CODE}-{YEAR}-{SEQUENCE}
```

The system should prevent duplicate certificate numbers.

## 7.10 Certificate Versioning

Certificate templates should be versioned.

Rules:

- Existing certificates remain linked to the template version used at issuance.
- Updating a template creates a new version.
- New certificates use the active template version.
- Old template versions remain viewable for audit and reprint purposes.

---

# 8. Medical Facility Settings

## 8.1 Purpose

Medical Facility Settings control state-level rules for facility accreditation and monitoring.

## 8.2 Example Settings

```txt
Required accreditation documents
Accreditation validity period
Re-accreditation reminder timeline
Facility inspection checklist default
Minimum facility requirements
Accreditation review SLA
Suspension reason categories
Facility performance thresholds
```

## 8.3 Operational Usage

These settings are used by:

```txt
Medical Facilities Module
Accreditation Workflow
Facility Reports
Notifications
```

---

# 9. Inspection Settings

## 9.1 Purpose

Inspection Settings define default rules for inspections and enforcement.

## 9.2 Example Settings

```txt
Default inspection templates
Inspection categories
Inspection severity levels
Default corrective action timelines
Notice response deadlines
Escalation rules
Re-inspection timelines
Critical violation rules
```

## 9.3 Operational Usage

These settings are used by:

```txt
Inspections & Enforcement Module
Forms Tool
Notices
Cases
Reports
```

---

# 10. Forms Settings

## 10.1 Purpose

Forms Settings define default behavior for forms in the state account.

## 10.2 Example Settings

```txt
Default inspection form template
Default employer data collection template
Default medical facility report template
Default response deadline
Allow offline responses by default
Allow draft responses by default
Default reminder schedule
Form retention period
```

## 10.3 Operational Usage

These settings are used by:

```txt
Forms Tool
Inspections
Medical Facilities
Employers
Reports
```

---

# 11. Notification Settings

## 11.1 Purpose

Notification Settings allow authorized users to configure state-level notification rules.

## 11.2 Example Settings

```txt
Assessment payment confirmation template
Certificate issued template
Certificate expiry reminder template
Accreditation application submitted template
Inspection assigned template
Notice issued template
Form assignment reminder template
Return-to-work clearance notification template
```

## 11.3 Channels

```txt
Email
SMS, if enabled
In-app notification
WhatsApp, if enabled in future
```

---

# 12. Security & Access Settings

## 12.1 Purpose

Security & Access Settings provide account-level security configuration.

However, user, role, and permission management should remain primarily under:

```txt
Stakeholder Management
```

## 12.2 Suggested Security Settings

```txt
Password policy, if configurable
Session timeout
Two-factor authentication requirement, if enabled
Allowed email domains, if policy allows
Login notification preferences
Account lockout rules
```

## 12.3 Relationship with Stakeholder Management

Use this distinction:

```txt
Stakeholder Management = Manage people, roles, permissions, units, invitations
Account Settings → Security & Access = Configure account-level security rules
```

---

# 13. Audit Logs

## 13.1 Purpose

All account setting changes must be audit logged.

## 13.2 Audit Events

Track:

```txt
Fee created
Fee edited
Fee approved
Fee activated
Fee archived
Settlement rule changed
Certificate template changed
Certificate template published
Signatory changed
Validity rule changed
Inspection setting changed
Notification template changed
Security setting changed
```

## 13.3 Audit Log Columns

```txt
Date / Time
Actor
Action
Setting Area
Old Value
New Value
Reason / Note
IP Address
Device / User Agent
```

---

# 14. Account Settings by Account Type

## 14.1 State Ministry Account Settings

```txt
State Profile
Fees & Payments
Certificate Settings
Medical Facility Settings
Inspection Settings
Forms Settings
Notification Settings
Security & Access
Audit Logs
```

## 14.2 Federal Ministry Account Settings

Federal settings should focus on national policy and oversight.

```txt
Federal Profile
National Policy Settings
National Certificate Rules, if applicable
National Reporting Settings
Forms Settings
Notification Settings
Security & Access
Audit Logs
```

Federal should not override state fees unless the product policy explicitly allows national fee bands or caps.

## 14.3 Medical Facility Account Settings

Medical facility settings should be limited to facility-owned configuration.

```txt
Facility Profile
Departments / Units
Operating Hours
Bank / Settlement Information
Notification Preferences
Security & Access
Audit Logs
```

Medical facilities should see state assessment fees as read-only.

## 14.4 Employer Account Settings

Employer settings should include:

```txt
Business Profile
Branches / Outlets Defaults
Billing & Subscription
Notification Preferences
Security & Access
Audit Logs
```

Employers should not configure state assessment fees or certificate templates.

## 14.5 Platform Admin System Settings

Platform Admin settings should include:

```txt
System Profile
Global Defaults
Account Type Settings
Payment Gateway Configuration
Form Engine Settings
Certificate Engine Settings
Feature Flags
Security Settings
Audit Logs
```

---

# 15. UI Consolidation Rules

## 15.1 Move Configuration Pages into Account Settings

Move these into State Account Settings:

```txt
Fees
Assessment Fees
Certificate Template
Certificate Branding
Certificate Validity Rules
Certificate Number Format
Inspection Defaults
Notification Defaults
```

## 15.2 Operational Modules Should Not Configure Account Rules

Operational modules should consume settings.

Examples:

```txt
Assessments use active assessment fee
Payments use settlement rules
Certificates use active certificate template
Inspections use default inspection settings
Forms use default form settings
Notifications use notification templates
```

## 15.3 Revenue Module Should Not Configure Fees

Payments & Revenue should show:

```txt
Transactions
Collections
Settlements
Reconciliation
Receipts
Revenue Reports
Refunds
```

It should not be the main configuration area for assessment fees.

## 15.4 Certificate Registry Should Not Configure Certificate Templates

Certificate Registry should show:

```txt
Issued certificates
Certificate statuses
Certificate search
Suspension/revocation, where permitted
Renewal tracking
Verification logs
```

It should not configure templates.

---

# 16. Recommended Routes

## 16.1 State Account Settings Routes

```txt
/state/account-settings
/state/account-settings?tab=profile
/state/account-settings?tab=fees-payments
/state/account-settings?tab=certificate-settings
/state/account-settings?tab=medical-facility-settings
/state/account-settings?tab=inspection-settings
/state/account-settings?tab=forms-settings
/state/account-settings?tab=notification-settings
/state/account-settings?tab=security-access
/state/account-settings?tab=audit-logs
```

## 16.2 Legacy Redirects

If old routes exist, redirect them.

```txt
/state/fees → /state/account-settings?tab=fees-payments
/state/assessment-fees → /state/account-settings?tab=fees-payments
/state/certificate-template → /state/account-settings?tab=certificate-settings
/state/certificate-settings → /state/account-settings?tab=certificate-settings
/state/inspection-settings → /state/account-settings?tab=inspection-settings
```

---

# 17. Data Model Requirements

## 17.1 AccountSetting

General account settings wrapper.

```txt
id
account_type
organization_id
setting_key
setting_value_json
setting_group
status
created_by
updated_by
created_at
updated_at
```

## 17.2 AssessmentFeeSetting

```txt
id
state_organization_id
fee_type
fee_name
amount
currency
applies_to
scope_json
effective_start_date
effective_end_date
status
approval_status
created_by
approved_by
approved_at
notes
created_at
updated_at
```

## 17.3 SettlementRule

```txt
id
state_organization_id
fee_type
state_share
facility_share
platform_share
gateway_fee_rule_json
tax_rule_json
effective_start_date
effective_end_date
status
created_by
approved_by
created_at
updated_at
```

## 17.4 CertificateTemplateSetting

```txt
id
state_organization_id
template_name
version_number
layout_json
branding_json
qr_display_json
numbering_format
validity_rule_json
status
published_by
published_at
created_by
created_at
updated_at
```

## 17.5 CertificateSignatory

```txt
id
state_organization_id
name
designation
department
signature_file_url
effective_start_date
effective_end_date
status
created_by
created_at
updated_at
```

## 17.6 AccountSettingsAuditLog

```txt
id
organization_id
account_type
actor_id
action
setting_group
setting_key
entity_type
entity_id
old_value_json
new_value_json
reason
ip_address
user_agent
created_at
```

---

# 18. API Requirements

## 18.1 Account Settings APIs

```txt
GET   /api/account-settings
GET   /api/account-settings/:group
PATCH /api/account-settings/:group
GET   /api/account-settings/audit-logs
```

## 18.2 Fees & Payments APIs

```txt
GET   /api/state/account-settings/fees
POST  /api/state/account-settings/fees
GET   /api/state/account-settings/fees/:id
PATCH /api/state/account-settings/fees/:id
POST  /api/state/account-settings/fees/:id/submit-for-approval
POST  /api/state/account-settings/fees/:id/approve
POST  /api/state/account-settings/fees/:id/archive
GET   /api/state/account-settings/fees/active
```

## 18.3 Settlement Rule APIs

```txt
GET   /api/state/account-settings/settlement-rules
POST  /api/state/account-settings/settlement-rules
PATCH /api/state/account-settings/settlement-rules/:id
POST  /api/state/account-settings/settlement-rules/:id/approve
GET   /api/state/account-settings/settlement-rules/active
```

## 18.4 Certificate Settings APIs

```txt
GET   /api/state/account-settings/certificate-template
POST  /api/state/account-settings/certificate-template
PATCH /api/state/account-settings/certificate-template/:id
POST  /api/state/account-settings/certificate-template/:id/preview
POST  /api/state/account-settings/certificate-template/:id/publish
GET   /api/state/account-settings/certificate-template/active
GET   /api/state/account-settings/certificate-template/versions
```

## 18.5 Certificate Signatory APIs

```txt
GET   /api/state/account-settings/certificate-signatories
POST  /api/state/account-settings/certificate-signatories
PATCH /api/state/account-settings/certificate-signatories/:id
POST  /api/state/account-settings/certificate-signatories/:id/activate
POST  /api/state/account-settings/certificate-signatories/:id/archive
```

---

# 19. Permissions

## 19.1 Account Settings Permissions

```txt
account_settings.view
account_settings.update
account_settings.audit.view
```

## 19.2 Fees Permissions

```txt
fees.view
fees.create
fees.update
fees.submit_for_approval
fees.approve
fees.archive
settlement_rules.view
settlement_rules.update
settlement_rules.approve
```

## 19.3 Certificate Settings Permissions

```txt
certificate_settings.view
certificate_settings.update
certificate_template.create
certificate_template.update
certificate_template.preview
certificate_template.publish
certificate_template.archive
certificate_signatory.view
certificate_signatory.create
certificate_signatory.update
certificate_signatory.activate
certificate_signatory.archive
```

## 19.4 Role Examples

| Role | Suggested Access |
|---|---|
| State Admin | View most settings; update non-financial settings if permitted |
| Policy Officer | Configure policy-related settings; draft fee/certificate rules |
| Finance Officer | Draft fee and settlement settings; view revenue-related settings |
| Permanent Secretary / Authorized Approver | Approve fee changes and certificate template publication |
| Certificate Officer | Manage certificate template drafts and preview certificates |
| M&E Officer | View settings and audit logs; no fee approval by default |
| Platform Admin | Manage global defaults and technical settings |

Backend permissions must remain the source of truth.

---

# 20. Frontend Components

## 20.1 Account Settings Components

```txt
AccountSettingsPage
AccountSettingsTabs
SettingsSectionHeader
SettingsPermissionGuard
SettingsSaveBar
SettingsAuditLogTable
```

## 20.2 Fees Components

```txt
FeesPaymentsSettings
AssessmentFeeTable
AssessmentFeeForm
FeeApprovalPanel
FeeHistoryDrawer
SettlementRulesTable
SettlementRuleForm
ActiveFeeSummaryCard
```

## 20.3 Certificate Settings Components

```txt
CertificateSettingsPage
CertificateTemplateEditor
CertificateTemplatePreview
CertificateBrandingPanel
CertificateValidityRulesForm
CertificateNumberingFormatForm
CertificateQrDisplayRulesForm
CertificateSignatoryTable
CertificateSignatoryForm
CertificateTemplateVersionHistory
```

## 20.4 Other Settings Components

```txt
StateProfileSettings
MedicalFacilitySettings
InspectionSettings
FormsSettings
NotificationSettings
SecurityAccessSettings
```

---

# 21. Acceptance Criteria

## 21.1 Account Settings

- State Ministry has an Account Settings module.
- Account Settings appears as one sidebar item.
- Account Settings contains the configured sections/tabs.
- Tabs are permission-based.
- Unauthorized users cannot update restricted settings.
- All setting changes are audit logged.

## 21.2 Fees & Payments

- Assessment Fees are configured under Account Settings → Fees & Payments.
- Assessment Fees are no longer a separate top-level module.
- State can create, approve, schedule, activate, and archive fees.
- Medical facilities cannot set official state assessment fees.
- Medical facilities can view active state fee schedule as read-only where relevant.
- Payments use the active fee at the time of transaction.
- Old fees remain in history.

## 21.3 Certificate Settings

- Certificate Template is configured under Account Settings → Certificate Settings.
- Certificate Template is no longer a separate top-level module.
- State can configure certificate branding, template layout, QR display rules, validity, signatory, and numbering format.
- Certificate templates are versioned.
- Existing certificates remain linked to the template version used at issuance.
- Certificate Registry uses the active template but does not configure it.

## 21.4 UI Consolidation

- No scattered top-level Fees menu remains for State Ministry.
- No scattered top-level Certificate Template menu remains for State Ministry.
- Operational modules consume settings but do not own configuration pages.
- Legacy routes redirect to Account Settings tabs.

---

# 22. Implementation Chunks for Codex

## Chunk 1: Account Settings Parent Module

### Goal

Create the Account Settings parent module for State Ministry.

### Tasks

- Add Account Settings to State Ministry navigation.
- Create `AccountSettingsPage`.
- Add tabs:
  - State Profile
  - Fees & Payments
  - Certificate Settings
  - Medical Facility Settings
  - Inspection Settings
  - Forms Settings
  - Notification Settings
  - Security & Access
  - Audit Logs
- Add permission-based tab visibility.

### Acceptance Criteria

- Account Settings appears as one sidebar item.
- Tabs render correctly.
- Unauthorized tabs/actions are hidden.
- Page follows FoodCert NG design system.

---

## Chunk 2: Move Fees into Account Settings

### Goal

Move assessment fee configuration into Account Settings → Fees & Payments.

### Tasks

- Create Fees & Payments settings tab.
- Add fee table.
- Add create/edit fee form.
- Add fee approval workflow.
- Add active fee summary.
- Add fee history.
- Redirect old fee routes.

### Acceptance Criteria

- State users configure fees from Account Settings.
- Old fee menu/route redirects correctly.
- Medical facilities cannot edit state fees.
- Active fee is available to payment workflows.
- Fee changes are audit logged.

---

## Chunk 3: Settlement Rules Settings

### Goal

Add settlement split configuration under Fees & Payments.

### Tasks

- Add settlement rules table.
- Add settlement rule form.
- Add approval workflow if required.
- Add effective dates.
- Connect active settlement rule to settlement calculation service.

### Acceptance Criteria

- Authorized users can configure settlement rules.
- Settlement rules are versioned/effective-dated.
- Payments and settlements use the active rule.
- Changes are audit logged.

---

## Chunk 4: Move Certificate Template into Account Settings

### Goal

Move certificate template configuration into Account Settings → Certificate Settings.

### Tasks

- Create Certificate Settings tab.
- Add certificate template editor.
- Add branding panel.
- Add QR display rule settings.
- Add validity rule settings.
- Add numbering format settings.
- Add preview function.
- Add publish/version workflow.
- Redirect old certificate template routes.

### Acceptance Criteria

- Certificate template is configured from Account Settings.
- Old Certificate Template route redirects correctly.
- Active template is available to certificate issuance.
- Certificate Registry does not configure templates.
- Template changes are versioned and audit logged.

---

## Chunk 5: Certificate Signatory Management

### Goal

Allow authorized users to manage certificate signatories.

### Tasks

- Add signatory table.
- Add signatory form.
- Add signature upload.
- Add effective date range.
- Add activate/archive action.
- Connect active signatory to certificate template preview and issuance.

### Acceptance Criteria

- Authorized users can manage signatories.
- Certificates use active signatory.
- Old certificates preserve signatory used at issuance.
- Signatory changes are audit logged.

---

## Chunk 6: Other Settings Sections

### Goal

Create placeholders/initial settings for other Account Settings tabs.

### Tasks

- Build State Profile settings.
- Build Medical Facility Settings.
- Build Inspection Settings.
- Build Forms Settings.
- Build Notification Settings.
- Build Security & Access settings.
- Ensure each tab has empty/loading/error states.

### Acceptance Criteria

- All settings sections are available or gracefully marked as coming soon.
- Settings are grouped logically.
- UI is consistent.

---

## Chunk 7: Settings Audit Logs

### Goal

Audit all account setting changes.

### Tasks

- Implement `AccountSettingsAuditLog`.
- Log fee changes.
- Log certificate settings changes.
- Log signatory changes.
- Log inspection/forms/notification/security settings changes.
- Build Audit Logs tab.

### Acceptance Criteria

- Every critical settings change is logged.
- Audit log shows actor, action, old value, new value, date, and setting area.
- Audit log is permission-controlled.

---

## Chunk 8: Operational Module Integration

### Goal

Ensure operational modules consume Account Settings.

### Tasks

- Update payment flow to read active assessment fee.
- Update settlement calculation to read active settlement rule.
- Update certificate issuance to read active certificate template.
- Update QR verification display to use active QR display rules.
- Update inspection workflows to read inspection settings.
- Update forms workflows to read forms settings.

### Acceptance Criteria

- Payments use configured active fee.
- Certificates use active template.
- Operational modules no longer own these configuration screens.
- System fails safely if required setting is missing.

---

## Chunk 9: Permissions and Scope

### Goal

Secure Account Settings.

### Tasks

- Implement permissions listed in this PRD.
- Add frontend guards.
- Add backend guards.
- Add state organization scoping.
- Add approval restrictions.

### Acceptance Criteria

- Unauthorized users cannot view or update restricted settings.
- Users cannot update settings outside their state/account.
- Approvals require correct permission.
- Backend remains source of truth.

---

## Chunk 10: Final UI QA and Route Consolidation

### Goal

Confirm UI consolidation is complete.

### QA Checklist

- Account Settings appears in State sidebar.
- Fees no longer appears as standalone menu.
- Certificate Template no longer appears as standalone menu.
- Old routes redirect to Account Settings.
- Fees & Payments tab works.
- Certificate Settings tab works.
- Audit Logs work.
- Permission restrictions work.
- Operational modules consume settings.
- UI is responsive and follows design system.

---

# 23. Codex Implementation Prompt

Use this prompt for Codex:

```txt
Create a FoodCert NG Account Settings UI consolidation for the State Ministry account.

Add one parent module:
Account Settings

Tabs:
- State Profile
- Fees & Payments
- Certificate Settings
- Medical Facility Settings
- Inspection Settings
- Forms Settings
- Notification Settings
- Security & Access
- Audit Logs

Move Assessment Fees into:
State Ministry → Account Settings → Fees & Payments

Move Certificate Template into:
State Ministry → Account Settings → Certificate Settings

Do not keep Fees or Certificate Template as separate top-level State Ministry modules.

Rules:
- Operational modules run workflows.
- Account Settings configures rules, templates, fees, defaults, and account-level policies.
- Payments & Revenue should monitor transactions, collections, settlements, reconciliation, and revenue reports, but should not configure fees.
- Certificate Registry should search/manage issued certificates, but should not configure templates.
- Medical facilities can view active state assessment fee as read-only, but cannot set the official state fee.

Implement:
- AccountSettingsPage
- AccountSettingsTabs
- FeesPaymentsSettings
- AssessmentFeeTable
- AssessmentFeeForm
- FeeApprovalPanel
- FeeHistoryDrawer
- SettlementRulesTable
- CertificateSettingsPage
- CertificateTemplateEditor
- CertificateTemplatePreview
- CertificateBrandingPanel
- CertificateValidityRulesForm
- CertificateNumberingFormatForm
- CertificateQrDisplayRulesForm
- CertificateSignatoryTable
- CertificateTemplateVersionHistory
- SettingsAuditLogTable

Data models:
- AccountSetting
- AssessmentFeeSetting
- SettlementRule
- CertificateTemplateSetting
- CertificateSignatory
- AccountSettingsAuditLog

Add legacy redirects:
/state/fees → /state/account-settings?tab=fees-payments
/state/assessment-fees → /state/account-settings?tab=fees-payments
/state/certificate-template → /state/account-settings?tab=certificate-settings
/state/certificate-settings → /state/account-settings?tab=certificate-settings

Enforce permissions and state scoping. Backend permissions remain the source of truth. Follow the FoodCert NG application-wide design system using Next.js + React + TypeScript + Tailwind CSS.
```

---

# 24. MVP Build Order

1. Account Settings parent module
2. Move Fees into Account Settings
3. Settlement Rules Settings
4. Move Certificate Template into Account Settings
5. Certificate Signatory Management
6. Other settings sections
7. Settings audit logs
8. Operational module integration
9. Permissions and scope
10. Final UI QA and route consolidation
