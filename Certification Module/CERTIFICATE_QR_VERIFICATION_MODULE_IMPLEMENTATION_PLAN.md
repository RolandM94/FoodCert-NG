# Certificate & QR Verification Module — Implementation Plan

## Audit Summary

| Component | Status |
|-----------|--------|
| Certificate request model and State validation queue | Mostly done |
| State approve/reject/clarification workflow | Mostly done |
| Certificate issuance service after State approval | Mostly done |
| Eligibility gates for payment, NIN, facility, doctor, lab, vaccination, and final decision | Mostly done |
| Facility accreditation-at-assessment validation | Partial |
| Unresolved illness/exclusion validation | Missing |
| Certificate number generation | Partial; unique but not PRD state-year sequence/check format |
| Certificate immutability and replacement lineage | Missing |
| Certificate PDF generation | Basic placeholder exists |
| QR generation | Done, but uses certificate number URL rather than opaque token |
| Public verification endpoint/page | Started |
| Manual verification by certificate number | Partial through current public route |
| Public suspicious certificate report | Missing |
| Inspector QR verification and inspection save | Partial through inspection scan action |
| Employer-safe certificate visibility | Mostly done |
| Food handler certificate wallet/download UX | Partial |
| State certificate registry | Mostly done |
| State reinstate/replace/audit/export actions | Missing/partial |
| Federal certificate registry | Started |
| Federal analytics, suspicious flagging, and aggregate-first privacy | Partial |
| Certificate template model/API/UI | Missing |
| Expiry and renewal reminders | Partial in reports, missing scheduled jobs |
| Verification logs | Started, needs verifier type/token/location/detail expansion |
| Audit logs for certificate actions | Partial |
| Backend tests | Partial |
| Frontend product polish | Partial |

## Implementation Status

| Chunk | Status |
|-------|--------|
| CQ0 Baseline audit, route map, and regression inventory | Done |
| CQ1 Certificate trust model, immutable fields, token, and numbering | Done |
| CQ2 Eligibility gate hardening and State approve-and-generate flow | Done |
| CQ3 PDF template foundation and secure QR generation | Done |
| CQ4 Public verification, manual lookup, and suspicious report workflow | Done |
| CQ5 Food handler certificate wallet, download, share, and renewal entry | Done |
| CQ6 Employer certificate visibility, downloads, reminders, and export | Done |
| CQ7 Inspector scan, verification save, and field-friendly UX | Done |
| CQ8 State certificate registry actions: suspend, reinstate, revoke, replace, audit, export | Done |
| CQ9 Certificate renewal lifecycle and expiry notification jobs | Done |
| CQ10 Federal registry oversight, analytics, flagging, and privacy defaults | Done |
| CQ11 Certificate template and policy management | Done |
| CQ12 Audit logging, tamper detection, rate limiting, and security hardening | Done |
| CQ13 Frontend product polish across all certificate routes | Done |
| CQ14 Final QA, regression tests, and production readiness | Done |

## Existing Foundations To Reuse

- Backend apps: `certificates`, `assessments`, `ministries`, `inspections`, `employers`, `food_handlers`, `facilities`, `policy`, `reports`, `notifications`, `audit`.
- Existing certificate APIs:
  - `/api/certificate-requests/`
  - `/api/certificate-requests/:id/approve/`
  - `/api/certificate-requests/:id/reject/`
  - `/api/certificate-requests/:id/request-clarification/`
  - `/api/certificates/`
  - `/api/certificates/generate/`
  - `/api/certificates/:id/download/`
  - `/api/public/certificates/verify/:certificate_number/`
- Existing State APIs:
  - `/api/state/certificate-validation-queue/`
  - `/api/state/certificate-validation-queue/:id/approve/`
  - `/api/state/certificate-validation-queue/:id/reject/`
  - `/api/state/certificate-validation-queue/:id/request-clarification/`
  - `/api/state/certificates/`
  - `/api/state/certificates/:id/`
  - `/api/state/certificates/:id/suspend/`
  - `/api/state/certificates/:id/revoke/`
- Existing Federal API:
  - `/api/federal/certificates/`
- Existing inspection support:
  - `/api/inspections/:id/scan-certificate/`
- Existing frontend routes:
  - `/verify/[certificateNumber]`
  - `/food-handler/certificate`
  - `/facility/certificates`
  - `/state/certificate-requests`
  - `/state/certificates`
  - `/employer/certificates`
  - `/federal/certificates`
  - `/inspector/scan`

