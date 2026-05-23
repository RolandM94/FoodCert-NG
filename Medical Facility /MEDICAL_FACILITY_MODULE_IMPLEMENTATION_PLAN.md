# Medical Facility Module — Implementation Plan

## Audit Summary

| Component | Status |
|-----------|--------|
| `MedicalFacility` model and base CRUD | Partially done |
| Facility accreditation application model/workflow | Partially done |
| Accreditation approval/rejection/suspend/reactivate actions | Done |
| Facility document management | Missing |
| Annual re-accreditation workflow | Missing |
| Department management through `OrganizationUnit` | Backend foundation exists, facility workflow missing |
| Facility staff invites and staff profiles | Invite foundation exists, facility workflow missing |
| Appointment model and base API | Partially done |
| Appointment actions: confirm, reschedule, cancel, no-show, assign doctor | Done |
| Assessment model and base API | Partially done |
| Assessment queue filters and facility aliases | Done |
| Health declaration review | Done |
| Physical examination workflow | Done |
| Lab test request/result/review workflow | Done |
| Vaccination review workflow | Done |
| Doctor final decision workflow | Partially done |
| Submit fit assessment to State validation | Partially done through certificates/state work, facility handoff missing |
| Facility clarification workflow | Missing |
| Medical report generation | Missing |
| Facility settlements dashboard and disputes | Partially done |
| Facility reports | Missing |
| Facility dashboard | Placeholder |
| Facility profile/accreditation/departments/staff/invites/appointments pages | Done |
| Facility assessments queue/detail pages | Done |
| Facility lab-tests page | Done |
| Facility certificates/settlements/reports pages | Mostly placeholder |
| Privacy and role-scoped medical access tests | Started — MF0 baseline added |

### Implementation Status

| Chunk | Status |
|-------|--------|
| MF0 Baseline audit, routes, and facility scope inventory | Done |
| MF1 Facility profile, registration, and accreditation readiness | Done |
| MF2 Accreditation documents and annual re-accreditation | Done |
| MF3 Departments using `OrganizationUnit` | Done |
| MF4 Facility staff, invites, and professional profiles | Done |
| MF5 Appointment management and payment gate | Done |
| MF6 Assessment queue and facility workflow detail | Done |
| MF7 Doctor declaration review and physical examination | Done |
| MF8 Laboratory requests, sample collection, results, and review | Done |
| MF9 Vaccination review and record workflow | Done |
| MF10 Doctor decision, medical reports, and immutable sign-off | Done |
| MF11 Submit to State validation and clarification workflow | Done |
| MF12 Settlements, finance dashboard, and disputes | Done |
| MF13 Facility dashboard, reports, notifications, and exports | Done |
| MF14 Security, privacy, QA, and product polish | Done |

## Existing Foundations To Reuse

- Backend apps: `facilities`, `assessments`, `lab_tests`, `vaccinations`, `certificates`, `payments`, `settlements`, `organizations`, `accounts`, `reports`, `notifications`, `audit`, `policy`.
- Organization scoping: use `Organization` and `OrganizationUnit` for facility departments rather than adding separate department models.
- Staff scoping: keep top-level roles `facility_admin`, `doctor`, `lab_staff`; add facility staff profile/sub-role helpers only where the existing `User.role`, `organization`, and `unit` fields are not enough.
- State validation: facilities submit completed fit assessments to the existing State certificate validation workflow. Facilities do not issue certificates directly.
- Finance privacy: reuse payment/settlement records, but expose finance-safe serializers that exclude declaration answers, lab details, diagnosis, and doctor notes.

## Build Order

```txt
MF0 → MF1 → MF2 → MF3 → MF4
 │     │     │     │     │
 ▼     ▼     ▼     ▼     ▼
Audit Profile Accred Dept  Staff

MF5 → MF6 → MF7 → MF8 → MF9
 │     │     │     │     │
 ▼     ▼     ▼     ▼     ▼
Appts Queue Clin  Lab   Vax

MF10 → MF11 → MF12 → MF13 → MF14
  │      │      │      │      │
  ▼      ▼      ▼      ▼      ▼
Decision State  Money  Reports QA
```

Each chunk should produce a working, testable increment. You can stop after any chunk.

---

## Chunk MF0: Baseline Audit, Routes, and Facility Scope Inventory

