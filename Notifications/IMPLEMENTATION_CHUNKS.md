# Notifications & Messaging Module — Implementation Chunks

> Derived from `FOODCERT_NOTIFICATIONS_MESSAGING_MODULE_PRD.md` (Sections 1–33)

---

## Chunk 0: Foundation — Data Models & Migrations

**PRD Ref:** §22 (Data Model Requirements)

**Deliverables:**
- [ ] `Notification` model — inbox record, recipient, category, priority, read state, related-object linking
- [ ] `NotificationDelivery` model — per-channel delivery attempt, provider response, retry fields
- [ ] `NotificationTemplate` model — template key, channel, subject/body, allowed variables, versioning, approval workflow
- [ ] `NotificationPreference` model — user/category/channel toggle, digest, quiet hours
- [ ] `NotificationProvider` model — provider config, default flag, rate limit, priority order
- [ ] `NotificationEvent` model — inbound domain event payload, processed flag
- [ ] `BroadcastMessage` model — audience filters, channel list, approval workflow, send counts
- [ ] Database migrations for all models
- [ ] Admin panel registrations for all models

**Dependencies:** `accounts.User`, `organizations.Organization`, `organizations.OrganizationUnit`, `geography.State`

---

## Chunk 1: In-App Notification Inbox + Bell

**PRD Ref:** §7.1 (In-App Notifications), §15 (Notification Inbox), §23.1 (Inbox API), §24.1–§24.6 (User Frontend Routes), §25 (Bell/Inbox Components)

**Deliverables:**
- [ ] Inbox API endpoints (`GET /api/notifications`, `GET /unread-count`, `POST /mark-read`, `POST /mark-all-read`, `POST /archive`)
- [ ] `NotificationBell` component with unread badge
- [ ] `NotificationInbox` list component
- [ ] `NotificationCard` component (title, message, category, priority, timestamp, action link)
- [ ] `NotificationDetailPanel` component
- [ ] `NotificationFilters` component (category, priority)
- [ ] `MarkAllReadButton` component
- [ ] Frontend routes: `/app/notifications`, `/app/notifications/[id]`
- [ ] Role-scoped routing (food handler sees only their own, employer sees employer-scoped, etc.)

**Dependencies:** Chunk 0

---

## Chunk 2: Notification Preferences

**PRD Ref:** §12 (Notification Preferences), §23.2 (Preference API), §24 (Settings Routes), §26 (Permissions)

**Deliverables:**
- [ ] Preference API endpoints (`GET /api/notification-preferences`, `PATCH /:id`, `POST /bulk-update`)
- [ ] `NotificationPreferenceForm` component
- [ ] `ChannelPreferenceToggle` component (per category: in-app / email / SMS / WhatsApp)
- [ ] Mandatory-notification enforcement — cannot disable security, regulatory, suspension/revocation, enforcement, payment receipts
- [ ] Quiet-hours UI
- [ ] Digest toggle
- [ ] Frontend routes: `/app/settings/notification-preferences`, `/app/employer/settings/notifications`, `/app/facility/settings/notifications`
- [ ] Employer-level recipient configuration (compliance, billing, branch, inspection, certificate expiry contacts)
- [ ] Facility-level recipient configuration (accreditation, appointment, clinical, lab, settlement, clarification contacts)

**Dependencies:** Chunk 0

---

## Chunk 3: Notification Templates Engine

**PRD Ref:** §13 (Notification Templates), §23.3 (Template API), §25 (Template Components), §29.1 (Template Errors)

**Deliverables:**
- [ ] `TemplateRenderer` service — variable interpolation, allowed-variable whitelist, sensitive-variable blocklist
- [ ] Template CRUD API (`GET/POST /api/admin/notification-templates`)
- [ ] Approval workflow API (`submit-for-approval`, `approve`, `archive`)
- [ ] Template preview API (`POST /preview`)
- [ ] `NotificationTemplateTable` component
- [ ] `NotificationTemplateEditor` component
- [ ] `TemplateVariableHelper` component (shows available variables per template)
- [ ] `TemplatePreviewPanel` component
- [ ] Template versioning — editing active template creates new version; archived templates cannot render
- [ ] Sensitive variable blocking: `full_nin`, `lab_results`, `diagnosis`, `doctor_notes`, `health_declaration_answers`, `treatment_details`, `payment_card_details`, `provider_secret_keys`
- [ ] Scope: national / state / system with state filter
- [ ] Frontend route: `/app/admin/notifications/templates`

**Dependencies:** Chunk 0

---

## Chunk 4: Provider Abstraction & Integration

**PRD Ref:** §18 (Provider Abstraction), §7.2–§7.4 (Email/SMS/WhatsApp Channels), §23.6 (Provider API)