## Build Order

```txt
CQ0 → CQ1 → CQ2 → CQ3 → CQ4
 │     │     │     │     │
 ▼     ▼     ▼     ▼     ▼
Audit Trust Gates PDF Verify

CQ5 → CQ6 → CQ7 → CQ8
 │     │     │     │
 ▼     ▼     ▼     ▼
Handler Employer Inspector State

CQ9 → CQ10 → CQ11 → CQ12 → CQ13 → CQ14
 │      │       │       │       │       │
 ▼      ▼       ▼       ▼       ▼       ▼
Renew  Federal Template Secure  UX      QA
```

Each chunk should leave the product in a testable state. Reuse the existing services and routes first, then add aliases or new models only where the PRD requires behavior the current app cannot represent.

---

## Chunk CQ0: Baseline Audit, Route Map, and Regression Inventory

### Goal
Confirm the exact gap between the QR/certificate PRD and the current implementation before changing the trust layer.

### Backend
- Inventory current certificate models, serializers, services, API routes, audit logs, reports, notifications, inspections, and ministry registry routes.
- Create or update a concise route map in this plan if implementation discovers route drift.
- Identify current role serializers and privacy boundaries:
  - public
  - food handler
  - employer
  - inspector
  - state ministry
  - federal ministry
- Capture current status values and map them to PRD statuses:
  - `pending_validation`
  - `active`
  - `expired`
  - `suspended`
  - `revoked`
  - `replaced`
  - `rejected`
  - future `draft_generation_failed`
  - future `correction_pending`

### Frontend
- Inventory all certificate routes and identify placeholder pages.
- Confirm where certificate data is fetched from `frontend/src/lib/api/certificates.ts`, `state.ts`, `federal.ts`, and employer APIs.

### CQ0 Findings

#### Current Backend Route Map

| Area | Current Route | Status |
|------|---------------|--------|
| Certificate requests | `GET /api/certificate-requests/` | Exists |
| Certificate request detail | `GET /api/certificate-requests/:id/` | Exists |
| Certificate request approval | `PATCH /api/certificate-requests/:id/approve/` | Exists |
| Certificate request rejection | `PATCH /api/certificate-requests/:id/reject/` | Exists |
| Certificate request clarification | `PATCH /api/certificate-requests/:id/request-clarification/` | Exists |
| Certificate generation | `POST /api/certificates/generate/` | Exists |
| Certificate registry | `GET /api/certificates/` | Exists |
| Certificate detail | `GET /api/certificates/:id/` | Exists |
| Certificate download | `GET /api/certificates/:id/download/` | Exists |
| Certificate suspend | `PATCH /api/certificates/:id/suspend/` | Exists |
| Certificate revoke | `PATCH /api/certificates/:id/revoke/` | Exists |
| Public verification | `GET /api/public/certificates/verify/:certificate_number/` | Exists, certificate-number based |
| Assessment request certificate | `POST /api/assessments/:assessment_id/request-certificate/` | Exists |
| State validation queue | `GET /api/state/certificate-validation-queue/` | Exists |
| State validation detail | `GET /api/state/certificate-validation-queue/:id/` | Exists |
| State approve and generate | `PATCH /api/state/certificate-validation-queue/:id/approve/` | Exists and generates certificate |
| State reject | `PATCH /api/state/certificate-validation-queue/:id/reject/` | Exists |
| State clarification | `PATCH /api/state/certificate-validation-queue/:id/request-clarification/` | Exists |
| State registry | `GET /api/state/certificates/` | Exists |
| State registry detail | `GET /api/state/certificates/:id/` | Exists |
| State suspend | `PATCH /api/state/certificates/:id/suspend/` | Exists |
| State revoke | `PATCH /api/state/certificates/:id/revoke/` | Exists |
| Federal registry | `GET /api/federal/certificates/` | Exists |
| Inspection scan | `POST /api/inspections/:id/scan-certificate/` | Exists |

#### Current Backend Gaps