### Goal
Confirm what exists, remove ambiguity, and prepare the facility module for implementation without breaking state/federal/employer workflows.

### Backend
- Inventory existing models, serializers, services, URLs, permissions, and tests in:
  - `backend/apps/facilities`
  - `backend/apps/assessments`
  - `backend/apps/lab_tests`
  - `backend/apps/vaccinations`
  - `backend/apps/certificates`
  - `backend/apps/settlements`
  - `backend/apps/organizations`
  - `backend/apps/accounts`
- Document current API names versus PRD aliases:
  - existing `/api/medical-facilities/`
  - existing `/api/facility-accreditation/`
  - existing `/api/appointments/`
  - existing `/api/medical-assessments/`
  - target `/api/facilities/:id/...` aliases
- Add or update facility permission helper tests around:
  - facility users only see their organization records
  - doctors/lab staff only act inside their facility
  - employers do not receive clinical details
  - state users only see facilities in their state

### Frontend
- Inventory facility routes and identify placeholder pages:
  - `/facility/dashboard`
  - `/facility/profile`
  - `/facility/accreditation`
  - `/facility/departments`
  - `/facility/staff`
  - `/facility/invites`
  - `/facility/appointments`
  - `/facility/assessments`
  - `/facility/lab-tests`
  - `/facility/certificates`
  - `/facility/settlements`
  - `/facility/reports`
- Confirm navigation labels match real workflow pages.

### Acceptance Criteria
- A clear gap list exists in this plan or PR notes.
- No facility placeholder page is mistaken for product-complete functionality.
- Baseline backend tests still pass before changing behavior.

### Checks
- `./.venv/bin/python manage.py test apps.facilities apps.assessments apps.lab_tests apps.vaccinations apps.certificates apps.settlements apps.organizations apps.accounts`
- `./.venv/bin/python manage.py check`

---

## Chunk MF1: Facility Profile, Registration, and Accreditation Readiness

### Goal
Facility admins can create and maintain a complete facility profile, with enough data for State accreditation and settlement setup.

### Backend
- Extend `MedicalFacility` where needed:
  - ward, optional
  - operating hours
  - service capacity
  - `is_active`
  - settlement/bank readiness fields if not already covered by payments/settlements
- Add `GET /api/medical-facilities/me/` or equivalent current-facility action.
- Keep state/LGA scoping strict for facility, state, and federal users.
- Add service methods for:
  - creating facility profile for a `facility_admin`
  - updating profile
  - checking profile completeness
  - blocking duplicate facility profile per organization
- Audit facility profile create/update.

### Frontend
- Replace `/facility/profile` placeholder with a real profile form:
  - facility name/type/ownership
  - license and registration number
  - address, state, LGA, ward
  - contact person, phone, email
  - operating hours and service capacity
  - standard assessment price
  - accreditation status summary
- Add loading, empty, save, validation, and error states.

### Files
| Backend | Frontend |
|---------|----------|
| `backend/apps/facilities/models.py` | `frontend/src/app/facility/profile/page.tsx` |
| `backend/apps/facilities/serializers.py` | `frontend/src/lib/api/facilities.ts` |
| `backend/apps/facilities/services.py` | `frontend/src/types/facilities.ts` |
| `backend/apps/facilities/views.py` | facility profile component files |
| facility migration | |

### Acceptance Criteria
- Facility admin can retrieve and update their own facility profile.
- State admin can view facilities only in their state.
- Facility cannot create a duplicate profile for the same organization.
- Profile updates create audit logs.

### Checks
- Backend unit/API tests for facility profile ownership and state scoping.
- Frontend typecheck/lint for updated facility profile page.

---

## Chunk MF2: Accreditation Documents and Annual Re-Accreditation

### Goal
Facility accreditation becomes a complete workflow: checklist, evidence uploads, submission, review status, renewal, and expiry controls.

### Backend
- Add `FacilityDocument` model:
  - facility
  - accreditation application
  - document type
  - file
  - status
  - uploaded by
  - reviewed metadata if needed
- Expand accreditation checklist to include PRD-required fields:
  - valid facility license
  - lab capacity
  - valid doctor credentials
  - valid lab staff credentials
  - infection prevention/control readiness
  - confidentiality/data protection procedure
