# State and Federal Ministry Modules - Implementation Plan

## Audit Summary

| Component | Status |
|-----------|--------|
| State/Federal PRD | Done |
| State and federal route shells | Done - state/federal `PortalPage` placeholders removed or replaced with real workflow screens |
| State dashboard service | Done - operational filters, queue metrics, and real dashboard UI added |
| Federal dashboard service | Done - national KPI dashboard and state performance comparison UI added |
| State organization units | Done - state unit CRUD UI, state-scoped backend endpoints, and invite linkage added |
| State invites | Done - state-scoped invite endpoint and ministry sub-role support added |
| Facility accreditation | Done - state registry, accreditation queue, and state review actions added |
| State assessment fees | Done - state fee endpoints, split validation, overlap checks, and finance UI added |
| Certificate validation | Done - state validation queue, approve-and-issue, reject, and clarification workflow added |
| State certificate registry | Done - state registry, filters, suspend, and revoke workflow added |
| Employer and food handler monitoring | Done - state-scoped employer and food handler monitoring endpoints, pages, filters, and safe CSV exports added |
| Inspections and enforcement | Done - state assignment, review, close, enforcement tracking, audit history, and supervision UI added |
| Illness and return-to-work monitoring | Done - privacy-safe illness and return-to-work monitoring endpoint, page, active filters, and safe CSV export added |
| State reports and federal submission | Done - `StateReport` generation, snapshot preservation, submission workflow, and state reports UI added |
| State revenue and settlement oversight | Done - state-scoped revenue snapshot, settlement list, split cards, filters, and CSV export added |
| Federal state performance monitoring | Done - all-state/FCT aggregate performance endpoint, summary endpoint, dashboards, and drill-down added |
| Federal national registry oversight | Done - privacy-safe certificate, facility, employer, and food handler summary endpoints/UI added |
| Federal policy configuration | Done - national policy defaults, state override monitoring, audit logging, and federal UI added |
| Federal M&E, data quality, audit oversight | Done - indicators, data-quality risk, and privacy-safe audit summary endpoints/pages added |
| Federal state queries/escalations | Done - `FederalStateQuery` model, lifecycle endpoints, audit events, and federal query UI added |
| Ministry-specific backend namespace | Done - `backend/apps/ministries` created with state/federal dashboard aliases |
| Backend tests for ministry workflows | Done - SF14 final affected-app regression suite passing |
| Frontend typecheck/lint/build coverage | Partial - SF0/SF3 typecheck and lint passed; SF4/SF14 frontend checks attempted but local Node tooling stalled |

### Product Direction

The implementation should reuse existing FoodCert NG domain apps wherever possible:

- `reports` for dashboard aggregations and report snapshots
- `facilities` for accreditation status and facility performance
- `certificates` for validation, issuance, registry, suspension, and revocation
- `payments`, `settlements`, and `policy` for fees, revenue, and policy settings
- `organizations` and `accounts` for ministry units, users, invites, and scoping
- `inspections`, `illness`, `employers`, and `food_handlers` for operational monitoring
- `audit` and `notifications` for traceability and workflow communications

Add a small `backend/apps/ministries` app only for cross-domain ministry workflows that do not belong cleanly inside one existing domain app.

---

## Build Order

```
SF0 -> SF1 -> SF2 -> SF3 -> SF4
 │      │      │      │      │
 ▼      ▼      ▼      ▼      ▼
Audit  Roles  Units  State  Facility
Base   Scope  Users  Dash   Accred

SF5 -> SF6 -> SF7 -> SF8 -> SF9 -> SF10
 │      │      │      │      │      │
 ▼      ▼      ▼      ▼      ▼      ▼
Fees   Cert   Cert   Employer Inspect State
       Queue  Reg    Monitor Enforce Reports

SF11 -> SF12 -> SF13 -> SF14
 │       │       │       │
 ▼       ▼       ▼       ▼
Fed     Policy  M&E     Final
Dash    +Reg    Audit   QA
```

Each chunk must leave the app in a working, testable state. Backend tests and frontend checks should pass before moving to the next chunk.

---

## Chunk SF0: Baseline Audit and Ministry Namespace

**Status: Done**

Implemented:

- Created `backend/apps/ministries`.
- Registered `apps.ministries` in backend settings.
- Registered ministry URLs under `/api/state/...` and `/api/federal/...`.
- Added `/api/state/dashboard/` and `/api/federal/dashboard/` aliases over existing report dashboard services.
- Added state/federal ministry permission classes.
- Added frontend API clients in `frontend/src/lib/api/state.ts` and `frontend/src/lib/api/federal.ts`.
- Added backend tests for namespace access control and dashboard alias payloads.

Verification:

- `./.venv/bin/python manage.py test apps.ministries` - passed
- `npm run typecheck` from `frontend/` - passed
- `npm run lint` from `frontend/` - passed

### Goal
Create the ministry implementation foundation without changing domain behavior.

### Backend
- Create `backend/apps/ministries/` with standard Django app structure:
  - `apps.py`
  - `models.py`
  - `serializers.py`
  - `permissions.py`
  - `services.py`
  - `views.py`
  - `urls.py`
  - `tests.py`
- Register the app in backend settings.
- Register ministry URLs under `/api/state/` and `/api/federal/`.
- Add lightweight health/list endpoints only if needed to prove routing is wired.
- Do not duplicate existing domain APIs; add aliases or orchestration endpoints that call existing services.

### Frontend
- Add shared ministry API client modules:
  - `frontend/src/lib/api/state.ts`
  - `frontend/src/lib/api/federal.ts`