**Deliverables:**
- [ ] Provider interface/abstract base class (`send()`, `validate_config()`)
- [ ] SMTP email provider adapter
- [ ] SMS provider adapter (Termii / Africa's Talking / Twilio)
- [ ] WhatsApp provider adapter (Meta Business API / Twilio WhatsApp)
- [ ] Provider config admin API (`GET/POST/PATCH /api/admin/notification-providers`)
- [ ] Provider test endpoint (`POST /:id/test`)
- [ ] Provider set-default endpoint (`POST /:id/set-default`)
- [ ] `NotificationProviderTable` component
- [ ] `ProviderConfigForm` component (with encrypted secrets)
- [ ] Fallback logic — if primary fails, try secondary provider where configured
- [ ] Rate-limiting per provider
- [ ] Frontend route: `/app/admin/notifications/providers`

**Dependencies:** Chunk 0

---

## Chunk 5: Event-Driven Notification Service

**PRD Ref:** §10 (Event-Based Architecture), §11 (Recipient Resolution), §23.4 (Send APIs), §31 (Shared Dependencies)

**Deliverables:**
- [ ] `NotificationService` with `send()`, `send_template()`, `emit_event()` entry points
- [ ] `RecipientResolver` service — resolves individual users, employer admins, branch managers, facility admins, doctors, lab staff, inspectors, State/Federal units
- [ ] `NotificationPreferenceService.is_channel_allowed()` — checks preferences, quiet hours, mandatory overrides
- [ ] Event contract: `{ event_key, source_module, related_object_type, related_object_id, actor_id, organization_id, state_id, payload }`
- [ ] Internal API endpoints (`POST /api/internal/notifications/events`, `POST /send`, `POST /send-template`, `POST /schedule`)
- [ ] Channel dispatch: in-app always created; email/SMS/WhatsApp dispatched per preferences + provider availability
- [ ] Privacy-safe variable classification per recipient role

**Dependencies:** Chunks 0–4

---

## Chunk 6: Delivery Tracking & Retry

**PRD Ref:** §19 (Delivery Tracking & Retry), §23.5 (Delivery API), §28.1–§28.2 (Queue & Retry Workers)

**Deliverables:**
- [ ] `DeliveryService.dispatch()` — queues message, selects provider, sends, records provider response
- [ ] Delivery status model: `Pending → Queued → Sending → Sent/Delivered/Failed/Bounced/Rejected`
- [ ] In-app read tracking, email open/click tracking where supported
- [ ] Delivery log admin API (`GET /api/admin/notification-deliveries`, `POST /:id/retry`)
- [ ] `DeliveryLogTable` component
- [ ] `DeliveryStatusBadge` component
- [ ] `RetryDeliveryButton` component
- [ ] **Queue Worker:** background job that processes `NotificationDelivery` records, renders templates, dispatches
- [ ] **Retry Worker:** finds retryable failed deliveries, applies backoff schedule (5 min / 30 min / 2 hr), marks permanently failed after max retries
- [ ] Terminal failure notification to super admin for provider outages
- [ ] Frontend route: `/app/admin/notifications/deliveries`

**Dependencies:** Chunks 0, 4, 5

---

## Chunk 7: Scheduled Reminders

**PRD Ref:** §16 (Scheduled Reminders), §28.3 (Reminder Worker)

**Deliverables:**
- [ ] Reminder schedule configuration model (or hardcoded schedules per reminder type)
- [ ] **Scheduled Reminder Worker** — background job/cron:
  - Appointment reminders (24 hr, 2 hr before)
  - Certificate expiry reminders (30d, 7d, expiry day)
  - Re-accreditation reminders (60d, 30d, 7d, expiry day)
  - Subscription expiry reminders (14d, 7d, expiry day)
  - Corrective action deadline reminders (7d, 3d, 1d, overdue)
  - State report due reminders (7d before, due day, overdue)
- [ ] Idempotency — reminders must not duplicate; completed actions stop future reminders
- [ ] Reminder delivery logging

**Dependencies:** Chunks 5, 6

---

## Chunk 8: Domain Event Wiring — Core Workflows

**PRD Ref:** §14 (Core Notification Workflows)

Wire up each domain event to the notification service. Each sub-chunk below can be built in parallel.

### Chunk 8a: Account & Identity
**PRD Ref:** §14.1, §14.2
- [ ] `user.invited` / `user.invite_accepted` / `user.invite_expired`
- [ ] `password.reset_requested`, `email.verified`, `phone.verified`
- [ ] `nin.verification_successful` / `nin.verification_failed`
- [ ] `nin.override_requested` / `nin.override_approved` / `nin.override_rejected`

### Chunk 8b: Appointments & Assessments
**PRD Ref:** §14.3, §14.4
- [ ] Appointment lifecycle: booked → confirmed → rescheduled → cancelled → no-show
- [ ] Assessment lifecycle: declaration pending/submitted → lab request/result → doctor decision → state clarification
- [ ] Recipients: food handler, doctor, facility admin, lab staff, state verification desk

### Chunk 8c: Certificates
**PRD Ref:** §14.5
- [ ] Certificate lifecycle: issued, generation failed, expiring (30d/7d), expired, suspended, reinstated, revoked, replaced
- [ ] Renewal started
- [ ] Recipients: food handler, employer, branch manager, facility admin, state verification desk

### Chunk 8d: Payments, Subscriptions & Settlements
**PRD Ref:** §14.6, §14.7, §14.8
- [ ] Payment: initiated, successful, failed, abandoned, refunded, receipt
- [ ] Subscription: activated, expiring, expired, past due, renewed, cancelled, plan changed
- [ ] Settlement: eligible, processing, paid, failed, dispute created/resolved

### Chunk 8e: Facility Accreditation
**PRD Ref:** §14.9
- [ ] Accreditation: submitted, info requested, approved, rejected, suspended, reinstated, expired
- [ ] Re-accreditation due reminders (wired to Scheduled Reminder Worker)

### Chunk 8f: Inspection & Enforcement
**PRD Ref:** §14.10
- [ ] Inspection: assigned, due today, overdue, submitted, returned for correction
- [ ] Enforcement: notice issued, acknowledged, corrective action due/overdue, response submitted
- [ ] Follow-up inspection, case escalated/closed

### Chunk 8g: Reports & M&E
**PRD Ref:** §14.11
- [ ] State report: due, overdue, submitted, returned, accepted
- [ ] National report: generated
- [ ] Data quality issues, M&E indicator below threshold

### Chunk 8h: Security
**PRD Ref:** §14.12
- [ ] Password changed, new device login, failed login threshold, role changed
- [ ] Sensitive record accessed, API key created/rotated, webhook signature failed
- [ ] Recipients: affected user, security admin, super admin (critical)

**Dependencies:** Chunk 5

---

## Chunk 9: Broadcast Messaging

**PRD Ref:** §17 (Bulk & Broadcast Notifications), §23.7 (Broadcast API), §25 (Broadcast Components)

**Deliverables:**
- [ ] Broadcast CRUD API (`GET/POST /api/admin/broadcasts`)
- [ ] Audience estimation (`POST /:id/estimate-audience`)
- [ ] Broadcast preview (`POST /:id/preview`)
- [ ] Approval workflow (`submit-for-approval`, `approve`)
- [ ] Broadcast send (`POST /:id/send`) — dispatches to resolved audience
- [ ] `BroadcastBuilder` component — audience selection, template/channel selection, preview
- [ ] `AudienceSelector` component
- [ ] `BroadcastPreviewPanel` component
- [ ] `BroadcastApprovalPanel` component
- [ ] Permission gating: State admin can broadcast to state scopes; Federal to national scopes
- [ ] Delivery tracking: `sent_count`, `failed_count`, per-recipient delivery status
- [ ] Restrictions enforced: no private medical data, no full NIN, no unapproved marketing
- [ ] Frontend routes: `/app/state/broadcasts`, `/app/federal/broadcasts`, `/app/admin/broadcasts`

**Dependencies:** Chunks 5, 6

---

## Chunk 10: Notification Dashboard

**PRD Ref:** §27 (Notification Dashboard), §25 (Dashboard Components)

**Deliverables:**
- [ ] Admin dashboard API (aggregate stats)
- [ ] Dashboard cards: total created today, emails/SMS/WhatsApp/in-app sent today, delivery success rate, failed deliveries, pending retries, critical sent, provider failures, broadcasts sent
- [ ] Charts: notifications by channel, delivery status distribution, failed delivery trend, notifications by category, provider performance, broadcast performance, critical notification trend
- [ ] Filters: date range, channel, category, priority, provider, delivery status, user type, organization, state
- [ ] `NotificationDashboardCards` component
- [ ] Frontend route: `/app/admin/notifications/dashboard`

**Dependencies:** Chunks 1, 6, 8, 9

---

## Chunk 11: Webhooks & Provider Callbacks

**PRD Ref:** §23.8 (Webhook Endpoints), §28.5 (Webhook Processor)

**Deliverables:**
- [ ] Webhook endpoints: `POST /api/webhooks/email-provider`, `/sms-provider`, `/whatsapp-provider`
- [ ] Signature validation per provider
- [ ] **Delivery Webhook Processor Worker** — processes inbound callbacks, updates `delivered_at`, handles bounce/failure events, stores provider raw response

**Dependencies:** Chunks 4, 6

---

## Chunk 12: Digest Worker

**PRD Ref:** §28.4 (Digest Worker)

**Deliverables:**
- [ ] Digest configuration per user/category (daily/weekly)
- [ ] **Digest Worker** — aggregates notifications per recipient, sends single digest email/in-app
- [ ] Daily employer compliance digest
- [ ] Weekly facility activity digest
- [ ] Weekly state enforcement digest

**Dependencies:** Chunks 5, 6

---

## Chunk 13: Audit Logging

**PRD Ref:** §21 (Audit Logging), §31.4 (Audit Log Contract)

**Deliverables:**
- [ ] Shared `AuditLogService.log()` with contract: actor, action_type, module, target_type, target_id, organization_id, state_id, metadata, ip_address, user_agent, created_at
- [ ] Audit events wired for: notification created, rendered, queued, sent, delivered, failed, retried, read
- [ ] Template events: created, updated, approved, archived
- [ ] Broadcast events: created, sent
- [ ] Preference changed
- [ ] Provider config changed
- [ ] Critical notification sent
- [ ] Sensitive notification blocked due to privacy rule

**Dependencies:** Chunks 0–12 (wired alongside each chunk)

---

## Chunk 14: Privacy & Security Enforcement Tests

**PRD Ref:** §20 (Privacy & Security Requirements), §30.8 (Privacy Acceptance Criteria), §29 (Error Handling)

**Deliverables:**
- [ ] Automated test suite verifying:
  - Sensitive variables (`full_nin`, `lab_results`, `diagnosis`, `doctor_notes`, `health_declaration_answers`, `treatment_details`, `payment_card_details`, `provider_secret_keys`) are blocked from template rendering
  - Employer notifications contain only operational statuses (no medical details)
  - Public links do not expose protected data
  - SMS/WhatsApp bodies contain no private clinical details
  - Mandatory notifications cannot be disabled by user preference
  - Provider secrets are not stored in plain text
- [ ] Template error handling tests (missing template, inactive, missing variable, blocked sensitive variable)
- [ ] Provider error handling tests (timeout, invalid key, insufficient balance, rate limit)
- [ ] Recipient error handling tests (no email, no phone, inactive user, opted out)

**Dependencies:** Chunks 0–13

---

## Chunk 15: Permission & Access Control Tests

**PRD Ref:** §26 (Permissions and Access Control), §30.9 (Acceptance Criteria — implied)

**Deliverables:**
- [ ] Test: General user can only see own notifications
- [ ] Test: General user cannot access admin/broadcast/template endpoints
- [ ] Test: Employer admin can manage employer routing but not facility or state scopes
- [ ] Test: Facility admin can manage facility routing but not state/national scopes
- [ ] Test: State admin can send state-scoped broadcasts only
- [ ] Test: Federal admin can send national broadcasts only
- [ ] Test: Super admin has full access (templates, providers, delivery logs, policies)
- [ ] Test: Unauthenticated access returns 401 on all notification endpoints

**Dependencies:** Chunks 1, 2, 5, 9

---

## Chunk 16: End-to-End Acceptance Tests

**PRD Ref:** §30 (Full Acceptance Criteria)

**Deliverables:**
- [ ] E2E test: Certificate issued → food handler, employer, facility, state all receive correct notification
- [ ] E2E test: Appointment booked → reminder sent 24h and 2h before; cancelled appointment stops reminders
- [ ] E2E test: Payment successful → receipt notification sent; payment failed → failure notification
- [ ] E2E test: Inspection assigned → inspector notified; overdue inspection escalates
- [ ] E2E test: Enforcement notice → employer notified; corrective action deadline reminders fire; completed action stops reminders
- [ ] E2E test: State report overdue → state + federal officers notified
- [ ] E2E test: Broadcast created → audience estimated → approved → sent → delivery tracked
- [ ] E2E test: Failed delivery → retried → permanently failed after max retries → super admin alerted
- [ ] E2E test: Sensitive data blocked in all channels

**Dependencies:** Chunks 0–15

---

## Suggested Build Sequence

```
Chunk 0   ──► Chunk 1   ──► Chunk 2
                │
                ▼
           Chunk 3   ──► Chunk 4
                │            │
                ▼            ▼
           Chunk 5 ◄─────────┘
                │
     ┌──────────┼──────────┐
     ▼          ▼          ▼
  Chunk 6   Chunk 7   Chunk 9
     │                    │
     ▼                    │
  Chunk 8a–8h ◄───────────┘
     │
     ├──► Chunk 10
     ├──► Chunk 11
     ├──► Chunk 12
     └──► Chunk 13 ──► Chunk 14 ──► Chunk 15 ──► Chunk 16
```

- **Chunks 3 and 4** can run in parallel after Chunk 1.
- **Chunks 8a–8h** can all run in parallel once Chunk 5 is done.
- **Chunks 10, 11, 12** can run in parallel after Chunk 8.
- **Chunk 13** (audit logging) should be wired incrementally alongside each chunk, then finalized at the end.
- **Chunks 14–16** are validation/test phases running after all implementation chunks.
