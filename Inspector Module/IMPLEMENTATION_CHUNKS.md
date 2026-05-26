# Inspector & Enforcement Module — Implementation Chunks

> Based on [FOODCERT_INSPECTOR_ENFORCEMENT_MODULE_PRD.md](./FOODCERT_INSPECTOR_ENFORCEMENT_MODULE_PRD.md)
> Codebase audit date: 2026-05-25

---

## Phase 1: Foundation Models & Extensions

### Chunk 1.1 — Extend Inspection Model

**Status:** Backend | **Depends on:** nothing

Add the following fields to the existing `Inspection` model:

| Field | Type | Notes |
|---|---|---|
| `reference` | CharField(max_length=100, unique=True) | Auto-gen: FCN-INS-YYYY-NNNNNN |
| `inspection_type` | CharField(max_length=80) | routine, follow_up, complaint_based, certificate_sweep, illness_risk, facility_linked (§7) |
| `priority` | CharField(max_length=50) | low, medium, high, critical (§9.3) |
| `scheduled_at` | DateTimeField(null=True) | |
| `started_at` | DateTimeField(null=True) | |
| `reviewed_at` | DateTimeField(null=True) | |
| `closed_at` | DateTimeField(null=True) | |
| `linked_complaint_id` | UUIDField(null=True) | |
| `linked_illness_report_id` | UUIDField(null=True) | |
| `parent_inspection` | FK("self", null=True) | For follow-up inspections |
| `supervising_officer` | FK(User, null=True) | related_name="supervised_inspections" |

Expand `InspectionStatus` choices to all 16 states:

```
draft, assigned, accepted, scheduled, in_progress, submitted,
under_review, returned_for_correction, notice_issued,
corrective_action_pending, corrective_action_submitted,
follow_up_required, follow_up_scheduled, resolved, escalated,
closed, cancelled
```

Add status transition validation that enforces the rules table in §8.3.

**Output:** 1 migration file, extended model + serializer

---

### Chunk 1.2 — InspectionChecklistItem Model (Template)

**Status:** Backend | **Depends on:** nothing

New model storing reusable checklist template items:

```python
class InspectionChecklistItem(models.Model):
    id = UUIDField(primary_key=True)
    category = CharField(max_length=100)        # §14.2 categories A-G
    question = TextField()
    severity_if_failed = CharField(max_length=50)  # minor, major, critical
    is_active = BooleanField(default=True)
    sort_order = PositiveIntegerField(default=0)
    created_at = DateTimeField(auto_now_add=True)
```

**Deliverables:**
- Model + migration
- Admin with drag-reorder
- Seed command: `manage.py seed_checklist_items` — creates 20+ default items across 7 categories (§14.2)
- API: `GET /api/inspection-checklist-items/` (list active items)
- API: `POST /api/inspection-checklist-items/` (state admin only)

---

### Chunk 1.3 — InspectionChecklistResponse Model (Runtime)

**Status:** Backend | **Depends on:** 1.1, 1.2

New model storing per-inspection checklist answers:

```python
class InspectionChecklistResponse(models.Model):
    id = UUIDField(primary_key=True)
    inspection = FK(Inspection, CASCADE)
    checklist_item = FK(InspectionChecklistItem, PROTECT)
    response = CharField(max_length=50)  # yes, no, n/a, not_observed, needs_follow_up
    severity = CharField(max_length=50, blank=True)
    note = TextField(blank=True)
    created_by = FK(User, SET_NULL, null=True)
    created_at = DateTimeField(auto_now_add=True)
```

**APIs:**
- `GET /api/inspections/:id/checklist-responses` — list all responses for inspection
- `POST /api/inspections/:id/checklist-responses` — create/update responses (upsert per item)
- `PATCH /api/inspections/:id/checklist-responses/:response_id` — update single response

**Note:** Keep existing `checklist_responses` JSONField for backward compat during transition, then deprecate.

**Output:** 1 migration, serializer, view, URL registration

---

### Chunk 1.4 — InspectionFinding Model

**Status:** Backend | **Depends on:** 1.1

New structured findings model (replaces flat text `findings` field):