- Add shared ministry route/type definitions where the existing pattern expects them.

### Files
| Backend | Frontend |
|---------|----------|
| `backend/apps/ministries/*` (new) | `frontend/src/lib/api/state.ts` (new) |
| `backend/config/settings.py` or app registry | `frontend/src/lib/api/federal.ts` (new) |
| root/backend API URL config | |

### Acceptance Criteria
- `/api/state/...` and `/api/federal/...` routing is available.
- No existing state/federal dashboard behavior regresses.
- Ministry namespace tests prove state/federal role permissions are enforced.

### Verification
- `./.venv/bin/python manage.py test apps.ministries`
- `npm run typecheck`
- `npm run lint`

---

## Chunk SF1: Ministry Roles, Permissions, and Data Scoping

**Status: Done**

Implemented:

- Added `MinistryStaffProfile` with ministry type, ministry sub-role, state, LGA, unit, creator, and active status.
- Added state ministry sub-roles for super admin, food safety, certificate verification, facility accreditation, policy/finance, inspectorate coordination, and LGA office users.
- Added federal ministry sub-roles for federal super admin, national food safety, M&E, policy, finance/oversight, and executive viewer users.
- Added ministry permission helpers:
  - `can_manage_state_users`
  - `can_review_facility_accreditation`
  - `can_validate_certificates`
  - `can_manage_state_fees`
  - `can_assign_inspections`
  - `can_submit_state_reports`
  - `can_view_federal_aggregate_data`
  - `can_manage_national_policy`
  - `can_review_state_reports`
  - `can_manage_federal_queries`
- Preserved legacy behavior: existing `state_admin` and `federal_admin` users without a ministry profile retain full ministry permissions.
- Added frontend ministry profile/sub-role types and labels.
- Added migration `backend/apps/ministries/migrations/0001_initial.py`.

Verification:

- `./.venv/bin/python manage.py test apps.ministries` - passed
- `npm run typecheck` from `frontend/` - passed
- `npm run lint` from `frontend/` - passed

### Goal
Define permission helpers for state and federal ministry users without creating unnecessary top-level roles.

### Backend
- Keep top-level roles:
  - `state_admin`
  - `federal_admin`
  - `inspector`
- Add ministry sub-role support using the lightest compatible approach:
  - preferred: `MinistryStaffProfile` model in `apps.ministries`
  - acceptable fallback: permission helper methods if the current account model already has enough fields
- State sub-role defaults:
  - super admin
  - food safety officer
  - certificate verification officer
  - facility accreditation officer
  - policy and finance officer
  - inspectorate coordinator
  - LGA officer
- Federal sub-role defaults:
  - super admin
  - national food safety programme officer
  - national M&E officer
  - national policy officer
  - national finance/oversight officer
  - executive viewer
- Add helpers:
  - `can_manage_state_users`
  - `can_review_facility_accreditation`
  - `can_validate_certificates`
  - `can_manage_state_fees`
  - `can_assign_inspections`
  - `can_submit_state_reports`
  - `can_view_federal_aggregate_data`
  - `can_manage_national_policy`
  - `can_review_state_reports`
  - `can_manage_federal_queries`
- Enforce state scoping:
  - state users only see records for `user.state`
  - LGA-scoped users only see assigned LGA where supported
  - federal users see national aggregates by default

### Frontend
- Add role/sub-role display helpers.
- Add route guard metadata for state/federal pages.
- Hide actions when the current user lacks the matching ministry permission.

### Files
| Backend | Frontend |
|---------|----------|
| `ministries/models.py` | `frontend/src/lib/permissions/roles.ts` |
| `ministries/permissions.py` | `frontend/src/lib/navigation/portal-nav.ts` |
| `ministries/serializers.py` | shared state/federal page components as needed |
| `accounts/models.py` only if required | |

### Acceptance Criteria
- A Lagos state user cannot access Oyo state ministry records.
- Federal viewers cannot perform write actions.
- Permission helpers are covered by unit tests.

### Verification
- `./.venv/bin/python manage.py test apps.ministries apps.accounts`
- `npm run typecheck`
- `npm run lint`

---

## Chunk SF2: State Organization Units, Users, and Invites

**Status: Done**

Implemented:

- Added state-scoped ministry endpoints:
  - `GET/POST /api/state/units/`
  - `GET/PATCH/DELETE /api/state/units/:id/`
  - `GET /api/state/users/`
  - `GET/POST /api/state/invites/`
  - `GET/DELETE /api/state/invites/:id/`
- Added state ministry organization resolution so state users do not need to decode or provide an organization id.
- Added `UserInvite.ministry_staff_role` and migration `backend/apps/accounts/migrations/0006_userinvite_ministry_staff_role.py`.
- Updated invite acceptance to create/update `MinistryStaffProfile` when a ministry staff role is attached to the invite.
- Replaced the State Users placeholder with a real ministry users table.
- Replaced the State Invites page with a state ministry invite workflow including ministry sub-role selection.
- Updated State Units to use `/api/state/units/` directly.
- Added frontend state API helpers for units, users, and invites.

Verification:

- `./.venv/bin/python manage.py test apps.ministries apps.accounts apps.organizations` - passed
- `npm run typecheck` from `frontend/` - passed
- `npm run lint` from `frontend/` - passed

### Goal
Make state ministry unit and user management production-ready for directorates, desks, inspectorates, and LGA offices.

