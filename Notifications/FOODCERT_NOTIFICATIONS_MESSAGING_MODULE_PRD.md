# PRD: Notifications & Messaging Module — FoodCert NG

## 1. Module Name

**Notifications & Messaging Module**

## 2. Product Context

The Notifications & Messaging Module is the communication layer of **FoodCert NG**. It ensures that food handlers, employers, medical facilities, doctors, lab staff, State Ministry users, Federal Ministry users, inspectors, finance users, and system administrators receive timely alerts, reminders, workflow updates, and regulatory notices.

FoodCert NG depends on notifications across almost every module:

- Food handler registration and NIN verification
- Assessment payment
- Appointment booking
- Health declaration submission
- Medical assessment workflow
- Lab request/result workflow
- Vaccination reminders
- Doctor fitness decision
- State Ministry validation
- Certificate issuance and renewal
- Employer subscriptions
- Facility accreditation and re-accreditation
- Inspection assignments
- Enforcement notices
- Corrective action deadlines
- Reports and M&E submissions
- Payments, settlements, and failed transactions

This module must support multi-channel messaging while respecting privacy, consent, user preferences, and role-based visibility.

---

# 3. Product Goal

To provide a reliable, configurable, auditable, and privacy-safe communication system that delivers the right message to the right user through the right channel at the right time.

---

# 4. Core Objectives

The Notifications & Messaging Module must:

1. Deliver in-app notifications to users.
2. Send email notifications.
3. Send SMS notifications.
4. Support WhatsApp notifications where enabled.
5. Support notification templates.
6. Support role-based notification routing.
7. Support user notification preferences.
8. Support system-triggered workflow notifications.
9. Support scheduled reminders.
10. Support escalation notifications.
11. Support failed delivery tracking and retry.
12. Support message audit logs.
13. Protect sensitive medical and personal data.
14. Support bulk/regulatory messaging where authorized.
15. Support state and federal notification dashboards.
16. Provide developer-friendly event-based notification services.

---

# 5. Key Actors

## 5.1 Food Handler

Receives notifications about:

- Account registration
- NIN verification status
- Assessment payment
- Appointment booking and reminders
- Health declaration reminder
- Lab result availability status, without medical detail where restricted
- Vaccination due or required
- Doctor decision status
- Certificate issued
- Certificate expiring soon
- Certificate expired
- Certificate suspended/revoked
- Renewal reminders
- Return-to-work status

Can:

- View in-app notifications.
- Receive SMS/email/WhatsApp alerts depending on preference and policy.
- Manage non-mandatory notification preferences.

Cannot:

- Disable mandatory regulatory/safety notices.
- View messages meant for employer, facility, or regulator.

## 5.2 Employer / Business Admin

Receives notifications about:

- Subscription activation/expiry
- Linked food handler certificate issued
- Certificate expiring soon
- Certificate expired
- Food handler temporarily not fit
- Return-to-work status
- Inspection scheduled or completed
- Enforcement notice issued
- Corrective action deadline
- Corrective action overdue
- Report exports completed

Can:

- Manage employer notification recipients.
- Configure branch-level recipients.
- Send internal reminders to linked food handlers.
- View notification history for employer-related events.

Cannot:

- Receive private medical details.
- Receive lab results, doctor notes, diagnoses, or declaration answers.

## 5.3 Medical Facility Admin

Receives notifications about:

- Accreditation application submission
- Accreditation approval/rejection
- More information requested
- Re-accreditation due
- New appointment
- Appointment cancellation/reschedule
- State clarification request
- Certificate issued from facility assessment
- Settlement eligible/paid/failed

Can:

- Configure facility notification contacts.
- View facility notification logs.
- Manage internal staff notification routing.

## 5.4 Doctor

Receives notifications about:

- Assessment assigned
- Declaration pending review
- Lab result submitted
- Vaccination review pending
- State clarification requested
- Return-to-work review assigned
- Assessment overdue

Can:

- View doctor-specific tasks and notifications.
- Receive time-sensitive alerts via configured channels.

## 5.5 Lab Staff

Receives notifications about:

- New lab request
- Sample collection pending
- Result upload pending
- Repeat test requested
- Lab turnaround overdue

## 5.6 State Ministry User

Receives notifications about:

- Facility accreditation application submitted
- Certificate validation pending
- Certificate generation failed
- State report due
- State report overdue
- Critical inspection finding
- Suspicious certificate flagged
- Enforcement escalation
- Revenue/settlement issue

## 5.7 Federal Ministry User

Receives notifications about:

- State reports submitted
- State reports overdue
- National M&E alerts
- Data quality issues
- Suspicious certificate trends
- High illness/enforcement signals
- National dashboard anomalies

## 5.8 Inspector / Environmental Health Officer

Receives notifications about:

- Inspection assigned
- Inspection due today
- Inspection overdue
- Follow-up inspection assigned
- Notice approved/rejected
- Report returned for correction

## 5.9 Finance User

Receives notifications about:

