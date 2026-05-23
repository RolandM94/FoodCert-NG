# Assessment Workflow Route and Gap Map

## Purpose

This file maps `FOODCERT_MEDICAL_ASSESSMENT_WORKFLOW_PRD.md` to the current FoodCert NG implementation so the AW chunks can build incrementally without duplicating existing facility, doctor, lab, certificate, and illness workflows.

## Current Backend Model Inventory

| Area | Current Model(s) | Current Status |
|------|------------------|----------------|
| Appointment | `assessments.Appointment` | Exists with facility, doctor assignment, payment-gated confirmation, reschedule/cancel/no-show |
| Medical assessment | `assessments.MedicalAssessment` | Exists with food handler, employer, facility, doctor, appointment, payment, step statuses, final decision, signature fields |
| Health declaration | `assessments.HealthDeclaration` | Exists with PRD questions, risk flag, certified true, submit/validate/clarification fields |
| Physical exam | `assessments.PhysicalExamination` | Exists with checklist, notes, examined by/at |
| Lab tests | `lab_tests.LabTest` | Exists with required test types, result document, sample/result/submission/review timestamps |
| Vaccination review | `vaccinations.VaccinationRecord` | Exists for typhoid, Hepatitis A, status derivation, doctor review |
| Fitness decision | `assessments.MedicalAssessment` fields | Implemented as final decision fields on assessment rather than separate `FitnessDecision` model |
| Return to work | `illness.IllnessReport` | Exists for employer/food-handler illness and doctor clearance, but not yet fully auto-created from temporary not-fit decisions |
| State validation | `certificates.CertificateRequest` | Exists and is used for State certificate validation queue |
| Reports | `reports.GeneratedReport` | Exists for generated reports, medical examination reports, and exports |
| Audit | `audit.AuditLog` | Exists and is used across workflow transitions and sensitive medical access |

## Current Status Mapping

| PRD Status | Current Equivalent | Gap / Action |
|------------|--------------------|--------------|
| Draft | `draft` | Exists |
| Awaiting NIN Verification | none | AW1 should expose as calculated blocker/status, avoid breaking stored status unless needed |
| Awaiting Payment | `payment_pending` | Exists |
| Payment Confirmed | `payment_confirmed` | Exists |
| Appointment Booked | `appointment_booked` | Exists |
| Declaration Pending | `declaration_status=pending` | Step status exists, stored assessment status missing |
| Declaration Submitted | `declaration_submitted` | Exists |
| Declaration Validated | `declaration_validated` | Exists |
| Physical Exam Pending | `physical_exam_status=pending` | Step status exists, stored assessment status missing |
| Physical Exam Completed | `physical_exam_completed` | Exists |
| Lab Tests Pending | `lab_tests_pending` | Exists |
| Lab Results Submitted | `lab_status=submitted` | Step status exists, stored assessment status missing |
| Lab Results Reviewed | `lab_results_reviewed` and `lab_status=reviewed` | Exists |
| Vaccination Review Pending | `vaccination_status=pending` | Step status exists, stored assessment status missing |
| Vaccination Reviewed | `vaccination_reviewed` and `vaccination_status=reviewed` | Exists |
| Doctor Decision Pending | `doctor_decision_pending` | Exists |
| Requires Vaccination | `final_decision=requires_vaccination` | Exists as decision, not stored status |
| Requires Lab Test | `final_decision=requires_lab_test` | Exists as decision, not stored status |
| Requires Re-Examination | `final_decision=requires_recheck` | Exists as decision naming variant |
| Temporarily Not Fit | `temporarily_not_fit` | Exists |
| Not Fit | `not_fit` | Exists |
| Fit | `fit` | Exists |
| Ready for State Submission | `can_request_certificate=true` | Calculated, no stored status |
| Submitted to State | `submitted_for_state_validation` and certificate request `pending_validation` | Exists |
| Clarification Requested | certificate request `correction_requested` | Exists, not mirrored to assessment status |
| Clarification Responded | certificate request response fields + `pending_validation` | Exists, not mirrored to assessment status |
| Approved by State | certificate request `approved` | Exists, not mirrored to assessment status |
| Rejected by State | certificate request `rejected` | Exists, not mirrored to assessment status |
| Certificate Issued | `certificate_issued` | Exists |
| Closed | `closed` | Exists, close/cancel actions need AW1 hardening |