### Backend
- Reuse `organizations` and `accounts` foundations.
- Add `/api/state/units` alias endpoints where the PRD expects them.
- Add `/api/state/users` and `/api/state/invites` ministry-scoped endpoints.
- Ensure invite creation supports:
  - ministry sub-role
  - unit assignment
  - LGA/state scope
  - inspector designation where applicable
- Add audit logs for invite creation, cancellation, acceptance, and role changes.

### Frontend
- Polish:
  - `frontend/src/app/state/units/page.tsx`
  - `frontend/src/app/state/units/[id]/page.tsx`
  - `frontend/src/app/state/users/page.tsx`
  - `frontend/src/app/state/invites/page.tsx`
- Replace placeholder user page with a real table:
  - name, email, phone, sub-role, unit, scope, status, last active
  - actions: invite, resend invite, deactivate, change unit, change sub-role
- Use real loading, empty, error, and unauthorized states.

### Files
| Backend | Frontend |
|---------|----------|
| `ministries/views.py` | `state/units/page.tsx` |
| `ministries/serializers.py` | `state/units/[id]/page.tsx` |
| `organizations/views.py` if alias support is needed | `state/users/page.tsx` |
| `accounts/views.py` if invite support is needed | `state/invites/page.tsx` |

### Acceptance Criteria
- State admins can manage only users and units in their state.
- Invited staff receive the correct role, unit, and state scope.
- Federal admins cannot accidentally create state users outside explicit federal workflows.

### Verification
- `./.venv/bin/python manage.py test apps.ministries apps.organizations apps.accounts`
- `npm run typecheck`
- `npm run lint`

---

## Chunk SF3: State Dashboard and Operational Filters

**Status: Done**

Implemented:

- Extended dashboard query filters with:
  - `date_from`
  - `date_to`
  - `employer_category`
  - `certificate_status`
  - existing `state` and `lga`
- Enhanced `DashboardService.state_dashboard` with:
  - pending facility applications
  - pending certificate validations
  - active illness exclusions
  - enforcement notices
  - state revenue collected
  - certificate status breakdown
  - facility accreditation status breakdown
  - operational queue sections
  - recent pending certificate requests
  - recent pending facility applications
- Updated `/api/state/dashboard/` and legacy `/api/dashboard/state/` to support the same filter payload.
- Replaced the State Dashboard placeholder with a real operational dashboard.
- Added filter controls for LGA, date range, employer category, and certificate status.
- Added KPI cards, operational queue links, pending certificate request table, and pending facility application table.

Verification:

- `./.venv/bin/python manage.py test apps.reports apps.ministries` - passed
- `npm run typecheck` from `frontend/` - passed
- `npm run lint` from `frontend/` - passed

### Goal
Turn the state dashboard into a useful ministry command center.

### Backend
- Add `/api/state/dashboard` as a PRD-aligned alias over `DashboardService.state_dashboard`.
- Support filters:
  - state
  - LGA
  - date range
  - facility
  - employer category
  - certificate status
- Add summary sections:
  - registered food handlers
  - certified food handlers
  - expired certificates
  - approved facilities
  - pending facility applications
  - pending certificate validations
  - active illness exclusions
  - inspections completed
  - enforcement notices
  - revenue collected
- Ensure dashboard payload never exposes lab results, doctor notes, or raw medical details.

### Frontend
- Replace `frontend/src/app/state/dashboard/page.tsx` shell with a real dashboard.
- Add KPI cards, charts, date/LGA filters, and operational queues.
- Link dashboard cards to the relevant state pages.
- Use the existing design system and avoid decorative marketing layouts.

### Files
| Backend | Frontend |
|---------|----------|
| `ministries/views.py` | `state/dashboard/page.tsx` |
| `reports/services.py` | `features/dashboard/dashboard-client.tsx` if shared dashboard support is better |
| `reports/tests.py` | `frontend/src/lib/api/state.ts` |

### Acceptance Criteria
- State dashboard is scoped to the current user's state.
- LGA filters affect all cards and charts.
- Clicking queue cards lands on filtered operational pages.

### Verification
- `./.venv/bin/python manage.py test apps.reports apps.ministries`
- `npm run typecheck`
- `npm run lint`

---

## Chunk SF4: Facility Accreditation Workflow

**Status: Done**

Implemented:

- Added state ministry facility endpoints:
  - `GET /api/state/facilities/`
  - `GET /api/state/facilities/applications/`
  - `PATCH /api/state/facilities/applications/:id/approve/`
  - `PATCH /api/state/facilities/applications/:id/reject/`
  - `PATCH /api/state/facilities/applications/:id/suspend/`
  - `PATCH /api/state/facilities/applications/:id/reinstate/`
  - facility-level action aliases for approve, reject, suspend, and reinstate
- Reused `FacilityAccreditationService` for auditable state transitions.
- Enforced state scoping for facility registry and accreditation applications.
- Enforced accreditation sub-role checks through `can_review_facility_accreditation`.
- Required review comments for reject and suspend actions.
- Replaced the State Facilities placeholder with a real state facility registry.
- Replaced the State Facility Accreditation placeholder with a real queue and action workflow.
- Added frontend state API helpers for facility registry, accreditation list, and review actions.
- Added backend tests for state-scoped facility listing, accreditation queue scoping, approval, required review comments, sub-role permissions, and cross-state blocking.

Verification:

- `./.venv/bin/python manage.py test apps.facilities apps.ministries` - passed
- `./.venv/bin/python manage.py check` - passed
- `npm run typecheck` / `npm run lint` from `frontend/` - attempted; local Node tooling stalled/ETIMEDOUT during startup and did not return diagnostics

### Goal
State ministry users can review, approve, reject, suspend, and reinstate medical facilities.

