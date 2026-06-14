# PRD: Account Settings — State Profile, Notification Settings, Security & Access, Audit Logs — FoodCert NG

## 1. Document Purpose

This PRD defines the missing **Account Settings** sections for FoodCert NG, specifically:

```txt
State Profile
Notification Settings
Security & Access
Audit Logs
```

These sections currently exist as placeholders and need to be fully designed and implemented.

The purpose of this PRD is to give Codex a clear implementation guide for building these settings under the State Ministry account.

---

# 2. Product Decision

FoodCert NG should have a dedicated **Account Settings** area for each account type.

For the **State Ministry account**, Account Settings should be the central place where the State Ministry configures state-level profile information, operational defaults, notification rules, security/access preferences, and audit visibility.

Recommended State Account Settings structure:

```txt
State Ministry
└── Account Settings
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

This PRD covers only:

```txt
State Profile
Notification Settings
Security & Access
Audit Logs
```

---

# 3. Core Product Principle

Use this rule across FoodCert NG:

```txt
Operational modules run workflows.
Account Settings configure rules, identity, defaults, permissions, notification behaviour, security controls, and audit visibility.
```

Examples:

```txt
Certificates Module = issue, validate, search, suspend certificates
Certificate Settings = configure certificate template, validity, signatories, QR display rules

Payments Module = track collections, settlements, reconciliation
Fees & Payments Settings = configure fees, fee validity, settlement rules

Inspections & Enforcement = create inspections, assign inspectors, issue notices, manage cases
Inspection Settings = configure templates, severity levels, deadlines, reminders