- Payment successful
- Payment failed
- Refund processed
- Settlement eligible
- Settlement paid
- Settlement failed
- Reconciliation issue
- Subscription past due

## 5.10 Super Admin

Receives notifications about:

- System delivery failures
- Provider outage
- Webhook failure
- High failed delivery rate
- Template approval required
- Critical security/audit events

Can:

- Manage notification providers.
- Manage templates.
- Manage global notification policies.
- View delivery logs.

---

# 6. Module Scope

## 6.1 In Scope

The module includes:

- In-app notifications
- Email notifications
- SMS notifications
- WhatsApp notifications, where enabled
- Notification templates
- Notification categories
- Event-based notification triggers
- Scheduled reminders
- Notification preferences
- Mandatory regulatory notifications
- Delivery status tracking
- Retry logic
- Provider abstraction
- Bulk notification, permission-controlled
- Notification inbox
- Notification read/unread state
- Notification audit logs
- Notification dashboards
- Admin template management
- Privacy-safe message rendering

## 6.2 Out of Scope for MVP

The following may be deferred:

- Two-way WhatsApp conversations
- Full customer support inbox
- AI-generated message drafting
- Push notifications for native mobile apps
- Advanced campaign automation
- Marketing CRM
- Chatbot support
- Voice calls/IVR
- International messaging optimization
- Complex A/B testing

---

# 7. Notification Channels

## 7.1 In-App Notifications

In-app notifications are the default channel for all authenticated users.

Features:

- Notification bell
- Unread count
- Notification list
- Notification detail view
- Mark as read
- Mark all as read
- Filter by category
- Link to related workflow record
- Role-safe content

## 7.2 Email Notifications

Email is used for:

- Account onboarding
- Invite acceptance
- Payment receipts
- Certificate issued
- Accreditation updates
- Report submissions
- Enforcement notices
- Subscription billing
- Formal regulatory communication

Rules:

- Emails must use verified sender domain.
- Emails must use templates.
- Sensitive medical data must not be included unless explicitly allowed.
- Emails should link users back to secure platform pages.

## 7.3 SMS Notifications

SMS is used for urgent or short alerts.

Examples:

- OTP or phone verification
- Appointment reminder
- Payment confirmation
- Certificate issued
- Certificate expiry reminder
- Corrective action deadline
- Inspection assignment reminder

Rules:

- SMS content must be short.
- SMS must not contain sensitive medical details.
- SMS should include safe call-to-action links only where appropriate.

## 7.4 WhatsApp Notifications

WhatsApp can be enabled for high-engagement reminders.

Examples:

- Appointment reminders
- Certificate renewal reminders
- Payment success
- Employer compliance reminders
- Inspection notice alerts

Rules:

- Must follow provider and WhatsApp template approval rules.
- Must respect user consent and opt-in rules where required.
- Must not expose sensitive medical data.

## 7.5 Future Push Notifications

Native mobile push notifications may be added later.

---

# 8. Notification Categories

Use the following categories:

- Account
- Identity Verification
- Employer Management
- Facility Accreditation
- Appointment
- Assessment
- Lab Workflow
- Vaccination
- Certificate
- Renewal
- Payments
- Subscriptions
- Settlements
- Inspection
- Enforcement
- Reports
- M&E
- Data Quality
- Security
- System

---

# 9. Notification Priority Levels

## 9.1 Priority Levels

- Low
- Normal
- High
- Critical

## 9.2 Priority Rules

| Priority | Meaning | Example |
|---|---|---|
| Low | Informational | Report export completed |
| Normal | Regular workflow update | Appointment confirmed |
| High | Time-sensitive action required | Certificate expiring in 7 days |
| Critical | Public health, regulatory, security, or system failure | Revoked certificate in use, critical inspection finding |

## 9.3 Critical Notification Rules

Critical notifications:

- May bypass user preference where legally/regulatorily required.
- Must be audit logged.
- May trigger escalation to supervisors.
- Should use more than one channel where configured.

---

# 10. Event-Based Notification Architecture

## 10.1 Purpose

Notifications should be triggered by domain events rather than hardcoded inside every controller.

## 10.2 Recommended Event Flow

```txt
Domain action occurs
→ Domain event is emitted
→ Notification service receives event
→ Notification policy determines recipients/channels
→ Template is rendered with safe variables
→ Message is queued
→ Provider sends message
→ Delivery status is updated
→ Audit log is created
```

## 10.3 Example Domain Events

```txt
user.invited
user.invite_accepted
nin.verification_successful
nin.verification_failed
assessment.payment_successful
assessment.appointment_booked
assessment.declaration_pending
assessment.lab_result_submitted
assessment.doctor_decision_finalized
certificate.issued
certificate.expiring_soon
certificate.expired
certificate.suspended
certificate.revoked
facility.accreditation_submitted
facility.accreditation_approved
facility.reaccreditation_due
inspection.assigned
enforcement.notice_issued
corrective_action.overdue
state_report.due
state_report.overdue
settlement.paid
settlement.failed
```