- Add more-information-required status support if missing.
- Add re-accreditation submission path:
  - create renewal application linked to prior approved facility
  - preserve old expiry until policy says otherwise
  - block new assessments after expiry unless policy permits grace period
- Add scheduled/status helper for due dates:
  - 60 days
  - 30 days
  - 7 days
  - expiry day
- Audit document upload, submission, state review, renewal, suspension, reinstatement.

### Frontend
- Replace `/facility/accreditation` placeholder with:
  - current accreditation status panel
  - checklist form
  - document upload section
  - submit button
  - review timeline and comments
  - renewal prompt when expiry approaches
- Add `/facility/re-accreditation` if route does not exist.

### Files
| Backend | Frontend |
|---------|----------|
| `backend/apps/facilities/models.py` | `frontend/src/app/facility/accreditation/page.tsx` |
| `backend/apps/facilities/serializers.py` | `frontend/src/app/facility/re-accreditation/page.tsx` |
| `backend/apps/facilities/services.py` | `frontend/src/lib/api/facilities.ts` |
| `backend/apps/facilities/views.py` | `frontend/src/types/facilities.ts` |
| facility migration | accreditation components |

### Acceptance Criteria
- Facility can upload required accreditation evidence.
- Facility cannot submit incomplete checklist.
- State can request more information, approve, reject, suspend, and reactivate.
- Expired/suspended facilities cannot receive new appointments.
- Renewal workflow is audit logged.

### Checks
- Backend tests for document upload, submission, review transitions, expiry blocking.
- Frontend typecheck/lint for accreditation pages.

---

## Chunk MF3: Departments Using OrganizationUnit

### Goal
Facility admins can create and manage internal departments, and users can be scoped to department workflows.

### Backend
- Add facility-scoped endpoints over `OrganizationUnit`:
  - `GET /api/facilities/:id/departments`
  - `POST /api/facilities/:id/departments`
  - `GET/PATCH /api/facilities/:id/departments/:department_id`
  - deactivate department action
- Support department types:
  - clinical assessment department
  - laboratory department
  - medical records department
  - finance/settlement unit
  - administration unit
  - other
- Add workload metrics per department:
  - open assessments
  - pending lab tests
  - pending records
  - pending settlements
- Audit create/update/deactivate.

### Frontend
- Replace `/facility/departments` placeholder with:
  - departments table
  - create/edit department modal
  - active/inactive filter
  - staff count and workload columns
- Replace `/facility/departments/[id]` with:
  - department detail
  - assigned staff
  - workload
  - performance snapshot

### Files
| Backend | Frontend |
|---------|----------|
| `backend/apps/organizations/views.py` | `frontend/src/app/facility/departments/page.tsx` |
| `backend/apps/organizations/serializers.py` | `frontend/src/app/facility/departments/[id]/page.tsx` |
| `backend/apps/organizations/services.py` | `frontend/src/lib/api/organizations.ts` |
| `backend/apps/facilities/views.py` | `frontend/src/types/organizations.ts` |

### Acceptance Criteria
- Facility admin can manage departments only inside their facility organization.
- Department names remain unique within the facility.
- Deactivated departments do not receive new task routing.
- Department workload is visible without exposing restricted clinical details to unauthorized finance/viewer users.

### Checks
- Backend tests for department scoping and deactivation.
- Frontend typecheck/lint for department pages.

---

## Chunk MF4: Facility Staff, Invites, and Professional Profiles

### Goal
Facility admins can invite and manage doctors, lab staff, records staff, finance users, and viewers.

### Backend
- Add `FacilityStaffProfile` if existing user fields are insufficient:
  - user
  - facility
  - department
  - staff type
  - professional registration number
  - digital signature URL or reference
  - active status
- Add facility invite endpoints:
  - `GET /api/facilities/:id/invites`
  - `POST /api/facilities/:id/invites`
  - resend invite
  - revoke invite
- Add staff endpoints:
  - `GET /api/facilities/:id/staff`
  - update role/profile
  - assign department
  - suspend/reactivate
- Preserve top-level roles:
  - `facility_admin`
  - `doctor`
  - `lab_staff`
  - use profile/sub-role for records, finance, viewer where useful
- Audit invite, revoke, role update, department assignment, suspension.