### Backend
- Add `/api/state/facilities` and `/api/state/facilities/applications`.
- Add state actions:
  - approve
  - reject with reason
  - request clarification
  - suspend with reason
  - reinstate
- Reuse existing facility models and services.
- Ensure only same-state applications appear to state users.
- Add review checklist fields if not already present:
  - license verification
  - medical director verification
  - lab capacity
  - doctor availability
  - location coverage
  - accreditation evidence
- Audit every accreditation action.

### Frontend
- Replace:
  - `state/facilities/page.tsx`
  - `state/facilities/accreditation/page.tsx`
- Build queue/table views:
  - submitted applications
  - approved facilities
  - suspended facilities
  - renewal/re-accreditation due
- Add detail drawer or page with review checklist and action controls.

### Files
| Backend | Frontend |
|---------|----------|
| `ministries/views.py` | `state/facilities/page.tsx` |
| `facilities/services.py` | `state/facilities/accreditation/page.tsx` |
| `facilities/views.py` | shared ministry table/detail components as needed |
| `facilities/tests.py` | |

### Acceptance Criteria
- State officers cannot review facilities outside their state.
- Rejection, suspension, and reinstatement require reasons.
- Facilities see updated accreditation status after state action.

### Verification
- `./.venv/bin/python manage.py test apps.facilities apps.ministries`
- `npm run typecheck`
- `npm run lint`

---

## Chunk SF5: State Fee Configuration and Finance Controls

**Status: Done**

Implemented:

- Added state ministry assessment fee endpoints:
  - `GET /api/state/fees/`
  - `POST /api/state/fees/`
  - `PATCH /api/state/fees/:id/`
- Reused the existing `AssessmentFee` model and serializer.
- State fee create/update automatically scopes to the authenticated user's state.
- Added server-side split validation:
  - `state_fee + facility_fee + platform_fee == amount`
- Added active fee overlap protection for the same state and facility type.
- Enforced state finance permissions with `can_manage_state_fees`.
- Added backend tests for:
  - state-scoped creation
  - split validation
  - overlapping active fee rejection
  - state-scoped listing
  - non-finance sub-role blocking
- Replaced `state/fees/page.tsx` placeholder with a real fee configuration table and create/edit modal.
- Added frontend state API helpers for fee listing, creation, and update.

Verification:

- `./.venv/bin/python manage.py test apps.payments apps.ministries` - passed
- `./.venv/bin/python manage.py check` - passed
- `npm run typecheck` / `npm run lint` from `frontend/` - attempted; local Node tooling stalled during startup and did not return diagnostics

### Goal
State policy/finance users can configure assessment fees and monitor active fee rules.

### Backend
- Add `/api/state/fees`.
- Reuse `payments.AssessmentFee` or the existing fee model.
- Support:
  - create draft fee
  - approve fee
  - activate fee by effective date
  - retire fee
  - list fee history
- Enforce server-side fee split validation:
  - gross amount equals facility + state + platform amounts
  - currency defaults to NGN
  - active fee periods cannot overlap for same state/facility type
- Audit fee changes.

### Frontend
- Replace `state/fees/page.tsx` with:
  - active fee cards
  - fee configuration form
  - facility type selector
  - split preview
  - approval/history table
  - immutable active fee warning

### Files
| Backend | Frontend |
|---------|----------|
| `ministries/views.py` | `state/fees/page.tsx` |
| `payments/models.py` if model gaps exist | `frontend/src/lib/api/state.ts` |
| `payments/services.py` | |
| `payments/tests.py` | |

### Acceptance Criteria
- State users can only configure fees for their state.
- Invalid splits are rejected by the backend.
- Active fee history remains auditable.

### Verification
- `./.venv/bin/python manage.py test apps.payments apps.ministries`
- `npm run typecheck`
- `npm run lint`

---

## Chunk SF6: Certificate Validation and Issuance Approval

**Status: Done**

Implemented:

- Added state certificate validation endpoints:
  - `GET /api/state/certificate-validation-queue/`
  - `GET /api/state/certificate-validation-queue/:id/`
  - `PATCH /api/state/certificate-validation-queue/:id/approve/`
  - `PATCH /api/state/certificate-validation-queue/:id/reject/`
  - `PATCH /api/state/certificate-validation-queue/:id/request-clarification/`
- Added state-scoped validation queue serializer with privacy-safe eligibility signals.
- Approval now validates eligibility, approves the request, and issues the certificate through `CertificateService.issue_certificate`.
- Rejection requires review notes.
- Clarification sets request status to `correction_requested` and records reviewer, notes, and audit event.
- Enforced certificate verification permissions with `can_validate_certificates`.
- Replaced the State Certificate Requests placeholder with a real validation queue UI.
- Added frontend state API helpers for validation queue and actions.
- Added backend tests for state scoping, cross-state blocking, approve-and-issue, rejection note requirements, clarification, and sub-role blocking.

Verification:

- `./.venv/bin/python manage.py test apps.certificates apps.ministries` - passed
- `./.venv/bin/python manage.py check` - passed
- `npm run typecheck` / `npm run lint` from `frontend/` - attempted; local Node tooling stalled during startup and did not return diagnostics

### Goal
State certificate verification officers can validate facility-submitted fit assessments before certificate issuance.

### Backend
- Add `/api/state/certificate-validation-queue`.
- Add detail endpoint and actions:
  - approve
  - reject with reason
  - request clarification