---

# 11. Recipient Resolution

## 11.1 Purpose

The system must determine who receives each notification based on event, organization, role, unit, branch, and permissions.

## 11.2 Recipient Types

- Individual user
- Food handler
- Employer admin
- Branch manager
- Facility admin
- Assigned doctor
- Assigned lab staff
- Inspector
- Inspectorate coordinator
- State Ministry unit
- Federal Ministry unit
- Finance user
- Super admin

## 11.3 Recipient Resolution Rules

Examples:

| Event | Recipients |
|---|---|
| Certificate issued | Food handler, linked employer admin/branch manager, facility admin, State registry users |
| Certificate expiring soon | Food handler, linked employer compliance officer |
| Assessment assigned | Assigned doctor |
| Lab request created | Lab staff in facility lab department |
| Accreditation submitted | State facility accreditation unit |
| Inspection assigned | Assigned inspector |
| Notice issued | Employer admin, branch manager, State inspectorate coordinator |
| Settlement paid | Facility finance user, facility admin |
| State report overdue | State M&E officer, State admin, Federal M&E officer |

## 11.4 Unit-Based Routing

Notifications should route to `OrganizationUnit` where relevant:

- State Verification Desk
- Facility Accreditation Unit
- Inspectorate
- Policy and Finance Unit
- LGA Office
- Facility Laboratory Department
- Facility Clinical Department
- Employer Branch

---

# 12. Notification Preferences

## 12.1 Purpose

Users should be able to control non-mandatory notification channels.

## 12.2 Preference Fields

- User
- Category
- Channel
- Enabled/disabled
- Quiet hours start
- Quiet hours end
- Preferred language, future
- Preferred frequency
- Digest enabled

## 12.3 Preference Rules

Users may disable:

- Low-priority reminders
- Digest emails
- Optional WhatsApp alerts
- Non-critical SMS alerts

Users may not disable:

- Security notifications
- Regulatory notices
- Certificate suspension/revocation notices
- Enforcement notices
- Payment receipts where legally required
- Critical public health notifications

## 12.4 Employer-Level Preferences

Employers can configure:

- Compliance recipient
- Billing recipient
- Branch manager recipients
- Inspection/enforcement recipient
- Certificate expiry recipient

## 12.5 Facility-Level Preferences

Facilities can configure:

- Accreditation contact
- Appointment contact
- Clinical workflow contact
- Lab workflow contact
- Settlement/finance contact
- State clarification contact

---

# 13. Notification Templates

## 13.1 Purpose

Templates allow administrators to manage consistent messages across channels.

## 13.2 Template Fields

- Template key
- Name
- Category
- Channel
- Subject, for email
- Body
- Variables allowed
- Language
- Scope: national/state/system
- State, optional
- Status
- Version
- Created by
- Approved by

## 13.3 Template Statuses

- Draft
- Pending Approval
- Active
- Archived
- Rejected

## 13.4 Template Variables

Allowed variables may include:

```txt
{{ user_name }}
{{ food_handler_name }}
{{ employer_name }}
{{ branch_name }}
{{ facility_name }}
{{ appointment_date }}
{{ certificate_number }}
{{ certificate_expiry_date }}
{{ state_name }}
{{ report_period }}
{{ notice_reference }}
{{ corrective_action_deadline }}
{{ payment_reference }}
{{ settlement_reference }}
{{ action_url }}
```

## 13.5 Sensitive Variable Rules

Templates must not expose:

```txt
full_nin
lab_results
diagnosis
doctor_notes
health_declaration_answers
treatment_details
payment_card_details
provider_secret_keys
```

## 13.6 Template Versioning

- Editing an active template creates a new version.
- Historical messages should preserve the rendered body or template version used.
- Archived templates cannot be used for new messages.

---

# 14. Core Notification Workflows

## 14.1 Account and Invite Notifications

Events:

- User invited
- Invite accepted
- Invite expired
- Password reset requested
- Email verified
- Phone verified

Recipients:

- Invited user
- Inviting admin

Channels:

- Email
- SMS for phone verification
- In-app for existing users

## 14.2 NIN Verification Notifications

Events:

- NIN verification successful
- NIN verification failed
- NIN override requested
- NIN override approved/rejected

Recipients:

- Food handler
- Authorized State/Federal/admin user where applicable

Privacy:

- Do not expose full NIN in notification body.

## 14.3 Appointment Notifications

Events:

- Appointment booked
- Appointment confirmed
- Appointment rescheduled
- Appointment cancelled
- Appointment reminder 24 hours before
- Appointment reminder 2 hours before
- No-show recorded

Recipients:

- Food handler
- Facility admin
- Assigned doctor, where assigned
- Employer branch manager, where policy allows

## 14.4 Assessment Notifications

Events:

- Declaration pending
- Declaration submitted
- Declaration clarification requested
- Physical exam pending
- Lab test requested
- Lab result submitted
- Vaccination review pending
- Doctor decision finalized
- Assessment submitted to State
- State clarification requested

