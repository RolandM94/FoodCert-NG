# Medical Assessment Workflow Module — Implementation Plan

## Audit Summary

| Component | Status |
|-----------|--------|
| `MedicalAssessment`, step statuses, final decision fields | Mostly done |
| Assessment creation with payment/facility gates | Partially done |
| NIN prerequisite enforcement | Done for final decision/certificate, needs lifecycle activation coverage |
| Appointment linkage and facility/doctor assignment | Done |
| Health declaration questions and risk flag | Mostly done |
| Declaration draft/version/reopen workflow | Missing |
| Doctor declaration validation and clarification | Done |
| Physical examination workflow | Mostly done |
| Physical examination draft/risk flag/signature details | Missing/partial |
| Doctor lab request workflow | Partially done |
| Lab sample/result/upload/submit/review workflow | Mostly done |
| Repeat lab request and linked parent test | Missing |
| Vaccination review for typhoid/Hepatitis A | Mostly done |
| Vaccine brand/batch/certificate fields | Partial |
| Doctor fitness decision and immutable digital sign-off | Done |
| Temporarily not-fit return-to-work trigger | Partial through illness workflow |
| Submit fit assessment to State validation | Done through facility/certificate workflow |
| Assessment report generation | Partial |
| Food handler assessment pages | Mostly placeholder |
| Doctor workflow pages | Mostly done |
| Lab workflow pages | Mostly done |
| Facility assessment queue/detail | Done |
| State certificate validation queue | Done |
| Employer/public privacy protections | Started, needs regression hardening |
| Audit logging | Broad coverage exists, needs lifecycle completeness pass |

## Implementation Status

| Chunk | Status |
|-------|--------|
| AW0 Baseline audit, model alignment, and route inventory | Done |
| AW1 Assessment lifecycle status engine and prerequisite gates | Done |
| AW2 Food handler assessment dashboard, detail, and next-step UX | Done |
| AW3 Declaration draft, submit, versioning, reopen, and lock rules | Done |
| AW4 Physical exam draft, risk flag, completion, and doctor safeguards | Done |
| AW5 Lab test request policy, required tests, repeat tests, and privacy | Done |
| AW6 Lab staff workflow hardening: sample, result, upload, submit | Done |
| AW7 Doctor lab result review, positive/inconclusive handling, repeats | Done |
| AW8 Vaccination review expansion and employer-safe compliance statuses | Done |
| AW9 Fitness decision drafts, return-to-work trigger, and operational statuses | Done |
| AW10 State submission aliases, clarification state sync, and certificate handoff | Done |
| AW11 Assessment reports and role-safe report access | Done |
| AW12 Audit timeline, sensitive-access logging, and status history | Done |
| AW13 Cross-role privacy, permission regression tests, and API hardening | Done |
| AW14 Frontend product polish and final QA | Done |

## Existing Foundations To Reuse

- Backend apps: `assessments`, `lab_tests`, `vaccinations`, `illness`, `certificates`, `facilities`, `payments`, `nin_verification`, `reports`, `notifications`, `audit`, `policy`.
- Existing nested facility workflows:
  - `/api/facilities/:id/assessments/`
  - `/api/facilities/:id/assessments/:assessment_id/`
  - `/api/facilities/:id/assessments/:assessment_id/submit-to-state/`
  - `/api/facilities/:id/assessments/:assessment_id/respond-to-clarification/`
- Existing doctor workflows:
  - `/api/doctor/assessments/`
  - `/api/doctor/assessments/:id/declaration/validate/`
  - `/api/doctor/assessments/:id/physical-exam/`
  - `/api/doctor/assessments/:id/vaccination-review/`
  - `/api/doctor/assessments/:id/fitness-decision/`
- Existing lab workflows:
  - `/api/lab/requests/`
  - `/api/lab/requests/:id/collect-sample/`
  - `/api/lab/requests/:id/record-result/`
  - `/api/lab/requests/:id/upload-result/`
  - `/api/lab/requests/:id/submit-to-doctor/`
- Existing state validation: certificate requests and `/api/state/certificate-validation-queue/`.
- Existing return-to-work foundation: `IllnessReport`, clearance actions, employer/food-handler illness reporting, and RTW certificate numbers.

## Build Order