### Frontend
- Replace `/facility/staff` placeholder with:
  - staff table
  - role, department, professional number, status, last login
  - row actions
- Replace `/facility/invites` with:
  - invite list
  - pending/accepted/revoked filters
  - resend/revoke actions
- Add invite modal:
  - email, phone, role, department, professional registration number, message, expiry.

### Files
| Backend | Frontend |
|---------|----------|
| `backend/apps/facilities/models.py` | `frontend/src/app/facility/staff/page.tsx` |
| `backend/apps/facilities/serializers.py` | `frontend/src/app/facility/invites/page.tsx` |
| `backend/apps/facilities/services.py` | `frontend/src/lib/api/facilities.ts` |
| `backend/apps/accounts/models.py` | `frontend/src/types/facilities.ts` |
| `backend/apps/accounts/serializers.py` | staff/invite components |

### Acceptance Criteria
- Facility admin can invite doctors/lab staff/records/finance/viewer users.
- Invited users are tied to the facility organization and optional department.
- Suspended users cannot perform workflow actions.
- Doctors and lab staff cannot access unrelated facility records.

### Checks
- Backend invite/profile/role-scoping tests.
- Frontend typecheck/lint for staff and invite pages.

---

## Chunk MF5: Appointment Management and Payment Gate

### Goal
Approved facilities can manage appointments, assign doctors, and enforce payment/accreditation rules.

### Backend
- Add appointment actions:
  - confirm
  - reschedule
  - cancel
  - mark no-show
  - assign doctor
- Add facility-scoped appointment endpoint alias:
  - `GET /api/facilities/:id/appointments`
  - `PATCH /api/facilities/:id/appointments/:appointment_id/...`
- Enforce:
  - only approved/current facilities accept new appointments
  - suspended/expired facilities cannot confirm appointments
  - confirmed appointments require successful payment unless policy allows override
  - assigned doctor must belong to the facility
- Notify food handler and linked employer on appointment changes.
- Audit all appointment transitions.

### Frontend
- Replace `/facility/appointments` placeholder with:
  - table/calendar toggle
  - filters by date, payment, declaration, doctor, status, employer
  - row actions: confirm, reschedule, cancel, no-show, assign doctor
- Add `/facility/appointments/[id]` if useful for detail view.

### Files
| Backend | Frontend |
|---------|----------|
| `backend/apps/assessments/models.py` | `frontend/src/app/facility/appointments/page.tsx` |
| `backend/apps/assessments/serializers.py` | `frontend/src/app/facility/appointments/[id]/page.tsx` |
| `backend/apps/assessments/services.py` | `frontend/src/lib/api/assessments.ts` |
| `backend/apps/assessments/views.py` | `frontend/src/types/assessments.ts` |

### Acceptance Criteria
- Facility can confirm/reschedule/cancel/no-show appointments.
- Doctor assignment respects facility membership.
- Payment and accreditation gates are enforced.
- Food handler/employer notifications are created where linked.

### Checks
- Backend tests for appointment transitions and payment/accreditation gates.
- Frontend typecheck/lint for appointment pages.

---

## Chunk MF6: Assessment Queue and Facility Workflow Detail

### Goal
Facility users get a central operational queue for all assessments, with safe filters and task status visibility.

### Backend
- Add facility-scoped assessment queue endpoint:
  - `GET /api/facilities/:id/assessments`
  - `GET /api/facilities/:id/assessments/:assessment_id`
  - `PATCH /api/facilities/:id/assessments/:assessment_id/assign-doctor`
- Add filters:
  - date range
  - doctor
  - lab status
  - decision status
  - employer
  - branch
  - payment status
  - certificate submission status
  - assessment status
- Add role-aware serializers:
  - admin/doctor: full operational assessment data
  - lab: lab-relevant data only
  - records: completed documentation data
  - finance: payment/settlement data only
  - viewer: safe summary only
- Audit sensitive assessment detail access.

### Frontend
- Replace `/facility/assessments` placeholder with:
  - queue table
  - status badges
  - workflow stepper
  - role-aware columns
  - filter bar
  - row actions based on role/status
- Add `/facility/assessments/[id]`:
  - food handler summary
  - payment/appointment status
  - declaration, physical exam, lab, vaccination, decision panels
  - state submission panel