## Current API Route Inventory

### Assessment and Appointment

| PRD Route | Current Route | Gap / Action |
|-----------|---------------|--------------|
| `POST /api/assessments` | `POST /api/assessments/` | Exists |
| `GET /api/assessments` | `GET /api/assessments/` | Exists |
| `GET /api/assessments/:id` | `GET /api/assessments/:id/` | Exists |
| `PATCH /api/assessments/:id` | `PATCH /api/assessments/:id/` | Exists |
| `POST /api/assessments/:id/cancel` | none | AW1 |
| `POST /api/assessments/:id/close` | none | AW1 |
| `GET /api/assessments/:id/status` | none | AW1 |
| Appointment management | `GET/POST/PATCH /api/appointments/`, `confirm`, `reschedule`, `cancel`, `no-show`, `assign-doctor` | Exists |

### Declaration

| PRD Route | Current Route | Gap / Action |
|-----------|---------------|--------------|
| `GET /api/assessments/:id/declaration` | detail includes declaration for clinical/facility roles | Dedicated alias missing |
| `POST /api/assessments/:id/declaration` | `POST /api/assessments/:id/declaration/` | Exists as submit, not draft |
| `PATCH /api/assessments/:id/declaration` | none | AW3 draft/correction |
| `POST /api/assessments/:id/declaration/submit` | none | AW3 alias |
| `POST /api/assessments/:id/declaration/validate` | doctor alias exists: `/api/doctor/assessments/:id/declaration/validate/` | AW3 can add generic alias |
| `POST /api/assessments/:id/declaration/reopen` | none | AW3 |

### Physical Examination

| PRD Route | Current Route | Gap / Action |
|-----------|---------------|--------------|
| `GET /api/assessments/:id/physical-exam` | detail includes physical exam for clinical/facility roles | Dedicated alias missing |
| `POST /api/assessments/:id/physical-exam` | doctor alias exists: `/api/doctor/assessments/:id/physical-exam/`; generic current route is `/physical-examination/` | Naming alias gap |
| `PATCH /api/assessments/:id/physical-exam` | none | AW4 draft update |
| `POST /api/assessments/:id/physical-exam/complete` | current post completes immediately | AW4 explicit completion alias |

### Lab Tests

| PRD Route | Current Route | Gap / Action |
|-----------|---------------|--------------|
| `GET /api/assessments/:id/lab-tests` | detail includes tests; `POST /api/assessments/:id/lab-tests/` exists | GET alias missing |
| `POST /api/assessments/:id/lab-tests` | `POST /api/assessments/:id/lab-tests/` | Exists |
| `GET /api/lab-tests/:id` | `GET /api/lab-tests/:id/` | Exists |
| `PATCH /api/lab-tests/:id/sample-collected` | lab alias exists under `/api/lab/requests/:id/collect-sample/` | Naming alias gap |
| `PATCH /api/lab-tests/:id/result` | `PATCH /api/lab-tests/:id/result/` and lab alias | Exists |
| `POST /api/lab-tests/:id/upload-result` | lab alias exists under `/api/lab/requests/:id/upload-result/` | Generic alias gap |
| `POST /api/lab-tests/:id/submit-to-doctor` | lab alias exists under `/api/lab/requests/:id/submit-to-doctor/` | Generic alias gap |
| `POST /api/lab-tests/:id/review` | `PATCH /api/lab-tests/:id/review/` | Exists with method/naming difference |
| `POST /api/lab-tests/:id/request-repeat` | none | AW5/AW7 |

### Vaccination Review