```txt
AW0 → AW1 → AW2
 │     │     │
 ▼     ▼     ▼
Audit Status Food Handler UX

AW3 → AW4 → AW5 → AW6 → AW7 → AW8
 │     │     │     │     │     │
 ▼     ▼     ▼     ▼     ▼     ▼
Decl  Exam  LabReq LabOps LabRev Vax

AW9 → AW10 → AW11 → AW12 → AW13 → AW14
 │      │      │      │      │      │
 ▼      ▼      ▼      ▼      ▼      ▼
Decision State Reports Audit Privacy QA
```

Each chunk should produce a working, testable increment. Existing working workflows should be reused before adding new abstractions.

---

## Chunk AW0: Baseline Audit, Model Alignment, and Route Inventory

### Goal
Confirm how the PRD maps to the current implementation and remove ambiguity before adding workflow changes.

### Backend
- Inventory current assessment, declaration, physical exam, lab, vaccination, illness, certificate, and report models.
- Map current status values to PRD statuses:
  - identify exact existing aliases
  - identify missing values
  - avoid broad breaking status renames unless compatibility is maintained
- Inventory current API routes versus PRD routes.
- Add a short `ASSESSMENT_WORKFLOW_ROUTE_MAP.md` or a section in this plan if useful.

### Frontend
- Inventory assessment routes for food handler, doctor, lab, facility, and state.
- Identify placeholder routes:
  - food-handler assessment pages
  - doctor sub-pages that only proxy to detail page
  - lab result list if still shell-like

### Acceptance Criteria
- Plan has an accurate gap map.
- No implementation begins without knowing what is reused versus replaced.

### Checks
- `backend/.venv/bin/python manage.py check`
- `npm run typecheck`

---

## Chunk AW1: Assessment Lifecycle Status Engine and Prerequisite Gates

### Goal
Make backend status calculation the source of truth for all assessment progression.

### Backend
- Add or harden `AssessmentService.status_snapshot(assessment)`.
- Add `GET /api/assessments/:id/status/`.
- Add lifecycle gate helpers:
  - profile completeness
  - NIN verified or override-approved
  - facility approved/current
  - payment confirmed when policy requires it
  - appointment booked/confirmed or permitted walk-in
  - doctor authorization
  - employer/branch linkage where applicable
- Ensure status is updated consistently after:
  - creation
  - payment link/verification
  - appointment confirmation
  - declaration submit/validate
  - physical exam complete
  - lab submit/review
  - vaccination review
  - final decision
  - State submission/clarification/approval
  - certificate issuance
  - cancellation/closure
- Add cancel/close actions if missing:
  - `POST /api/assessments/:id/cancel/`
  - `POST /api/assessments/:id/close/`

### Frontend
- Add reusable `AssessmentStepper`, `AssessmentStatusBadge`, and `AssessmentPrerequisiteChecklist`.
- Replace frontend-derived workflow status with backend status payloads.

### Files
| Backend | Frontend |
|---------|----------|
| `backend/apps/assessments/models.py` | `frontend/src/types/assessments.ts` |
| `backend/apps/assessments/services.py` | `frontend/src/lib/api/assessments.ts` |
| `backend/apps/assessments/serializers.py` | `frontend/src/components/assessments/*` |
| `backend/apps/assessments/views.py` | |

### Acceptance Criteria
- Backend status endpoint returns current stage, next action, blockers, and safe user-facing text.
- Frontend does not infer final workflow status independently.
- Blockers are specific and role-safe.

### Checks
- Backend tests for each major transition and blocker.
- Frontend typecheck/lint.

---

## Chunk AW2: Food Handler Assessment Dashboard, Detail, and Next-Step UX

### Goal
Replace food-handler assessment placeholders with real self-service workflow pages.

### Backend
- Ensure food handler can list and retrieve only their own assessments.
- Add/shape food-handler-safe serializer:
  - no doctor notes
  - no detailed lab result values
  - no internal audit metadata
  - masked identifiers only
- Add report/certificate download links only where permitted.

### Frontend
- Replace:
  - `/food-handler/assessments`
  - `/food-handler/assessments/:id`
  - `/food-handler/declaration`
  - `/food-handler/certificate` where assessment-linked
- Show:
  - current assessment status
  - prerequisite blockers
  - appointment details
  - declaration status
  - limited lab status
  - vaccination status
  - final fitness outcome
  - next required action
  - certificate/report links where permitted