### Files
| Backend | Frontend |
|---------|----------|
| `backend/apps/assessments/views.py` | `frontend/src/app/facility/assessments/page.tsx` |
| `backend/apps/assessments/serializers.py` | `frontend/src/app/facility/assessments/[id]/page.tsx` |
| `backend/apps/assessments/services.py` | `frontend/src/lib/api/assessments.ts` |
| `backend/apps/facilities/permissions.py` | `frontend/src/types/assessments.ts` |

### Acceptance Criteria
- Facility users only see assessments in their facility.
- Lab/finance/viewer users do not see restricted clinical details.
- Filters work without leaking cross-facility or cross-state data.
- Sensitive detail reads are audit logged.

### Checks
- Backend queue filter, scoping, and privacy tests.
- Frontend typecheck/lint for assessment queue/detail.

---

## Chunk MF7: Doctor Declaration Review and Physical Examination

### Goal
Doctors can validate declarations, document physical exams, and move assessments toward lab/vaccination/decision steps.

### Backend
- Add doctor-friendly endpoint aliases:
  - `GET /api/doctor/assessments`
  - `GET /api/doctor/assessments/:assessment_id`
  - `PATCH /api/doctor/assessments/:assessment_id/declaration/validate`
  - clarification/request-changes action for declarations
  - `POST /api/doctor/assessments/:assessment_id/physical-exam`
- Enforce:
  - doctor belongs to facility
  - doctor is assigned or facility admin allowed assignment first
  - declaration is locked after validation
  - changes require new declaration version or explicit correction flow
- Add risk flag visibility and audit logging.
- Add sensitive note privacy tests.

### Frontend
- Add doctor assessment surfaces or integrate into facility detail:
  - declaration review panel
  - risk flag panel
  - physical exam form
  - save/complete actions
  - next-step prompts for lab/vaccination/decision
- Add `/doctor/assessments` and `/doctor/assessments/[id]` if not present.

### Files
| Backend | Frontend |
|---------|----------|
| `backend/apps/assessments/models.py` | `frontend/src/app/doctor/assessments/page.tsx` |
| `backend/apps/assessments/serializers.py` | `frontend/src/app/doctor/assessments/[id]/page.tsx` |
| `backend/apps/assessments/services.py` | assessment clinical components |
| `backend/apps/assessments/views.py` | |

### Acceptance Criteria
- Doctor can validate a declaration and complete a physical exam.
- Risky declarations require doctor attention but do not auto-disqualify.
- Employer and finance users cannot see declaration answers or doctor notes.
- Workflow transitions are audit logged.

### Checks
- Backend tests for doctor permissions, declaration locking, physical exam completion.
- Frontend typecheck/lint for doctor pages/components.

---

## Chunk MF8: Laboratory Requests, Sample Collection, Results, and Review

### Goal
Lab staff can process lab requests and doctors can review results before final decision.

### Backend
- Expand lab status support if needed:
  - requested
  - sample collected
  - in progress
  - result uploaded/submitted
  - positive
  - negative
  - inconclusive
  - repeat required
  - reviewed
- Add fields where needed:
  - sample collected date/time
  - result document upload
  - lab staff notes
  - submitted-to-doctor timestamp
- Add lab endpoint aliases:
  - `GET /api/lab/requests`
  - `GET /api/lab/requests/:lab_test_id`
  - `PATCH /api/lab/requests/:lab_test_id/sample-collected`
  - `PATCH /api/lab/requests/:lab_test_id/result`
  - `POST /api/lab/requests/:lab_test_id/upload-result`
  - `PATCH /api/lab/requests/:lab_test_id/review`
- Enforce:
  - lab staff cannot make fitness decisions
  - doctors review lab results
  - positive/inconclusive results are flagged
  - repeat test can be requested
- Audit request, sample collection, result submission, review.

### Frontend
- Replace `/facility/lab-tests` placeholder with:
  - lab request queue
  - sample collection actions
  - result entry form
  - upload document control
  - doctor review status
- Add `/lab/requests` and `/lab/requests/[id]` if separate lab portal pages are needed.