| PRD Need | Current Gap |
|----------|-------------|
| Opaque QR token verification | QR currently points to certificate-number verification. |
| `FCNG-{STATE}-{YEAR}-{SEQUENCE}-{CHECK}` numbering | Current format is `FCN-{STATE}-{YYYYMMDD}-{random}`. |
| Replacement lineage | No `replaced_by` or replacement action. |
| Reinstatement after suspension | Missing State/API service action. |
| Separate suspension metadata | Suspension reuses revoked fields. |
| Manual public verify by number POST | Current public verify is GET by certificate number. |
| Suspicious certificate report | Missing model/API/workflow. |
| Certificate template management | Missing model/API/UI. |
| Expiry and reminder jobs | Missing scheduled command/service; reports calculate expiry dynamically. |
| Generation failure recovery | Missing explicit `draft_generation_failed` state/retry flow. |
| Expanded verification logs | Current log lacks token attempted, verifier type, verifier user, and optional location. |
| Federal flagging/analytics | Federal registry exists; flagging and deeper certificate analytics are incomplete. |
| State audit/export endpoints | Missing dedicated certificate audit timeline and export endpoints. |

#### Current Frontend Route Map

| Route | Status |
|-------|--------|
| `/verify/[certificateNumber]` | Exists; public verification by certificate number. |
| Landing page verification form | Exists; sends users to `/verify/:certificateNumber`. |
| `/food-handler/certificate` | Exists; basic wallet/status page. |
| `/facility/certificates` | Exists; request and issued certificate tracking. |
| `/state/certificate-requests` | Exists; validation queue. |
| `/state/certificates` | Exists; registry with suspend/revoke. |
| `/employer/certificates` | Exists; table and metrics. |
| `/federal/certificates` | Exists; national registry table/export. |
| `/inspector/scan` | Placeholder `PortalPage`. |
| `/inspector/inspections/[id]` | Placeholder `PortalPage`. |
| `/verify` | Missing dedicated manual verification page. |
| `/verify/certificate-number` | Missing dedicated manual number page. |
| `/report-suspicious-certificate` | Missing. |
| `/state/certificates/[id]` | Missing dedicated detail page. |
| `/state/certificates/[id]/audit` | Missing. |
| `/state/certificate-templates` | Missing. |
| `/federal/certificates/[id]` | Missing. |
| `/federal/certificates/analytics` | Missing; broader federal analytics exists at `/federal/analytics`. |

#### Current Test Coverage

Existing certificate tests already cover:

- direct generation blocked before State approval
- clarification/status sync
- request requires State approval
- public verification privacy excludes obvious medical/private fields
- employer privacy serializer excludes medical/internal fields
- revoked certificate verifies as revoked
- non-fit assessment cannot request certificate
- policy can disable State validation.

Key missing regression tests:

- token-based verification
- hash tamper detection
- suspension-specific metadata and reinstatement
- replacement workflow
- suspicious report
- inspector scan via token and inspection save
- State-only registry scoping for lifecycle actions
- federal aggregate-first privacy
- certificate template permissions
- expiry/reminder job idempotency.

### Acceptance Criteria
- The team has a confirmed reuse map.
- No sensitive field is planned for public/employer/inspector serializers.
- Next chunks have clear file ownership.

### Checks
- `cd backend && PYTHONPYCACHEPREFIX=/private/tmp/foodcert-pycache ./.venv/bin/python manage.py check`
- `cd frontend && npm run typecheck`

---

## Chunk CQ1: Certificate Trust Model, Immutable Fields, Token, and Numbering

### Goal
Make certificate records tamper-resistant, non-guessable for QR verification, and capable of replacement lineage.

### Backend
- Extend `Certificate` with:
  - `public_id`
  - `verification_token`
  - `business_branch`
  - `replaced_by`
  - `replacement_reason`
  - `suspended_by`
  - `suspended_at`
  - `suspension_reason`
  - generation failure fields if using `draft_generation_failed`
- Consider adding `CertificateAction` for a permanent action timeline if `audit` records are not enough for registry display.
- Expand `CertificateVerificationLog` with:
  - token attempted
  - verifier type
  - verifier user
  - optional latitude/longitude
  - normalized result fields while preserving existing data.
- Replace certificate number generation with state-year sequence plus check segment:
  - format: `FCNG-{STATE_CODE}-{YEAR}-{SEQUENCE}-{CHECK}`
  - never reuse numbers
  - keep database uniqueness as final protection.
- Update HMAC/hash inputs to include immutable certificate fields and verification token.
- Add migrations and admin updates.

### Frontend
- Update `Certificate`, public verification, state registry, federal registry, and employer certificate types.
- Keep backward-compatible fields while backend transitions.