Recipients:

- Food handler
- Doctor
- Facility admin
- Lab staff
- State verification desk

Privacy:

- Employer receives only operational status updates.

## 14.5 Certificate Notifications

Events:

- Certificate issued
- Certificate generation failed
- Certificate expiring in 30 days
- Certificate expiring in 7 days
- Certificate expired
- Certificate suspended
- Certificate reinstated
- Certificate revoked
- Certificate replaced
- Renewal started

Recipients:

- Food handler
- Employer admin/compliance officer
- Branch manager
- Facility admin
- State certificate verification desk

## 14.6 Payment Notifications

Events:

- Payment initiated
- Payment successful
- Payment failed
- Payment abandoned
- Refund requested
- Refund processed
- Receipt generated

Recipients:

- Payer
- Employer finance user, where applicable
- Facility finance user, where settlement-related

Privacy:

- Do not include card details.
- Include payment reference and amount only to authorized parties.

## 14.7 Subscription Notifications

Events:

- Subscription activated
- Subscription expiring soon
- Subscription expired
- Subscription past due
- Subscription renewed
- Subscription cancelled
- Plan changed

Recipients:

- Employer admin
- Employer finance user
- Employer compliance officer, where relevant

## 14.8 Settlement Notifications

Events:

- Settlement eligible
- Settlement processing
- Settlement paid
- Settlement failed
- Settlement dispute created
- Settlement dispute resolved

Recipients:

- Facility finance user
- Facility admin
- State finance user, where applicable
- Platform finance user

## 14.9 Facility Accreditation Notifications

Events:

- Accreditation application submitted
- More information requested
- Accreditation approved
- Accreditation rejected
- Facility suspended
- Facility reinstated
- Re-accreditation due in 60/30/7 days
- Accreditation expired

Recipients:

- Facility admin
- State accreditation unit
- Facility staff where applicable

## 14.10 Inspection and Enforcement Notifications

Events:

- Inspection assigned
- Inspection due today
- Inspection overdue
- Inspection submitted
- Report returned for correction
- Notice issued
- Notice acknowledged
- Corrective action due
- Corrective action overdue
- Employer response submitted
- Follow-up inspection assigned
- Case escalated
- Case closed

Recipients:

- Inspector
- Inspectorate coordinator
- Employer admin
- Branch manager
- State Ministry admin

## 14.11 Reports and M&E Notifications

Events:

- State report due
- State report overdue
- State report submitted
- State report returned for correction
- State report accepted
- National report generated
- Data quality issue detected
- M&E indicator below threshold

Recipients:

- State M&E officer
- State admin
- Federal M&E officer
- Federal admin

## 14.12 Security Notifications

Events:

- Password changed
- New device login
- Failed login threshold reached
- Role changed
- Sensitive medical record accessed
- API key created/rotated
- Provider webhook signature failed

Recipients:

- Affected user
- Security admin
- Super admin, where critical

---

# 15. Notification Inbox

## 15.1 Purpose

The notification inbox allows users to see all relevant notifications inside the platform.

## 15.2 Inbox Features

- Notification list
- Unread count
- Mark as read
- Mark all as read
- Filter by category
- Filter by priority
- Search notifications
- Open related record
- Archive notification

## 15.3 Notification Card Fields

- Title
- Short message
- Category
- Priority
- Timestamp
- Read/unread status
- Action link
- Related record type
- Related record ID

---

# 16. Scheduled Reminders

## 16.1 Reminder Types

The module should support scheduled reminders for:

- Appointment reminders
- Declaration reminders
- Certificate expiry reminders
- Subscription expiry reminders
- Facility re-accreditation reminders
- State report due reminders
- Corrective action deadline reminders
- Follow-up inspection reminders
- Settlement reconciliation reminders

## 16.2 Reminder Schedule Examples

| Reminder | Default Schedule |
|---|---|
| Appointment reminder | 24 hours and 2 hours before appointment |
| Certificate expiry | 30 days, 7 days, and expiry day |
| Facility re-accreditation | 60 days, 30 days, 7 days, expiry day |
| Subscription expiry | 14 days, 7 days, expiry day |
| Corrective action deadline | 7 days, 3 days, 1 day, overdue |
| State report due | 7 days before, due day, overdue |

## 16.3 Reminder Rules

- Reminders should not duplicate excessively.
- Reminders should stop when the action is completed.
- Reminder jobs must be idempotent.
- Reminder delivery should be logged.

---

# 17. Bulk and Broadcast Notifications

## 17.1 Purpose

Authorized users may need to send policy, compliance, public health, or administrative messages to groups.

## 17.2 Allowed Broadcast Scopes

- All users in a state
- All employers in a state
- All facilities in a state
- All inspectors in a state
- All State Ministry users
- All Federal Ministry users
- All users in an organization
- All users in an organization unit
- All food handlers with certificates expiring soon

## 17.3 Broadcast Requirements

