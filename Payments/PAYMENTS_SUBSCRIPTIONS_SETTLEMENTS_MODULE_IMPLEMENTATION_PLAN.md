# FoodCert NG Payments, Subscriptions & Settlements Module Implementation Plan

This plan converts `FOODCERT_PAYMENTS_SUBSCRIPTIONS_SETTLEMENTS_MODULE_PRD.md` into executable Codex chunks. It is grounded in the current implementation: `backend/apps/payments`, `backend/apps/subscriptions`, `backend/apps/settlements`, employer billing endpoints, facility settlement pages, state/federal finance foundations, audit logging, reports, inspections, certificates, assessments, and organization scoping.

The implementation should reuse the existing apps before introducing new abstractions. Build toward product-complete financial workflows first: trusted assessment payments, state fee control, employer subscriptions, facility settlements, refunds, reconciliation, privacy-safe state/federal finance dashboards, and auditability.

---

## Current Audit Summary

| Area | Current State | Gap |
| --- | --- | --- |
| Payment models | `AssessmentFee` and `PaymentTransaction` exist with state/facility/platform split metadata. | Needs provider config, richer statuses, fee schedule approval/versioning, allocation records, receipts, invoices, webhook events, immutable ledger entries, refunds. |
| Provider abstraction | `PaymentProvider`, `MockPaymentProvider`, initialize/verify/refund hooks exist. | Needs persisted `PaymentProvider`, provider-specific adapters, signature validation per provider, amount verification, webhook idempotency, provider fee normalization. |
| Assessment payments | Assessment payment initiation exists from facility and food handler id. | Needs assessment-specific fee quote, eligibility checks, payment-required gates, status sync into assessment workflow, receipt generation, retry/abandonment handling. |
| Subscriptions | Employer plans/subscriptions and activation service exist. | Needs invoices, receipts, renewals, upgrade/downgrade policy, entitlement enforcement, expiry jobs, billing dashboard completeness. |
| Settlements | `Settlement` model, facility access checks, dispute, report, and process action exist. | Needs payment allocation linkage, settlement eligibility jobs, batches, payout retry/hold/release, dispute response workflow, provider/bank transfer references. |
| State finance | State admins can scope assessment fees and transactions by state. | Needs state fee approval workflow, state finance dashboards, revenue reports, refunds/reconciliation views, LGA/facility breakdowns. |
| Federal finance | Federal admins can see broad payment/settlement data. | Needs aggregate-first national views, provider performance, state fee compliance, reconciliation/anomaly reporting, privacy guardrails. |
| Frontend | Facility settlement page and payments API clients exist. | Needs food handler payment screens, employer billing screens, admin provider/refund/reconciliation pages, state/federal finance pages. |
| Security/audit | Payment events use audit logging in core service paths. | Needs immutable financial ledger, full audit coverage, provider secret protection, privacy-safe serializers, permission regression tests. |

## PSS0 Baseline Inventory

Completed implementation inventory before PSS1:

| Surface | Existing Implementation | Notes for Future Chunks |
| --- | --- | --- |
| API wiring | `backend/config/urls.py` includes `apps.payments.urls`, `apps.subscriptions.urls`, and `apps.settlements.urls` under `/api/`. | Preserve existing endpoints as aliases while adding PRD-aligned namespaces. |
| Payment endpoints | `/api/assessment-fees/`, `/api/payments/`, `/api/payments/assessment/initiate/`, `/api/payments/subscription/initiate/`, `/api/payments/verify/:reference/`, `/api/payments/webhook/`. | PSS2/PSS4 should add provider-coded webhooks, assessment-specific quote/init endpoints, receipts, and transaction status/detail aliases. |
| Subscription endpoints | `/api/subscription-plans/`, `/api/employers/:id/subscribe/`. | Frontend already references checkout/change-plan/invoices/payments endpoints that need backend completion or aliasing in PSS7/PSS8. |
| Settlement endpoints | `/api/settlements/`, `/api/settlements/create-from-payment/`, `/api/settlements/:id/process/`, `/api/settlements/:id/dispute/`, facility settlement list/detail/dispute/report endpoints. | PSS10/PSS11 should keep facility URLs stable and add batch/eligible/retry/hold/release/admin dispute endpoints. |
| Payment service | `PaymentService` creates assessment/subscription transactions, calls provider initialize/verify/refund, logs payment events, and treats successful verification idempotently. | PSS2/PSS4/PSS5 must add amount/currency verification, persisted provider config, webhook event persistence, receipts, allocations, and immutable ledger entries. |
| Provider abstraction | `PaymentProvider` plus `MockPaymentProvider` support initialize, verify, and refund. | PSS2 should expand the adapter contract without breaking the mock provider used by tests. |
| Fee configuration | `AssessmentFeeViewSet` validates split totals and scopes state admins to their state. | PSS3 should evolve this into fee schedule approval/versioning and historical immutability. |
| Assessment workflow integration | `AssessmentService.payment_required()` and `has_confirmed_payment()` already block progression when policy requires payment. | PSS4/PSS5 should wire successful assessment payment directly to the assessment record and allocation ledger. |
| Subscription service | `EmployerSubscriptionService.activate()`, `change_plan()`, `current_for_employer()`, and capacity checks exist. | PSS7/PSS8 should build invoices/receipts/renewals around this service instead of replacing it. |
| Settlement service | Settlement access, eligibility validation, create-from-payment, process, dispute, and facility metrics exist. | PSS10/PSS11 should add allocation-backed settlement records, batch processing, provider payout references, and dispute resolution. |
| Current tests | `backend/apps/payments/tests.py` covers fee split validation, facility payment eligibility, payment verification, signed webhook, idempotent verification, employer subscribe, settlement creation/process. | Future tests should extend this file or split by app once models grow; there is no separate `backend/apps/subscriptions/tests.py` yet. |
| Frontend payments API | `frontend/src/lib/api/payments.ts` contains assessment fee, payment initiation/verification, subscription plan, employer subscription, invoices/payments, and settlement helpers. | Some referenced endpoints are ahead of backend and should be reconciled in PSS7/PSS8. |
| Frontend settlements API | `frontend/src/lib/api/settlements.ts` contains facility settlement list/detail/dispute/report helpers. | Keep these stable during PSS10/PSS11 dashboard expansion. |
| Employer billing UI | `/employer/subscription` is implemented with plan cards, current plan, usage, billing history, and payment history. | PSS7/PSS8 should either keep this route as the employer billing entry or alias it from PRD billing routes. |
| Facility settlements UI | `/facility/settlements` is implemented with finance cards, filters, CSV export, ledger table, and dispute submission. | PSS10/PSS11 should extend this page rather than rebuild it. |
| State/federal finance context | `apps.ministries` and `apps.reports` already aggregate some payment/settlement data for state/federal dashboards. | PSS13/PSS14 should reuse these aggregation patterns and enforce aggregate-first federal privacy. |

---

## Build Order

```txt
PSS0 Baseline audit and inventory
  -> PSS1 Roles, permissions, financial privacy, and policy constants
  -> PSS2 Provider configuration, adapter contract, webhook events
  -> PSS3 State fee schedules, split validation, approval workflow
  -> PSS4 Assessment payment quote, checkout, verification, receipt
  -> PSS5 Payment allocations, immutable ledger, assessment workflow gates
  -> PSS6 Food handler payment UI and retry/refund request entry
  -> PSS7 Employer subscription plans, invoices, receipts
  -> PSS8 Employer billing dashboard, renewals, upgrades, entitlements
  -> PSS9 Bulk employer assessment payments
  -> PSS10 Settlement eligibility, ledger traceability, facility finance
  -> PSS11 Settlement batches, payouts, retry, holds, disputes
  -> PSS12 Refunds, reversals, chargebacks, adjustment ledger
  -> PSS13 Reconciliation, provider performance, exports
  -> PSS14 State/Federal finance dashboards, privacy, final QA
```

---

## Chunk PSS0 - Baseline Audit and Inventory

**Goal:** Confirm the existing financial surface before changing behavior.

| Layer | Work |
| --- | --- |
| Backend | Inventory models, migrations, URLs, services, permissions, audit hooks, assessment/certificate integration points, employer subscription usage gates, settlement creation paths. |
| Frontend | Inventory payment, subscription, settlement API clients, types, pages, dashboard shells, route gaps, shared finance components. |
| Docs | Update this file with any changed assumptions before implementation begins. |

**Files:** `backend/apps/payments/*`, `backend/apps/subscriptions/*`, `backend/apps/settlements/*`, `backend/apps/assessments/*`, `backend/apps/certificates/*`, `backend/apps/employers/*`, `frontend/src/lib/api/payments.ts`, `frontend/src/lib/api/settlements.ts`, `frontend/src/types/payments.ts`, `frontend/src/types/settlements.ts`.