Account Settings = manage state profile, notification rules, security rules, and audit records
```

---

# 4. UI Consolidation Decision

Do not create separate top-level modules for:

```txt
State Profile
Notifications
Security
Audit Logs
```

They should not appear as separate primary sidebar modules.

They must be consolidated under:

```txt
Account Settings
```

Correct sidebar:

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

Inside Account Settings:

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

---

# 5. Account Settings Page Shell

## 5.1 Page Header

```txt
Account Settings
Manage your state profile, system configuration, notifications, security controls, and audit records.
```

## 5.2 Settings Navigation

Use a left settings sub-navigation or tab structure:

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

## 5.3 Recommended Layout

Desktop:

```txt
Account Settings Page
├── Header
├── Left Settings Navigation
└── Main Settings Content
```

Mobile:

```txt
Account Settings Page
├── Header
├── Settings Category Dropdown
└── Main Settings Content
```

## 5.4 Permissions

Each settings section should be permission controlled.

A user may have access to Account Settings but only see the sections they are allowed to manage.

---

# 6. State Profile

## 6.1 Purpose

The **State Profile** section stores the official State Ministry identity and administrative details used across FoodCert NG.

This profile should control how the State Ministry appears across:

```txt
Certificates
Notifications
Reports
Public verification pages
Payment receipts
Facility accreditation records
Inspection notices
Enforcement notices
```

## 6.2 State Profile Should Include

```txt
State Ministry Name
State Name
State Code
State Logo / Seal
Ministry Address
Official Email
Official Phone Number
Website
Default Timezone
Default Currency
Official Contact Person
Ministry Department / Directorate
Authorized Signatory Information
Public Display Name
```

## 6.3 State Profile Fields

### Basic Information

```txt
state_name
state_code
ministry_name
public_display_name
state_lga_coverage
```

Example:

```txt
State Name: Lagos State
State Code: LA
Ministry Name: Lagos State Ministry of Health
Public Display Name: Lagos State MOH
```

### Contact Information

```txt
official_email
official_phone
website
address_line_1
address_line_2
city
state
country
postal_code
```

### Branding

```txt
state_logo_url
state_seal_url
primary_brand_color
secondary_brand_color
certificate_logo_url
receipt_logo_url
```

### Authorized Signatory

```txt
signatory_name
signatory_title
signatory_signature_url
signatory_start_date
signatory_end_date
is_active
```

### Administrative Defaults

```txt
timezone
currency
working_days
working_hours_start
working_hours_end
public_holidays_source
```

## 6.4 State Profile UI

Recommended sections:

```txt
State Identity
Contact Information
Branding & Logos
Authorized Signatories
Administrative Defaults
```

## 6.5 State Identity Card

Fields:

```txt
State Name
State Code
Ministry Name
Public Display Name
```

## 6.6 Contact Information Card

Fields:

```txt
Official Email
Official Phone Number
Website
Official Address
```

## 6.7 Branding & Logos Card

Fields:

```txt
State Logo
State Seal
Certificate Logo
Receipt Logo
Primary Brand Color
Secondary Brand Color
```

Rules:

- Logo uploads should support PNG, JPG, SVG where allowed.
- Certificate logo should be used on certificate templates where configured.
- Receipt logo should be used on payment receipts.
- Public verification page may use the State logo/seal where permitted.

## 6.8 Authorized Signatories Card

The State should be able to manage one or more signatories.

Fields:

```txt
Name
Title
Signature Upload
Effective Start Date
Effective End Date
Status
```

Rules:

- Only one default active certificate signatory should be active at a time unless the certificate template supports multiple signatories.
- Old signatories should not be deleted if used on issued certificates.
- Issued certificates should retain the signatory that was active at issuance time.
- Signatory changes must be audit logged.

## 6.9 Administrative Defaults Card

Fields:

```txt
Timezone
Currency
Working Days
Working Hours
Public Holiday Rule
```

Rules:

- Review timeline calculations should use working days if configured.
- Reminder schedules should respect timezone.
- Payment values should use configured currency.

## 6.10 State Profile Acceptance Criteria

- Authorized users can view State Profile.
- Authorized users can edit State Profile.
- Logo uploads work.
- Signatory management works.
- State profile changes appear in relevant documents, receipts, and certificate templates.
- Changes are audit logged.
- Old certificate records are not retroactively changed unless specifically allowed.

---

# 7. Notification Settings

## 7.1 Purpose

Notification Settings allow the State Ministry to configure how users and organizations are notified about FoodCert NG events.

This should include notification preferences for:

```txt
Facility accreditation
Re-accreditation
Certificate validation
Certificate expiry
Assessment payments
Inspection assignments
Corrective action deadlines
Enforcement notices
Form assignments
Form response reminders
Illness exclusion exceptions
Return-to-work oversight signals
System/security events
```

## 7.2 Notification Channels

Support the following channels:

```txt
In-app Notification
Email
SMS, optional
WhatsApp, optional
Push Notification, future
Webhook, future
```

MVP can support:

```txt
In-app Notification
Email
```

SMS and WhatsApp can be feature-flagged.

## 7.3 Notification Categories

Recommended categories:

```txt
Accreditation Notifications
Certificate Notifications
Inspection & Enforcement Notifications
Forms Notifications
Payment & Revenue Notifications
Medical Facility Notifications
Employer Notifications
Food Handler Notifications
Security Notifications
System Announcements
```

## 7.4 Notification Events

### Accreditation Events

```txt
Facility accreditation application submitted
Application assigned to reviewer
Application pending review reminder
More information requested
Facility resubmitted application
Application approved
Application rejected
Accreditation expiring soon
Re-accreditation window opened
Facility accreditation expired
Facility accreditation suspended
```

### Certificate Events

```txt
Assessment submitted for certificate validation
Certificate validation pending
Certificate approved
Certificate rejected
Certificate issued
Certificate expiring soon
Certificate expired
Certificate suspended
Certificate revoked
QR verification anomaly detected
```

### Inspection & Enforcement Events

```txt
Inspection created
Inspector assigned
Inspection due soon
Inspection overdue
Inspection submitted
Inspection returned for correction
High severity finding submitted
Critical finding submitted
Enforcement notice issued
Corrective action due soon
Corrective action overdue
Enforcement case escalated
Follow-up inspection required
```

### Forms Events

```txt
Form template published
Form assigned
Form due soon
Form overdue
Form response submitted
Form response returned
Form response reviewed
```

### Payment & Revenue Events

```txt
Assessment payment received
Payment failed
Receipt generated
Settlement initiated
Settlement completed
Reconciliation exception detected
Refund requested
Refund completed
```

### Security Events

```txt
New user invited
User accepted invite
Role changed
Permission changed
Password changed
MFA enabled
Suspicious login detected
Account locked
API token created
API token revoked
```

## 7.5 Notification Settings UI

Use a grouped settings UI:

```txt
Notification Settings
├── Channels
├── Event Rules
├── Reminder Schedules
├── Recipients
├── Templates
└── Delivery Logs
```

## 7.6 Channels Section

Fields:

```txt
Enable In-app Notifications
Enable Email Notifications
Enable SMS Notifications
Enable WhatsApp Notifications
Default Sender Name
Default Reply-to Email
```

Channel status should show:

```txt
Active
Disabled
Not Configured
Feature Not Enabled
```

## 7.7 Event Rules Section

Each event should have configurable rules:

```txt
Event Name
Enabled / Disabled
Channels
Recipient Roles
Recipient Users
Trigger Timing
Escalation Rule
Template
```

Example:

```txt
Event: Corrective Action Overdue
Enabled: Yes
Channels: In-app, Email
Recipients: Assigned Inspector, State Enforcement Officer, State Admin
Trigger: 1 day after due date
Escalation: Notify Director after 3 days overdue
```

## 7.8 Reminder Schedules Section

Reminder schedules should be configurable for:

```txt
Certificate expiry reminders
Facility accreditation expiry reminders
Re-accreditation reminders
Inspection due reminders
Corrective action due reminders
Form due reminders
Payment reconciliation reminders
```

Example:

```txt
Certificate Expiry Reminder: 30 days, 14 days, 7 days before expiry
Facility Accreditation Expiry Reminder: 90 days, 60 days, 30 days, 14 days, 7 days
Corrective Action Reminder: 3 days before due date, on due date, 1 day overdue
```

## 7.9 Recipient Rules

Recipients can be defined by:

```txt
Specific User
Role
Organization Type
Organization
Assigned Officer
Assigned Reviewer
Assigned Inspector
Employer Admin
Facility Admin
Food Handler
State Admin
Federal Oversight User
```

## 7.10 Notification Templates

Notification templates should support:

```txt
Subject
Message Body
Channel
Variables
Preview
Language
Status
```

Variables:

```txt
{{recipient_name}}
{{state_name}}
{{facility_name}}
{{employer_name}}
{{food_handler_name}}
{{certificate_number}}
{{application_reference}}
{{inspection_reference}}
{{due_date}}
{{status}}
{{action_link}}
```

## 7.11 Delivery Logs

Delivery logs should show:

```txt
Notification Event
Recipient
Channel
Status
Sent At
Delivered At
Failed Reason
Retry Count
Action Link
```

Statuses:

```txt
Queued
Sent
Delivered
Failed
Retrying
Cancelled
```

## 7.12 Notification Acceptance Criteria

- Authorized users can configure notification channels.
- Authorized users can enable/disable event notifications.
- Reminder schedules can be configured.
- Recipients can be configured by role/user/context.
- Templates can be previewed.
- Delivery logs are visible to authorized users.
- Failed notifications can be retried where supported.
- Notification changes are audit logged.

---

# 8. Security & Access

## 8.1 Purpose

Security & Access controls state-level account security settings and high-level access policies.

Detailed user, role, and permission management should remain under:

```txt
Stakeholder Management
```

Security & Access should configure broader account security rules, not replace stakeholder management.

## 8.2 Separation from Stakeholder Management

### Stakeholder Management Handles

```txt
Users
Invites
Roles
Permissions
Teams
Units
Memberships
Role assignments
```

### Security & Access Handles

```txt
Password policy
MFA policy
Session timeout
Login restrictions
Account lockout rules
API access rules
Trusted domains
Data export restrictions
IP allowlist, optional
Security alerts
Access review settings
```

## 8.3 Security & Access UI Structure

```txt
Security & Access
├── Authentication Policy
├── Multi-Factor Authentication
├── Session & Login Rules
├── Account Lockout
├── Trusted Domains
├── API Access
├── Export & Data Access Controls
├── Access Review
└── Security Events
```

## 8.4 Authentication Policy

Fields:

```txt
Minimum Password Length
Require Uppercase
Require Lowercase
Require Number
Require Symbol
Password Expiry Days
Prevent Password Reuse
Force Password Reset for New Users
```

Recommended defaults:

```txt
Minimum Password Length: 8 or 10
Require Number: Yes
Require Symbol: Optional
Password Expiry: Disabled by default unless policy requires
Force Password Reset for New Users: Yes
```

## 8.5 Multi-Factor Authentication

Settings:

```txt
MFA Required for All Users
MFA Required for Admin Roles
MFA Required for Finance Roles
MFA Required for Certificate Approvers
MFA Required for Enforcement Officers
Allowed MFA Methods
Grace Period
```

Allowed methods:

```txt
Authenticator App
Email OTP
SMS OTP, optional
```

## 8.6 Session & Login Rules

Fields:

```txt
Session Timeout
Idle Timeout
Remember Device Duration
Concurrent Sessions Allowed
Force Logout on Role Change
Force Logout on Password Change
```

Recommended defaults:

```txt
Session Timeout: 8 hours
Idle Timeout: 30 minutes
Force Logout on Role Change: Yes
Force Logout on Password Change: Yes
```

## 8.7 Account Lockout Rules

Fields:

```txt
Failed Login Attempts Before Lockout
Lockout Duration
Notify Admin on Lockout
Notify User on Lockout
Require Admin Unlock
```

Example:

```txt
5 failed attempts → lock account for 30 minutes
```

## 8.8 Trusted Domains

The State can restrict invited users to approved email domains.

Fields:

```txt
Allowed Email Domains
Block Public Email Domains, optional
Allow Exceptions
Exception Approval Required
```

Example:

```txt
lagosstate.gov.ng
health.lagosstate.gov.ng
```

## 8.9 API Access

API access should be controlled carefully.

Fields:

```txt
Enable API Access
Allow API Tokens
Require Token Expiry
Default Token Expiry
IP Restrictions
Webhook Access
API Audit Logging
```

MVP may show this as disabled or admin-only if APIs are not exposed to state users yet.

## 8.10 Export & Data Access Controls

Settings:

```txt
Require Approval for Sensitive Exports
Restrict Medical Data Export
Restrict Bulk Food Handler Export
Restrict Revenue Export
Watermark PDF Exports
Export Expiry Links
Audit All Exports
```

This is important because FoodCert contains personal and potentially sensitive health-related information.

## 8.11 Access Review

Access review helps State admins periodically review users and permissions.

Settings:

```txt
Enable Periodic Access Review
Review Frequency
Reviewer Role
Notify Reviewers
Disable Users Not Reviewed, optional
```

Example:

```txt
Every 90 days, State Admin reviews users with certificate approval, finance, enforcement, and settings permissions.
```

## 8.12 Security Events

Security Events should show a filtered view of security-related audit logs, such as:

```txt
Failed login attempts
Role changes
Permission changes
MFA changes
Password changes
Export events
API token events
Suspicious activity
```

This can also link to the full Audit Logs section.

## 8.13 Security & Access Acceptance Criteria

- Security & Access appears under Account Settings.
- It does not duplicate Stakeholder Management.
- Authorized users can configure authentication policies.
- Authorized users can configure MFA rules.
- Authorized users can configure session and login rules.
- Export and data access controls can be configured.
- Security events are visible to authorized users.
- Changes are audit logged.

---

# 9. Audit Logs

## 9.1 Purpose

Audit Logs provide an official record of important actions taken on the FoodCert NG platform.

The Audit Logs section should help State Ministry users answer:

```txt
Who did what?
When did it happen?
What record was affected?
What changed?
From where?
Was the action successful?
```

## 9.2 Audit Logs Should Cover

```txt
User and role changes
Settings changes
Certificate actions
Facility accreditation actions
Inspection and enforcement actions
Form template and response actions
Payment and settlement actions
Medical assessment actions
Security events
Export/download events
Login/session events
```

## 9.3 Audit Log UI Structure

```txt
Audit Logs
├── Overview
├── Activity Logs
├── Security Logs
├── Settings Change Logs
├── Export Logs
└── Retention & Export
```

For a simpler MVP, use one table with filters:

```txt
Audit Logs
├── Filter Toolbar
├── Audit Log Table
└── Audit Log Detail Drawer
```

## 9.4 Audit Log Table Columns

```txt
Date / Time
Actor
Action
Module
Entity Type
Entity Name / Reference
Status
IP Address
Device
Actions
```

## 9.5 Audit Log Detail Drawer

When a log row is clicked, show:

```txt
Event Summary
Actor Details
Action Details
Module
Entity Type
Entity ID
Entity Reference
Old Values
New Values
IP Address
User Agent
Device
Location, if available
Timestamp
Request ID
Status
Failure Reason, if applicable
```

## 9.6 Audit Log Filters

Filters should include:

```txt
Date Range
Actor
Role
Module
Action Type
Entity Type
Status
IP Address
Severity
Event Category
```

## 9.7 Audit Event Categories

Recommended categories:

```txt
Authentication
User Management
Role & Permission
Settings
Certificates
Medical Facilities
Medical Assessments
Inspections
Enforcement
Forms
Payments
Reports
Exports
Notifications
System
```

## 9.8 Important Audit Actions

### Authentication

```txt
login_success
login_failed
logout
password_changed
password_reset_requested
mfa_enabled
mfa_disabled
account_locked
account_unlocked
```

### User / Access

```txt
user_invited
invite_accepted
user_deactivated
user_reactivated
role_assigned
role_removed
permission_changed
unit_assignment_changed
```

### Settings

```txt
state_profile_updated
fee_settings_updated
certificate_settings_updated
medical_facility_settings_updated
inspection_settings_updated
notification_settings_updated
security_settings_updated
```

### Certificates

```txt
certificate_requested
certificate_approved
certificate_rejected
certificate_issued
certificate_suspended
certificate_revoked
certificate_verified
certificate_template_changed
```

### Medical Facilities

```txt
facility_registered
accreditation_application_submitted
accreditation_review_started
accreditation_more_info_requested
facility_accredited
facility_rejected
facility_suspended
facility_reactivated
facility_expired
```

### Inspections & Enforcement

```txt
inspection_created
inspector_assigned
inspection_template_assigned
inspection_submitted
inspection_reviewed
finding_created
notice_issued
case_opened
corrective_action_submitted
corrective_action_approved
case_escalated
case_closed
```

### Forms

```txt
form_template_created
form_template_published
form_template_versioned
form_assigned
form_response_started
form_response_submitted
form_response_reviewed
form_response_returned
form_exported
```

### Payments

```txt
payment_initiated
payment_successful
payment_failed
receipt_generated
settlement_initiated
settlement_completed
refund_requested
refund_completed
reconciliation_exception_created
```

### Exports

```txt
report_exported
certificate_exported
food_handler_data_exported
payment_data_exported
audit_log_exported
```

## 9.9 Audit Log Retention

Retention settings may be configured by Platform Admin globally, but State users can view the current retention policy.

Recommended:

```txt
Minimum retention: 7 years, or policy-defined
Security logs: 7 years
Payment logs: 7 years
Certificate logs: permanent or certificate lifecycle + retention period
Medical-related logs: policy-defined
```

State users should not be allowed to delete audit logs.

## 9.10 Audit Log Export

Authorized users may export audit logs.

Export formats:

```txt
CSV
Excel
PDF Summary
```

Export rules:

```txt
Date range required
Reason for export required
Export is audit logged
Sensitive fields may be masked
Large exports may require approval
```

## 9.11 Audit Log Acceptance Criteria

- Audit Logs appears under Account Settings.
- Authorized users can view audit logs.
- Unauthorized users cannot view audit logs.
- Logs are filterable.
- Log details are visible in a drawer/page.
- Settings changes are captured.
- Export events are captured.
- Audit logs can be exported where permitted.
- Audit logs cannot be edited or deleted by State users.

---

# 10. Data Model Requirements

## 10.1 StateProfile

```txt
id
state_id
state_name
state_code
ministry_name
public_display_name
official_email
official_phone
website
address_json
logo_url
seal_url
certificate_logo_url
receipt_logo_url
primary_brand_color
secondary_brand_color
timezone
currency
working_days_json
working_hours_json
created_by
updated_by
created_at
updated_at
```

## 10.2 StateSignatory

```txt
id
state_profile_id
name
title
signature_url
usage_type
effective_start_date
effective_end_date
is_default
is_active
created_by
updated_by
created_at
updated_at
```

Usage types:

```txt
Certificate
Notice
Report
Receipt
General
```

## 10.3 NotificationSetting

```txt
id
state_id
event_key
event_category
enabled
channels_json
recipient_rules_json
template_id
reminder_rules_json
escalation_rules_json
created_by
updated_by
created_at
updated_at
```

## 10.4 NotificationTemplate

```txt
id
state_id
name
event_key
channel
subject
body
variables_json
language
status
created_by
updated_by
created_at
updated_at
```

## 10.5 NotificationDeliveryLog

```txt
id
state_id
event_key
recipient_user_id
recipient_contact
channel
status
sent_at
delivered_at
failed_at
failure_reason
retry_count
metadata_json
created_at
updated_at
```

## 10.6 SecurityAccessPolicy

```txt
id
state_id
password_policy_json
mfa_policy_json
session_policy_json
lockout_policy_json
trusted_domains_json
api_access_policy_json
export_controls_json
access_review_policy_json
created_by
updated_by
created_at
updated_at
```

## 10.7 AuditLog

```txt
id
state_id
actor_user_id
actor_name
actor_role
action
event_category
module
entity_type
entity_id
entity_reference
old_values_json
new_values_json
status
severity
ip_address
user_agent
device_id
request_id
failure_reason
metadata_json
created_at
```

---

# 11. API Requirements

## 11.1 State Profile APIs

```txt
GET    /api/state/account-settings/profile
PATCH  /api/state/account-settings/profile
POST   /api/state/account-settings/profile/logo
POST   /api/state/account-settings/profile/seal
GET    /api/state/account-settings/profile/signatories
POST   /api/state/account-settings/profile/signatories
PATCH  /api/state/account-settings/profile/signatories/:id
DELETE /api/state/account-settings/profile/signatories/:id
```

Delete should be soft-delete/deactivate if the signatory has been used.

## 11.2 Notification Settings APIs

```txt
GET   /api/state/account-settings/notifications
PATCH /api/state/account-settings/notifications
GET   /api/state/account-settings/notifications/events
GET   /api/state/account-settings/notifications/templates
POST  /api/state/account-settings/notifications/templates
PATCH /api/state/account-settings/notifications/templates/:id
GET   /api/state/account-settings/notifications/delivery-logs
POST  /api/state/account-settings/notifications/delivery-logs/:id/retry
```

## 11.3 Security & Access APIs

```txt
GET   /api/state/account-settings/security
PATCH /api/state/account-settings/security
GET   /api/state/account-settings/security/events
POST  /api/state/account-settings/security/access-review/start
GET   /api/state/account-settings/security/access-review
```

## 11.4 Audit Logs APIs

```txt
GET  /api/state/account-settings/audit-logs
GET  /api/state/account-settings/audit-logs/:id
POST /api/state/account-settings/audit-logs/export
GET  /api/state/account-settings/audit-logs/export/:exportId
```

---

# 12. Permissions

## 12.1 State Profile Permissions

```txt
account_settings.profile.view
account_settings.profile.update
account_settings.profile.manage_branding
account_settings.profile.manage_signatories
```

## 12.2 Notification Permissions

```txt
account_settings.notifications.view
account_settings.notifications.update
account_settings.notifications.manage_templates
account_settings.notifications.view_delivery_logs
account_settings.notifications.retry_delivery
```

## 12.3 Security Permissions

```txt
account_settings.security.view
account_settings.security.update
account_settings.security.manage_mfa
account_settings.security.manage_api_access
account_settings.security.manage_export_controls
account_settings.security.view_events
```

## 12.4 Audit Log Permissions

```txt
account_settings.audit_logs.view
account_settings.audit_logs.view_detail
account_settings.audit_logs.export
```

## 12.5 Permission Rules

- Only authorized State users can update settings.
- Federal users may view settings for oversight if permitted, but should not update State settings unless explicitly authorized.
- Employers, Medical Facilities, Food Handlers, and Inspectors cannot access State Account Settings.
- Audit logs are read-only.
- Security settings changes require audit logging.
- Sensitive settings changes may require MFA confirmation in future.

---

# 13. Frontend Components

## 13.1 Account Settings Components

```txt
AccountSettingsPage
AccountSettingsSidebar
AccountSettingsSectionHeader
SettingsCard
SettingsEditDrawer
SettingsSaveBar
SettingsAuditTrailLink
```

## 13.2 State Profile Components

```txt
StateProfileSettingsPage
StateIdentityCard
StateContactInfoCard
StateBrandingCard
LogoUploadField
StateSignatoriesCard
SignatoryFormDrawer
AdministrativeDefaultsCard
```

## 13.3 Notification Components

```txt
NotificationSettingsPage
NotificationChannelsCard
NotificationEventRulesTable
NotificationEventRuleDrawer
ReminderSchedulesCard
RecipientRulesBuilder
NotificationTemplatesTable
NotificationTemplateEditor
NotificationDeliveryLogsTable
```

## 13.4 Security Components

```txt
SecurityAccessSettingsPage
AuthenticationPolicyCard
MfaPolicyCard
SessionPolicyCard
AccountLockoutCard
TrustedDomainsCard
ApiAccessCard
ExportControlsCard
AccessReviewCard
SecurityEventsTable
```

## 13.5 Audit Log Components

```txt
AuditLogsPage
AuditLogFilters
AuditLogTable
AuditLogDetailDrawer
AuditLogExportModal
AuditEventCategoryBadge
AuditStatusBadge
AuditSeverityBadge
```

---

# 14. UI Consolidation Rules

## 14.1 Keep Settings Under Account Settings

Do not create separate modules for:

```txt
State Profile
Notification Center Settings
Security Settings
Audit Logs
```

They belong under Account Settings.

## 14.2 Do Not Duplicate Stakeholder Management

Security & Access should not recreate:

```txt
Users
Roles
Permissions
Invites
Units
```

Those remain in Stakeholder Management.

Security & Access configures security policies and links to Stakeholder Management where needed.

## 14.3 Do Not Mix Audit Logs with Reports

Audit Logs are operational/system accountability records.

Reports are analytical outputs.

Audit Logs belong under Account Settings.

## 14.4 Notifications Settings vs Notifications Inbox

Notification Settings configures notification rules.

The Notifications Inbox shows received notifications.

Do not mix both.

---

# 15. Acceptance Criteria

## 15.1 Account Settings Shell

- Account Settings contains State Profile, Notification Settings, Security & Access, and Audit Logs.
- Sections are permission-based.
- Unauthorized users do not see restricted settings.

## 15.2 State Profile

- State user can update ministry profile information.
- State user can upload logos/seals.
- State user can manage authorized signatories.
- Signatory history is preserved.
- Profile changes are audit logged.

## 15.3 Notification Settings

- State user can configure channels.
- State user can enable/disable notification events.
- State user can configure recipients and reminders.
- State user can manage templates.
- State user can view delivery logs.
- Notification setting changes are audit logged.

## 15.4 Security & Access

- State user can configure password policy, MFA policy, session rules, lockout rules, trusted domains, API access, export controls, and access review rules.
- Security & Access does not duplicate Stakeholder Management.
- Security setting changes are audit logged.

## 15.5 Audit Logs

- State user can view audit logs.
- Audit logs are filterable.
- Audit log detail drawer works.
- Audit logs are exportable where permitted.
- Audit logs cannot be edited or deleted.
- Exporting audit logs creates an audit event.

---

# 16. Implementation Chunks for Codex

## Chunk 1: Account Settings Shell Update

### Goal

Add the missing Account Settings sections.

### Tasks

- Update Account Settings navigation.
- Add routes for:
  - State Profile
  - Notification Settings
  - Security & Access
  - Audit Logs
- Add permission-based section visibility.
- Add layout, loading, empty, and error states.

### Acceptance Criteria

- New sections appear under Account Settings.
- Unauthorized sections are hidden.
- Routes work.
- Layout follows FoodCert NG design system.

---

## Chunk 2: State Profile Data Model and APIs

### Goal

Implement State Profile backend.

### Tasks

- Create/update `StateProfile`.
- Create/update `StateSignatory`.
- Add profile GET/PATCH APIs.
- Add logo/seal upload APIs.
- Add signatory CRUD APIs.
- Add audit logs for changes.

### Acceptance Criteria

- State profile can be viewed and updated.
- Logos can be uploaded.
- Signatories can be created/updated/deactivated.
- Used signatories are not hard-deleted.
- All changes are audit logged.

---

## Chunk 3: State Profile UI

### Goal

Build State Profile settings page.

### Tasks

- Build State Identity card.
- Build Contact Information card.
- Build Branding & Logos card.
- Build Authorized Signatories card.
- Build Administrative Defaults card.
- Add edit drawers/modals.
- Add validation.

### Acceptance Criteria

- User can update profile fields.
- User can upload branding assets.
- User can manage signatories.
- Validation works.
- Save feedback works.

---

## Chunk 4: Notification Settings Data Model and APIs

### Goal

Implement notification settings backend.

### Tasks

- Create/update `NotificationSetting`.
- Create/update `NotificationTemplate`.
- Create/update `NotificationDeliveryLog`.
- Add event registry.
- Add APIs for settings, templates, and delivery logs.
- Add audit logging.

### Acceptance Criteria

- Notification events are returned.
- Event rules can be configured.
- Templates can be managed.
- Delivery logs can be viewed.
- Changes are audit logged.

---

## Chunk 5: Notification Settings UI

### Goal

Build notification settings interface.

### Tasks

- Build Channels card.
- Build Event Rules table.
- Build Event Rule edit drawer.
- Build Reminder Schedules card.
- Build Recipient Rules builder.
- Build Templates table/editor.
- Build Delivery Logs table.

### Acceptance Criteria

- Channels can be enabled/disabled.
- Event rules can be configured.
- Recipients can be set by role/user/context.
- Templates can be edited and previewed.
- Delivery logs show status.

---

## Chunk 6: Security & Access Data Model and APIs

### Goal

Implement security policy backend.

### Tasks

- Create/update `SecurityAccessPolicy`.
- Add GET/PATCH APIs.
- Add security events endpoint.
- Add access review endpoint placeholders.
- Add audit logs for changes.

### Acceptance Criteria

- Security policy can be fetched and updated.
- Security events can be viewed.
- Changes are audit logged.
- Policy is state-scoped.

---

## Chunk 7: Security & Access UI

### Goal

Build Security & Access settings page.

### Tasks

- Build Authentication Policy card.
- Build MFA Policy card.
- Build Session Policy card.
- Build Account Lockout card.
- Build Trusted Domains card.
- Build API Access card.
- Build Export Controls card.
- Build Access Review card.
- Build Security Events table.

### Acceptance Criteria

- Security settings are editable by authorized users.
- UI clearly separates policy settings from user/role management.
- Security events are visible.
- Save and validation work.

---

## Chunk 8: Audit Logs Data Model and APIs

### Goal

Implement audit log storage and retrieval.

### Tasks

- Create/update `AuditLog`.
- Add audit logging service.
- Add audit logs list API.
- Add audit log detail API.
- Add export API.
- Add filters.
- Ensure logs are immutable for State users.

### Acceptance Criteria

- Audit logs are generated for important actions.
- Logs can be listed and filtered.
- Log detail can be viewed.
- Logs can be exported where permitted.
- Logs cannot be edited/deleted by State users.

---

## Chunk 9: Audit Logs UI

### Goal

Build audit logs interface.

### Tasks

- Build Audit Logs page.
- Add filters.
- Add table.
- Add detail drawer.
- Add export modal.
- Add category/severity/status badges.

### Acceptance Criteria

- User can filter logs.
- User can open log details.
- User can export logs where permitted.
- Export action is audit logged.

---

## Chunk 10: Permissions, Scope, and Final QA

### Goal

Secure and polish the Account Settings sections.

### Tasks

- Implement all permissions.
- Enforce state scoping.
- Add tests for unauthorized access.
- Add tests for audit logging.
- Add responsive layouts.
- Add loading/empty/error states.
- Final UI QA.

### Acceptance Criteria

- Permissions work correctly.
- State scoping works.
- UI is responsive.
- All settings changes are audit logged.
- Account Settings is consolidated and not scattered.

---

# 17. Codex Implementation Prompt

Use this prompt for Codex:

```txt
Implement the missing Account Settings sections for the FoodCert NG State Ministry account.