### Files
| Backend | Frontend |
|---------|----------|
| `backend/apps/certificates/models.py` | `frontend/src/types/certificates.ts` |
| `backend/apps/certificates/services.py` | `frontend/src/lib/api/certificates.ts` |
| `backend/apps/certificates/admin.py` | `frontend/src/lib/api/state.ts` |
| `backend/apps/certificates/migrations/*` | `frontend/src/lib/api/federal.ts` |

### Acceptance Criteria
- Certificate numbers follow the PRD format.
- QR verification can use an opaque token.
- Replacement lineage can be represented without editing original certificate identity.
- Hash mismatch can be detected deterministically.

### Checks
- Model migration check.
- Backend tests for uniqueness, token creation, hash verification, and replacement linkage.

---

## Chunk CQ2: Eligibility Gate Hardening and State Approve-and-Generate Flow

### Goal
Make State approval the single authoritative issuance trigger and ensure all PRD blockers are enforced.

### Backend
- Harden `CertificateService.validate_assessment_eligible`.
- Add missing blockers:
  - food handler profile completeness
  - facility accreditation valid at assessment time
  - unresolved illness or exclusion
  - valid certificate policy
  - certificate template availability after CQ11, with a temporary default until then
  - no existing certificate for same assessment
  - no conflicting active certificate unless renewal/replacement path permits it
- Add `CertificateIssuanceService.approve_and_generate` or equivalent service method that:
  - approves the request
  - generates the certificate
  - writes PDF/QR
  - logs audit
  - sends notifications
  - returns the issued certificate/request payload.
- Align `/api/state/certificate-validation-queue/:id/approve/` with approve-and-generate behavior.
- Add alias if useful:
  - `POST /api/state/certificate-validation/:assessment_id/approve-and-generate/`

### Frontend
- Update State validation detail/actions to show eligibility checklist and generation result.
- Avoid a separate manual "Generate" button for normal State approval unless the backend reports generation failure/retry.

### Acceptance Criteria
- A certificate cannot be generated before State approval when policy requires validation.
- State approval produces a certificate in one controlled transaction.
- Failed eligibility returns specific, role-safe blocker messages.

### Checks
- Backend workflow tests for every major blocker.
- Regression test that facility/doctor/food handler cannot generate certificates directly.

---

## Chunk CQ3: PDF Template Foundation and Secure QR Generation

### Goal
Produce a credible certificate PDF and QR artifact without exposing sensitive medical data.

### Backend
- Replace basic PDF output with a structured certificate layout:
  - platform name/logo
  - issuing State Ministry
  - certificate number
  - food handler name/photo
  - masked NIN or approved identifier
  - employer/branch where applicable
  - facility
  - doctor and registration number
  - assessment date
  - issue/expiry date
  - QR code
  - verification URL
  - digital hash/signature short display
  - privacy disclaimer.
- Ensure PDF excludes:
  - lab result details
  - diagnosis
  - doctor notes
  - declaration answers
  - full NIN.
- Generate QR from verification token URL, not embedded medical or identity data.
- Make artifact write failures auditable and recoverable.

### Frontend
- Add reusable `QRCodeDisplay`, `CertificatePreview`, and `CertificatePDFViewer` where useful.
- Ensure download links use backend download endpoints rather than raw storage URLs for protected contexts.

### Acceptance Criteria
- PDF can be downloaded by authorized users.
- QR scan lands on public verification.
- PDF/QR generation failure is not silent.

### Checks
- Backend tests for PDF/QR fields and privacy exclusions.
- Manual PDF spot-check from generated test certificate.

---

## Chunk CQ4: Public Verification, Manual Lookup, and Suspicious Report Workflow

### Goal
Make public verification trustworthy, privacy-safe, rate-limited, and usable without login.

### Backend
- Support:
  - `GET /api/public/certificates/verify/:verification_token/`
  - `POST /api/public/certificates/verify-by-number/`
  - `POST /api/public/certificates/report-suspicious/`
- Keep existing certificate-number route as backward-compatible alias if already used by issued QR codes.
- Return public-safe statuses:
  - valid
  - expired
  - revoked
  - suspended
  - replaced
  - invalid
  - not found.
- Log every verification attempt with verifier type and submitted token/number.
- Add tamper warning path for hash mismatch.
- Apply public throttling and safe error messages.

### Frontend
- Add/complete:
  - `/verify`
  - `/verify/[verificationToken]`
  - `/verify/certificate-number`
  - `/report-suspicious-certificate`