**Acceptance Criteria:**
- Current payment/subscription/settlement endpoints are mapped.
- Existing migrations and model names are preserved unless there is a clear compatibility reason.
- Known gaps are listed before PSS1 implementation starts.

---

## Chunk PSS1 - Roles, Permissions, Financial Privacy, and Policy Constants

**Goal:** Establish safe financial access rules for all actors.

| Layer | Work |
| --- | --- |
| Backend | Add reusable finance permission helpers for food handler, employer finance/admin, facility finance/admin, state finance/admin, federal finance/oversight, platform finance. Add privacy-safe serializer mixins/helpers that exclude lab results, diagnosis, notes, declarations, treatment details, and full NIN. |
| Frontend | Add role-aware route guards and finance-safe display helpers for names, references, amounts, states, facilities, and statuses. |
| Tests | Permission tests for own-record access, employer scoping, facility organization scoping, state scoping, federal aggregate access, and platform finance access. |

**Files:** `backend/apps/accounts/permissions.py`, `backend/apps/payments/permissions.py`, `backend/apps/payments/serializers.py`, `backend/apps/settlements/services.py`, `frontend/src/lib/auth/*`, finance route shells.

**Acceptance Criteria:**
- Food handlers see only their payments and receipts.
- Employers see only their billing and approved bulk payment records.
- Facilities see only their settlements and disputes.
- State users see only their state financial data.
- Federal views default to aggregate or privacy-safe data.

---

## Chunk PSS2 - Provider Configuration, Adapter Contract, and Webhook Events

**Goal:** Make provider integration configurable, auditable, and idempotent.

| Layer | Work |
| --- | --- |
| Backend | Add `PaymentProvider` and `PaymentWebhookEvent`. Expand adapter interface for initialize, verify, webhook parse, refund, transfer, provider fee normalization. Store raw webhook payload, signature result, processing status, and idempotency key/reference. Protect provider secrets using existing encryption/settings patterns. |
| API | Add `/api/admin/payment-providers/...` and `/api/payments/webhooks/:provider_code`. Keep existing webhook URL as compatibility alias if needed. |
| Frontend | Add platform admin provider settings table/form with activation/deactivation and supported methods. |
| Tests | Provider activation, secret redaction, webhook invalid signature rejection, duplicate webhook idempotency. |

**Files:** `backend/apps/payments/models.py`, `providers.py`, `services.py`, `views.py`, `serializers.py`, `urls.py`, migrations, `frontend/src/app/admin/payments/providers/*`, `frontend/src/lib/api/payments.ts`.

**Acceptance Criteria:**
- No client callback can mark a payment successful without server verification.
- Duplicate webhook events do not duplicate ledger/payment side effects.
- Provider secrets are never serialized back to users.

---

## Chunk PSS3 - State Fee Schedules, Split Validation, and Approval Workflow

**Goal:** Replace simple active fees with state-approved, versioned fee schedules.

| Layer | Work |
| --- | --- |
| Backend | Introduce or evolve `AssessmentFee` into `AssessmentFeeSchedule` semantics: draft, pending approval, active, scheduled, expired, suspended, replaced. Enforce one active schedule per state/facility type/effective period. Add immutable historical rules once used by a payment. |
| API | Add `/api/state/fee-schedules`, submit, approve, suspend, export. Federal users can view nationally. |
| Frontend | Add state fee schedule list/detail/form, approval panel, fee split preview, active schedule warning. |
| Tests | Split totals, state scoping, approval permissions, overlapping effective period prevention, historical schedule immutability. |

**Files:** `backend/apps/payments/models.py`, `services.py`, `views.py`, `serializers.py`, migrations, `frontend/src/app/state/finance/fee-schedules/*`, `frontend/src/components/payments/*`.

**Acceptance Criteria:**
- Only approved active/scheduled fee schedules can price new payments.
- State users cannot configure another state’s fees.
- Old transactions retain the schedule and split used at payment time.

---

## Chunk PSS4 - Assessment Payment Quote, Checkout, Verification, and Receipt

**Goal:** Complete the food handler assessment payment lifecycle.

| Layer | Work |
| --- | --- |
| Backend | Add assessment payment quote endpoint, initialize endpoint by assessment id, server-side verify action, status endpoint, receipt model/service, receipt number generation, retry handling, abandoned/expired status. Verify provider amount/currency against expected fee. |
| API | Add `/api/payments/assessment/:assessment_id/fee`, initialize, transaction status, verify, receipt. |
| Frontend | Add food handler assessment payment page, payment status page, receipt viewer, retry action, terms/refund policy notice. |
| Tests | Missing fee schedule, unaccredited facility, mismatched amount rejection, successful receipt generation, failed retry path. |