- Reuse certificate request and certificate issuance services.
- Validation checklist must confirm:
  - assessment complete
  - doctor decision present
  - required lab results complete
  - vaccination requirements complete or clinically cleared
  - payment confirmed
  - facility is approved in issuing state
  - food handler identity is verified where policy requires it
- Do not expose sensitive lab values beyond what the officer needs for eligibility validation.
- Audit all decisions.

### Frontend
- Replace `state/certificate-requests/page.tsx`.
- Add validation queue:
  - pending
  - clarification requested
  - approved
  - rejected
- Add detail review panel with eligibility checklist and action controls.
- Add filters by facility, date, category, and queue status.

### Files
| Backend | Frontend |
|---------|----------|
| `ministries/views.py` | `state/certificate-requests/page.tsx` |
| `certificates/services.py` | ministry certificate validation components |
| `certificates/views.py` | `frontend/src/lib/api/state.ts` |
| `certificates/tests.py` | |

### Acceptance Criteria
- Approved requests issue certificates using existing certificate service.
- Rejected requests preserve reason and audit trail.
- State users cannot validate requests outside their state.

### Verification
- `./.venv/bin/python manage.py test apps.certificates apps.ministries`
- `npm run typecheck`
- `npm run lint`

---

## Chunk SF7: State Certificate Registry and Lifecycle Actions

**Status: Done**

Implemented:

- Added state certificate registry endpoints:
  - `GET /api/state/certificates/`
  - `GET /api/state/certificates/:id/`
  - `PATCH /api/state/certificates/:id/suspend/`
  - `PATCH /api/state/certificates/:id/revoke/`
- Added state-scoped certificate registry serializer with privacy-safe certificate fields.
- Added registry filters:
  - search by certificate number, food handler, employer, or facility
  - status
  - facility
  - employer
  - expiry window
- Enforced state scoping for registry detail and lifecycle actions.
- Required reasons for suspend and revoke.
- Reused `CertificateService.suspend` and `CertificateService.revoke` for audited lifecycle transitions.
- Replaced the State Certificates placeholder with a real certificate registry table.
- Added frontend state API helpers for certificate registry, suspend, and revoke.
- Added backend tests for state scoping, cross-state blocking, search, required lifecycle reasons, suspend, and revoke.

Verification:

- `./.venv/bin/python manage.py test apps.certificates apps.ministries` - passed
- `./.venv/bin/python manage.py check` - passed
- `npm run typecheck` / `npm run lint` from `frontend/` - attempted; local Node tooling stalled during startup and did not return diagnostics

### Goal
State ministry users can search issued certificates and perform authorized lifecycle actions.

### Backend
- Add `/api/state/certificates`.
- Support filters:
  - certificate number
  - food handler name/ID
  - employer
  - facility
  - status
  - expiry window
  - LGA
- Add actions:
  - suspend with reason
  - revoke with reason
  - reinstate if policy allows
  - replace/reissue where existing certificate service supports it
- Return privacy-safe registry data by default.
- Audit every lifecycle action.

### Frontend
- Replace `state/certificates/page.tsx`.
- Add registry table:
  - certificate number
  - food handler
  - employer/category
  - facility
  - issue/expiry dates
  - status
  - actions
- Add lifecycle action modal with required reason and confirmation.

### Files
| Backend | Frontend |
|---------|----------|
| `ministries/views.py` | `state/certificates/page.tsx` |
| `certificates/views.py` | `frontend/src/lib/api/state.ts` |
| `certificates/services.py` | shared certificate status badge if needed |
| `certificates/tests.py` | |

### Acceptance Criteria
- Registry results are state-scoped.
- Suspension/revocation changes public verification status.
- Action reasons are stored and auditable.

### Verification
- `./.venv/bin/python manage.py test apps.certificates apps.ministries`
- `npm run typecheck`
- `npm run lint`

---

## Chunk SF8: Employer, Food Handler, Illness, and Return-to-Work Monitoring

**Status: Done**

Implemented state-scoped monitoring APIs for employers, food handlers, and illness reports under `/api/state/...`, using privacy-safe serializers that omit NIN, date of birth, raw symptoms, clinical notes, and raw lab/medical details. Replaced the employer and food handler state pages, added the illness reports page, and added CSV export buttons that use only the already-filtered safe monitoring rows.

Verification:
- Passed: `./.venv/bin/python manage.py test apps.ministries apps.employers apps.food_handlers apps.illness` (81 tests)
- Passed: `./.venv/bin/python manage.py check`
- Attempted: `npm run typecheck` stalled silently and was stopped
- Attempted: `npm run lint` stalled silently and was stopped

### Goal
State ministry users can monitor compliance without exposing unnecessary medical details.

### Backend
- Add endpoints:
  - `/api/state/employers`
  - `/api/state/food-handlers`
  - `/api/state/illness-reports`
- Support filters by LGA, employer category, compliance status, certificate status, illness status, and expiry window.
- Add summary metrics:
  - registered employers
  - registered food handlers
  - certified handlers
  - expired/expiring certificates
  - active illness exclusions
  - return-to-work pending
- Enforce privacy rules:
  - no raw lab results
  - no doctor notes unless explicitly required and permissioned
  - illness views show fitness/work restriction status, not unnecessary diagnosis detail

### Frontend
- Replace:
  - `state/employers/page.tsx`
  - `state/food-handlers/page.tsx`
- Add `state/illness-reports/page.tsx` if missing.
- Build monitoring tables with filters, status badges, and safe exports.
- Link employer rows to compliance summaries rather than employer-private operational data.