```python
class InspectionFinding(models.Model):
    id = UUIDField(primary_key=True)
    inspection = FK(Inspection, CASCADE)
    category = CharField(max_length=100)
    finding_type = CharField(max_length=100)   # compliance_confirmed, minor, major, critical, suspicious_cert, public_health_risk, doc_gap, repeat_violation
    severity = CharField(max_length=50)         # minor, major, critical
    description = TextField()
    recommended_action = TextField(blank=True)
    food_handler = FK(FoodHandlerProfile, SET_NULL, null=True)
    certificate = FK(Certificate, SET_NULL, null=True)
    status = CharField(max_length=50)           # open, under_review, notice_issued, corrective_action_pending, corrected, not_corrected, escalated, closed
    created_by = FK(User, SET_NULL, null=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

**APIs:**
- `GET /api/inspections/:id/findings`
- `POST /api/inspections/:id/findings`
- `GET /api/inspections/:id/findings/:finding_id`
- `PATCH /api/inspections/:id/findings/:finding_id`

**Output:** 1 migration, serializer, view, URL registration

---

### Chunk 1.5 — InspectionEvidence Model

**Status:** Backend | **Depends on:** 1.1, 1.4

Proper evidence model (replaces `evidence_files` JSON list):

```python
class InspectionEvidence(models.Model):
    id = UUIDField(primary_key=True)
    inspection = FK(Inspection, CASCADE)
    finding = FK(InspectionFinding, CASCADE, null=True)
    evidence_type = CharField(max_length=50)    # photo, video, document, cert_screenshot, signed_notice, employer_response_doc, inspector_note, gps_location
    file_url = URLField()
    caption = CharField(max_length=255, blank=True)
    uploaded_by = FK(User, SET_NULL, null=True)
    latitude = DecimalField(max_digits=10, decimal_places=7, null=True)
    longitude = DecimalField(max_digits=10, decimal_places=7, null=True)
    created_at = DateTimeField(auto_now_add=True)