**Files:** `backend/apps/payments/models.py`, `services.py`, `serializers.py`, `views.py`, `urls.py`, `backend/apps/assessments/services.py`, `frontend/src/app/food-handler/assessment/[assessment_id]/pay/*`, `frontend/src/app/food-handler/payments/*`.

**Acceptance Criteria:**
- Assessment payment amount comes only from the active approved schedule.
- Successful payment creates a receipt.
- Failed or abandoned payments can be retried safely.

---

## Chunk PSS5 - Payment Allocations, Immutable Ledger, and Assessment Workflow Gates

**Goal:** Make the platform ledger the internal financial source of truth.

| Layer | Work |
| --- | --- |
| Backend | Add `PaymentAllocation` and `PaymentLedgerEntry` or equivalent immutable ledger. Create allocation records for each successful assessment payment with facility/state/platform/provider fee amounts. Add payment-required gates to assessment progression where policy requires prepayment. |
| Services | Ensure successful assessment payment updates assessment payment status and unlocks appointment/clinical workflow only when appropriate. |
| Tests | Ledger immutability, no destructive deletes, split traceability, assessment cannot proceed without payment, duplicate allocation prevention. |

**Files:** `backend/apps/payments/models.py`, `services.py`, migrations, `backend/apps/assessments/models.py`, `backend/apps/assessments/services.py`, `backend/apps/assessments/views.py`.

**Acceptance Criteria:**
- Every successful assessment payment has allocation and ledger records.
- Allocation traces to payment, assessment, food handler, facility, state, fee schedule, and split rule.
- Finance surfaces expose no clinical data.

---

## Chunk PSS6 - Food Handler Payment UI and Refund Request Entry

**Goal:** Give food handlers a clean payment history and receipt/refund experience.

| Layer | Work |
| --- | --- |
| Frontend | Build `/app/food-handler/payments`, detail, receipt, and assessment pay routes with status badges, receipt download/view, retry button, refund request modal where eligible. |
| Backend | Add refund request creation endpoint with eligibility rules but defer approval/processing to PSS12. |
| Tests | Own-payment access, receipt privacy, refund request eligibility, UI typecheck/lint. |

**Files:** `frontend/src/app/food-handler/payments/*`, `frontend/src/components/payments/*`, `frontend/src/lib/api/payments.ts`, `backend/apps/payments/views.py`, `serializers.py`.

**Acceptance Criteria:**
- Food handler can see current assessment payment status, history, and receipts.
- Payment screens show financial context only, not medical results.

---

## Chunk PSS7 - Employer Subscription Plans, Invoices, and Receipts

**Goal:** Make employer billing record-complete.

| Layer | Work |
| --- | --- |
| Backend | Add invoice and receipt support for employer subscriptions. Expand subscription plan fields for billing cycle, food handler/branch/user limits, feature entitlements, trial days, status. Preserve existing `EmployerSubscriptionPlan` compatibility where possible. |
| API | Add subscription plan admin endpoints, employer invoices, employer receipts, invoice detail. |
| Frontend | Add plan cards, invoice table, receipt table, current subscription summary. |
| Tests | Invoice number uniqueness, receipt issuance after payment, employer scoping, inactive plan exclusion. |

**Files:** `backend/apps/subscriptions/models.py`, `services.py`, `serializers.py`, `views.py`, migrations, `backend/apps/payments/models.py`, `frontend/src/app/employer/billing/*`.

**Acceptance Criteria:**
- Employer can view plans, subscribe, and receive invoice/receipt records.
- Subscription payment success activates subscription and entitlements.

---

## Chunk PSS8 - Employer Billing Dashboard, Renewals, Upgrades, and Entitlements

**Goal:** Complete ongoing subscription lifecycle management.

| Layer | Work |
| --- | --- |
| Backend | Add renew, upgrade, downgrade, cancel, grace period/past due/expired handling, renewal reminder job hooks, entitlement helper functions for premium features. Regulatory visibility must remain available even when payment lapses. |
| Frontend | Build employer billing dashboard, subscription detail, upgrade/downgrade flow, usage cards, renewal prompts. |
| Tests | Upgrade immediate effect, downgrade next-cycle behavior if selected, expired premium restrictions, regulatory access preservation. |