- Public verification page must show status-specific messaging and never medical details.
- Add print-friendly verification result.

### Acceptance Criteria
- Verification works by QR token and certificate number.
- Public response never exposes full NIN, lab results, diagnosis, doctor notes, declaration answers, payment, or employer private records.
- Suspicious report creates an auditable record/notification.

### Checks
- Public API tests for each status.
- Public privacy regression tests.
- Frontend typecheck/lint.

---

## Chunk CQ5: Food Handler Certificate Wallet, Download, Share, and Renewal Entry

### Goal
Give food handlers a clear self-service certificate area.

### Backend
- Ensure food handlers can list and retrieve only their own certificates.
- Add wallet-safe serializer if current general serializer exposes too much.
- Add renewal intent endpoint if needed:
  - `POST /api/food-handler/certificates/:id/start-renewal/`
- Audit certificate downloads and renewal starts.

### Frontend
- Replace or complete:
  - `/food-handler/certificate`
  - `/food-handler/certificates`
  - `/food-handler/certificates/[id]`
  - `/food-handler/certificates/[id]/renew`
- Show active, expiring, expired, suspended, revoked, and replaced states.
- Provide download, share link, QR display, and renewal CTA where policy permits.

### Acceptance Criteria
- Food handler understands certificate validity and next action.
- Food handler cannot access another handler certificate.
- Suspended/revoked notices are clear without exposing internal investigation details.

### Checks
- Backend ownership tests.
- Frontend typecheck/lint.

---

## Chunk CQ6: Employer Certificate Visibility, Downloads, Reminders, and Export

### Goal
Make employer certificate management operational without leaking medical data.

### Backend
- Harden employer certificate queryset:
  - linked employer only
  - organization unit/branch scoping
  - unit-restricted users only see their unit.
- Add/complete:
  - `GET /api/employers/:id/certificates/`
  - `GET /api/employers/:id/certificates/:certificate_id/`
  - `GET /api/employers/:id/certificates/:certificate_id/download/`
  - `POST /api/employers/:id/certificates/:certificate_id/send-renewal-reminder/`
- Audit employer downloads and reminder sends.

### Frontend
- Complete `/employer/certificates` and `/employer/certificates/[id]`.
- Add filters for status, branch, facility, expiry window.
- Add CSV export using employer-safe fields only.
- Add renewal reminder action.

### Acceptance Criteria
- Employer can manage compliance by certificate state and expiry.
- Employer cannot see medical assessment details or full NIN.
- Branch-restricted employer users cannot see certificates outside their branch.

### Checks
- Backend scope/privacy tests.
- Frontend typecheck/lint.

---

## Chunk CQ7: Inspector Scan, Verification Save, and Field-Friendly UX

### Goal
Give inspectors a mobile-first verification flow that can be tied to inspections.

### Backend
- Add inspector-specific verification endpoints if current inspection action is insufficient:
  - `GET /api/inspector/certificates/verify/:verification_token/`
  - `POST /api/inspector/certificates/verify-by-number/`
  - `POST /api/inspector/certificates/:id/save-to-inspection/`
  - `POST /api/inspector/certificates/:id/flag/`
- Reuse `InspectionCertificateScan` where possible.
- Log verifier type as inspector.
- Add suspicious flag notifications to State/Federal where relevant.

### Frontend
- Replace `/inspector/scan` placeholder with:
  - QR scanner where browser support exists
  - manual certificate number fallback
  - result panel
  - save-to-inspection action
  - suspicious flag action
  - continue inspection CTA.

### Acceptance Criteria
- Inspector can verify certificate in the field on mobile.
- Inspector-safe result excludes medical details.
- Verification result can be attached to an inspection record.

### Checks
- Backend tests for scan/save/flag permissions.
- Frontend typecheck/lint.
- Browser smoke test on mobile viewport.

---

## Chunk CQ8: State Certificate Registry Actions

### Goal
Make State Ministry registry management complete and audit-ready.

### Backend
- Complete State APIs:
  - `GET /api/state/certificates/`
  - `GET /api/state/certificates/:id/`
  - `PATCH /api/state/certificates/:id/suspend/`
  - `PATCH /api/state/certificates/:id/reinstate/`
  - `PATCH /api/state/certificates/:id/revoke/`
  - `POST /api/state/certificates/:id/replace/`
  - `GET /api/state/certificates/:id/audit/`
  - `GET /api/state/certificates/export/`