### Files
| Backend | Frontend |
|---------|----------|
| `ministries/views.py` | `state/employers/page.tsx` |
| `employers/views.py` | `state/food-handlers/page.tsx` |
| `food_handlers/views.py` | `state/illness-reports/page.tsx` (new if missing) |
| `illness/views.py` | |

### Acceptance Criteria
- State monitoring pages never expose prohibited clinical details.
- LGA-scoped users see only assigned local records.
- CSV exports use the same privacy-safe serializers as list views.

### Verification
- `./.venv/bin/python manage.py test apps.employers apps.food_handlers apps.illness apps.ministries`
- `npm run typecheck`
- `npm run lint`

---

## Chunk SF9: State Inspections and Enforcement Workflow

**Status: Done**

Implemented state ministry inspection supervision over the existing inspections app: `/api/state/inspections/` now supports scoped listing and coordinator assignment, while `/api/state/inspections/:id/review/` and `/api/state/inspections/:id/close/` support enforcement review and closure with audit history. Replaced the state inspections placeholder with a workflow page for assignment, active/submitted/enforcement queues, CSV export, review, closure, and recent audit activity. Added a state inspection detail page for findings, checklist responses, employer responses, and enforcement/audit history.

Verification:
- Passed: `./.venv/bin/python manage.py test apps.inspections apps.ministries` (50 tests)
- Passed: `./.venv/bin/python manage.py check`
- Attempted: `npm run typecheck` stalled silently and was stopped
- Attempted: `npm run lint` stalled silently and was stopped

### Goal
State inspectorate coordinators can assign, review, and close inspection/enforcement workflows.

### Backend
- Add endpoints:
  - `/api/state/inspections`
  - `/api/state/inspections/assign`
  - `/api/state/inspections/:id/review`
  - `/api/state/inspections/:id/close`
- Reuse `inspections` app models/services.
- Support:
  - inspection assignment
  - inspector/LGA filtering
  - checklist review
  - evidence review
  - enforcement notice status
  - follow-up due dates
  - closure decision
- Audit assignment, review, notice, and closure events.

### Frontend
- Replace `state/inspections/page.tsx`.
- Add `state/inspections/[id]/page.tsx` if missing.
- Build:
  - assignment queue
  - active inspections
  - submitted reports
  - enforcement notices
  - follow-up tracker
- Preserve inspector-facing pages; state pages supervise the workflow.

### Files
| Backend | Frontend |
|---------|----------|
| `ministries/views.py` | `state/inspections/page.tsx` |
| `inspections/services.py` | `state/inspections/[id]/page.tsx` (new if missing) |
| `inspections/views.py` | |
| `inspections/tests.py` | |

### Acceptance Criteria
- Coordinators can assign inspections only within their state.
- Inspectors cannot close their own reports unless policy allows it.
- Enforcement action history is visible to authorized state users.

### Verification
- `./.venv/bin/python manage.py test apps.inspections apps.ministries`
- `npm run typecheck`
- `npm run lint`

---

## Chunk SF10: State Reports, Revenue, Settlements, and Federal Submission

**Status: Done**

Added `StateReport` in `apps.ministries` with generated/submitted lifecycle fields and immutable `data_snapshot` storage. Added state-scoped endpoints for report listing, generation, submission, revenue snapshots, and settlements. Built state reports UI for report generation and federal submission, plus a state revenue UI with settlement split cards, filters, and CSV export.

Verification:
- Passed: `./.venv/bin/python manage.py test apps.ministries apps.reports apps.payments apps.settlements` (66 tests)
- Passed: `./.venv/bin/python manage.py check`
- Attempted: `npm run typecheck` stalled silently and was stopped
- Attempted: `npm run lint` stalled silently and was stopped

### Goal
State ministries can generate reports, review revenue/settlement metrics, and submit official reports to the Federal Ministry.

### Backend
- Add `StateReport` model in `apps.ministries`:
  - state
  - report_type
  - reporting_period_start
  - reporting_period_end
  - status
  - generated_by
  - submitted_by
  - submitted_at
  - reviewed_by
  - reviewed_at
  - file_url
  - data_snapshot
  - review_comment
  - timestamps
- Add endpoints:
  - `/api/state/reports`
  - `/api/state/reports/generate`
  - `/api/state/reports/:id/submit`
  - `/api/state/revenue`
  - `/api/state/settlements`
- Report statuses:
  - draft
  - generated
  - submitted
  - returned
  - accepted
- Use report snapshots so submitted reports remain stable after later data changes.
- Reuse payments and settlements services for finance metrics.

### Frontend
- Replace `state/reports/page.tsx`.
- Add:
  - report builder
  - generated report table
  - submit-to-federal action
  - federal review status
- Add `state/revenue/page.tsx` if missing.
- Show state revenue, platform split, facility settlement status, and reconciliation indicators.

### Files
| Backend | Frontend |
|---------|----------|
| `ministries/models.py` | `state/reports/page.tsx` |
| `ministries/services.py` | `state/revenue/page.tsx` (new if missing) |
| `ministries/views.py` | `frontend/src/lib/api/state.ts` |
| `reports/services.py` | |
| `payments/services.py` | |
| `settlements/services.py` | |

### Acceptance Criteria
- State reports can be generated, submitted, returned, and accepted.
- Submitted reports preserve a snapshot of the numbers.
- Revenue and settlement data is state-scoped.

### Verification
- `./.venv/bin/python manage.py test apps.ministries apps.reports apps.payments apps.settlements`
- `npm run typecheck`
- `npm run lint`

---

## Chunk SF11: Federal Dashboard and State Performance Monitoring

**Status: Done**