- Requires permission.
- Must select audience.
- Must select channel.
- Must use approved template or admin-reviewed custom content.
- Must show estimated recipient count.
- Must support preview.
- Must log sender, audience, and delivery results.

## 17.4 Broadcast Restrictions

Broadcast must not be used for:

- Sending private medical details.
- Sharing lab results.
- Sharing full NIN.
- Unapproved marketing messages.
- Spam or unrelated content.

---

# 18. Provider Abstraction

## 18.1 Purpose

The platform should support different providers without hardcoding business logic to a single vendor.

## 18.2 Provider Types

- Email provider
- SMS provider
- WhatsApp provider
- In-app notification service

## 18.3 Suggested Providers

Possible providers include:

- Email: SMTP, SendGrid, Mailgun, Amazon SES
- SMS: Termii, Africa's Talking, Twilio, local Nigerian SMS gateway
- WhatsApp: Meta WhatsApp Business API, Twilio WhatsApp, Termii WhatsApp where supported

## 18.4 Provider Configuration Fields

- Provider name
- Channel
- API key/secret
- Sender ID
- Webhook secret
- Status
- Priority/order
- Rate limit
- Retry policy
- Default provider flag

## 18.5 Provider Rules

- Secrets must be encrypted or stored in secure environment variables.
- Failed provider should allow fallback where configured.
- Provider response must be stored for troubleshooting.
- Provider-specific payloads should not leak into domain models.

---

# 19. Delivery Tracking and Retry

## 19.1 Delivery Statuses

Use the following statuses:

- Pending
- Queued
- Sending
- Sent
- Delivered
- Failed
- Bounced
- Rejected
- Opened, email where supported
- Clicked, email where supported
- Read, in-app
- Cancelled

## 19.2 Retry Rules

- Failed messages should retry based on channel and error type.
- Permanent failures should not retry indefinitely.
- Transient failures can retry with backoff.
- Critical notifications may attempt fallback channel.

## 19.3 Retry Schedule Example

- Retry 1: after 5 minutes
- Retry 2: after 30 minutes
- Retry 3: after 2 hours
- Mark failed after max retries

## 19.4 Failure Handling

Track:

- Error code
- Provider message
- Retry count
- Last retry time
- Final failure reason

---

# 20. Privacy and Security Requirements

## 20.1 Sensitive Data Rules

Notifications must not expose:

- Full NIN
- Lab results
- Diagnosis
- Doctor notes
- Health declaration answers
- Treatment details
- Full medical report
- Payment card details
- Provider secrets

## 20.2 Safe Messaging Rules

- Use general action wording.
- Link users to secure authenticated pages for details.
- Use role-safe template variables.
- Do not include private clinical details in SMS/WhatsApp.
- Do not include sensitive records in public links.

## 20.3 Example Safe Messages

Safe:

```txt
Your FoodCert assessment has been updated. Please log in to view your next steps.
```

Unsafe:

```txt
Your lab result is positive for [disease].
```

Safe:

```txt
A linked food handler requires compliance attention. Log in to review the operational status.
```

Unsafe:

```txt
Your employee tested positive for [condition].
```

---

# 21. Audit Logging

Create audit logs for:

- Notification created
- Notification rendered
- Notification queued
- Notification sent
- Notification delivered
- Notification failed
- Notification retried
- Notification read
- Template created
- Template updated
- Template approved
- Template archived
- Broadcast created
- Broadcast sent
- Preference updated
- Provider configuration updated
- Critical notification sent
- Sensitive notification blocked due to privacy rule

---

# 22. Data Model Requirements

## 22.1 Notification

```python
class Notification(models.Model):
    id = models.UUIDField(primary_key=True)
    recipient = models.ForeignKey("accounts.User", null=True, blank=True, on_delete=models.CASCADE)
    recipient_email = models.EmailField(blank=True)
    recipient_phone = models.CharField(max_length=50, blank=True)
    recipient_type = models.CharField(max_length=50)
    organization = models.ForeignKey("organizations.Organization", null=True, blank=True, on_delete=models.SET_NULL)
    organization_unit = models.ForeignKey("organizations.OrganizationUnit", null=True, blank=True, on_delete=models.SET_NULL)
    category = models.CharField(max_length=80)
    priority = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    message = models.TextField()
    action_url = models.URLField(blank=True)
    related_object_type = models.CharField(max_length=100, blank=True)
    related_object_id = models.UUIDField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 22.2 NotificationTemplate

```python
class NotificationTemplate(models.Model):
    id = models.UUIDField(primary_key=True)
    template_key = models.CharField(max_length=150)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=80)
    channel = models.CharField(max_length=50)
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    allowed_variables = models.JSONField(default=list)
    language = models.CharField(max_length=20, default="en")
    scope = models.CharField(max_length=50)  # system, national, state
    state = models.ForeignKey("geography.State", null=True, blank=True, on_delete=models.SET_NULL)
    version = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=50)
    created_by = models.ForeignKey("accounts.User", null=True, related_name="notification_templates_created", on_delete=models.SET_NULL)
    approved_by = models.ForeignKey("accounts.User", null=True, blank=True, related_name="notification_templates_approved", on_delete=models.SET_NULL)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("template_key", "channel", "language", "version")