- Enforce:
  - State users only manage certificates issued by their state.
  - Suspension requires reason and can be reinstated.
  - Revocation requires reason and cannot be reversed.
  - Replacement creates a new certificate and marks the original `replaced`.
- Add notifications to food handler, employer, facility, and relevant ministry users.

### Frontend
- Complete `/state/certificates` and `/state/certificates/[id]`.
- Add modals:
  - suspend
  - reinstate
  - revoke
  - replace.
- Add audit timeline page:
  - `/state/certificates/[id]/audit`
- Add export action.

### Acceptance Criteria
- State registry can perform all PRD lifecycle actions.
- Public verification reflects suspension/revocation/replacement immediately.
- Lifecycle actions are permanently auditable.

### Checks
- Backend transition tests.
- State scoping regression tests.
- Frontend typecheck/lint.

---

## Chunk CQ9: Certificate Renewal Lifecycle and Expiry Notification Jobs

### Goal
Make certificate expiry and renewal proactive instead of report-only.

### Backend
- Add renewal status helpers:
  - not started
  - started
  - assessment pending
  - awaiting State validation
  - new certificate issued
  - overdue.
- Add management commands or scheduled-job-ready service methods:
  - daily expiry marker
  - 30-day reminder
  - 7-day reminder
  - generation retry for safe failed artifacts.
- Notify:
  - food handler
  - employer
  - facility where appropriate.
- Ensure default renewal requires a fresh assessment.

### Frontend
- Show renewal status on food handler and employer certificate pages.
- Add renewal reminder actions and clear expired/overdue states.

### Acceptance Criteria
- Expired certificates become invalid automatically.
- Expiring certificates create notifications.
- Renewal does not mutate the old certificate.

### Checks
- Backend tests for jobs and notification idempotency.
- Frontend typecheck/lint.

---

## Chunk CQ10: Federal Registry Oversight, Analytics, Flagging, and Privacy Defaults

### Goal
Give Federal Ministry national oversight without turning federal views into unrestricted medical or identity access.

### Backend
- Expand federal certificate registry filters:
  - state
  - status
  - facility
  - employer
  - issue date
  - expiry date
  - suspicious flags.
- Add aggregate analytics:
  - issuance by state
  - revocation/suspension rates
  - expired/expiring counts
  - invalid verification attempt trends
  - high-risk states/facilities.
- Add flag action:
  - `POST /api/federal/certificates/:id/flag/`
- Ensure individual detail is permission-gated and audit logged.

### Frontend
- Complete:
  - `/federal/certificates`
  - `/federal/certificates/[id]`
  - `/federal/certificates/analytics`
  - `/federal/certificate-registry`
- Default federal dashboards to aggregate metrics and privacy-safe tables.

### Acceptance Criteria
- Federal users can monitor national certificate trust.
- Sensitive individual access is permission-controlled and audited.
- Federal cannot revoke/replace State certificates unless explicit policy says so.

### Checks
- Backend federal privacy tests.
- Frontend typecheck/lint.

---

## Chunk CQ11: Certificate Template and Policy Management

### Goal
Support national and state certificate templates while preserving platform consistency.

### Backend
- Add `CertificateTemplate` model if no equivalent exists:
  - national/state scope
  - state
  - logo/signatory fields
  - status
  - default marker
  - created by.
- Add APIs:
  - `GET /api/certificate-templates/`
  - `POST /api/certificate-templates/`
  - `GET /api/certificate-templates/:id/`
  - `PATCH /api/certificate-templates/:id/`
  - `DELETE /api/certificate-templates/:id/`
  - `POST /api/certificate-templates/:id/set-default/`
- Enforce policy:
  - federal can manage national defaults
  - state can manage state templates only where policy permits
  - super admin can resolve emergency/template failures.
- Integrate template selection into PDF generation.

### Frontend
- Add:
  - `/state/certificate-templates`
  - `/admin/certificate-templates`
  - use existing `/federal/policy-config` for defaults if appropriate.
- Build `CertificateTemplateEditor`.

### Acceptance Criteria
- Certificate generation uses an active default template.
- State branding/signatory can be applied when policy allows.
- Template changes are audited.

### Checks
- Backend tests for template permissions/default selection.
- Frontend typecheck/lint.

---