### Acceptance Criteria
- Food handler can understand and complete their own next workflow step.
- Food handler cannot see internal clinical notes or private facility/state notes.

### Checks
- Food-handler API scoping tests.
- Frontend typecheck/lint/build.

---

## Chunk AW3: Declaration Draft, Submit, Versioning, Reopen, and Lock Rules

### Goal
Make health declaration behavior match the PRD: draft before submit, locked after validation, and corrections through versioning/reopen.

### Backend
- Add declaration `version` and `is_locked` if missing.
- Support:
  - save draft
  - submit with `certified_true`
  - validate
  - request clarification
  - reopen with doctor authorization
  - create new version on correction
- Add route aliases:
  - `GET /api/assessments/:id/declaration/`
  - `PATCH /api/assessments/:id/declaration/`
  - `POST /api/assessments/:id/declaration/submit/`
  - `POST /api/assessments/:id/declaration/validate/`
  - `POST /api/assessments/:id/declaration/reopen/`
- Preserve existing submit endpoint compatibility.

### Frontend
- Build `HealthDeclarationForm`.
- Add risk flag warning text:
  - “This does not automatically disqualify you. A doctor will review your response.”
- Food handler declaration page supports draft and submit.
- Doctor panel shows version, risk flag, clarification history, and lock state.

### Acceptance Criteria
- Food handler can draft before submission.
- Submitted declarations are read-only to food handler.
- Validated declarations are locked.
- Corrections create a new version or explicit reopened version.

### Checks
- Declaration versioning, lock, and privacy tests.

---

## Chunk AW4: Physical Exam Draft, Risk Flag, Completion, and Doctor Safeguards

### Goal
Harden physical examination as a clinical workflow with draft, completion, risk flag, and sensitive notes.

### Backend
- Add missing risk flag fields if needed.
- Support draft save and explicit complete action:
  - `GET /api/assessments/:id/physical-exam/`
  - `POST/PATCH /api/assessments/:id/physical-exam/`
  - `POST /api/assessments/:id/physical-exam/complete/`
- Ensure only assigned/authorized doctor can complete.
- Audit physical exam view and completion.
- Employer/public serializers must not expose exam detail.

### Frontend
- Build/standardize `PhysicalExamForm`.
- Doctor detail page should show save draft and complete states.
- Show risk flags clearly without overstating diagnosis.

### Acceptance Criteria
- Doctor can save draft and complete exam.
- Completion updates status engine.
- Sensitive notes are role-restricted.

### Checks
- Backend doctor authorization and privacy tests.
- Frontend typecheck/lint.

---

## Chunk AW5: Lab Test Request Policy, Required Tests, Repeat Tests, and Privacy

### Goal
Align lab request behavior with required FoodCert tests and repeat-test policy.

### Backend
- Add policy-backed required tests:
  - stool microscopy
  - stool culture and sensitivity
  - Hepatitis A antigen
- Support additional doctor-requested tests.
- Add repeat request support:
  - `parent_lab_test`
  - repeat reason
  - repeat required status
  - `POST /api/lab-tests/:id/request-repeat/`
- Ensure positive/inconclusive results are flagged.
- Hide detailed lab results from employers/public/finance users.

### Frontend
- Build `LabTestRequestForm`.
- Doctor can request required and additional tests.
- Doctor can request repeat tests from result review.
- Facility/lab queues show repeat/inconclusive status.

### Acceptance Criteria
- Required tests can be requested consistently.
- Repeat tests preserve linkage to original lab test.
- Lab details remain private outside authorized roles.

### Checks
- Backend lab request/repeat/privacy tests.

---

## Chunk AW6: Lab Staff Workflow Hardening: Sample, Result, Upload, Submit

### Goal
Make lab staff workflow complete and ergonomic from request queue to doctor submission.

### Backend
- Confirm lab staff can:
  - view only facility/department scoped requests
  - mark sample collected
  - enter result status and summary
  - upload result file
  - submit to doctor
- Add missing status aliases:
  - requested
  - sample_collection_pending
  - sample_collected
  - in_progress
  - result_uploaded
  - submitted_to_doctor
- Audit lab result access and submission.

### Frontend
- Polish:
  - `/lab/test-requests`
  - `/lab/test-requests/:id`
  - `/lab/results`
- Show queue filters and clear result state transitions.