```

## 22.3 NotificationDelivery

```python
class NotificationDelivery(models.Model):
    id = models.UUIDField(primary_key=True)
    notification = models.ForeignKey("notifications.Notification", on_delete=models.CASCADE)
    channel = models.CharField(max_length=50)
    provider = models.CharField(max_length=100, blank=True)
    destination = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    provider_message_id = models.CharField(max_length=255, blank=True)
    provider_response = models.JSONField(default=dict)
    error_code = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 22.4 NotificationPreference

```python
class NotificationPreference(models.Model):
    id = models.UUIDField(primary_key=True)
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    category = models.CharField(max_length=80)
    channel = models.CharField(max_length=50)
    is_enabled = models.BooleanField(default=True)
    digest_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "category", "channel")
```

## 22.5 NotificationProvider

```python
class NotificationProvider(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100)
    channel = models.CharField(max_length=50)
    sender_id = models.CharField(max_length=100, blank=True)
    config = models.JSONField(default=dict)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    priority_order = models.PositiveIntegerField(default=1)
    rate_limit_per_minute = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 22.6 NotificationEvent

```python
class NotificationEvent(models.Model):
    id = models.UUIDField(primary_key=True)
    event_key = models.CharField(max_length=150)
    source_module = models.CharField(max_length=100)
    related_object_type = models.CharField(max_length=100, blank=True)
    related_object_id = models.UUIDField(null=True, blank=True)
    payload = models.JSONField(default=dict)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 22.7 BroadcastMessage

