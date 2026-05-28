# Reports, Dashboards & M&E Module — Implementation Chunks

> Based on [FOODCERT_REPORTS_DASHBOARDS_ME_MODULE_PRD.md](./FOODCERT_REPORTS_DASHBOARDS_ME_MODULE_PRD.md)
> Codebase audit date: 2026-05-27

---

## Existing Foundation (Do Not Rebuild)

The `apps/reports/` app already has:

- **Models**: `ReportSchedule`, `GeneratedReport`, `ReportType` (enum), `ReportFormat` (enum)
- **Services**: `DashboardService` (employer, facility, state, federal), `ReportService` (generate, CSV/PDF/Excel export), `EmployerReportService` (compliance, certificates, vaccinations)
- **Views/URLs**: `GET /api/dashboard/employer/`, `GET /api/dashboard/facility/`, `GET /api/dashboard/state/`, `GET /api/dashboard/federal/`, `GET /api/reports/*` (7 report types), `ReportScheduleViewSet`, `GeneratedReportViewSet`

All new work must extend, not replace, the existing codebase.

---

## Phase 1: Enhanced Data Models

### Chunk 1.1 — Extend GeneratedReport Model

**Status:** Backend | **Depends on:** existing `GeneratedReport`

Add PRD-specified fields to the existing `GeneratedReport` model:

| Field | Type | Notes |
|---|---|---|
| `title` | CharField(max_length=255) | User-friendly title |
| `organization` | FK(Organization, null=True) | Scoping |
| `state` | FK(State, null=True) | Scoping |
| `reporting_period_start` | DateField(null=True) | |
| `reporting_period_end` | DateField(null=True) | |
| `data_snapshot` | JSONField(default=dict) | Archived metric snapshot |
| `error_message` | TextField(blank=True) | For failed reports |
| `submitted_to_federal_at` | DateTimeField(null=True) | State→Federal workflow |
| `reviewed_by` | FK(User, null=True, related_name="reviewed_generated_reports") | |
| `reviewed_at` | DateTimeField(null=True) | |
| `review_status` | CharField(max_length=50, blank=True) | pending_review, accepted, returned_for_correction |
| `review_comment` | TextField(blank=True) | |

Update `GeneratedReportStatus` to include: `pending, generating, generated, failed, submitted, returned_for_correction, accepted, archived`.

**Output:** 1 migration, updated model, updated serializer

---

### Chunk 1.2 — ReportTemplate Model

**Status:** Backend | **Depends on:** nothing

New model per PRD §26.1:

```python
class ReportTemplate(models.Model):
    id = UUIDField(primary_key=True)
    code = CharField(max_length=100, unique=True)
    name = CharField(max_length=255)
    description = TextField(blank=True)
    module = CharField(max_length=100)
    scope = CharField(max_length=50)  # food_handler, employer, facility, state, federal, admin
    output_formats = JSONField(default=list)
    default_filters = JSONField(default=dict)
    required_permissions = JSONField(default=list)
    privacy_level = CharField(max_length=50)
    is_active = BooleanField(default=True)
    created_by = FK(User, null=True, SET_NULL)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

**APIs:**
- `GET /api/report-templates` — list active templates (scoped by user role)
- `POST /api/report-templates` — super admin only
- `GET /api/report-templates/:id`
- `PATCH /api/report-templates/:id` — super admin only
- `DELETE /api/report-templates/:id` — super admin only

**Seed data:** Create default templates for all report types listed in `ReportType` enum.

**Output:** 1 migration, model, serializer, viewset, URL registration, seed command

---

### Chunk 1.3 — MEIndicator and MEIndicatorValue Models

**Status:** Backend | **Depends on:** nothing

New models per PRD §26.3-26.4:

```python
class MEIndicator(models.Model):
    id = UUIDField(primary_key=True)
    code = CharField(max_length=100, unique=True)
    name = CharField(max_length=255)
    description = TextField(blank=True)
    category = CharField(max_length=100)
    numerator_definition = TextField(blank=True)
    denominator_definition = TextField(blank=True)
    formula = TextField()
    data_sources = JSONField(default=list)
    reporting_frequency = CharField(max_length=50)
    disaggregation_fields = JSONField(default=list)
    target_value = DecimalField(max_digits=12, decimal_places=2, null=True)
    warning_threshold = DecimalField(max_digits=12, decimal_places=2, null=True)
    critical_threshold = DecimalField(max_digits=12, decimal_places=2, null=True)
    visualization_type = CharField(max_length=50)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