## Chunk CQ12: Audit Logging, Tamper Detection, Rate Limiting, and Security Hardening

### Goal
Close the trust and privacy gaps before final UI polish.

### Backend
- Ensure audit events exist for:
  - State certificate approval
  - generation
  - PDF generation
  - QR generation
  - public verification
  - inspector verification
  - employer download
  - food handler download
  - suspension
  - reinstatement
  - revocation
  - replacement
  - renewal start
  - template update
  - policy update
  - suspicious report
  - failed generation
  - hash mismatch.
- Harden rate limiting for public verification and suspicious reports.
- Add privacy regression tests for public, employer, inspector, federal, and state serializers.
- Add tamper test by modifying a hash-relevant field and verifying public result becomes invalid.

### Frontend
- Ensure error states are safe and non-technical.
- Ensure no route renders sensitive fields from broader serializers.

### Acceptance Criteria
- All sensitive certificate access/action paths are auditable.
- Public abuse patterns are throttled.
- Tampered certificates fail verification.

### Checks
- Backend API/security/privacy tests.
- Frontend typecheck/lint.

---

## Chunk CQ13: Frontend Product Polish Across Certificate Routes

### Goal
Make certificate workflows feel complete across every actor.

### Frontend
- Build/standardize components:
  - `CertificateStatusBadge`
  - `CertificatePreview`
  - `CertificatePDFViewer`
  - `QRCodeDisplay`
  - `QRScanner`
  - `PublicVerificationResult`
  - `CertificateNumberVerificationForm`
  - `CertificateRegistryTable`
  - `CertificateValidationChecklist`
  - `CertificateIssuancePanel`
  - `CertificateAuditTimeline`
  - `CertificateSuspensionModal`
  - `CertificateRevocationModal`
  - `CertificateReplacementModal`
  - `CertificateRenewalCard`
  - `CertificateTemplateEditor`
  - `CertificateAnalyticsCards`
  - `SuspiciousCertificateReportForm`
  - `InspectorVerificationPanel`
  - `EmployerCertificateTable`.
- Replace remaining certificate `PortalPage` placeholders.
- Check mobile layouts for:
  - public verification
  - inspector scan
  - food handler certificate wallet
  - employer certificate table
  - state registry.

### Backend
- Fix any response shape issues discovered by frontend integration.

### Acceptance Criteria
- Every PRD route has a real workflow page or a deliberate redirect to an equivalent page.
- No text overlaps or broken tables on mobile.
- Empty, loading, error, and success states are present.

### Checks
- `cd frontend && npm run typecheck`
- `cd frontend && npm run lint`
- `cd frontend && npm run build`
- Browser smoke tests for public, inspector, employer, state, and federal certificate routes.

---

## Chunk CQ14: Final QA, Regression Tests, and Production Readiness

### Goal
Verify the module end to end as the official certificate trust layer.

### Backend
- Add end-to-end tests:
  - assessment fit → facility submit → State approve → certificate generated → public verify valid
  - expired certificate verifies expired
  - suspended certificate verifies suspended, then reinstates
  - revoked certificate verifies revoked and cannot reinstate
  - replaced certificate keeps old number and links new certificate
  - public suspicious report is logged
  - inspector scan saves to inspection
  - employer cannot see medical fields
  - federal aggregate view does not expose sensitive data by default.
- Confirm migrations are complete.
- Confirm generated artifacts are ignored or stored safely.

### Frontend
- Run full certificate route QA.
- Confirm production build.
- Confirm public verification works without auth token.

### Acceptance Criteria
- Certificate module can be demoed end to end.
- Public, employer, inspector, State, and Federal privacy boundaries pass tests.
- All placeholder certificate pages are removed or redirected.
- No known critical product gaps remain for MVP.

### Final Checks
- `cd backend && PYTHONPYCACHEPREFIX=/private/tmp/foodcert-pycache ./.venv/bin/python manage.py makemigrations --check --dry-run`
- `cd backend && PYTHONPYCACHEPREFIX=/private/tmp/foodcert-pycache ./.venv/bin/python manage.py check`
- `cd backend && PYTHONPYCACHEPREFIX=/private/tmp/foodcert-pycache ./.venv/bin/python manage.py test apps.certificates apps.assessments apps.ministries apps.inspections apps.employers apps.food_handlers apps.reports apps.notifications apps.audit --verbosity 1`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run lint`
- `cd frontend && npm run build`