### Files
| Backend | Frontend |
|---------|----------|
| `backend/apps/lab_tests/models.py` | `frontend/src/app/facility/lab-tests/page.tsx` |
| `backend/apps/lab_tests/serializers.py` | `frontend/src/app/lab/requests/page.tsx` |
| `backend/apps/lab_tests/services.py` | `frontend/src/app/lab/requests/[id]/page.tsx` |
| `backend/apps/lab_tests/views.py` | `frontend/src/lib/api/lab-tests.ts` |

### Acceptance Criteria
- Doctor can request required and optional food handler tests.
- Lab staff can mark sample collected and enter/upload results.
- Doctor can review results and update assessment lab status.
- Employers/finance/public cannot see detailed lab results.

### Checks
- Backend lab workflow and privacy tests.
- Frontend typecheck/lint for lab pages.

---

## Chunk MF9: Vaccination Review and Record Workflow

### Goal
Doctors or authorized facility users can review, validate, prescribe, and record vaccination status.

### Backend
- Add vaccination review action:
  - mark valid
  - mark missing
  - mark expired
  - prescribe vaccination
  - record administered vaccination
  - set next dose date
  - complete vaccination review for assessment
- Keep PRD policy defaults:
  - typhoid validity: 3 years
  - hepatitis A dose 2 due after 6 months
- Add endpoint alias:
  - `PATCH /api/doctor/assessments/:assessment_id/vaccination-review`
- Enforce employer-safe visibility:
  - compliance status only, no clinical notes.
- Audit vaccination changes and review completion.

### Frontend
- Add vaccination panel in assessment detail:
  - existing records
  - uploaded proof
  - status controls
  - administered vaccine form
  - next dose/expiry display
- Add clear status badges for valid, expired, missing, second dose due, doctor cleared.

### Files
| Backend | Frontend |
|---------|----------|
| `backend/apps/vaccinations/models.py` | vaccination review components |
| `backend/apps/vaccinations/serializers.py` | `frontend/src/lib/api/vaccinations.ts` |
| `backend/apps/vaccinations/services.py` | `frontend/src/types/vaccinations.ts` |
| `backend/apps/vaccinations/views.py` | doctor/facility assessment detail pages |

### Acceptance Criteria
- Vaccination review can be completed before doctor decision.
- Typhoid and hepatitis A defaults are applied correctly.
- Employers see only vaccination compliance status.
- Vaccination changes create audit logs.

### Checks
- Backend vaccination review tests.
- Frontend typecheck/lint for vaccination components.

---

## Chunk MF10: Doctor Decision, Medical Reports, and Immutable Sign-Off

### Goal
Doctors can submit final fitness decisions with required checks, digital sign-off, and medical report generation.

### Backend
- Harden `set_fitness_decision` requirements:
  - payment confirmed
  - NIN verified or override-approved
  - facility approved/current
  - doctor authorized
  - declaration validated
  - physical exam completed
  - required lab results reviewed
  - vaccination reviewed
  - no unresolved exclusion/illness issue
  - digital sign-off present
- Add decision draft/save if needed.
- Add medical report model/service or generated report integration:
  - medical examination report
  - temporarily not fit report
  - return-to-work report
  - vaccination record
  - restricted lab summary
  - assessment completion summary
- Make submitted final decisions immutable except formal correction flow.
- Audit decision and report generation.

### Frontend
- Add fitness decision panel:
  - readiness checklist
  - decision options
  - return-to-work date where applicable
  - doctor notes restricted display
  - digital sign-off confirmation
  - report preview
- Show not-fit/temporary-not-fit report outcome without offering certificate issuance.

### Files
| Backend | Frontend |
|---------|----------|
| `backend/apps/assessments/services.py` | fitness decision components |
| `backend/apps/assessments/serializers.py` | medical report preview components |
| `backend/apps/assessments/views.py` | doctor/facility assessment detail pages |
| `backend/apps/reports/models.py` | `frontend/src/lib/api/reports.ts` |
| `backend/apps/reports/services.py` | |

### Acceptance Criteria
- Fit decision cannot be submitted until all required checks pass.
- Final decision is digitally signed and immutable.
- Not-fit decisions generate reports, not certificates.
- Employers receive operational fitness category only.

### Checks
- Backend decision readiness, immutability, privacy, and report tests.
- Frontend typecheck/lint for decision/report UI.

---

## Chunk MF11: Submit to State Validation and Clarification Workflow

### Goal
Completed fit assessments move from facility workflow into State certificate validation, including clarification loops.