| PRD Route | Current Route | Gap / Action |
|-----------|---------------|--------------|
| `GET /api/assessments/:id/vaccination-reviews` | detail includes vaccinations | Dedicated alias missing |
| `POST /api/assessments/:id/vaccination-reviews` | `POST /api/assessments/:id/vaccinations/` and doctor review alias | Naming alias gap |
| `PATCH /api/vaccination-reviews/:id` | `PATCH /api/vaccinations/:id/` depends on viewset support | Verify in AW8 |
| `mark-valid`, `mark-missing`, `prescribe`, `administer` | doctor review supports status values | Explicit action aliases missing |

### Fitness Decision and State Submission

| PRD Route | Current Route | Gap / Action |
|-----------|---------------|--------------|
| `GET /api/assessments/:id/fitness-decision` | assessment detail includes final decision fields | Dedicated alias missing |
| `POST/PATCH /api/assessments/:id/fitness-decision` | `PATCH /api/assessments/:id/fitness-decision/`; doctor alias exists | Exists for final update |
| `POST /api/assessments/:id/fitness-decision/finalize` | current patch finalizes immediately with signature confirmation | AW9 draft/finalize split |
| `POST /api/assessments/:id/submit-to-state` | nested facility route exists | Direct assessment alias missing |

### Reports

| PRD Route | Current Route | Gap / Action |
|-----------|---------------|--------------|
| `GET /api/assessments/:id/reports` | `GeneratedReport` records exist | Dedicated assessment report list missing |
| `GET /api/assessments/:id/reports/summary` | generated summary exists internally | Alias missing |
| `GET /api/assessments/:id/reports/medical` | generated medical report exists | Alias/access control missing |
| `GET /api/assessments/:id/reports/return-to-work` | illness RTW certificate exists | Alias missing |

## Current Frontend Route Inventory

| User Area | Current Route(s) | Status |
|-----------|------------------|--------|
| Food handler assessments | `/food-handler/assessments` | Placeholder/proxy shell, AW2 |
| Food handler assessment detail | missing `/food-handler/assessments/:id` | AW2 |
| Food handler declaration | `/food-handler/declaration` | Placeholder/proxy shell, AW2/AW3 |
| Food handler certificate | `/food-handler/certificate` | Placeholder/proxy shell, later AW2/AW11 |
| Doctor queue | `/doctor/assessments` | Working queue |
| Doctor detail | `/doctor/assessments/:id` | Working combined workflow detail |
| Doctor subroutes | declaration-review, physical-exam, lab-results, vaccinations, fitness-decision | Thin proxy routes to detail page |
| Lab queue/detail | `/lab/test-requests`, `/lab/test-requests/:id` | Working |
| Lab dashboard/results | `/lab/dashboard`, `/lab/results` | Placeholder/proxy shell, AW6/AW14 |
| Facility queue/detail | `/facility/assessments`, `/facility/assessments/:id` | Working |
| Facility certificates | `/facility/certificates` | Working State validation/certificate view |
| State validation | `/state/certificate-requests` | Working validation queue |

## Implementation Risks and Decisions

- Do not split `FitnessDecision` into a new model unless a later chunk proves the current assessment-field approach cannot support draft/finalize/report access cleanly.
- Do not rename stored statuses broadly. Prefer calculated status snapshots and additive aliases to protect existing tests and integrations.
- Treat certificate request statuses as the State validation source of truth, and mirror only where the UX needs assessment-level display.
- Keep existing facility/doctor/lab endpoints working while adding PRD aliases.
- Employer, finance, public, and default federal views must remain medically safe.

## AW0 Outcome

AW0 establishes that the workflow is already partly implemented through the medical facility module. The next chunks should prioritize:

1. Status snapshot and blocker API.
2. Food-handler-facing assessment UX.
3. Declaration versioning/reopen.
4. Repeat lab test support.
5. Return-to-work auto-trigger from temporary not-fit.
6. Role-safe assessment report access.