Added federal aggregate endpoints for `/api/federal/states/performance/` and `/api/federal/states/:state_id/summary/`, returning one privacy-safe aggregate row per state/FCT, including zero-data states, report submission status, open queues, implementation metrics, and data quality score. Replaced the federal dashboard and states placeholders with national KPI cards, state comparison tables, CSV export, and a state drill-down page that explicitly stays inside aggregate/privacy-safe reporting.

Verification:
- Passed: `./.venv/bin/python manage.py test apps.reports apps.ministries` (62 tests)
- Passed: `./.venv/bin/python manage.py check`
- Attempted: `npm run typecheck` stalled silently and was stopped
- Attempted: `npm run lint` stalled silently and was stopped

### Goal
Federal users can monitor national implementation and compare state performance.

### Backend
- Add `/api/federal/dashboard` as PRD-aligned alias over `DashboardService.federal_dashboard`.
- Add `/api/federal/states/performance`.
- Add `/api/federal/states/:state_id/summary`.
- State performance metrics:
  - registered handlers
  - certified handlers
  - certification coverage
  - approved facilities
  - pending facility applications
  - pending certificate validations
  - inspection count
  - illness reports
  - report submission status
  - data quality score
- Return aggregate and privacy-safe data by default.

### Frontend
- Replace:
  - `federal/dashboard/page.tsx`
  - `federal/states/page.tsx`
- Add `federal/states/[id]/page.tsx` if missing.
- Build national KPI cards, state comparison table, maps/charts if existing chart tooling supports it, and drill-down summaries.

### Files
| Backend | Frontend |
|---------|----------|
| `ministries/views.py` | `federal/dashboard/page.tsx` |
| `reports/services.py` | `federal/states/page.tsx` |
| `reports/tests.py` | `federal/states/[id]/page.tsx` (new if missing) |

### Acceptance Criteria
- Federal dashboard shows all states and FCT.
- State drill-downs remain privacy-safe.
- Non-federal users cannot access federal endpoints.

### Verification
- `./.venv/bin/python manage.py test apps.reports apps.ministries`
- `npm run typecheck`
- `npm run lint`

---

## Chunk SF12: Federal Registries, Policy Configuration, and State Overrides

**Status: Done**

Added a national policy defaults model and federal policy endpoint, plus privacy-safe federal registry endpoints for certificates, facilities, employers, and food handler summaries. Added state override monitoring over existing `StatePolicyConfig` records. Replaced federal certificate, facility, and policy placeholder pages, and added the federal employers registry page with filters and CSV exports.

Verification:
- Passed: `./.venv/bin/python manage.py test apps.policy apps.certificates apps.facilities apps.ministries` (64 tests)
- Passed: `./.venv/bin/python manage.py check`
- Attempted: `npm run typecheck` stalled silently and was stopped
- Attempted: `npm run lint` stalled silently and was stopped

### Goal
Federal users can oversee national registries and manage national policy defaults.

### Backend
- Add endpoints:
  - `/api/federal/certificates`
  - `/api/federal/certificates/:id`
  - `/api/federal/certificates/:id/flag`
  - `/api/federal/facilities`
  - `/api/federal/employers`
  - `/api/federal/food-handlers/summary`
  - `/api/federal/policy`
  - `/api/federal/state-overrides`
- Reuse policy configuration models/services where possible.
- National policy fields:
  - certificate validity
  - renewal reminders
  - vaccination validity
  - NIN requirement
  - payment-before-assessment requirement
  - state-validation-before-certificate requirement
  - public QR verification toggle
- State overrides must be visible and auditable.
- Registry results must be privacy-safe, with detail access gated by permission.

### Frontend
- Replace:
  - `federal/certificates/page.tsx`
  - `federal/facilities/page.tsx`
  - `federal/policy-config/page.tsx`
- Add `federal/employers/page.tsx` if missing.
- Add policy version/history table and state override comparison.

### Files
| Backend | Frontend |
|---------|----------|
| `ministries/views.py` | `federal/certificates/page.tsx` |
| `policy/views.py` | `federal/facilities/page.tsx` |
| `policy/models.py` if gaps exist | `federal/policy-config/page.tsx` |
| `certificates/views.py` | `federal/employers/page.tsx` (new if missing) |
| `facilities/views.py` | |

### Acceptance Criteria
- Federal users can configure national policy defaults.
- State overrides are visible with effective dates and approval status.
- Federal registry pages do not expose raw medical details.

### Verification
- `./.venv/bin/python manage.py test apps.policy apps.certificates apps.facilities apps.ministries`
- `npm run typecheck`
- `npm run lint`

---

## Chunk SF13: Federal M&E, Data Quality, Audit, and State Queries

**Status: Done**

Added `FederalStateQuery` with create, respond, and close lifecycle endpoints plus audit events. Added federal M&E indicator, data-quality risk, and privacy-safe audit summary endpoints. Replaced the federal analytics and national reports placeholders, and added federal data-quality, audit, and state query pages.

Verification:
- Passed: `./.venv/bin/python manage.py test apps.ministries apps.audit apps.reports` (68 tests)
- Passed: `./.venv/bin/python manage.py check`
- Attempted: `npm run typecheck` stalled silently and was stopped
- Attempted: `npm run lint` stalled silently and was stopped

### Goal
Federal users can monitor M&E indicators, data quality risks, audit activity, and official state queries.

### Backend
- Add `FederalStateQuery` model in `apps.ministries`:
  - state
  - subject
  - description
  - category
  - priority
  - status
  - raised_by
  - assigned_to
  - response
  - responded_by
  - responded_at
  - closed_at
  - timestamps