**Files:** `backend/apps/subscriptions/services.py`, `views.py`, `backend/apps/employers/services.py`, `frontend/src/app/employer/billing/subscription/*`, `plans/*`.

**Acceptance Criteria:**
- Premium features follow active plan entitlements.
- Expired/suspended subscriptions do not block legally required compliance visibility.

---

## Chunk PSS9 - Bulk Employer Assessment Payments

**Goal:** Allow employers to pay assessment fees for multiple eligible handlers in one transaction.

| Layer | Work |
| --- | --- |
| Backend | Add quote and initialize endpoints. Validate assessment eligibility and active fee schedules for every selected handler. Create per-assessment allocations and line-item receipts after payment success. Support partial refund allocation references for PSS12. |
| Frontend | Build bulk assessment payment builder with selectable handlers, quote summary, line-item receipt, and payment status. |
| Tests | Recalculation when an assessment becomes ineligible, no over/under allocation, per-assessment receipt lines, employer scoping. |

**Files:** `backend/apps/payments/services.py`, `views.py`, `serializers.py`, `backend/apps/employers/views.py`, `frontend/src/app/employer/billing/bulk-assessment-payments/*`.

**Acceptance Criteria:**
- One bulk payment can fund multiple assessment allocations without losing individual traceability.
- Ineligible assessments are excluded or force quote refresh before checkout.

---

## Chunk PSS10 - Settlement Eligibility, Ledger Traceability, and Facility Finance

**Goal:** Create settlements only when assessment and certificate policy conditions are satisfied.

| Layer | Work |
| --- | --- |
| Backend | Link settlement records to payment allocations and fee schedules. Add eligibility service/job that checks successful payment, completed assessment, finalized doctor decision, state validation/certificate approval where required, and no active refund/dispute hold. |
| Frontend | Expand facility settlement dashboard with allocation references, payment references, filters, exports, and no medical details. |
| Tests | Fit assessment requires certificate/state approval before settlement, not-fit finalized reports can settle by policy, duplicate settlement prevention, facility scoping. |

**Files:** `backend/apps/settlements/models.py`, `services.py`, `views.py`, migrations, `frontend/src/app/facility/settlements/*`, `frontend/src/types/settlements.ts`.

**Acceptance Criteria:**
- Settlement traceability includes payment allocation, assessment, facility, state, fee schedule, and split.
- Facility finance users cannot see clinical data.

---

## Chunk PSS11 - Settlement Batches, Payouts, Retry, Holds, and Disputes

**Goal:** Move from single settlement processing to finance-ready batch operations.

| Layer | Work |
| --- | --- |
| Backend | Add `SettlementBatch`, batch creation/approval/processing, provider/bank payout references, retry failed transfer, hold/release, dispute response/close workflow. Prevent paying records twice. |
| API | Add `/api/admin/settlement-batches/...`, eligible settlements, retry/hold/release actions, settlement dispute management. |
| Frontend | Add platform/admin settlement batches page, eligible settlements review, dispute queue, facility dispute detail updates. |
| Tests | Batch totals, approval permissions, idempotent processing, failed retry, hold release, dispute resolution audit logs. |

**Files:** `backend/apps/settlements/models.py`, `services.py`, `serializers.py`, `views.py`, `urls.py`, `frontend/src/app/admin/settlements/*`, `frontend/src/app/admin/disputes/*`.

**Acceptance Criteria:**
- Paid settlements cannot be paid twice.
- Failed settlements can be retried only after authorized action.
- Every batch action is audit logged.

---

## Chunk PSS12 - Refunds, Reversals, Chargebacks, and Adjustment Ledger

**Goal:** Complete controlled refund and dispute financial flows.

| Layer | Work |
| --- | --- |
| Backend | Add `RefundRequest`, statuses, approval/rejection/process actions, partial refund support for bulk allocations, provider refund verification, reversal ledger entries, chargeback handling, settlement hold/recovery records. |
| API | Add food handler refund request, admin refund queue, approve/reject/process, chargeback webhook handling. |
| Frontend | Add refund request modal, admin refund approval panel, refund status history, state revenue impact badges. |
| Tests | Permissioned refunds, partial allocation refunds, settlement hold on chargeback, reversal ledger immutability, audit logs. |

**Files:** `backend/apps/payments/models.py`, `services.py`, `views.py`, `serializers.py`, `backend/apps/settlements/services.py`, `frontend/src/app/admin/refunds/*`, `frontend/src/components/payments/refund-request-modal.tsx`.