```python
class BroadcastMessage(models.Model):
    id = models.UUIDField(primary_key=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    category = models.CharField(max_length=80)
    priority = models.CharField(max_length=50)
    audience_type = models.CharField(max_length=100)
    audience_filters = models.JSONField(default=dict)
    channels = models.JSONField(default=list)
    status = models.CharField(max_length=50)
    estimated_recipient_count = models.PositiveIntegerField(default=0)
    sent_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey("accounts.User", null=True, on_delete=models.SET_NULL)
    approved_by = models.ForeignKey("accounts.User", null=True, blank=True, related_name="broadcasts_approved", on_delete=models.SET_NULL)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

---

# 23. API Requirements

## 23.1 Notification Inbox

```txt
GET    /api/notifications
GET    /api/notifications/unread-count
GET    /api/notifications/:id
POST   /api/notifications/:id/mark-read
POST   /api/notifications/mark-all-read
POST   /api/notifications/:id/archive
```

## 23.2 Notification Preferences

```txt
GET    /api/notification-preferences
PATCH  /api/notification-preferences/:id
POST   /api/notification-preferences/bulk-update
```

## 23.3 Notification Templates

```txt
GET    /api/admin/notification-templates
POST   /api/admin/notification-templates
GET    /api/admin/notification-templates/:id
PATCH  /api/admin/notification-templates/:id
POST   /api/admin/notification-templates/:id/submit-for-approval
POST   /api/admin/notification-templates/:id/approve
POST   /api/admin/notification-templates/:id/archive
POST   /api/admin/notification-templates/:id/preview
```

## 23.4 Notification Sending / Internal Service APIs

```txt
POST   /api/internal/notifications/events
POST   /api/internal/notifications/send
POST   /api/internal/notifications/send-template
POST   /api/internal/notifications/schedule
```

## 23.5 Delivery Logs

```txt
GET    /api/admin/notification-deliveries
GET    /api/admin/notification-deliveries/:id
POST   /api/admin/notification-deliveries/:id/retry
```

## 23.6 Providers

```txt
GET    /api/admin/notification-providers
POST   /api/admin/notification-providers
GET    /api/admin/notification-providers/:id
PATCH  /api/admin/notification-providers/:id
POST   /api/admin/notification-providers/:id/test
POST   /api/admin/notification-providers/:id/set-default
```

## 23.7 Broadcasts

```txt
GET    /api/admin/broadcasts
POST   /api/admin/broadcasts
GET    /api/admin/broadcasts/:id
PATCH  /api/admin/broadcasts/:id
POST   /api/admin/broadcasts/:id/estimate-audience
POST   /api/admin/broadcasts/:id/preview
POST   /api/admin/broadcasts/:id/submit-for-approval
POST   /api/admin/broadcasts/:id/approve
POST   /api/admin/broadcasts/:id/send
```

## 23.8 Webhooks

```txt
POST /api/webhooks/email-provider
POST /api/webhooks/sms-provider
POST /api/webhooks/whatsapp-provider
```

---

# 24. Frontend Routes

## 24.1 User Routes

```txt
/app/notifications
/app/notifications/[id]
/app/settings/notification-preferences
```

## 24.2 Employer Routes

```txt
/app/employer/settings/notifications
/app/employer/notifications
```

## 24.3 Facility Routes

```txt
/app/facility/settings/notifications
/app/facility/notifications
```

## 24.4 State Ministry Routes

```txt
/app/state/notifications
/app/state/notification-settings
/app/state/broadcasts
```

## 24.5 Federal Ministry Routes

```txt
/app/federal/notifications
/app/federal/broadcasts
```

## 24.6 Admin Routes

```txt
/app/admin/notifications/dashboard
/app/admin/notifications/templates
/app/admin/notifications/templates/[id]
/app/admin/notifications/providers
/app/admin/notifications/deliveries
/app/admin/broadcasts
/app/admin/broadcasts/[id]
```

---

# 25. Core Frontend Components

- NotificationBell
- NotificationUnreadBadge
- NotificationInbox
- NotificationCard
- NotificationDetailPanel
- NotificationFilters
- MarkAllReadButton
- NotificationPreferenceForm
- ChannelPreferenceToggle
- NotificationTemplateTable
- NotificationTemplateEditor
- TemplateVariableHelper
- TemplatePreviewPanel
- NotificationProviderTable
- ProviderConfigForm
- DeliveryLogTable
- DeliveryStatusBadge
- RetryDeliveryButton
- BroadcastBuilder
- AudienceSelector
- BroadcastPreviewPanel
- BroadcastApprovalPanel
- NotificationDashboardCards

---

# 26. Permissions and Access Control

## 26.1 General User

Can:

- View own notifications.
- Mark own notifications as read.
- Update own non-mandatory preferences.

## 26.2 Employer Admin

Can:

- Manage employer notification routing.
- View employer-related notifications.
- Configure branch recipients.

## 26.3 Facility Admin

Can:

- Manage facility notification routing.
- View facility-related notifications.
- Configure staff workflow recipients.

## 26.4 State Ministry Admin

Can:

- View state notification logs.
- Send authorized state broadcasts.
- Manage state-scoped templates where allowed.

## 26.5 Federal Ministry Admin

Can:

- View national notification summaries.
- Send federal-level broadcasts where authorized.
- Manage national templates where allowed.

## 26.6 Super Admin

Can:

- Manage global templates.
- Manage providers.
- View delivery logs.
- Retry failed deliveries.
- Configure notification policies.

---

# 27. Notification Dashboard

## 27.1 Admin Dashboard Cards

Show:

- Total notifications created today
- Emails sent today
- SMS sent today
- WhatsApp messages sent today
- In-app notifications created today
- Delivery success rate
- Failed deliveries
- Pending retries
- Critical notifications sent
- Provider failures
- Broadcasts sent

## 27.2 Charts

Suggested charts:

- Notifications by channel
- Delivery status distribution
- Failed delivery trend
- Notifications by category
- Provider performance
- Broadcast delivery performance
- Critical notification trend

## 27.3 Filters

- Date range
- Channel
- Category
- Priority
- Provider
- Delivery status
- User type
- Organization
- State

---

# 28. Background Jobs

## 28.1 Notification Queue Worker

Processes queued notifications.

Tasks:

- Render templates
- Check preferences
- Select provider
- Send message
- Update delivery status
- Log provider response

## 28.2 Retry Worker

Retries failed notifications.

Tasks:

- Find retryable failed deliveries
- Apply retry policy
- Resend message
- Update retry count
- Mark permanently failed where applicable

## 28.3 Scheduled Reminder Worker

Runs reminders.

Tasks:

- Appointment reminders
- Certificate expiry reminders
- Re-accreditation reminders
- Subscription expiry reminders
- Corrective action reminders
- State report reminders

## 28.4 Digest Worker

Sends digest notifications where configured.

Examples:

- Daily employer compliance digest
- Weekly facility activity digest
- Weekly state enforcement digest

## 28.5 Delivery Webhook Processor

Processes provider webhook callbacks.

Tasks:

- Validate webhook signature
- Update delivery status
- Store provider response
- Handle bounce/failure

---

# 29. Error Handling

## 29.1 Template Errors

Possible errors:

- Missing template
- Inactive template
- Missing variable
- Sensitive variable blocked
- Invalid channel

Handling:

- Block send.
- Log error.
- Notify admin for critical templates.

## 29.2 Provider Errors

Possible errors:

- API timeout
- Invalid API key
- Insufficient balance
- Invalid recipient phone/email
- Rate limit exceeded
- Provider outage

Handling:

- Retry where possible.
- Fallback to secondary provider where configured.
- Mark final failure after max retries.
- Notify super admin for provider outage.

## 29.3 Recipient Errors

Possible errors:

- No email address
- No phone number
- User inactive
- User opted out of optional channel
- Invalid contact details

Handling:

- Skip unavailable channel.
- Use available channel if permitted.
- Log skipped delivery.

---

# 30. Acceptance Criteria

## 30.1 In-App Notifications

- User receives in-app notification for relevant workflow events.
- User can view notification inbox.
- User can mark notification as read.
- Unread count updates correctly.
- Notification links to related record where permitted.

## 30.2 Email/SMS/WhatsApp

- System can send email using active provider.
- System can send SMS using active provider.
- System can send WhatsApp notification where enabled.
- Delivery status is tracked.
- Failed delivery can retry.
- Provider response is stored.

## 30.3 Templates

- Admin can create notification template.
- Admin can preview template.
- Admin can approve/archive template.
- Templates support allowed variables.
- Sensitive variables are blocked.
- Template versions are preserved.

## 30.4 Preferences

- User can update non-mandatory preferences.
- Mandatory notifications cannot be disabled.
- Preference settings are respected during delivery.
- Quiet hours are respected where configured, except for critical notifications.

## 30.5 Workflow Triggers

- Certificate issued triggers notification.
- Appointment booked triggers notification.
- Payment successful triggers notification.
- Inspection assigned triggers notification.
- Enforcement notice issued triggers notification.
- State report overdue triggers notification.

## 30.6 Scheduled Reminders

- Certificate expiry reminders are sent on schedule.
- Appointment reminders are sent on schedule.
- Re-accreditation reminders are sent on schedule.
- Corrective action deadline reminders are sent on schedule.
- Completed actions stop future reminders.

## 30.7 Broadcasts

- Authorized user can create broadcast.
- System estimates audience count.
- Broadcast can be previewed.
- Broadcast can require approval.
- Broadcast delivery results are tracked.

## 30.8 Privacy

- Notifications do not expose lab results, diagnosis, doctor notes, declaration answers, or full NIN.
- Employer notifications only show operational statuses.
- Public links do not expose protected data.
- Sensitive notification attempts are blocked and logged.

---

# 31. Shared Dependencies With Other Modules

## 31.1 Modules That Depend on Notifications

The Notifications & Messaging Module will be used by:

- Users/Roles/Organization module
- Employers module
- Medical Facility module
- Medical Assessment Workflow module
- Certificate & QR Verification module
- Payments, Subscriptions & Settlements module
- Inspector & Enforcement module
- Reports, Dashboards & M&E module
- Admin, Policy & Settings module

## 31.2 Required Shared Services

Recommended shared services:

```txt
NotificationService.send()
NotificationService.send_template()
NotificationService.emit_event()
NotificationPreferenceService.is_channel_allowed()
RecipientResolver.resolve()
TemplateRenderer.render()
DeliveryService.dispatch()
AuditLogService.log()
```

## 31.3 Event Contract

All modules should emit events using a shared structure:

```json
{
  "event_key": "certificate.issued",
  "source_module": "certificates",
  "related_object_type": "Certificate",
  "related_object_id": "uuid",
  "actor_id": "uuid-or-null",
  "organization_id": "uuid-or-null",
  "state_id": "uuid-or-null",
  "payload": {}
}
```

## 31.4 Audit Log Contract

Use shared audit fields:

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

## 31.5 Privacy Contract

Every module must classify notification variables as:

- Public-safe
- User-private
- Employer-safe
- Facility-safe
- Regulator-safe
- Sensitive medical
- Financial-sensitive
- Security-sensitive

Notification templates must not render variables outside the recipient’s privacy level.

---

# 32. Codex Implementation Instructions

Use this prompt for Codex:

```txt
Implement the Notifications & Messaging Module for FoodCert NG.