- Add endpoints:
  - `/api/federal/m-and-e/indicators`
  - `/api/federal/data-quality`
  - `/api/federal/audit-logs`
  - `/api/federal/queries`
  - `/api/federal/queries/:id/respond`
  - `/api/federal/queries/:id/close`
- Add data quality checks:
  - states with missing reports
  - unusually low certification coverage
  - facilities with high pending assessment counts
  - stale certificate validation queues
  - missing LGA/state metadata
  - inconsistent fee/policy configuration
- Query statuses:
  - open
  - assigned
  - awaiting_state_response
  - responded
  - closed
- Audit views should summarize actor, action, object, state, timestamp, and risk level.

### Frontend
- Replace `federal/analytics/page.tsx` with M&E indicator dashboard or add `federal/m-and-e/page.tsx`.
- Replace `federal/reports/page.tsx` with national report workflow.
- Add pages if missing:
  - `federal/data-quality/page.tsx`
  - `federal/audit/page.tsx`
  - `federal/queries/page.tsx`
  - `federal/state-reports/page.tsx`
- Build action flows for federal query creation, response review, and closure.

### Files
| Backend | Frontend |
|---------|----------|
| `ministries/models.py` | `federal/analytics/page.tsx` or `federal/m-and-e/page.tsx` |
| `ministries/services.py` | `federal/reports/page.tsx` |
| `ministries/views.py` | `federal/data-quality/page.tsx` (new if missing) |
| `audit/services.py` | `federal/audit/page.tsx` (new if missing) |
| `reports/services.py` | `federal/queries/page.tsx` (new if missing) |

### Acceptance Criteria
- Federal users can see data quality risks across all states.
- Federal queries can be created, responded to, and closed.
- Audit logs are searchable and privacy-safe.

### Verification
- `./.venv/bin/python manage.py test apps.ministries apps.audit apps.reports`
- `npm run typecheck`
- `npm run lint`

---

## Chunk SF14: Privacy, Security, Test Hardening, and Final Product Polish

**Status: Done**

Completed final state/federal polish by removing stray duplicate placeholder route files, confirming no state/federal pages still import the generic `PortalPage` shell, and updating state/federal navigation to expose the real workflow pages added across the module. Re-ran sensitive-field scans over ministry serializers and state/federal frontend/API code; state/federal views remain intentionally privacy-safe for NIN, DOB, raw symptoms, doctor notes, and clinical details, with policy fields such as `nin_required` kept only as configuration metadata.

Verification:
- Passed: `./.venv/bin/python manage.py test apps.ministries apps.reports apps.facilities apps.certificates apps.payments apps.settlements apps.organizations apps.accounts apps.inspections apps.illness apps.employers apps.food_handlers apps.policy apps.audit` (172 tests)
- Passed: `./.venv/bin/python manage.py check`
- Confirmed: `rg -n "PortalPage" frontend/src/app/state frontend/src/app/federal` returned no matches
- Attempted: `npm run typecheck` stalled silently and was stopped
- Attempted: `npm run lint` stalled silently and was stopped
- Attempted: `npm run build` stalled silently and was stopped

### Goal
Complete the state/federal modules with privacy-safe UX, reliable tests, and production-quality polish.

### Backend
- Add regression tests for:
  - state scoping across all state endpoints
  - LGA scoping where applicable
  - federal-only access to federal endpoints
  - federal aggregate privacy defaults
  - audit logging for all ministry workflow actions
  - state report snapshot immutability
  - certificate validation lifecycle
  - facility accreditation lifecycle
  - fee lifecycle and split validation
  - federal query lifecycle
- Review serializers for sensitive fields:
  - lab result details
  - doctor notes
  - NIN values
  - raw diagnosis/illness details
  - private phone/email exposure where not needed
- Add missing audit events and notification events.

### Frontend
- Replace remaining state/federal placeholder shells.
- Add consistent empty, loading, error, unauthorized, and success states.
- Ensure tables have filters, pagination, and clear row actions.
- Check responsive behavior across desktop and mobile.
- Remove stale sample-data surfaces from state/federal pages.
- Ensure every action button has a real backend action or is removed.

### Files
| Backend | Frontend |
|---------|----------|
| affected ministry/domain tests | all `state/*` and `federal/*` pages |
| serializers across affected apps | shared ministry components |
| audit/notification services as needed | navigation and permissions helpers |

### Acceptance Criteria
- All PRD state and federal routes have real product screens or intentionally documented deferrals.
- No state/federal page relies on generic placeholder content.
- Sensitive medical data is not exposed to employer, state, or federal views beyond explicit permission rules.
- Final test and build commands pass.

### Final Verification
- `./.venv/bin/python manage.py test apps.ministries apps.reports apps.facilities apps.certificates apps.payments apps.settlements apps.organizations apps.accounts apps.inspections apps.illness apps.employers apps.food_handlers apps.policy apps.audit`
- `npm run typecheck`
- `npm run lint`
- `npm run build`

---

## Implementation Defaults

- Use existing domain services first; only add ministry orchestration logic where a workflow crosses multiple domains.
- Keep public route names aligned with the PRD:
  - `/api/state/...`
  - `/api/federal/...`
- Keep state/federal frontend pages operational and dense, not marketing-style.
- Prefer privacy-safe aggregate views for federal users.
- Store action reasons for rejection, suspension, revocation, return-for-correction, and closure.
- Every ministry workflow action should create an audit event.
- Every chunk should be implemented with backend tests and frontend checks before the next chunk begins.