**Acceptance Criteria:**
- Refunds never overwrite original payment records.
- Refunds create reversal/refund ledger entries.
- State/facility/platform revenue views reflect refunds accurately.

---

## Chunk PSS13 - Reconciliation, Provider Performance, and Exports

**Goal:** Give finance teams a trusted reconciliation workspace.

| Layer | Work |
| --- | --- |
| Backend | Add reconciliation import/pull model or service, match statuses, amount/currency/reference checks, duplicate provider reference detection, manual resolution with reason, provider performance aggregates. |
| API | Add state finance reconciliation, federal finance reconciliation/provider performance, platform admin reconciliation endpoints, CSV/PDF/XLSX export hooks. |
| Frontend | Build reconciliation tables, mismatch badges, provider performance chart, export actions. |
| Tests | Matched/missing/mismatch detection, manual resolution audit requirement, state scoping, federal aggregate behavior. |

**Files:** `backend/apps/payments/models.py`, `services.py`, `views.py`, `backend/apps/reports/*`, `frontend/src/app/admin/payments/reconciliation/*`, `frontend/src/app/state/finance/reconciliation/*`, `frontend/src/app/federal/finance/reconciliation/*`.

**Acceptance Criteria:**
- Provider records can be compared with internal ledger records.
- Mismatches are flagged and resolvable only with reason and audit log.
- Exports respect actor scoping and privacy rules.

---

## Chunk PSS14 - State/Federal Finance Dashboards, Security, and Final QA

**Goal:** Finish oversight dashboards and harden the whole financial module.

| Layer | Work |
| --- | --- |
| Backend | Add state finance dashboard/revenue/settlements/refunds/export endpoints and federal dashboard/revenue-by-state/subscriptions/settlements/provider-performance endpoints. Add background jobs for payment expiry, verification retry, subscription renewal/expiry, settlement eligibility, reconciliation. |
| Frontend | Build state finance dashboard, revenue, settlements, refunds, reports; federal finance dashboard, revenue by state, subscriptions, settlements, provider performance, reports. Replace any remaining generic portal shells with real workflows. |
| Security | Verify provider secrets, webhook signatures, idempotency keys, immutable ledger, privacy-safe serializers, audit coverage, financial permission boundaries. |
| Tests | Full module regression: backend tests, frontend typecheck/lint/build, privacy tests, permission tests, webhook idempotency, settlement duplicate-prevention. |

**Files:** `backend/apps/payments/*`, `backend/apps/subscriptions/*`, `backend/apps/settlements/*`, `backend/apps/reports/*`, `frontend/src/app/state/finance/*`, `frontend/src/app/federal/finance/*`, shared dashboard components.

**Acceptance Criteria:**
- State dashboards show only state data with LGA/facility breakdowns where allowed.
- Federal dashboards aggregate sensitive national data by default.
- Final QA passes or all environment blockers are documented with exact failing commands.

---

## API Namespace Targets

Use PRD-aligned routes while preserving existing endpoints as aliases where needed:

- `/api/payments/...`
- `/api/admin/payment-providers/...`
- `/api/admin/payments/...`
- `/api/admin/refunds/...`
- `/api/admin/settlement-batches/...`
- `/api/state/fee-schedules/...`
- `/api/state/finance/...`
- `/api/federal/finance/...`
- `/api/employers/:id/subscription/...`
- `/api/employers/:id/bulk-assessment-payments/...`
- `/api/facilities/:id/settlements/...`

---

## Final QA Checklist

- `./.venv/bin/python manage.py makemigrations --check`
- `./.venv/bin/python manage.py test apps.payments apps.subscriptions apps.settlements`
- `./.venv/bin/python manage.py test apps.assessments apps.employers apps.reports`
- `npm run typecheck`
- `npm run lint`
- `npm run build`
- Payment amount mismatch cannot mark successful.
- Invalid webhook signature is rejected and logged.
- Duplicate webhook is idempotent.
- Food handler sees only own payment/receipt/refund records.
- Employer sees only own subscription, invoices, receipts, and bulk payments.
- Facility sees only own settlements and disputes.
- State users see only their state finance data.
- Federal users see privacy-safe aggregate national data by default.
- Finance serializers do not expose lab results, diagnosis, doctor notes, declaration answers, treatment details, or full NIN.
- Paid settlements cannot be paid twice.
- Refunds and chargebacks create reversal/adjustment ledger entries.
- All financial actions are audit logged.