Add the following sections under:
State Ministry → Account Settings

Sections:
1. State Profile
2. Notification Settings
3. Security & Access
4. Audit Logs

Do not create these as separate top-level modules. They must live under Account Settings.

State Profile:
- Manage State/Ministry identity, contact information, branding/logos, authorized signatories, timezone, currency, working days, and administrative defaults.
- Preserve signatory history.
- Audit all changes.

Notification Settings:
- Configure notification channels, event rules, reminder schedules, recipients, templates, and delivery logs.
- Support in-app and email for MVP.
- SMS/WhatsApp can be optional/feature-flagged.
- Audit all changes.

Security & Access:
- Configure password policy, MFA policy, session timeout, lockout rules, trusted domains, API access, export/data access controls, access review policy, and security events.
- Do not duplicate Stakeholder Management. Users, roles, permissions, invites, and units remain in Stakeholder Management.
- Audit all changes.

Audit Logs:
- Provide immutable audit log list, filters, detail drawer, and export.
- Capture authentication, user/access, settings, certificates, facilities, inspections, enforcement, forms, payments, notifications, exports, and system events.
- Audit logs cannot be edited or deleted by State users.

Implement models:
- StateProfile
- StateSignatory
- NotificationSetting
- NotificationTemplate
- NotificationDeliveryLog
- SecurityAccessPolicy
- AuditLog

Implement APIs:
- /api/state/account-settings/profile
- /api/state/account-settings/notifications
- /api/state/account-settings/security
- /api/state/account-settings/audit-logs

Implement permissions:
- account_settings.profile.view/update/manage_branding/manage_signatories
- account_settings.notifications.view/update/manage_templates/view_delivery_logs/retry_delivery
- account_settings.security.view/update/manage_mfa/manage_api_access/manage_export_controls/view_events
- account_settings.audit_logs.view/view_detail/export

Use Next.js + React + TypeScript + Tailwind CSS and follow the FoodCert NG application-wide design system. Backend permissions and state scoping remain the source of truth.
```

---

# 18. MVP Build Order

1. Account Settings shell update
2. State Profile data model and APIs
3. State Profile UI
4. Notification Settings data model and APIs
5. Notification Settings UI
6. Security & Access data model and APIs
7. Security & Access UI
8. Audit Logs data model and APIs
9. Audit Logs UI
10. Permissions, scope, and final QA