### Backend
- Add facility submission action:
  - `POST /api/facilities/:id/assessments/:assessment_id/submit-to-state`
- Validate submission requirements:
  - final fit decision
  - signed doctor decision
  - required sections complete
  - lab reviewed
  - vaccination reviewed
  - payment confirmed
  - facility accreditation active
  - medical report generated
- Create or link certificate validation record for State queue.
- Add `FacilityClarificationRequest` model if state clarification cannot be handled by existing certificate workflow:
  - facility
  - assessment
  - accreditation application optional
  - requested by
  - responded by
  - subject/message/response/status
- Add actions:
  - state requests clarification
  - facility responds
  - facility resubmits
- Notify doctor/facility admin on clarification.
- Audit submission and clarification responses.

### Frontend
- Add state submission panel to assessment detail:
  - readiness checklist
  - submit to State button
  - current submission status
  - clarification request/response thread
- Replace `/facility/certificates` placeholder with:
  - pending validation list
  - clarification requested list
  - approved/certificate issued list
  - rejected list
  - certificate view/download/verify links where available.

### Files
| Backend | Frontend |
|---------|----------|
| `backend/apps/assessments/views.py` | `frontend/src/app/facility/certificates/page.tsx` |
| `backend/apps/assessments/services.py` | assessment state submission components |
| `backend/apps/certificates/services.py` | `frontend/src/lib/api/certificates.ts` |
| `backend/apps/certificates/views.py` | `frontend/src/types/certificates.ts` |
| `backend/apps/facilities/models.py` | |

### Acceptance Criteria
- Facility can submit only eligible fit assessments to State.
- Facility cannot issue certificates directly.
- State clarification requests are visible and answerable by facility users.
- Submission and clarification history is audit logged.

### Checks
- Backend tests for submission readiness, state handoff, clarification loop.
- Frontend typecheck/lint for certificate/submission pages.

---

## Chunk MF12: Settlements, Finance Dashboard, and Disputes

### Goal
Facility finance users can track payments, settlements, reconciliation, and disputes without seeing medical details.

### Backend
- Add facility settlement endpoint aliases:
  - `GET /api/facilities/:id/settlements`
  - `GET /api/facilities/:id/settlements/:settlement_id`
  - `GET /api/facilities/:id/reports/settlements`
  - `POST /api/facilities/:id/settlements/:settlement_id/dispute`
- Add settlement eligibility service:
  - payment confirmed
  - assessment completed
  - doctor decision submitted
  - State validation completed
  - certificate issued or report finalized according to policy
- Expose metrics:
  - paid assessments
  - completed assessments
  - pending/processing/paid/failed settlements
  - gross amount
  - facility amount
  - state amount
  - platform amount
  - refunds
  - disputes
- Add finance-safe serializer.
- Audit settlement dispute creation and settlement detail access.

### Frontend
- Replace `/facility/settlements` placeholder with:
  - metrics cards
  - settlement table
  - filters by status/date
  - receipt/reconciliation export
  - dispute action modal
- Ensure finance users see only financial columns.

### Files
| Backend | Frontend |
|---------|----------|
| `backend/apps/settlements/models.py` | `frontend/src/app/facility/settlements/page.tsx` |
| `backend/apps/settlements/serializers.py` | `frontend/src/lib/api/settlements.ts` |
| `backend/apps/settlements/services.py` | `frontend/src/types/settlements.ts` |
| `backend/apps/settlements/views.py` | settlement components |
| `backend/apps/payments/services.py` | |

### Acceptance Criteria
- Finance users can view settlement and reconciliation data.
- Finance users cannot see declaration answers, lab results, diagnosis, or doctor notes.
- Disputes can be raised and audit logged.
- Settlement eligibility respects policy and State validation.

### Checks
- Backend settlement eligibility, dispute, and finance privacy tests.
- Frontend typecheck/lint for settlement page.

---

## Chunk MF13: Facility Dashboard, Reports, Notifications, and Exports

### Goal
Facility users have operational dashboards, reports, notifications, and exports that respect role-based privacy.

### Backend
- Add `GET /api/facilities/:id/dashboard`:
  - accreditation status
  - re-accreditation due date
  - appointments today
  - pending appointments
  - assessments in progress
  - lab requests pending
  - lab results pending doctor review
  - vaccination reviews pending
  - doctor decisions pending
  - submitted to State
  - certificates issued
  - not-fit reports
  - pending settlements
  - settled amount