### Acceptance Criteria
- Lab staff can complete the workflow without doctor privileges.
- Result submission updates assessment lab status.

### Checks
- Backend lab role tests.
- Frontend typecheck/lint/build.

---

## Chunk AW7: Doctor Lab Result Review, Positive/Inconclusive Handling, Repeats

### Goal
Let doctors review lab evidence and route positive/inconclusive results correctly.

### Backend
- Add/confirm doctor review action:
  - `POST /api/lab-tests/:id/review/`
- Capture doctor review notes separately from lab result summary.
- Positive and inconclusive results should support:
  - repeat request
  - temporary not-fit recommendation
  - public health clearance requirement where applicable
- Audit review.

### Frontend
- Build/standardize `LabResultReviewPanel`.
- Doctor detail page should display:
  - lab result statuses
  - uploaded file links
  - repeat button
  - review decision

### Acceptance Criteria
- Doctor review is required before final decision.
- Inconclusive results can trigger repeat tests.
- Employers see only limited lab status.

### Checks
- Backend review/repeat/status tests.

---

## Chunk AW8: Vaccination Review Expansion and Employer-Safe Compliance Statuses

### Goal
Complete vaccination review fields and policy-driven compliance outputs.

### Backend
- Expand vaccination records/reviews if missing:
  - brand name
  - batch number
  - vaccinator name
  - facility name/address
  - certificate upload
  - next dose date
- Policy-driven rules:
  - typhoid default validity 3 years
  - Hepatitis A second dose due at 6 months
  - other vaccines configurable later
- Add actions:
  - mark valid
  - mark missing
  - mark expired
  - mark incomplete
  - prescribe
  - administer
- Expose employer-safe compliance:
  - compliant
  - due
  - expired
  - second dose pending

### Frontend
- Build/standardize `VaccinationReviewPanel`.
- Food handler sees vaccination status and next dose date.
- Employer sees compliance status only.

### Acceptance Criteria
- Vaccination review can block final fit decision when required.
- Employer cannot see clinical/vaccination notes.

### Checks
- Backend policy/compliance/privacy tests.

---

## Chunk AW9: Fitness Decision Drafts, Return-to-Work Trigger, and Operational Statuses

### Goal
Harden decision workflow beyond final sign-off by adding draft support and automatic return-to-work triggers.

### Backend
- Add decision draft/save if needed without mutating final immutable decision.
- Finalization remains digitally signed and immutable.
- Temporarily not-fit creates or links a return-to-work/illness workflow record.
- Decision outcomes update food handler operational status.
- `requires_public_health_clearance` should map to illness/public-health clearance workflow.
- Not-fit generates report and blocks State submission.

### Frontend
- Extend `FitnessDecisionForm`.
- Show temporary restriction and RTW requirements.
- Employer-safe pages should show operational category only.

### Acceptance Criteria
- Temporary not-fit triggers return-to-work workflow.
- Not-fit never offers certificate submission.
- Fit becomes ready for State submission.

### Checks
- Backend finalization, immutability, RTW trigger, and employer privacy tests.

---

## Chunk AW10: State Submission Aliases, Clarification State Sync, and Certificate Handoff

### Goal
Ensure assessment workflow and certificate workflow stay synchronized.

### Backend
- Add direct assessment alias if missing:
  - `POST /api/assessments/:id/submit-to-state/`
- Keep facility nested submission route.
- Sync statuses:
  - ready for state submission
  - submitted to state
  - clarification requested
  - clarification responded
  - approved by state
  - rejected by state
  - certificate issued
- Notifications:
  - facility admin
  - assigned doctor
  - food handler where appropriate
- Audit submission and clarification.

### Frontend
- Add `SubmitToStatePanel` reusable component.
- Facility detail uses same component.
- State certificate validation pages should show assessment evidence summary.

### Acceptance Criteria
- Fit assessments route to State validation, never direct facility issuance.
- Clarification loop is visible and answerable.
- Certificate issuance follows State approval.

### Checks
- Backend submission/clarification/certificate handoff tests.

---

## Chunk AW11: Assessment Reports and Role-Safe Report Access

### Goal
Provide all assessment-related report types with strict role-based access.

### Backend
- Add report endpoints:
  - `GET /api/assessments/:id/reports/`
  - `GET /api/assessments/:id/reports/summary/`
  - `GET /api/assessments/:id/reports/medical/`
  - `GET /api/assessments/:id/reports/return-to-work/`