class MEIndicatorValue(models.Model):
    id = UUIDField(primary_key=True)
    indicator = FK(MEIndicator, CASCADE)
    state = FK(State, null=True, SET_NULL)
    lga = FK(LGA, null=True, SET_NULL)
    organization = FK(Organization, null=True, SET_NULL)
    period_start = DateField()
    period_end = DateField()
    numerator_value = DecimalField(max_digits=18, decimal_places=4, null=True)
    denominator_value = DecimalField(max_digits=18, decimal_places=4, null=True)
    calculated_value = DecimalField(max_digits=18, decimal_places=4)
    disaggregation = JSONField(default=dict)
    calculated_at = DateTimeField(auto_now_add=True)
```

**Seed data:** Create indicators for all 10 categories in PRD §18.2 (A-J), minimum 30 indicators.

**Output:** 2 migrations, models, serializers, seed command

---

### Chunk 1.4 — DashboardWidget Model

**Status:** Backend | **Depends on:** nothing

New model per PRD §26.5:

```python
class DashboardWidget(models.Model):
    id = UUIDField(primary_key=True)
    code = CharField(max_length=100, unique=True)
    name = CharField(max_length=255)
    dashboard_scope = CharField(max_length=50)
    widget_type = CharField(max_length=50)  # kpi_card, line_chart, bar_chart, pie_chart, table, trend_card
    metric_code = CharField(max_length=100, blank=True)
    configuration = JSONField(default=dict)
    required_permissions = JSONField(default=list)
    sort_order = PositiveIntegerField(default=0)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

**Seed data:** Create default widgets for all dashboards (food_handler, employer, facility, doctor, lab, inspector, state, federal, admin).

**Output:** 1 migration, model, serializer, seed command

---

### Chunk 1.5 — DataQualityIssue Model

**Status:** Backend | **Depends on:** nothing

New model per PRD §26.7:

```python
class DataQualityIssue(models.Model):
    id = UUIDField(primary_key=True)
    issue_type = CharField(max_length=100)
    severity = CharField(max_length=50)  # low, medium, high, critical
    module = CharField(max_length=100)
    target_type = CharField(max_length=100)  # food_handler, certificate, employer, facility, assessment, inspection
    target_id = UUIDField(null=True)
    state = FK(State, null=True, SET_NULL)
    organization = FK(Organization, null=True, SET_NULL)
    description = TextField()
    status = CharField(max_length=50)  # open, assigned, in_progress, resolved, rejected, escalated
    assigned_to = FK(User, null=True, SET_NULL)
    resolved_by = FK(User, null=True, related_name="resolved_data_quality_issues", SET_NULL)
    resolved_at = DateTimeField(null=True)
    metadata = JSONField(default=dict)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

**APIs (to be built in Phase 5):**
- `GET /api/data-quality/issues`
- `GET /api/data-quality/issues/:id`
- `PATCH /api/data-quality/issues/:id`
- `POST /api/data-quality/issues/:id/assign`
- `POST /api/data-quality/issues/:id/resolve`
- `POST /api/data-quality/issues/:id/escalate`
- `GET /api/data-quality/dashboard`

**Output:** 1 migration, model

---

### Chunk 1.6 — ScheduledReport Model (Enhanced)

**Status:** Backend | **Depends on:** 1.2

New model per PRD §26.6 (alongside existing `ReportSchedule` for backward compat):

```python
class ScheduledReport(models.Model):
    id = UUIDField(primary_key=True)
    report_template = FK(ReportTemplate, PROTECT)
    owner = FK(User, CASCADE)
    name = CharField(max_length=255)
    schedule_frequency = CharField(max_length=50)  # daily, weekly, monthly, quarterly
    filters = JSONField(default=dict)
    output_format = CharField(max_length=20)
    delivery_channels = JSONField(default=list)  # ["email", "in_app", "download_link"]
    recipients = JSONField(default=list)
    is_active = BooleanField(default=True)
    last_run_at = DateTimeField(null=True)
    next_run_at = DateTimeField(null=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

**APIs (to be built in Phase 5):**
- `GET /api/scheduled-reports`
- `POST /api/scheduled-reports`
- `PATCH /api/scheduled-reports/:id`
- `DELETE /api/scheduled-reports/:id`
- `POST /api/scheduled-reports/:id/run-now`

**Output:** 1 migration, model

---

## Phase 2: Dashboard Services (New Dashboards)

### Chunk 2.1 — Food Handler Dashboard

**Status:** Backend | **Depends on:** existing `DashboardService`

Add `DashboardService.food_handler_dashboard(user)`:

**KPI Cards:**
- certificate_status, certificate_expiry_date, days_to_expiry
- assessment_status, vaccination_status, renewal_status
- return_to_work_status (where applicable)

**Sections:**
- My certificate (type, number, issue date, expiry, status)
- My assessment (latest: status, facility, doctor, decision)
- My vaccination records (typhoid, hep A doses, next due)
- Renewal reminders (if expiring within 90 days)
- Illness/return-to-work status

**API:** `GET /api/dashboard/food-handler/`

**Output:** 1 new service method, 1 view class, URL registration

---

### Chunk 2.2 — Doctor Dashboard

**Status:** Backend | **Depends on:** existing appointment/assessment models

Add `DashboardService.doctor_dashboard(user, facility_id=None)`:

**KPI Cards:**
- assigned_assessments, declaration_reviews_pending, physical_exams_pending
- lab_results_pending_review, vaccination_reviews_pending
- decisions_pending, temporarily_not_fit_cases, return_to_work_reviews_pending

**Sections:**
- Pending queue (declaration review, physical exam, lab review, vaccination review, decision)
- Recent decisions table
- Workload summary (assessments by status)

**API:** `GET /api/dashboard/doctor/`

**Output:** 1 new service method, 1 view class, URL registration

---

### Chunk 2.3 — Lab Dashboard

**Status:** Backend | **Depends on:** existing lab_test models

Add `DashboardService.lab_dashboard(user, facility_id=None)`:

**KPI Cards:**
- lab_requests_pending, samples_pending_collection, results_pending_upload
- results_submitted_today, repeat_tests_required
- average_turnaround_time (hours)

**Sections:**
- Pending sample collection queue
- Pending result upload queue
- Recent lab results table
- Turnaround time chart

**API:** `GET /api/dashboard/lab/`

**Output:** 1 new service method, 1 view class, URL registration

---

### Chunk 2.4 — Inspector Dashboard (Enhance)

**Status:** Backend | **Depends on:** existing inspection models

Add `DashboardService.inspector_dashboard(user)`:

**KPI Cards:**
- assigned_inspections, due_today, overdue, in_progress, submitted
- notices_issued, corrective_actions_pending, follow_ups_due
- high_priority, closed_this_month

**Sections:**
- Task list (paginated, filterable by status/priority/type/date)
- Performance summary (closed vs open inspections)

**API:** `GET /api/dashboard/inspector/`

**Output:** 1 new service method, 1 view class, URL registration

---

### Chunk 2.5 — Enhance State & Federal Dashboards

**Status:** Backend | **Depends on:** existing `DashboardService.state_dashboard`, `DashboardService.federal_dashboard`

**State Dashboard Enhancements:**
- Add `vaccination_coverage_rate` card
- Add `state_compliance_percentage` card
- Add `return_to_work_pending` card
- Add `certificates_expiring_soon` card (30 days)
- Add LGA drill-down chart data
- Add `enforcement_notices_by_status` chart
- Add `illness_trends` chart (last 12 months)
- Add `assessment_volume_by_facility` chart
- Add `revenue_trend` chart (permission-based)
- State performance rating calculation

**Federal Dashboard Enhancements:**
- Add `states_with_active_implementation` card
- Add `states_with_overdue_reports` card
- Add `national_vaccination_coverage` card
- Add `national_inspection_count` card
- Add `national_illness_reports` card
- Add `national_return_to_work_pending` card
- Add state comparison table data
- Add `certification_coverage_by_state` chart
- Add `facility_accreditation_by_state` chart
- Add `vaccination_coverage_by_state` chart
- Add `state_report_submission_status` chart

**Output:** Enhanced service methods, updated views

---

### Chunk 2.6 — Admin/Platform Dashboard

**Status:** Backend | **Depends on:** existing models

Add `DashboardService.admin_dashboard(user)`:

**KPI Cards:**
- total_users, active_organizations, active_employers, active_facilities
- active_state_ministry_accounts, active_federal_users
- api_errors (recent), failed_payments, failed_certificate_generation
- failed_report_jobs, background_job_health, storage_usage

**API:** `GET /api/dashboard/admin/`

**Output:** 1 new service method, 1 view class, URL registration

---

## Phase 3: M&E Framework

### Chunk 3.1 — M&E Indicator Seed Data

**Status:** Backend | **Depends on:** 1.3

Seed all 10 indicator categories (PRD §18.2A-J) with minimum 5 indicators each:

- **A. Registration & Coverage** (5 indicators)
- **B. Certification** (8 indicators)
- **C. Medical Assessment** (7 indicators)
- **D. Vaccination** (5 indicators)
- **E. Facility** (6 indicators)
- **F. Employer Compliance** (6 indicators)
- **G. Inspection & Enforcement** (7 indicators)
- **H. Illness & Return-to-Work** (6 indicators)
- **I. Finance** (6 indicators, permission-based)
- **J. Data Quality** (5 indicators)

**Output:** `manage.py seed_me_indicators` — creates 60+ indicators with metadata

---

### Chunk 3.2 — M&E Calculation Service

**Status:** Backend | **Depends on:** 1.3, 3.1

`MEIndicatorService` with methods:

```python
calculate_indicator(indicator, state=None, lga=None, period_start=None, period_end=None)
calculate_all_indicators(state=None)  # runs all active indicators
calculate_category(category, state=None)
get_indicator_history(indicator_id, periods=12)  # last N values
get_state_performance(state_id)  # compliance + quality scorecard
get_national_summary()  # all states performance comparison
```

Formula parsing: Support basic arithmetic (`numerator / denominator * 100`), `SUM()`, `COUNT()`, `AVG()`.

**APIs:**
- `GET /api/m-and-e/indicators` — list active indicators
- `POST /api/m-and-e/indicators` — create (admin)
- `GET /api/m-and-e/indicators/:id` — detail
- `PATCH /api/m-and-e/indicators/:id` — update (admin)
- `GET /api/m-and-e/indicators/:id/values` — historical values
- `POST /api/m-and-e/calculate` — trigger calculation for indicator(s)
- `GET /api/m-and-e/dashboard` — national M&E dashboard
- `GET /api/m-and-e/state-performance` — state comparison
- `GET /api/m-and-e/national-summary` — federal summary

**Output:** Service class, serializer, viewset, URL registration

---

### Chunk 3.3 — State-to-Federal Report Submission Workflow

**Status:** Backend | **Depends on:** 1.1, existing generate

State user flow:
1. State user selects report type and period
2. Generates report (reuses `ReportService.generate`)
3. Reviews report preview
4. Submits to Federal (`POST /api/reports/:id/submit-to-federal`)
5. Report status → `submitted`

Federal user flow:
1. Views submitted state reports (`GET /api/federal/state-reports`)
2. Reviews report detail (`GET /api/federal/state-reports/:id`)
3. Accepts (`POST /api/federal/state-reports/:id/accept`)
4. Returns for correction (`POST /api/federal/state-reports/:id/return-for-correction`) with comment
5. Escalates overdue (`POST /api/federal/state-reports/:id/escalate`)

**New action endpoints:**
- `POST /api/reports/:id/submit-to-federal`
- `POST /api/reports/:id/archive`
- `POST /api/reports/:id/regenerate`
- `GET /api/federal/state-reports`
- `GET /api/federal/state-reports/:id`
- `POST /api/federal/state-reports/:id/accept`
- `POST /api/federal/state-reports/:id/return-for-correction`
- `POST /api/federal/state-reports/:id/escalate`

**Output:** Service methods, view actions, URL registration, status transitions

---

### Chunk 3.4 — M&E Calculation Job

**Status:** Backend (Celery Beat) | **Depends on:** 3.2

Celery periodic task that runs daily:

- Calculate daily indicators
- Calculate monthly indicators (on 1st of month)
- Store `MEIndicatorValue` snapshots
- Compare against thresholds (warning/critical)
- Generate alerts for threshold breaches
- Warm state performance cache

**Output:** Celery task, Celery Beat schedule entry

---

## Phase 4: Privacy & Analytics Layer

### Chunk 4.1 — Privacy-Safe Serializers

**Status:** Backend | **Depends on:** existing serializers

Create role-based report serializers:

```python
FoodHandlerReportSerializer       # own data only, no doctor internals
EmployerSafeComplianceSerializer  # no medical, no NIN, no lab
InspectorSafeReportSerializer     # no medical, no NIN, no finance
FacilityOperationalSerializer     # full facility data (assessments, labs)
StateRegulatoryReportSerializer   # state-wide, privacy-safe
FederalAggregateReportSerializer  # aggregate only, no PII
FinanceReportSerializer           # finance-only, no medical
MedicalRestrictedSerializer       # full clinical, audit logged
AdminReportSerializer             # system metrics only
```

Each serializer must filter out fields per PRD §31.1 (NIN, lab results, diagnosis, doctor notes, declaration answers, treatment notes, payment secrets, bank details).

**Output:** Serializer module with 9 role-safe serializers, tests verifying no medical data leaks

---

### Chunk 4.2 — ComplianceStatusService (Shared)

**Status:** Backend | **Depends on:** existing food_handler, employer, certificate, inspection, illness models

Central compliance status service per PRD §36.3:

```python
class ComplianceStatusService:
    get_food_handler_operational_status(food_handler_id) → dict
    get_branch_compliance_summary(branch_id) → dict
    get_employer_compliance_summary(employer_id) → dict
    get_state_compliance_summary(state_id) → dict
    get_national_compliance_summary() → dict
    get_overall_compliance_status(metrics) → str  # compliant|partially_compliant|non_compliant|high_risk
```

All dashboards must call this service rather than duplicating logic. Refactor existing `DashboardService` methods to use this.

**Output:** Service class, refactored dashboard service methods

---

### Chunk 4.3 — Analytics APIs

**Status:** Backend | **Depends on:** 4.2

Dedicated analytics endpoints for chart data (separate from dashboard cards):

```txt
GET /api/analytics/certificates    — issuance, expiry, status, verification by state/time
GET /api/analytics/assessments     — volume, decisions, turnaround by facility/state
GET /api/analytics/vaccinations    — coverage, compliance, due by state/LGA
GET /api/analytics/facilities      — accreditation, volume, renewal by state
GET /api/analytics/employers       — compliance, subscription, branch by state
GET /api/analytics/inspections     — counts, outcomes, findings by severity/state
GET /api/analytics/enforcement     — notices, corrective actions, cases by state
GET /api/analytics/illness         — trends, exclusions, return-to-work by state
GET /api/analytics/payments        — volume, revenue, failures (finance permission)
GET /api/analytics/settlements     — status, amounts, disputes (finance permission)
GET /api/analytics/data-quality    — issues by type, severity, status
```

Each endpoint supports query params: `state`, `lga`, `date_from`, `date_to`, `employer_category`, `facility_type`.

**Output:** Analytics service class, 11 view classes, URL registration

---

## Phase 5: Data Quality & Background Jobs

### Chunk 5.1 — Data Quality Scan Service & APIs

**Status:** Backend | **Depends on:** 1.5

`DataQualityService` scan checks (PRD §23.2):

- Scan for duplicate NINs
- Scan for duplicate certificates
- Scan for missing passport photos
- Scan for missing employer branch assignments
- Scan for missing vaccination records
- Scan for expired facility conducting assessments
- Scan for certificates generated without complete assessment
- Scan for assessments without payment (where required)
- Scan for lab result pending beyond threshold (48h)
- Scan for state validation pending beyond threshold (7 days)
- Scan for suspicious certificate verification patterns
- Scan for facilities with unusually high certificate volume
- Scan for employers with high expired certificate burden

**APIs (on model from Chunk 1.5):**
- `GET /api/data-quality/issues` — list, filterable by type/severity/status/module
- `GET /api/data-quality/issues/:id`
- `PATCH /api/data-quality/issues/:id` — update notes/severity
- `POST /api/data-quality/issues/:id/assign` — assign to user
- `POST /api/data-quality/issues/:id/resolve` — mark resolved
- `POST /api/data-quality/issues/:id/escalate` — escalate to higher role
- `GET /api/data-quality/dashboard` — summary cards + severity distribution chart

**Output:** Service class, serializer, viewset, URL registration

---

### Chunk 5.2 — Data Quality Scan Job

**Status:** Backend (Celery Beat) | **Depends on:** 5.1

Runs daily. Tasks:

- Run all 13 data quality scans
- Create/update `DataQualityIssue` records
- Auto-escalate critical issues
- Notify state admins of high-severity issues in their state
- Notify federal admins of critical cross-state issues
- Log scan completion metrics

**Output:** Celery task, Celery Beat schedule entry

---

### Chunk 5.3 — Scheduled Report Job

**Status:** Backend (Celery Beat) | **Depends on:** 1.6, 1.2

Runs on schedule. Tasks:

- Query active `ScheduledReport` records where `next_run_at <= now`
- Generate report using `ReportService.generate`
- Store file
- Deliver via configured channels (email, in-app notification, download link)
- Update `last_run_at`, calculate `next_run_at`
- Notify owner on failure
- Log generation and delivery

**Output:** Celery task, Celery Beat schedule entry

---

### Chunk 5.4 — Dashboard Aggregation Job

**Status:** Backend (Celery Beat) | **Depends on:** all dashboard services

Runs hourly/daily. Tasks:

- Precompute dashboard KPI card values for all dashboards
- Warm chart datasets (last 12 months)
- Cache state/federal comparison tables
- Refresh compliance summaries
- Update widget metric values
- Track aggregation run metrics (success/failure/latency)

Use Django cache framework (`REDIS_URL` for production, LocMemCache for dev).

**Output:** Celery task, Celery Beat schedule entry, cache integration

---

### Chunk 5.5 — State Report Reminder Job

**Status:** Backend (Celery Beat) | **Depends on:** 3.3

Runs daily. Tasks:

- Check upcoming report deadlines (7 days, 3 days, 1 day before)
- Notify state admins of upcoming deadlines
- Identify overdue state reports (past deadline, not submitted)
- Notify state admins of overdue reports
- Notify federal admins of states with overdue reports
- Auto-escalate if >14 days overdue

**Output:** Celery task, Celery Beat schedule entry

---

## Phase 6: Frontend

### Chunk 6.1 — Food Handler Dashboard Page

**Status:** Frontend | **Depends on:** 2.1 API

- Route: `/food-handler/dashboard`
- Components:
  - `FoodHandlerDashboardCards` — certificate, assessment, vaccination KPI cards
  - `MyCertificateCard` — certificate details, expiry countdown, download
  - `MyAssessmentTimeline` — latest assessment status stepper
  - `VaccinationRecordsTable` — typhoid & hep A records, next due dates
  - `RenewalReminderBanner` — if expiring within 90 days
  - `ReturnToWorkBanner` — if in excluded state with clearance pending
- Uses `react-query`, polling every 60s

---

### Chunk 6.2 — Doctor Dashboard & Workflow Pages

**Status:** Frontend | **Depends on:** 2.2 API

- Route: `/doctor/dashboard`
- Components:
  - `DoctorKPICards` — 8 metric cards
  - `PendingReviewQueue` — tabs: declaration, physical exam, lab results, vaccinations, decisions
  - `RecentDecisionsTable` — last 20 fitness decisions
  - `WorkloadBarChart` — assessments by status over time
- Uses `react-query`

---

### Chunk 6.3 — Lab Dashboard Page

**Status:** Frontend | **Depends on:** 2.3 API

- Route: `/lab/dashboard`
- Components:
  - `LabKPICards` — pending requests, samples, results, turnaround
  - `PendingSampleCollectionTable` — ordered by request date
  - `PendingResultUploadTable` — ordered by collection date
  - `TurnaroundTimeChart` — line chart, last 30 days
  - `RepeatTestsTable` — tests requiring repeats

---

### Chunk 6.4 — Inspector Dashboard Page

**Status:** Frontend | **Depends on:** 2.4 API

- Route: `/inspector/dashboard`
- Components:
  - `InspectorDashboardCards` — assigned, due, overdue, in-progress, submitted, notices, etc.
  - `InspectionTaskTable` — sortable, filterable (status, priority, type, date)
  - Row actions: Accept, Request Reschedule, Start, View

---

### Chunk 6.5 — Enhanced State & Federal Dashboards

**Status:** Frontend | **Depends on:** 2.5 API, 3.2 API, 4.3 API

**State Dashboard pages:**

| Route | Components |
|---|---|
| `/state/dashboard` | `StateDashboardCards`, Recharts (certification trend, compliance by LGA, facility accreditation, inspections, vaccination, illness), filter toolbar |
| `/state/reports` | `ReportBuilder` with template selector, period picker, format selector, generate button, submission workflow |
| `/state/reports/submissions` | Submission history table with status badges |
| `/state/m-and-e` | `MEIndicatorDashboard` — category tabs, indicator cards, trend charts |
| `/state/data-quality` | `DataQualityIssueTable` with severity badges, filter toolbar |
| `/state/analytics/certificates` | Certificate analytics deep-dive |
| `/state/analytics/employers` | Employer compliance analytics |
| `/state/analytics/facilities` | Facility performance analytics |
| `/state/analytics/inspections` | Inspection/enforcement analytics |

**Federal Dashboard pages:**

| Route | Components |
|---|---|
| `/federal/dashboard` | `FederalDashboardCards`, `NationalCertificationChart`, state comparison table, `StatePerformanceTable` |
| `/federal/reports` | `ReportBuilder` with federal templates |
| `/federal/state-reports` | `StateReportSubmissionTable` — all states, filter by status, `FederalReportReviewPanel` for accept/return |
| `/federal/m-and-e` | `NationalMEOverview` — all indicator categories, disaggregation by state |
| `/federal/state-performance` | `StatePerformanceComparisonTable` — sortable by all metrics |
| `/federal/data-quality` | National data quality dashboard |
| `/federal/analytics/*` | Deep-dive analytics pages (certificates, facilities, employers, enforcement) |

---

### Chunk 6.6 — Report Builder & Shared Components

**Status:** Frontend | **Depends on:** 1.2, existing report endpoints

Shared components across all dashboards:

| Component | Purpose |
|---|---|
| `DashboardLayout` | Common layout with sidebar, header, filter bar |
| `DashboardFilterBar` | Date range, state, LGA, employer, facility dropdowns |
| `DateRangePicker` | Start/end date selector |
| `KPICard` | Singular metric card (label, value, trend arrow, icon) |
| `TrendCard` | Metric + sparkline trend |
| `ChartCard` | Chart with title, description, export button |
| `DataTableCard` | Sortable, filterable data table |
| `DrillDownBreadcrumb` | Navigation breadcrumb trail |
| `ExportButton` | Dropdown: PDF, Excel, CSV |
| `ReportBuilder` | Template selector → filters → preview → generate |
| `ReportTemplateSelector` | Grid of report template cards |
| `ReportPreview` | Generated report data preview |
| `ReportStatusBadge` | Color-coded badge (draft, generated, submitted, accepted, returned) |
| `ScheduledReportForm` | Schedule config form |
| `MEIndicatorCard` | Single indicator KPI with target threshold gauge |
| `StatePerformanceTable` | Sortable state comparison matrix |
| `ComplianceSummaryCard` | Compliance percentage gauge + breakdown |
| `DataQualityIssueTable` | Issues list with severity badges |
| `DataQualitySeverityBadge` | Color-coded (low=blue, medium=yellow, high=orange, critical=red) |
| `StateReportSubmissionTable` | State reports with status, date, action buttons |
| `FederalReportReviewPanel` | Accept/return modal with comment field |
| `PrivacyWarningBanner` | Role-safe privacy notice where applicable |

**Output:** 25 shared components in `frontend/src/components/reports/` and `frontend/src/components/dashboards/`

---

### Chunk 6.7 — Admin Dashboard Pages

**Status:** Frontend | **Depends on:** 2.6 API

| Route | Components |
|---|---|
| `/admin/dashboards` | `AdminKPICards` (users, orgs, errors, jobs), system health widgets |
| `/admin/report-templates` | CRUD table for report templates |
| `/admin/m-and-e/indicators` | `MEIndicatorManagementTable` — CRUD, activate/deactivate |
| `/admin/data-quality` | Admin data quality overview, reassign issues |
| `/admin/system-reports` | Failed jobs, errors, audit log summary |

---

## Phase 7: Permissions, Tests & Polish

### Chunk 7.1 — Permissions & Access Control

**Status:** Backend | **Depends on:** all backend chunks

Define Django permissions:

```txt
report.view / report.generate / report.export / report.schedule
report.submit_to_federal / report.review_state_report
report.manage_templates
dashboard.view_food_handler / dashboard.view_employer / dashboard.view_facility
dashboard.view_state / dashboard.view_federal / dashboard.view_admin
m_and_e.view / m_and_e.manage_indicators / m_and_e.calculate / m_and_e.export
data_quality.view / data_quality.assign / data_quality.resolve / data_quality.escalate
```

Assign to roles per PRD §30.2:

- **Food Handler:** dashboard.view_food_handler
- **Employer:** dashboard.view_employer, report.view, report.generate, report.export, report.schedule
- **Branch Manager:** same as employer, scoped to branch
- **Facility Admin:** dashboard.view_facility, report.view, report.generate, report.export
- **Doctor:** dashboard.view_facility (scoped to own workload)
- **Lab Staff:** dashboard.view_facility (scoped to lab unit)
- **Inspector:** dashboard.view_employer, dashboard.view_state
- **State Admin:** dashboard.view_state, all report.*, m_and_e.view, m_and_e.export, data_quality.*
- **Federal Admin:** dashboard.view_federal, all report.*, m_and_e.*, data_quality.*
- **Super Admin:** all permissions

**Output:** Permission definitions, role assignments (migration or management command), permission checks in all views

---

### Chunk 7.2 — Audit Log Integration

**Status:** Backend | **Depends on:** all backend chunks

Add audit log entries using existing shared format (PRD §36.4) for all events in §32:

```txt
dashboard_viewed              (state, federal, admin dashboards)
report_generated              (all report types)
report_exported               (PDF, Excel, CSV)
report_downloaded             (file download)
scheduled_report_created      (schedule create/update/delete)
state_report_submitted        (submission to federal)
federal_report_accepted       (accept by federal)
federal_report_returned       (return for correction)
me_indicator_created          (indicator management)
me_indicator_updated
data_quality_issue_assigned   (assignment actions)
data_quality_issue_resolved
data_quality_issue_escalated
sensitive_report_accessed     (medical reports)
finance_report_exported       (finance reports)
medical_report_exported
report_generation_failed      (failure events)
```

**Output:** Audit log entries in all service method calls

---

### Chunk 7.3 — Backend Tests

**Status:** Backend | **Depends on:** all backend chunks

Test categories:

1. **Model tests:** validation, constraints, unique codes for indicators/templates
2. **Dashboard API tests:** all 8 dashboards return correct shape and data
3. **Analytics API tests:** all 11 analytics endpoints, filter combinations
4. **M&E API tests:** CRUD indicators, calculate, historical values, state performance
5. **Report workflow tests:** generate, submit, accept, return for correction
6. **Scheduled report tests:** create, update, delete, run-now
7. **Data quality tests:** scan, create issues, assign, resolve, escalate
8. **Privacy tests:** verify NO medical data in employer/inspector/federal responses
9. **Permission tests:** verify role scoping (food handler can't see other handlers, employer can't see facility data, etc.)
10. **Export tests:** CSV/PDF/Excel generation, privacy-safe content

**Output:** Comprehensive test suite in `apps/reports/tests.py`

---

### Chunk 7.4 — Frontend Tests & Type Safety

**Status:** Frontend | **Depends on:** all frontend chunks

- TypeScript type definitions for: dashboard responses, M&E indicators, analytics responses, report templates, data quality issues, scheduled reports, state performance
- API client functions in: `frontend/src/lib/api/reports.ts`, `frontend/src/lib/api/analytics.ts`, `frontend/src/lib/api/me.ts`, `frontend/src/lib/api/data-quality.ts`
- Component unit tests for: `KPICard`, `ChartCard`, `ReportBuilder`, `MEIndicatorCard`, `DataQualityIssueTable`
- Page-level integration tests for: food_handler dashboard, doctor dashboard, state dashboard, federal dashboard

**Output:** Type definitions, API client modules, tests

---

## Summary

| Phase | Chunks | Description |
|---|---|---|
| 1. Enhanced Models | 6 | GeneratedReport ext, ReportTemplate, MEIndicator, DashboardWidget, DataQualityIssue, ScheduledReport |
| 2. Dashboard Services | 6 | Food Handler, Doctor, Lab, Inspector, Enhanced State/Federal, Admin dashboards |
| 3. M&E Framework | 4 | Indicator seeds, Calculation service, State→Federal workflow, Calculation job |
| 4. Privacy & Analytics | 3 | Privacy-safe serializers, ComplianceStatusService, Analytics APIs |
| 5. Data Quality & Jobs | 5 | DQ scan service/APIs, DQ scan job, Scheduled report job, Aggregation job, Reminder job |
| 6. Frontend | 7 | Food Handler, Doctor, Lab, Inspector, State/Federal, Shared components, Admin pages |
| 7. Polish | 4 | Permissions, Audit logs, Backend tests, Frontend tests/typings |

**Total: 35 chunks, 7 phases**

### Execution Order

```
Phase 1 (models) → Phase 2 (dashboards) + Phase 3 (M&E) in parallel
→ Phase 4 (privacy/analytics) → Phase 5 (jobs) + Phase 6 (frontend) in parallel
→ Phase 7 (polish)

Within each phase, chunks marked "Depends on: nothing" can run in parallel.
```