- Add report endpoints:
  - assessment volume
  - appointments
  - lab tests
  - doctor decisions
  - certificate submissions
  - State clarifications
  - settlements
  - department workload
  - re-accreditation readiness
- Support CSV/PDF/Excel exports using existing reports infrastructure.
- Add notifications for PRD events:
  - accreditation, appointments, declaration, lab, decision, State clarification, certificate, settlement.
- Audit report exports and sensitive report access.

### Frontend
- Replace `/facility/dashboard` placeholder with:
  - operational metric cards
  - queue summaries
  - charts/tables for volume, status distribution, lab turnaround, decision distribution, settlements
  - filters by date, department, doctor, lab status, assessment status, employer/category
- Replace `/facility/reports` placeholder with:
  - report builder
  - role-aware report list
  - export controls
  - recent generated reports table

### Files
| Backend | Frontend |
|---------|----------|
| `backend/apps/facilities/views.py` | `frontend/src/app/facility/dashboard/page.tsx` |
| `backend/apps/facilities/services.py` | `frontend/src/app/facility/reports/page.tsx` |
| `backend/apps/reports/models.py` | `frontend/src/lib/api/reports.ts` |
| `backend/apps/reports/services.py` | `frontend/src/types/reports.ts` |
| `backend/apps/reports/views.py` | dashboard/report components |
| `backend/apps/notifications/models.py` | |

### Acceptance Criteria
- Facility dashboard shows real counts, not static placeholders.
- Reports export only fields allowed for the current role.
- Finance reports exclude medical details.
- Lab/clinical reports are restricted to authorized users.
- Notifications are created for key workflow events.

### Checks
- Backend dashboard/report/privacy/export tests.
- Frontend typecheck/lint for dashboard and reports.

---

## Chunk MF14: Security, Privacy, QA, and Product Polish

### Goal
Harden the facility module end to end and make the portal feel product-complete.

### Backend
- Add regression tests for:
  - facility organization scoping
  - state scoping
  - doctor/lab department scoping
  - finance privacy
  - employer/public medical privacy
  - sensitive access audit logs
  - accreditation expiry/suspension gates
  - appointment transitions
  - declaration validation
  - physical exam
  - lab workflow
  - vaccination review
  - final decision readiness
  - State submission
  - settlement eligibility
- Ensure all new endpoints use consistent permission helpers.
- Ensure all workflow transitions write audit logs.
- Confirm migrations are present and apply cleanly.

### Frontend
- Remove all facility `PortalPage` placeholders.
- Add empty, loading, error, and success states to every facility page.
- Verify role-specific UI does not show forbidden actions.
- Polish tables, filters, status badges, forms, and modals for mobile and desktop.
- Keep facility UI utilitarian and workflow-focused:
  - dense but readable tables
  - clear status badges
  - stable layout dimensions
  - no decorative dashboards in place of work queues.

### Final QA Checklist
- Backend:
  - `./.venv/bin/python manage.py makemigrations --check --dry-run`
  - `./.venv/bin/python manage.py migrate`
  - `./.venv/bin/python manage.py check`
  - `./.venv/bin/python manage.py test apps.facilities apps.assessments apps.lab_tests apps.vaccinations apps.certificates apps.settlements apps.organizations apps.accounts apps.reports apps.notifications apps.audit`
- Frontend:
  - `npm run typecheck`
  - `npm run lint`
  - `npm run build`
- Manual product QA:
  - facility admin profile/accreditation/staff/departments
  - appointment assignment and payment gate
  - doctor assessment workflow
  - lab workflow
  - vaccination review
  - decision and State submission
  - State clarification response
  - settlement view/dispute
  - dashboard and reports
  - privacy checks for employer, finance, lab, public verifier, state user.

### Acceptance Criteria
- No facility placeholder pages remain.
- All medical details are role-restricted.
- Accredited facilities can complete the full assessment workflow.
- Suspended/expired facilities are blocked from new work.
- Fit assessments route to State validation, not direct certificate issuance.
- Backend tests pass for affected apps.
- Frontend typecheck, lint, and production build pass.