```

**APIs:**
- `POST /api/inspections/:id/evidence`
- `GET /api/inspections/:id/evidence`
- `DELETE /api/inspections/:id/evidence/:evidence_id`

**Note:** Migrate existing `evidence_files` JSON entries to this table via data migration.

**Output:** 1 migration (+ 1 data migration), serializer, view, URL registration

---

## Phase 2: Enforcement & Case Models

### Chunk 2.1 — EnforcementNotice Model

**Status:** Backend | **Depends on:** 1.1, 1.4

```python
class EnforcementNotice(models.Model):
    id = UUIDField(primary_key=True)
    notice_reference = CharField(max_length=100, unique=True)
    inspection = FK(Inspection, CASCADE)
    employer = FK(Employer, PROTECT)
    branch = FK(OrganizationUnit, SET_NULL, null=True)
    notice_type = CharField(max_length=100)     # advisory, warning, compliance, corrective_action, follow_up, suspension_recommendation, closure_recommendation, public_health_escalation, cert_review_recommendation, facility_review_recommendation
    status = CharField(max_length=80)           # draft, pending_approval, issued, acknowledged, corrective_action_pending, response_submitted, under_review, accepted, rejected, follow_up_required, escalated, closed
    description = TextField()
    required_corrective_actions = TextField()
    deadline = DateField(null=True)
    issued_by = FK(User, related_name="notices_issued", SET_NULL, null=True)
    approved_by = FK(User, related_name="notices_approved", SET_NULL, null=True)
    issued_at = DateTimeField(null=True)
    acknowledged_at = DateTimeField(null=True)
    closed_at = DateTimeField(null=True)
    closure_note = TextField(blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

**APIs:**
- `GET /api/enforcement-notices` — scoped by role (inspector sees own, employer sees theirs, etc.)
- `POST /api/inspections/:id/notices` — create notice from inspection findings
- `GET /api/enforcement-notices/:id`
- `PATCH /api/enforcement-notices/:id`
- `POST /api/enforcement-notices/:id/submit-for-approval`
- `POST /api/enforcement-notices/:id/approve`
- `POST /api/enforcement-notices/:id/issue`
- `POST /api/enforcement-notices/:id/acknowledge`
- `POST /api/enforcement-notices/:id/close`

**Output:** 1 migration, serializer, viewset, URL registration

---

### Chunk 2.2 — CorrectiveActionResponse Model

**Status:** Backend | **Depends on:** 2.1

```python
class CorrectiveActionResponse(models.Model):
    id = UUIDField(primary_key=True)
    notice = FK(EnforcementNotice, CASCADE)
    submitted_by = FK(User, SET_NULL, null=True)
    response_note = TextField()
    action_taken = TextField()
    status = CharField(max_length=80)           # submitted, under_review, accepted, rejected, more_evidence_requested
    reviewed_by = FK(User, related_name="corrective_actions_reviewed", SET_NULL, null=True)
    review_note = TextField(blank=True)
    submitted_at = DateTimeField(auto_now_add=True)
    reviewed_at = DateTimeField(null=True)
```

**APIs:**
- `GET /api/enforcement-notices/:id/corrective-actions`
- `POST /api/enforcement-notices/:id/corrective-actions`
- `POST /api/corrective-actions/:id/review`
- `POST /api/corrective-actions/:id/accept`
- `POST /api/corrective-actions/:id/reject`
- `POST /api/corrective-actions/:id/request-more-evidence`

**Output:** 1 migration, serializer, view, URL registration

---

### Chunk 2.3 — EnforcementCase Model

**Status:** Backend | **Depends on:** 1.1, 2.1

```python
class EnforcementCase(models.Model):
    id = UUIDField(primary_key=True)
    case_reference = CharField(max_length=100, unique=True)
    state = FK(State, PROTECT)
    employer = FK(Employer, PROTECT)
    branch = FK(OrganizationUnit, SET_NULL, null=True)
    status = CharField(max_length=80)           # open, under_review, awaiting_employer_response, follow_up_required, escalated, resolved, closed
    severity = CharField(max_length=50)          # low, medium, high, critical
    summary = TextField()
    opened_by = FK(User, related_name="enforcement_cases_opened", SET_NULL, null=True)
    assigned_to = FK(User, related_name="enforcement_cases_assigned", SET_NULL, null=True)
    escalated_to = CharField(max_length=100, blank=True)  # inspectorate_coordinator, state_admin, federal, other_authority
    opened_at = DateTimeField(auto_now_add=True)
    closed_at = DateTimeField(null=True)
    closure_note = TextField(blank=True)
```

**APIs:**
- `GET /api/enforcement-cases`
- `POST /api/enforcement-cases`
- `GET /api/enforcement-cases/:id`
- `PATCH /api/enforcement-cases/:id`
- `POST /api/enforcement-cases/:id/close`

Case timeline query: join inspections → findings → notices → corrective_actions → follow_ups → escalations, ordered by timestamp.

**Output:** 1 migration, serializer, viewset, URL registration

---

## Phase 3: Workflow & Lifecycle Actions

### Chunk 3.1 — Inspection Lifecycle Actions

**Status:** Backend | **Depends on:** 1.1

New ViewSet actions + service methods:

| Action | Endpoint | From → To | Who |
|---|---|---|---|
| Accept | `POST /api/inspections/:id/accept` | assigned → accepted | Inspector |
| Start | `POST /api/inspections/:id/start` | accepted/scheduled → in_progress | Inspector |
| Reschedule request | `POST /api/inspections/:id/reschedule-request` | assigned/accepted → assigned (with note) | Inspector |
| Submit | `POST /api/inspections/:id/submit` | in_progress → submitted | Inspector (already partially exists, extend) |
| Return for correction | `POST /api/inspections/:id/return-for-correction` | submitted/under_review → returned_for_correction | Coordinator |
| Cancel | `POST /api/inspections/:id/cancel` | any active → cancelled | Coordinator/Admin |

Create a status transition validator decorator/class that reads from the rules table in §8.3.

**Output:** 5 new service methods, 6 new view actions, updated URL registration

---

### Chunk 3.2 — Follow-Up Inspection Workflow

**Status:** Backend | **Depends on:** 1.1, 1.4, 3.1

- `POST /api/inspections/:id/create-follow-up` — creates new Inspection linked via `parent_inspection`, copies unresolved findings to new inspection
- Follow-up checklist auto-populates from unresolved findings of parent
- Follow-up outcome statuses: corrected, partially_corrected, not_corrected, new_violation, escalated, closed
- Service: `InspectionService.create_follow_up(parent_inspection, scheduled_date, assigned_inspector)`

---

### Chunk 3.3 — Escalation Workflow

**Status:** Backend | **Depends on:** 2.3, 2.1, 3.2

- `POST /api/inspections/:id/escalate` — creates EnforcementCase, sets inspection status to escalated
- `POST /api/enforcement-cases/:id/escalate` — escalates existing case to next level
- Escalation triggers (auto-detect where possible): critical findings, revoked/suspended cert in use, overdue critical notices, repeated violations
- Notification dispatch to appropriate role level
- Escalation levels: coordinator → state_admin → federal (configurable per case severity)

---

## Phase 4: Dashboards & Reports

### Chunk 4.1 — Inspector Dashboard API

**Status:** Backend | **Depends on:** 1.1, 2.1

**`GET /api/inspector/dashboard`** — Aggregated metric cards:
- assigned_inspections, due_today, overdue, in_progress, submitted, notices_issued, corrective_actions_pending, follow_ups, high_priority, closed_this_month

**`GET /api/inspector/tasks`** — Paginated task list with filters:
- status, priority, inspection_type, scheduled_at range
- Columns: reference, employer, branch, LGA, type, scheduled_date, priority, status, actions

---

### Chunk 4.2 — Employer/Branch Inspection Context API

**Status:** Backend | **Depends on:** 1.1, existing employer/food_handler/certificate models

**`GET /api/inspections/:id/employer-context`** — Employer profile, branch info
**`GET /api/inspections/:id/compliance-summary`** — Aggregated counts per §11.3:
```json
{
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
  "overall_compliance_status": "compliant|partially_compliant|non_compliant|high_risk"
}
```

**`GET /api/inspections/:id/food-handlers`** — Linked food handlers with inspector-safe fields only (name, photo, cert status, fitness status — no medical data).

**`ComplianceStatusService`** class with methods: `get_branch_compliance_summary()`, `get_employer_compliance_summary()`, `get_food_handler_operational_status()`

---

### Chunk 4.3 — State Enforcement Dashboard API

**Status:** Backend | **Depends on:** 1.1, 2.1, 2.2, 2.3

**`GET /api/state/enforcement/dashboard`** — Card metrics + chart data:
- Cards: total_inspections, inspections_this_month, inspections_by_lga, open_cases, notices_issued, overdue_corrective_actions, critical_findings, suspicious_certs, follow_ups_pending, employer_compliance_rate, branches_inspected, inspectors_active
- Charts: inspections over time, findings by severity, notices by type, compliance by LGA, compliance by establishment category, cert issues detected, corrective action completion rate, inspector workload, repeat violations by employer
- Filters: date_range, state, lga, inspector, employer, branch, inspection_type, notice_status, finding_severity, cert_issue_type, establishment_category

**Report endpoints:**
- `GET /api/state/enforcement/reports/inspections`
- `GET /api/state/enforcement/reports/notices`
- `GET /api/state/enforcement/reports/corrective-actions`
- `GET /api/state/enforcement/reports/critical-findings`

Export formats: PDF, Excel, CSV. Must respect privacy rules.

---

### Chunk 4.4 — Federal Enforcement Dashboard API

**Status:** Backend | **Depends on:** 1.1, 4.3

**`GET /api/federal/enforcement/dashboard`** — National aggregate metrics:
- Total inspections nationally, inspections by state, notices by state, critical findings by state, overdue corrective actions by state, suspicious certs flagged, employer compliance trends, inspection coverage by state, repeat violation patterns, public health risk escalations

**`GET /api/federal/enforcement/reports/summary`** — National comparison reports.
- Aggregate only by default. No medical data exposure.
- Federal users do not drill into individual records by default.

---

## Phase 5: Background Jobs & Notifications

### Chunk 5.1 — Inspection Reminder Job

**Status:** Backend (Celery Beat) | **Depends on:** 1.1

Runs daily/hourly. Tasks:
- Notify inspectors of inspections due today
- Notify inspectors of overdue inspections (escalate if >X days)
- Notify coordinators of overdue assignments

Uses existing notification system (§35.10): events `inspection_due`, `inspection_assigned`

---

### Chunk 5.2 — Notice Deadline Job

**Status:** Backend (Celery Beat) | **Depends on:** 2.1, 2.2

Runs daily. Tasks:
- Notify employers of upcoming corrective action deadlines (48h, 24h before)
- Mark overdue notices, escalate overdue critical notices per policy (7 days overdue)
- Notify coordinators of overdue corrective actions

Uses notification events: `corrective_action_due`, `corrective_action_overdue`

---

### Chunk 5.3 — Follow-Up & Analytics Jobs

**Status:** Backend (Celery Beat) | **Depends on:** 1.1, 2.1, 3.2

Runs daily. Tasks:
- Notify coordinators/inspectors of follow-up inspections due
- Recalculate state inspection metrics (cache warm)
- Identify repeat violations (>2 same-issue findings for same employer)
- Identify suspicious certificate patterns (>3 flags from same facility)
- Flag employers with compliance rate below threshold

---

## Phase 6: Frontend

### Chunk 6.1 — Inspector Dashboard Page

**Status:** Frontend | **Depends on:** 4.1 API

- Route: `/inspector/dashboard`
- Components:
  - `InspectorDashboardCards` — 10 metric cards with counts
  - `InspectionTaskTable` — sortable, filterable by status/priority/type/date
- Actions per row: Accept, Request Reschedule, Start Inspection, View
- Uses `react-query` for data fetching, polling for updates

---

### Chunk 6.2 — Inspection Workflow Pages (Inspector)

**Status:** Frontend | **Depends on:** 1.1-1.5 APIs, 3.1

| Route | Key Components | Function |
|---|---|---|
| `/inspector/inspections/[id]/start` | `EmployerBranchInspectionContext`, `InspectionStatusBadge` | Confirm employer/branch details, set inspection type |
| `/inspector/inspections/[id]/scan` | `InspectorQRScanner` (html5-qrcode), `ManualCertificateVerificationForm`, `InspectorVerificationResultCard` | Scan or enter certificate, view inspector-safe result, flag issues |
| `/inspector/inspections/[id]/food-handlers` | `FoodHandlerInspectionList` | Tabular list with present/absent/scan/flag actions, issue types dropdown |
| `/inspector/inspections/[id]/checklist` | `InspectionChecklistForm`, `ChecklistSeverityBadge` | Per-category sections, response types, severity selector |
| `/inspector/inspections/[id]/findings` | `FindingForm`, `FindingList` | Link findings to checklist items, food handlers, certificates |
| `/inspector/inspections/[id]/evidence` | `EvidenceUploadPanel`, `EvidenceGallery` | Upload photos/docs, link to findings, add captions |
| `/inspector/inspections/[id]/submit` | `InspectionReportBuilder` | Summary review of all findings, evidence, checklist; final submit |

---

### Chunk 6.3 — Inspectorate Coordinator Pages

**Status:** Frontend | **Depends on:** 2.1-2.3, 3.2-3.3 APIs

| Route | Key Components | Function |
|---|---|---|
| `/state/inspectorate/dashboard` | Sidebar + summary cards | Coordinator's oversight view |
| `/state/inspectorate/assignments` | `InspectionAssignmentForm` | Form: select employer/branch, inspector, type, priority, schedule date, link complaint/illness |
| `/state/inspectorate/notices` | List with `NoticeStatusBadge` | All notices, filterable by status/type |
| `/state/inspectorate/notices/[id]` | `NoticeBuilder`, `CorrectiveActionReviewPanel` | Review notice, approve/reject, review employer response |
| `/state/inspectorate/cases` | List with status badges | Enforcement cases list |
| `/state/inspectorate/cases/[id]` | `EnforcementCaseTimeline`, `EscalationModal`, `FollowUpInspectionPanel` | Case detail, timeline, escalate, create follow-up |

---

### Chunk 6.4 — Employer Notices Pages

**Status:** Frontend | **Depends on:** 2.1, 2.2 APIs

| Route | Key Components | Function |
|---|---|---|
| `/employer/notices` | Notice list with status, deadlines | All notices for employer's branches |
| `/employer/notices/[id]` | Notice detail, deadline countdown | View notice, corrective actions required |
| `/employer/notices/[id]/respond` | `CorrectiveActionResponseForm`, evidence upload | Submit response + evidence |

---

### Chunk 6.5 — State & Federal Enforcement Dashboards

**Status:** Frontend | **Depends on:** 4.3, 4.4 APIs

| Route | Key Components | Function |
|---|---|---|
| `/state/enforcement/dashboard` | `StateEnforcementDashboardCards`, Recharts (inspections over time, findings by severity, notices by type, compliance by LGA, inspector workload), filter toolbar | State admin enforcement overview |
| `/state/enforcement/reports` | Report builder with format selector (PDF/Excel/CSV) | Exportable reports |
| `/federal/enforcement/dashboard` | `FederalEnforcementSummaryCards`, state comparison bar charts, trend lines | Federal oversight view (aggregate only) |
| `/federal/enforcement/reports` | National report builder | Export national summaries |

---

## Phase 7: Permissions, Tests & Integration

### Chunk 7.1 — Permissions & Access Control

**Status:** Backend | **Depends on:** all backend chunks

Define Django permissions:
```
inspection.view / inspection.create / inspection.assign
inspection.conduct / inspection.submit / inspection.review
inspection.close / inspection.escalate
notice.create / notice.approve / notice.issue / notice.close
corrective_action.review
certificate.verify
```

Assign to roles:
- **Inspector:** view, conduct, submit, certificate.verify
- **Coordinator:** + assign, review, close, notice.*, corrective_action.review, escalate
- **State Admin:** + notice.close (override), config checklist templates
- **LGA Officer:** view, conduct, submit (scoped to LGA)
- **Employer:** view (own), corrective_action (submit)
- **Federal:** view (aggregate), export reports

Privacy enforcement at serializer/service level:
- Filter out medical fields (lab_results, diagnosis, doctor_notes, declaration_answers, full_nin)
- Inspector-safe certificate verification response shape
- Employer-safe notice view (no internal notes)

---

### Chunk 7.2 — Backend Tests

**Status:** Backend | **Depends on:** all backend chunks

Test categories:
1. **Model tests:** validation, constraints, status transitions (reject invalid transitions)
2. **API tests (happy path):** all endpoints for all roles
3. **API tests (error cases):** permission denied, invalid state transitions, missing required fields
4. **Privacy tests:** verify no medical data in inspector/federal responses
5. **Permission tests:** verify role scoping (inspector can't review, employer can't edit findings)
6. **Shared contract integration tests (§35.12):** 10 checkpoints
7. **Background job tests:** reminders fire correctly, deadlines trigger escalation

---

### Chunk 7.3 — Audit Log Integration

**Status:** Backend | **Depends on:** all backend chunks

Add audit log entries using existing shared format for all 20+ events in §32:

```
inspection_assignment_created, inspector_reassigned,
inspection_accepted, inspection_started, certificate_scanned,
manual_certificate_verification, identity_match_confirmed,
certificate_issue_flagged, checklist_response_created,
finding_created, evidence_uploaded, evidence_deleted,
inspection_submitted, inspection_returned_for_correction,
notice_drafted, notice_approved, notice_issued,
notice_acknowledged, employer_response_submitted,
corrective_action_reviewed, follow_up_created,
case_escalated, case_closed, sensitive_record_viewed
```

---

## Summary

| Phase | Chunks | Description |
|---|---|---|
| 1. Foundation | 5 | Inspection ext, ChecklistItem, ChecklistResponse, Finding, Evidence |
| 2. Enforcement | 3 | Notice, CorrectiveAction, EnforcementCase |
| 3. Workflow | 3 | Lifecycle actions, Follow-ups, Escalation |
| 4. Dashboards | 4 | Inspector dashboard, Context, State dash, Federal dash |
| 5. Jobs | 3 | Reminders, Deadlines, Analytics |
| 6. Frontend | 5 | Inspector pages, Coordinator, Employer notices, Dashboards |
| 7. Polish | 3 | Permissions, Tests, Audit logs |

**Total: 23 chunks, 7 phases**

Chunks within a phase can be parallelized. Phases must be sequential (1 → 2 → 3 → 4/5 → 6 → 7). Phases 4 and 5 can be done in parallel.