The module must support in-app notifications, email, SMS, WhatsApp where enabled, notification templates, event-based triggers, scheduled reminders, notification preferences, delivery tracking, retry logic, provider abstraction, broadcast messaging, notification inbox, notification dashboards, audit logs, and privacy-safe message rendering.

Important rules:
- Notifications must be triggered by domain events where possible.
- Sensitive medical data must never be exposed in notification messages.
- Employers must only receive operational/compliance-safe messages.
- Users can disable optional notifications but not mandatory regulatory, security, payment receipt, suspension/revocation, or enforcement notices.
- Templates must support versioning and approved variables.
- Delivery status must be tracked per channel.
- Failed deliveries should retry based on retry policy.
- Critical notifications may use multiple channels and bypass quiet hours.
- Broadcast messaging must be permission-controlled and audited.
- Provider secrets must not be stored in plain text.

Build backend models, services, serializers, permissions, API endpoints, background jobs, tests, and frontend pages for the module.
```

---

# 33. MVP Build Order

1. Notification model
2. NotificationDelivery model
3. NotificationTemplate model
4. NotificationPreference model
5. In-app notification inbox
6. Notification bell/unread count
7. Template rendering service
8. Event-based notification service
9. Email provider integration
10. SMS provider integration
11. Delivery tracking
12. Retry worker
13. Scheduled reminder worker
14. Certificate notification events
15. Assessment notification events
16. Payment/subscription notification events
17. Inspection/enforcement notification events
18. Report/M&E notification events
19. Notification preferences page
20. Admin template management
21. Provider configuration admin
22. Broadcast messaging MVP
23. Notification dashboard
24. Privacy-safe template tests
25. Delivery retry tests
26. Permission tests
27. Audit log tests