- Generate:
  - assessment summary report
  - medical examination report
  - temporarily not-fit report
  - return-to-work clearance report
  - vaccination review report
  - restricted lab summary report
- Role access matrix:
  - doctor: full medical report
  - lab staff: lab section only
  - facility admin: operational/admin summary
  - state: assessment summary/evidence
  - employer: operational status only
  - public: no assessment report access

### Frontend
- Add report views for food handler, doctor, facility, and state.
- Use download links only when API permits.

### Acceptance Criteria
- Report access matches PRD matrix.
- Sensitive report views are audit logged.

### Checks
- Backend report permission/privacy tests.

---

## Chunk AW12: Audit Timeline, Sensitive-Access Logging, and Status History

### Goal
Make the assessment workflow fully auditable and visible to authorized users.

### Backend
- Add or expose assessment audit timeline.
- Log every PRD event:
  - assessment created
  - prerequisite checks
  - declaration submit/validate/reopen
  - physical exam start/complete
  - lab request/sample/result/submit/review/repeat
  - vaccination reviewed/prescribed/administered
  - decision drafted/finalized
  - State submission/clarification
  - RTW workflow created/cleared
  - sensitive medical record viewed
  - cancelled/closed
- Consider `AssessmentStatusHistory` if audit logs alone are insufficient.

### Frontend
- Build `AssessmentAuditTimeline`.
- Show to facility admin/doctor/state where permitted.
- Hide from employer/public.

### Acceptance Criteria
- Authorized users can see a trustworthy timeline.
- Sensitive record access is logged.

### Checks
- Audit log assertions in backend tests.

---

## Chunk AW13: Cross-Role Privacy, Permission Regression Tests, and API Hardening

### Goal
Harden all workflow APIs against cross-role data leakage.

### Backend
- Regression tests for:
  - food handler own-assessment scoping
  - employer linked-handler operational status only
  - facility organization scoping
  - doctor assigned-assessment scoping
  - lab facility/department scoping
  - state own-state scoping
  - federal aggregate-only default
  - public no assessment access
  - finance no medical details
- Ensure serializers are separated:
  - public
  - employer-safe
  - food-handler-safe
  - facility-admin-safe
  - clinical
  - regulatory
- Confirm full NIN is masked outside authorized contexts.

### Frontend
- Hide forbidden actions by role.
- Ensure pages fail gracefully on 403/404.

### Acceptance Criteria
- No role can view or mutate out-of-scope assessment data.
- Employer/public never receive sensitive medical fields.

### Checks
- Backend privacy test matrix.
- Frontend typecheck/lint.

---

## Chunk AW14: Frontend Product Polish and Final QA

### Goal
Make the assessment workflow feel product-complete across food handler, doctor, lab, facility, and state users.

### Frontend
- Replace remaining placeholder assessment pages.
- Standardize:
  - loading states
  - empty states
  - error states
  - success banners
  - status badges
  - stepper layout
  - mobile table behavior
- Add route-level polish:
  - food handler assessment status
  - declaration
  - vaccination status
  - reports
  - doctor decision
  - lab queue/detail
  - facility assessment detail
  - state validation detail

### Backend
- Final QA:
  - migration drift
  - Django system check
  - affected test suite
  - audit/privacy assertions

### Acceptance Criteria
- Assessment workflow can be completed end-to-end:
  - create assessment
  - verify prerequisites
  - submit declaration
  - doctor validate/exam
  - lab request/result/review
  - vaccination review
  - doctor decision
  - State submission
  - State approval
  - certificate issuance
- No assessment placeholder pages remain for target MVP users.

### Final Checks
- `cd backend && PYTHONPYCACHEPREFIX=/private/tmp/foodcert-pycache ./.venv/bin/python manage.py makemigrations --check --dry-run`
- `cd backend && PYTHONPYCACHEPREFIX=/private/tmp/foodcert-pycache ./.venv/bin/python manage.py check`
- `cd backend && PYTHONPYCACHEPREFIX=/private/tmp/foodcert-pycache ./.venv/bin/python manage.py test apps.assessments apps.lab_tests apps.vaccinations apps.illness apps.certificates apps.facilities apps.reports apps.notifications apps.audit`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run lint`
- `cd frontend && npm run build`
