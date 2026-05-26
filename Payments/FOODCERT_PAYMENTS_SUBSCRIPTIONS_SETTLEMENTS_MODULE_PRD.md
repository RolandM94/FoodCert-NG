# PRD: Payments, Subscriptions & Settlements Module — FoodCert NG

## 1. Module Name

**Payments, Subscriptions & Settlements Module**

## 2. Product Context

The Payments, Subscriptions & Settlements Module is the financial transaction engine of **FoodCert NG**. It enables food handlers to pay for medical assessments, employers to pay subscription fees for compliance management tools, medical facilities to receive settlement payouts for completed assessments, and State/Federal regulators to monitor revenue, fee schedules, and reconciliation.

This module must support a national rollout across all 36 states and the FCT while respecting state-level fee configuration. It must also support multiple payment providers through a provider abstraction layer so the platform can use Paystack, Flutterwave, Remita, bank transfer, USSD, card, mobile money, or other approved payment channels without rewriting core business logic.

The module connects directly with:

- Food Handler registration and assessment initiation
- Medical Facility appointment and assessment workflow
- State Ministry fee configuration
- Employer subscription access
- Certificate issuance eligibility
- Facility settlement processing
- State and Federal revenue dashboards
- Audit, reconciliation, refunds, and dispute management

---

# 3. Product Goal

To provide a secure, auditable, configurable, and scalable financial system for managing assessment payments, employer subscriptions, fee splits, facility settlements, refunds, reconciliation, receipts, and regulatory revenue reporting on FoodCert NG.

---

# 4. Core Objectives

The module must allow the platform to:

1. Collect medical assessment payments from food handlers.
2. Collect employer subscription payments from food businesses/FBOs.
3. Support state-approved assessment fees.
4. Split assessment fees between facility, state, platform, and other approved parties.
5. Track payments from initiation to settlement.
6. Validate payment before assessment where policy requires it.
7. Validate subscription before employer premium access.
8. Generate payment receipts and invoices.
9. Process webhooks from payment providers.
10. Reconcile provider transactions with internal ledger.
11. Settle medical facilities after completed/validated assessments.
12. Support refunds, failed payments, reversals, and chargebacks.
13. Provide State Ministry revenue reports.
14. Provide Federal Ministry national financial oversight dashboards.
15. Maintain complete financial audit logs.
16. Protect medical privacy by separating financial data from clinical records.

---

# 5. Key Actors

## 5.1 Food Handler

Can:

- View assessment fee before payment.
- Pay assessment fee.
- Select payment method.
- View payment status.
- Download payment receipt.
- Retry failed payment.
- Request refund where policy allows.
- View assessment payment history.

Cannot:

- Manually mark payment as successful.
- Change fee amount.
- Select unapproved fee.
- Access facility settlement details.
- Access state/platform fee split unless exposed by policy.

## 5.2 Employer / Food Business Owner

Can:

- View available subscription plans.
- Subscribe to a plan.
- Renew subscription.
- Upgrade or downgrade plan.
- View invoices and receipts.
- View payment history.
- Manage billing contact.
- Pay for food handler assessments in bulk, if enabled.
- View subscription usage limits.

Cannot:

- Access medical payment details beyond linked operational workflows.
- See clinical data through billing.
- Change subscription entitlement manually.
- Change platform pricing.

## 5.3 Medical Facility Finance User

Can:

- View assessments linked to facility payments.
- View pending settlements.
- View paid settlements.
- View failed settlements.
- Download settlement reports.
- Raise settlement disputes.
- View settlement bank account on file.
- Request bank details update, if permitted.

Cannot:

- View doctor notes, diagnosis, lab results, or declaration answers.
- Change payment status.
- Approve own settlement.
- Access other facilities’ settlement records.

## 5.4 Medical Facility Admin

Can:

- View facility-level payment/settlement summary.
- View settlement eligibility status.
- View assessment payment status.
- Manage authorized finance users.
- Initiate settlement dispute.

Cannot:

- Override payment confirmation.
- Issue refunds directly unless policy grants permission.
- Edit fee split.

## 5.5 State Ministry Finance / Policy Officer

Can:

- Configure state assessment fee schedules.
- Configure fee split, where permitted.
- View state revenue dashboard.
- View facility settlement summaries within state.
- View state fee collections.
- Export state reconciliation reports.
- Approve state fee schedules.
- View refunds affecting state revenue.

Cannot:

- View clinical medical details.
- View unrelated states’ revenue unless also federal/super admin.
- Directly alter provider payment records.

## 5.6 State Ministry Admin

Can:

- Approve state fee schedules.
- View state payment dashboard.
- Monitor settlement disputes.
- Review state revenue reports.
- Manage state finance users.

## 5.7 Federal Ministry Finance/Oversight User

Can:

- View national revenue summaries.
- View state-by-state payment performance.
- View national subscription revenue summary.
- View settlement performance by state/facility.
- View policy compliance around fees.
- Export national finance reports.
- Monitor unusual payment/settlement patterns.

Cannot by default:

- Replace state fee authority unless national policy grants that control.
- Access individual clinical records.
- Modify state revenue records without explicit authority.

## 5.8 Platform Finance / Super Admin

Can:

- Configure payment providers.
- Configure platform fee rules.
- Manage settlement batches.
- Reconcile provider transactions.
- Retry failed settlements.
- Process approved refunds.
- Manage invoices and receipts.
- View audit logs.
- Configure payment webhooks.

Must not:

- Edit payment ledger records destructively.
- Delete historical financial records.
- Access medical details unless separately authorized.

---

# 6. Module Scope

## 6.1 In Scope

This module includes:

- Assessment payment initiation
- Assessment fee calculation
- State fee schedule management
- Payment provider abstraction
- Payment checkout
- Payment status tracking
- Payment webhook processing
- Payment receipts
- Payment ledger
- Employer subscription plans
- Employer subscription billing
- Subscription entitlements
- Subscription invoices and receipts
- Subscription renewals
- Plan upgrades/downgrades
- Facility settlement eligibility
- Facility settlement ledger
- Settlement batch processing
- Settlement disputes
- Refunds and reversals
- Reconciliation dashboard
- State revenue dashboard
- Federal finance oversight dashboard
- Payment audit logs
- Finance-safe privacy rules

## 6.2 Out of Scope for MVP

The following can be deferred:

- Full accounting suite
- Tax remittance automation
- Payroll integration
- Insurance/HMO billing
- POS terminal integration
- Complex credit terms
- Multi-currency settlement beyond NGN
- Automated government TSA remittance integration, unless required immediately
- Blockchain payment proof
- Full ERP integration

---

# 7. Payment Design Principles

## 7.1 Provider Independence

The platform must not be tightly coupled to one payment provider.

Implement a provider abstraction layer:

```txt
PaymentService
→ ProviderAdapter
→ PaystackAdapter / FlutterwaveAdapter / RemitaAdapter / BankTransferAdapter
```

## 7.2 Ledger Integrity

Every financial transaction must be recorded in an internal ledger. Provider status is important, but the platform ledger is the source of truth for internal reporting after successful verification.

Rules:

- Never delete ledger records.
- Use reversal/refund entries instead of destructive edits.
- Store provider reference and internal reference.
- Reconcile provider amount against expected amount.
- Reject mismatched payment confirmations.

## 7.3 Privacy Separation

Finance users must not gain access to clinical information through payment screens.

Payment pages may show:

- Food handler name
- Assessment reference
- Facility
- Amount
- Payment status
- Receipt

Payment pages must not show:

- Lab results
- Diagnosis
- Doctor notes
- Declaration answers
- Treatment notes

## 7.4 State-Level Fee Control

Assessment fee pricing is state-specific. Each State Ministry may configure approved assessment fee schedules, subject to national policy rules.

## 7.5 Settlement Traceability

Every settlement must be traceable back to:

- Payment transaction
- Assessment
- Food handler
- Facility
- State
- Fee schedule
- Split rule
- Settlement batch

---

# 8. Core Financial Flows

## 8.1 Food Handler Assessment Payment Flow

```txt
Food handler starts assessment
→ Selects approved facility
→ System calculates state-approved assessment fee
→ Food handler chooses payment method
→ Payment initialized with provider
→ Food handler completes payment
→ Provider sends webhook
→ System verifies payment with provider
→ Payment marked successful
→ Receipt generated
→ Assessment status changes to Payment Confirmed
→ Facility appointment/assessment workflow can proceed
```

## 8.2 Employer Subscription Flow

```txt
Employer registers business
→ Selects subscription plan
→ System creates invoice
→ Employer pays subscription fee
→ Provider webhook confirms payment
→ Subscription becomes active
→ Employer gains plan entitlements
→ Renewal reminders are scheduled
```

## 8.3 Facility Settlement Flow

```txt
Food handler payment confirmed
→ Assessment completed by facility
→ Doctor marks fit or report finalized
→ State validates certificate, where required
→ Settlement eligibility created
→ Settlement batch generated
→ Provider/bank payout processed
→ Settlement marked paid
→ Facility receives notification and report
```

## 8.4 Refund Flow

```txt
Refund requested
→ Eligibility checked
→ Authorized user approves/rejects
→ Refund initiated with payment provider
→ Provider confirms refund
→ Ledger records refund entry
→ Related payment/assessment updated
→ Parties notified
```

---

# 9. Assessment Payment Requirements

## 9.1 Assessment Fee Calculation

Assessment fee should be calculated using:

- State
- Facility type
- Active assessment fee schedule
- Effective date
- Applicable policy overrides
- Discount/subsidy, if enabled
- Bulk payment rule, if employer pays for multiple handlers

## 9.2 Assessment Fee Components

A fee may include:

- Facility amount
- State amount
- Platform amount
- Payment provider fee
- Tax or levy, if applicable
- Discount/subsidy, if applicable

## 9.3 Fee Display to Food Handler

Before payment, show:

- Assessment fee amount
- Facility name
- State
- Payment method options
- Transaction reference
- Refund policy summary
- Terms and privacy notice

Optional detailed breakdown may be shown depending on policy.

## 9.4 Assessment Payment Statuses

- Not Required
- Pending
- Initialized
- Awaiting Provider Confirmation
- Successful
- Failed
- Abandoned
- Cancelled
- Reversed
- Refunded
- Partially Refunded
- Disputed

## 9.5 Assessment Payment Rules

- Assessment cannot proceed until payment is successful where policy requires prepayment.
- Payment amount must match active fee schedule.
- Payment cannot be reused across multiple assessments unless explicitly designed for bulk payments.
- A successful payment must create a receipt.
- Failed payments should allow retry.
- Abandoned payments should expire after a configurable time.
- Duplicate provider webhook events must be idempotent.

---

# 10. State Assessment Fee Configuration

## 10.1 Purpose

State Ministries need to define approved assessment prices and fee splits for their jurisdiction.

## 10.2 Fee Schedule Fields

- State
- Facility type
- Fee name
- Gross amount
- Facility share
- State share
- Platform share
- Provider fee handling
- Currency
- Effective start date
- Effective end date
- Status
- Created by
- Approved by
- Approval date
- Notes

## 10.3 Fee Schedule Statuses

- Draft
- Pending Approval
- Active
- Scheduled
- Expired
- Suspended
- Replaced

## 10.4 Fee Configuration Rules

- Only one active fee schedule should exist for a state/facility type/effective period.
- Historical fee schedules must not be edited after payments have used them.
- Changes should create a new fee schedule version.
- Fee schedules require approval before activation.
- Fee schedule changes must be audit logged.
- State users can only configure their state fees.
- Federal users can view state fee schedules nationally.

## 10.5 Fee Schedule Approval Workflow

```txt
State finance officer creates draft fee schedule
→ Submits for approval
→ State admin approves
→ Fee becomes scheduled or active
→ New assessments use the active schedule
→ Old transactions retain original fee schedule reference
```

---

# 11. Payment Provider Abstraction

## 11.1 Purpose

Support multiple payment providers without changing business logic.

## 11.2 Provider Adapter Responsibilities

Each provider adapter should implement:

- Initialize payment
- Verify payment
- Handle webhook payload
- Initiate refund
- Verify refund
- Initialize transfer/settlement, if supported
- Verify transfer/settlement
- Normalize provider status
- Normalize provider fees
- Return provider reference

## 11.3 Supported Providers

MVP can support one provider first, but architecture should allow:

- Paystack
- Flutterwave
- Remita
- Bank transfer
- USSD
- Mobile money
- Card payment

## 11.4 Provider Configuration Fields

- Provider name
- Environment: test/live
- Public key
- Secret key, encrypted
- Webhook secret
- Callback URL
- Webhook URL
- Is active
- Supported payment methods
- Supported settlement methods
- Created by
- Updated by

## 11.5 Webhook Rules

- Verify webhook signature.
- Reject unsigned/invalid webhooks.
- Process webhook idempotently.
- Store raw webhook payload.
- Log webhook processing result.
- Re-verify transaction with provider before marking successful.
- Do not trust client-side callback alone.

---

# 12. Payment Receipts and Invoices

## 12.1 Receipt Requirements

A receipt should be generated after successful payment.

Receipt should include:

- Receipt number
- Transaction reference
- Payer name
- Payer type
- Payment purpose
- Amount paid
- Currency
- Payment method
- Provider reference
- Date paid
- Facility, if assessment payment
- State, if assessment payment
- Subscription plan, if employer subscription
- Platform support contact

## 12.2 Invoice Requirements

Invoices are required for employer subscriptions and may be used for unpaid assessment payment initiation.

Invoice should include:

- Invoice number
- Customer name
- Customer type
- Billing email
- Description
- Amount due
- Due date
- Payment status
- Line items
- Tax/levy, if applicable
- Payment link

## 12.3 Receipt/Invoice Rules

- Receipt numbers must be unique.
- Invoice numbers must be unique.
- Receipts should not be editable after issuance.
- Cancelled invoices should retain record.
- Refunded receipts should show refund status.

---

# 13. Employer Subscription Management

## 13.1 Purpose

Employers pay subscription fees to use compliance management tools for their food handler workforce.

## 13.2 Subscription Plan Examples

### Basic Plan

For small food businesses.

May include:

- Limited number of food handlers
- Basic compliance dashboard
- Certificate tracking
- Renewal alerts
- Limited exports

### Standard Plan

For medium businesses.

May include:

- Higher food handler limit
- Branch management
- Bulk upload
- Compliance reports
- Inspection readiness reports
- More exports

### Enterprise Plan

For large/multi-branch businesses.

May include:

- Multi-branch management
- Advanced analytics
- Custom reporting
- API access, future
- Priority support
- Dedicated compliance dashboard

## 13.3 Subscription Plan Fields

- Plan name
- Description
- Billing cycle: monthly, quarterly, yearly
- Price
- Currency
- Food handler limit
- Branch limit
- User limit
- Feature entitlements
- Trial days
- Status

## 13.4 Subscription Statuses

- Trial
- Active
- Past Due
- Grace Period
- Suspended
- Cancelled
- Expired

## 13.5 Subscription Lifecycle

```txt
Employer selects plan
→ Invoice generated
→ Employer pays
→ Subscription activated
→ Entitlements applied
→ Renewal reminders sent
→ Subscription renewed or expires
```

## 13.6 Subscription Entitlements

Possible entitlements:

- Maximum food handlers
- Maximum branches
- Maximum users
- Bulk upload
- Certificate exports
- Advanced reports
- Inspection readiness reports
- API access
- Priority support
- Custom dashboard

## 13.7 Subscription Access Rules

When subscription is active:

- Employer can access paid features based on plan.

When subscription is past due:

- Employer receives warning.
- Grace period may apply.

When subscription is expired/suspended:

- Employer should retain basic regulatory visibility.
- Employer should not lose access to compliance obligations.
- Premium features can be restricted.
- Adding new food handlers may be restricted depending on policy.
- State/Federal regulatory access must not be blocked by employer non-payment.

## 13.8 Upgrade/Downgrade Rules

- Upgrade may take effect immediately.
- Downgrade may take effect next billing cycle.
- Proration can be deferred for MVP or handled by provider.
- Feature limits must be recalculated after plan change.
- Plan changes must be audit logged.

---

# 14. Bulk Employer Assessment Payments

## 14.1 Purpose

Employers may pay assessment fees for multiple food handlers at once.

## 14.2 Bulk Payment Flow

```txt
Employer selects food handlers
→ System validates assessment eligibility
→ System calculates total amount
→ Employer pays once
→ Payment is allocated across individual assessment records
→ Receipts generated
→ Assessments marked payment confirmed
```

## 14.3 Bulk Payment Rules

- Each assessment must still have its own allocation record.
- Bulk payment must not overpay/underpay individual assessments.
- If one assessment becomes ineligible before payment, amount must be recalculated.
- Refunds may be full or per-assessment partial refunds.
- Employer receipt should show line items.

---

# 15. Facility Settlements

## 15.1 Purpose

Medical facilities should receive their share of assessment fees after completing eligible assessments.

## 15.2 Settlement Eligibility

Settlement eligibility should be created when configured conditions are met.

Recommended default eligibility:

- Payment confirmed.
- Assessment completed.
- Doctor decision finalized.
- Assessment submitted to State.
- State validates certificate issuance or report finalized according to policy.
- No active dispute/refund hold.

## 15.3 Settlement Statuses

- Not Eligible
- Eligible
- Pending Batch
- Batched
- Processing
- Paid
- Failed
- Reversed
- On Hold
- Disputed

## 15.4 Settlement Batch Flow

```txt
System identifies eligible settlements
→ Finance user reviews settlement batch
→ Batch approved
→ Transfer initiated via provider/bank
→ Provider confirms payout
→ Settlement records marked paid
→ Facility notified
```

## 15.5 Settlement Batch Fields

- Batch reference
- State
- Date range
- Facility count
- Settlement count
- Gross amount
- Facility amount
- State amount
- Platform amount
- Status
- Created by
- Approved by
- Processed at
- Provider reference

## 15.6 Settlement Record Fields

- Settlement reference
- Facility
- Assessment
- Payment transaction
- Fee schedule
- Gross assessment amount
- Facility amount
- State amount
- Platform amount
- Provider fee
- Status
- Batch
- Paid date
- Failure reason

## 15.7 Settlement Rules

- A settlement record must link to one payment allocation or assessment.
- Settlement should not be paid twice.
- Failed settlements can be retried.
- Settlement amount must match fee split at time of payment.
- Facility bank details changes should not affect historical paid settlements.
- Settlement actions must be audit logged.

---

# 16. State Revenue and Platform Revenue

## 16.1 State Revenue

State revenue may come from:

- State share of assessment fees
- Other regulatory fees, if configured

State revenue dashboard should show:

- Gross assessment collections
- State share earned
- Facility share
- Platform share
- Provider fees
- Refunds
- Net state revenue
- Pending settlement/remittance
- Paid/remitted amount

## 16.2 Platform Revenue

Platform revenue may come from:

- Platform share of assessment payments
- Employer subscription payments
- Service fees
- Other configured charges

Platform dashboard should show:

- Total assessment platform fees
- Total subscription revenue
- Gross transaction volume
- Provider fees
- Refunds
- Net platform revenue

## 16.3 Federal Oversight

Federal dashboard should show aggregate national view:

- Gross assessment collections by state
- Subscription revenue nationally
- Settlement performance nationally
- Refund trends
- Failed payment rates
- Active state fee schedules
- States without active fee schedules
- Revenue by payment provider

---

# 17. Refunds, Reversals, Chargebacks and Disputes

## 17.1 Refund Reasons

Examples:

- Duplicate payment
- Assessment cancelled before service
- Facility unavailable
- Payment made with wrong amount
- Technical error
- State/facility rejection before assessment
- Policy-approved refund request

## 17.2 Refund Statuses

- Requested
- Under Review
- Approved
- Rejected
- Processing
- Refunded
- Failed
- Cancelled

## 17.3 Refund Rules

- Refunds require permission.
- Refunds must reference original payment.
- Refunds must create ledger reversal/refund entry.
- Refunds should update assessment status where relevant.
- Partial refunds must be supported for bulk payments.
- Refund approvals must be audit logged.

## 17.4 Chargebacks

If provider reports chargeback:

- Mark transaction disputed.
- Put related settlement on hold if unpaid.
- If already settled, create recovery record.
- Notify finance/admin users.
- Maintain audit trail.

## 17.5 Settlement Disputes

Facility can raise dispute for:

- Missing settlement
- Wrong amount
- Failed payout
- Bank details issue
- Assessment not included in settlement batch

Dispute fields:

- Facility
- Settlement
- Subject
- Description
- Evidence upload
- Status
- Assigned finance user
- Resolution note

---

# 18. Reconciliation

## 18.1 Purpose

Reconciliation ensures provider records match platform records.

## 18.2 Reconciliation Sources

- Payment provider transactions
- Internal payment ledger
- Assessment records
- Subscription records
- Settlement records
- Bank transfer reports

## 18.3 Reconciliation Statuses

- Matched
- Amount Mismatch
- Missing Internally
- Missing at Provider
- Duplicate Provider Reference
- Pending Verification
- Manually Resolved

## 18.4 Reconciliation Dashboard

Show:

- Total transactions
- Matched transactions
- Unmatched transactions
- Amount mismatches
- Failed payments
- Pending settlements
- Failed settlements
- Refunds
- Provider downtime/errors

## 18.5 Reconciliation Rules

- Provider amount must match expected internal amount.
- Provider currency must match expected currency.
- Provider reference must be unique.
- Suspicious records must be flagged.
- Manual resolution requires reason and audit log.

---

# 19. Payment and Settlement Dashboards

## 19.1 Food Handler Payment View

Cards/fields:

- Current assessment payment status
- Amount due
- Payment method
- Receipt
- Retry payment button
- Refund request button, if eligible

## 19.2 Employer Billing Dashboard

Cards:

- Current subscription plan
- Subscription status
- Renewal date
- Food handler usage
- Branch usage
- Outstanding invoices
- Last payment
- Available upgrade options

Tables:

- Invoices
- Receipts
- Subscription history
- Bulk assessment payments

## 19.3 Facility Settlement Dashboard

Cards:

- Eligible settlements
- Pending settlements
- Paid settlements
- Failed settlements
- Gross completed assessments
- Total facility earnings
- Current settlement batch

Tables:

- Settlement records
- Payment allocations
- Disputes
- Reports

## 19.4 State Finance Dashboard

Cards:

- Gross assessment collections
- State revenue share
- Facility settlements
- Platform share
- Refunds
- Failed payments
- Active fee schedule
- Facilities pending settlement

Charts:

- Revenue trend
- Revenue by facility
- Revenue by LGA
- Payment status distribution
- Settlement status distribution

## 19.5 Federal Finance Dashboard

Cards:

- National gross collections
- Subscription revenue
- State revenue summary
- Facility settlement summary
- Failed payment rate
- Refund rate
- Provider performance

Charts:

- Revenue by state
- Collections over time
- Settlement volume by state
- Active subscriptions by plan
- Provider transaction success rate

---

# 20. Reports and Exports

## 20.1 Food Handler Reports

- Payment receipt
- Payment history
- Refund status

## 20.2 Employer Reports

- Subscription invoices
- Subscription receipts
- Billing history
- Bulk assessment payment report
- Usage report

## 20.3 Facility Reports

- Settlement report
- Paid assessments report
- Pending settlement report
- Failed settlement report
- Settlement dispute report

## 20.4 State Reports

- Assessment revenue report
- State fee collection report
- Facility settlement report
- Refund report
- Reconciliation report
- Fee schedule report

## 20.5 Federal Reports

- National revenue report
- State-by-state collection report
- Subscription revenue report
- Payment provider performance report
- Settlement performance report
- Refund/chargeback report

## 20.6 Export Formats

- PDF
- Excel
- CSV

---

# 21. Notifications

## 21.1 Food Handler Notifications

Notify when:

- Payment initialized
- Payment successful
- Payment failed
- Receipt generated
- Refund approved/rejected
- Refund processed
- Assessment can proceed

## 21.2 Employer Notifications

Notify when:

- Subscription payment successful
- Subscription expiring soon
- Subscription expired
- Payment failed
- Invoice generated
- Receipt generated
- Bulk assessment payment successful
- Plan upgraded/downgraded

## 21.3 Facility Notifications

Notify when:

- Settlement eligible
- Settlement batched
- Settlement paid
- Settlement failed
- Settlement dispute updated
- Bank details update required

## 21.4 State Ministry Notifications

Notify when:

- Fee schedule pending approval
- New revenue report available
- Failed settlements exceed threshold
- Refund affects state revenue
- Reconciliation issue detected

## 21.5 Federal Ministry Notifications

Notify when:

- State has no active fee schedule
- National reconciliation issue detected
- Provider failure rate exceeds threshold
- Unusual revenue pattern detected
- High refund/chargeback rate detected

---

# 22. Privacy and Security Requirements

## 22.1 Financial Security

- Encrypt provider secrets.
- Do not store card details unless using PCI-compliant provider tokenization.
- Verify webhook signatures.
- Use idempotency keys.
- Use server-side payment verification.
- Restrict refund and settlement permissions.
- Maintain immutable ledger records.
- Log all financial actions.

## 22.2 Privacy Rules

Finance views must not expose:

- Lab results
- Diagnosis
- Doctor notes
- Declaration answers
- Full NIN
- Treatment details

## 22.3 Access Control Rules

- Food handler sees own payments.
- Employer sees own subscription and allowed bulk payments.
- Facility sees own settlements.
- State sees only state-level financial data.
- Federal sees national aggregate/oversight data.
- Platform finance sees provider and reconciliation data.

---

# 23. Data Model Requirements

## 23.1 PaymentProvider

```python
class PaymentProvider(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    environment = models.CharField(max_length=20)  # test, live
    public_key = models.CharField(max_length=255, blank=True)
    encrypted_secret_key = models.TextField(blank=True)
    webhook_secret = models.TextField(blank=True)
    callback_url = models.URLField(blank=True)
    webhook_url = models.URLField(blank=True)
    supported_methods = models.JSONField(default=list)
    supports_refunds = models.BooleanField(default=False)
    supports_transfers = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 23.2 AssessmentFeeSchedule

```python
class AssessmentFeeSchedule(models.Model):
    id = models.UUIDField(primary_key=True)
    state = models.ForeignKey("geography.State", on_delete=models.CASCADE)
    facility_type = models.CharField(max_length=100)
    fee_name = models.CharField(max_length=255)
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2)
    facility_amount = models.DecimalField(max_digits=12, decimal_places=2)
    state_amount = models.DecimalField(max_digits=12, decimal_places=2)
    platform_amount = models.DecimalField(max_digits=12, decimal_places=2)
    provider_fee_handling = models.CharField(max_length=50, default="deduct_from_platform")
    currency = models.CharField(max_length=10, default="NGN")
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50)
    created_by = models.ForeignKey("accounts.User", related_name="fee_schedules_created", null=True, on_delete=models.SET_NULL)
    approved_by = models.ForeignKey("accounts.User", related_name="fee_schedules_approved", null=True, blank=True, on_delete=models.SET_NULL)
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 23.3 PaymentTransaction

```python
class PaymentTransaction(models.Model):
    id = models.UUIDField(primary_key=True)
    internal_reference = models.CharField(max_length=100, unique=True)
    provider_reference = models.CharField(max_length=255, blank=True)
    provider = models.ForeignKey("payments.PaymentProvider", null=True, blank=True, on_delete=models.SET_NULL)
    payer_user = models.ForeignKey("accounts.User", null=True, blank=True, on_delete=models.SET_NULL)
    payer_type = models.CharField(max_length=50)  # food_handler, employer, facility, state, other
    payment_purpose = models.CharField(max_length=50)  # assessment, subscription, refund, other
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="NGN")
    status = models.CharField(max_length=50)
    payment_method = models.CharField(max_length=50, blank=True)
    checkout_url = models.URLField(blank=True)
    metadata = models.JSONField(default=dict)
    initialized_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 23.4 PaymentAllocation

```python
class PaymentAllocation(models.Model):
    id = models.UUIDField(primary_key=True)
    payment_transaction = models.ForeignKey("payments.PaymentTransaction", on_delete=models.CASCADE)
    assessment = models.ForeignKey("assessments.MedicalAssessment", null=True, blank=True, on_delete=models.SET_NULL)
    fee_schedule = models.ForeignKey("payments.AssessmentFeeSchedule", null=True, blank=True, on_delete=models.SET_NULL)
    facility = models.ForeignKey("facilities.MedicalFacility", null=True, blank=True, on_delete=models.SET_NULL)
    state = models.ForeignKey("geography.State", null=True, blank=True, on_delete=models.SET_NULL)
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2)
    facility_amount = models.DecimalField(max_digits=12, decimal_places=2)
    state_amount = models.DecimalField(max_digits=12, decimal_places=2)
    platform_amount = models.DecimalField(max_digits=12, decimal_places=2)
    provider_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 23.5 Receipt

```python
class Receipt(models.Model):
    id = models.UUIDField(primary_key=True)
    receipt_number = models.CharField(max_length=100, unique=True)
    payment_transaction = models.OneToOneField("payments.PaymentTransaction", on_delete=models.CASCADE)
    payer_name = models.CharField(max_length=255)
    payer_email = models.EmailField(blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="NGN")
    receipt_url = models.URLField(blank=True)
    issued_at = models.DateTimeField(auto_now_add=True)
```

## 23.6 SubscriptionPlan

```python
class SubscriptionPlan(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    billing_cycle = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="NGN")
    food_handler_limit = models.PositiveIntegerField(null=True, blank=True)
    branch_limit = models.PositiveIntegerField(null=True, blank=True)
    user_limit = models.PositiveIntegerField(null=True, blank=True)
    entitlements = models.JSONField(default=dict)
    trial_days = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 23.7 EmployerSubscription

```python
class EmployerSubscription(models.Model):
    id = models.UUIDField(primary_key=True)
    employer = models.ForeignKey("employers.Employer", on_delete=models.CASCADE)
    plan = models.ForeignKey("payments.SubscriptionPlan", on_delete=models.PROTECT)
    status = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    trial_end_date = models.DateField(null=True, blank=True)
    auto_renew = models.BooleanField(default=False)
    last_payment = models.ForeignKey("payments.PaymentTransaction", null=True, blank=True, on_delete=models.SET_NULL)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 23.8 Invoice

```python
class Invoice(models.Model):
    id = models.UUIDField(primary_key=True)
    invoice_number = models.CharField(max_length=100, unique=True)
    customer_user = models.ForeignKey("accounts.User", null=True, blank=True, on_delete=models.SET_NULL)
    employer = models.ForeignKey("employers.Employer", null=True, blank=True, on_delete=models.SET_NULL)
    subscription = models.ForeignKey("payments.EmployerSubscription", null=True, blank=True, on_delete=models.SET_NULL)
    description = models.TextField(blank=True)
    line_items = models.JSONField(default=list)
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default="NGN")
    status = models.CharField(max_length=50)
    due_date = models.DateField(null=True, blank=True)
    payment_transaction = models.ForeignKey("payments.PaymentTransaction", null=True, blank=True, on_delete=models.SET_NULL)
    issued_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
```

## 23.9 SettlementRecord

```python
class SettlementRecord(models.Model):
    id = models.UUIDField(primary_key=True)
    settlement_reference = models.CharField(max_length=100, unique=True)
    facility = models.ForeignKey("facilities.MedicalFacility", on_delete=models.PROTECT)
    assessment = models.ForeignKey("assessments.MedicalAssessment", null=True, blank=True, on_delete=models.SET_NULL)
    payment_allocation = models.ForeignKey("payments.PaymentAllocation", on_delete=models.PROTECT)
    state = models.ForeignKey("geography.State", on_delete=models.PROTECT)
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2)
    facility_amount = models.DecimalField(max_digits=12, decimal_places=2)
    state_amount = models.DecimalField(max_digits=12, decimal_places=2)
    platform_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=50)
    batch = models.ForeignKey("payments.SettlementBatch", null=True, blank=True, on_delete=models.SET_NULL)
    paid_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 23.10 SettlementBatch

```python
class SettlementBatch(models.Model):
    id = models.UUIDField(primary_key=True)
    batch_reference = models.CharField(max_length=100, unique=True)
    state = models.ForeignKey("geography.State", null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=50)
    total_gross_amount = models.DecimalField(max_digits=14, decimal_places=2)
    total_facility_amount = models.DecimalField(max_digits=14, decimal_places=2)
    total_state_amount = models.DecimalField(max_digits=14, decimal_places=2)
    total_platform_amount = models.DecimalField(max_digits=14, decimal_places=2)
    record_count = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey("accounts.User", related_name="settlement_batches_created", null=True, on_delete=models.SET_NULL)
    approved_by = models.ForeignKey("accounts.User", related_name="settlement_batches_approved", null=True, blank=True, on_delete=models.SET_NULL)
    processed_at = models.DateTimeField(null=True, blank=True)
    provider_reference = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 23.11 RefundRequest

```python
class RefundRequest(models.Model):
    id = models.UUIDField(primary_key=True)
    payment_transaction = models.ForeignKey("payments.PaymentTransaction", on_delete=models.PROTECT)
    requested_by = models.ForeignKey("accounts.User", related_name="refunds_requested", null=True, on_delete=models.SET_NULL)
    approved_by = models.ForeignKey("accounts.User", related_name="refunds_approved", null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=50)
    provider_refund_reference = models.CharField(max_length=255, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
```

## 23.12 PaymentWebhookEvent

```python
class PaymentWebhookEvent(models.Model):
    id = models.UUIDField(primary_key=True)
    provider = models.ForeignKey("payments.PaymentProvider", null=True, blank=True, on_delete=models.SET_NULL)
    event_type = models.CharField(max_length=100)
    provider_reference = models.CharField(max_length=255, blank=True)
    raw_payload = models.JSONField(default=dict)
    signature_valid = models.BooleanField(default=False)
    processing_status = models.CharField(max_length=50)
    processing_message = models.TextField(blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

# 24. API Requirements

## 24.1 Payment Provider Configuration

```txt
GET    /api/admin/payment-providers
POST   /api/admin/payment-providers
GET    /api/admin/payment-providers/:id
PATCH  /api/admin/payment-providers/:id
PATCH  /api/admin/payment-providers/:id/activate
PATCH  /api/admin/payment-providers/:id/deactivate
```

## 24.2 Assessment Payments

```txt
GET    /api/payments/assessment/:assessment_id/fee
POST   /api/payments/assessment/:assessment_id/initialize
GET    /api/payments/transactions/:id
GET    /api/payments/transactions/:id/status
POST   /api/payments/transactions/:id/verify
GET    /api/payments/transactions/:id/receipt
POST   /api/payments/transactions/:id/refund-request
```

## 24.3 Bulk Employer Assessment Payments

```txt
POST   /api/employers/:id/bulk-assessment-payments/quote
POST   /api/employers/:id/bulk-assessment-payments/initialize
GET    /api/employers/:id/bulk-assessment-payments
GET    /api/employers/:id/bulk-assessment-payments/:payment_id
```

## 24.4 Webhooks

```txt
POST   /api/payments/webhooks/:provider_code
```

## 24.5 State Fee Schedules

```txt
GET    /api/state/fee-schedules
POST   /api/state/fee-schedules
GET    /api/state/fee-schedules/:id
PATCH  /api/state/fee-schedules/:id
POST   /api/state/fee-schedules/:id/submit
POST   /api/state/fee-schedules/:id/approve
POST   /api/state/fee-schedules/:id/suspend
GET    /api/state/fee-schedules/export
```

## 24.6 Subscription Plans

```txt
GET    /api/subscription-plans
GET    /api/subscription-plans/:id
POST   /api/admin/subscription-plans
PATCH  /api/admin/subscription-plans/:id
PATCH  /api/admin/subscription-plans/:id/archive
```

## 24.7 Employer Subscriptions

```txt
GET    /api/employers/:id/subscription
POST   /api/employers/:id/subscription/subscribe
POST   /api/employers/:id/subscription/renew
POST   /api/employers/:id/subscription/upgrade
POST   /api/employers/:id/subscription/downgrade
POST   /api/employers/:id/subscription/cancel
GET    /api/employers/:id/invoices
GET    /api/employers/:id/invoices/:invoice_id
GET    /api/employers/:id/receipts
```

## 24.8 Facility Settlements

```txt
GET    /api/facilities/:id/settlements
GET    /api/facilities/:id/settlements/:settlement_id
GET    /api/facilities/:id/settlements/export
POST   /api/facilities/:id/settlements/:settlement_id/dispute
```

## 24.9 Platform Settlement Management

```txt
GET    /api/admin/settlements/eligible
POST   /api/admin/settlement-batches
GET    /api/admin/settlement-batches
GET    /api/admin/settlement-batches/:id
POST   /api/admin/settlement-batches/:id/approve
POST   /api/admin/settlement-batches/:id/process
POST   /api/admin/settlement-records/:id/retry
POST   /api/admin/settlement-records/:id/hold
POST   /api/admin/settlement-records/:id/release-hold
```

## 24.10 State Finance Reports

```txt
GET    /api/state/finance/dashboard
GET    /api/state/finance/revenue
GET    /api/state/finance/settlements
GET    /api/state/finance/refunds
GET    /api/state/finance/reconciliation
GET    /api/state/finance/export
```

## 24.11 Federal Finance Reports

```txt
GET    /api/federal/finance/dashboard
GET    /api/federal/finance/revenue-by-state
GET    /api/federal/finance/subscriptions
GET    /api/federal/finance/settlements
GET    /api/federal/finance/reconciliation
GET    /api/federal/finance/provider-performance
GET    /api/federal/finance/export
```

## 24.12 Refunds and Disputes

```txt
GET    /api/admin/refunds
GET    /api/admin/refunds/:id
POST   /api/admin/refunds/:id/approve
POST   /api/admin/refunds/:id/reject
POST   /api/admin/refunds/:id/process
GET    /api/admin/settlement-disputes
GET    /api/admin/settlement-disputes/:id
POST   /api/admin/settlement-disputes/:id/respond
POST   /api/admin/settlement-disputes/:id/close
```

---

# 25. Frontend Routes

## 25.1 Food Handler Routes

```txt
/app/food-handler/payments
/app/food-handler/payments/:id
/app/food-handler/payments/:id/receipt
/app/food-handler/assessment/:assessment_id/pay
```

## 25.2 Employer Routes

```txt
/app/employer/billing
/app/employer/billing/plans
/app/employer/billing/subscription
/app/employer/billing/invoices
/app/employer/billing/invoices/[id]
/app/employer/billing/receipts
/app/employer/billing/bulk-assessment-payments
```

## 25.3 Facility Routes

```txt
/app/facility/settlements
/app/facility/settlements/[id]
/app/facility/settlements/disputes
/app/facility/settlements/reports
```

## 25.4 State Ministry Routes

```txt
/app/state/finance/dashboard
/app/state/finance/fee-schedules
/app/state/finance/fee-schedules/[id]
/app/state/finance/revenue
/app/state/finance/settlements
/app/state/finance/refunds
/app/state/finance/reconciliation
/app/state/finance/reports
```

## 25.5 Federal Ministry Routes

```txt
/app/federal/finance/dashboard
/app/federal/finance/revenue-by-state
/app/federal/finance/subscriptions
/app/federal/finance/settlements
/app/federal/finance/reconciliation
/app/federal/finance/provider-performance
/app/federal/finance/reports
```

## 25.6 Platform Admin Routes

```txt
/app/admin/payments/providers
/app/admin/payments/transactions
/app/admin/payments/reconciliation
/app/admin/subscription-plans
/app/admin/settlements
/app/admin/settlements/batches
/app/admin/refunds
/app/admin/disputes
```

---

# 26. Core Frontend Components

- PaymentStatusBadge
- PaymentMethodSelector
- AssessmentFeeSummaryCard
- PaymentCheckoutButton
- PaymentReceiptViewer
- RefundRequestModal
- SubscriptionPlanCards
- SubscriptionStatusBadge
- BillingUsageCard
- InvoiceTable
- ReceiptTable
- BulkAssessmentPaymentBuilder
- FeeScheduleForm
- FeeScheduleApprovalPanel
- FeeSplitPreview
- FacilitySettlementDashboardCards
- SettlementTable
- SettlementBatchTable
- SettlementDisputeModal
- StateFinanceDashboardCards
- FederalFinanceDashboardCards
- ReconciliationStatusTable
- ProviderPerformanceChart
- PaymentProviderSettingsForm
- RefundApprovalPanel

---

# 27. Permissions and Access Control

## 27.1 Food Handler

Can access own payment records and receipts.

## 27.2 Employer Admin/Finance User

Can manage employer subscription and billing.

## 27.3 Employer Viewer

May view subscription status but not manage payment methods or plans.

## 27.4 Facility Finance User

Can view facility settlements and raise disputes.

## 27.5 Facility Admin

Can view settlement summaries and manage finance users.

## 27.6 State Finance Officer

Can view state financial data and create fee schedules.

## 27.7 State Admin

Can approve fee schedules and view state finance reports.

## 27.8 Federal Finance/Oversight User

Can view national finance dashboards and exports according to permission.

## 27.9 Platform Finance Admin

Can manage providers, reconciliation, refunds, and settlement batches.

---

# 28. Audit Logging

Create audit logs for:

- Payment initialized
- Payment verified
- Payment failed
- Provider webhook received
- Webhook verification failed
- Receipt generated
- Refund requested
- Refund approved/rejected
- Refund processed
- Fee schedule created
- Fee schedule approved
- Fee schedule suspended
- Subscription plan created/updated
- Employer subscribed
- Subscription renewed
- Subscription upgraded/downgraded
- Subscription cancelled
- Settlement eligibility created
- Settlement batch created
- Settlement batch approved
- Settlement processed
- Settlement failed
- Settlement retried
- Settlement dispute created/responded/closed
- Reconciliation mismatch detected
- Manual reconciliation resolution
- Provider configuration changed

---

# 29. Background Jobs

## 29.1 Payment Expiry Job

Runs periodically.

Tasks:

- Find initialized payments not completed within configured time.
- Mark as abandoned/expired.
- Notify payer where appropriate.

## 29.2 Payment Verification Retry Job

Tasks:

- Re-check transactions stuck in awaiting provider confirmation.
- Verify provider status.
- Update internal status.

## 29.3 Subscription Renewal Reminder Job

Tasks:

- Notify employers before renewal/expiry.
- Generate renewal invoices.
- Process auto-renewal where enabled.

## 29.4 Subscription Expiry Job

Tasks:

- Mark expired subscriptions.
- Apply access restrictions.
- Notify employer.

## 29.5 Settlement Eligibility Job

Tasks:

- Identify completed/validated assessments eligible for facility settlement.
- Create settlement records.

## 29.6 Settlement Batch Job

Tasks:

- Prepare eligible settlement batches for review or auto-processing depending on policy.

## 29.7 Reconciliation Job

Tasks:

- Pull or import provider transactions.
- Match against internal ledger.
- Flag mismatches.

---

# 30. Error Handling

## 30.1 Payment Initialization Errors

Examples:

- No active payment provider
- Fee schedule missing
- Invalid amount
- Assessment not eligible for payment
- Provider unavailable

User-safe response:

- “Payment could not be started. Please try again or contact support.”

## 30.2 Webhook Errors

Examples:

- Invalid signature
- Unknown provider reference
- Amount mismatch
- Duplicate webhook
- Provider verification failed

Rules:

- Store webhook event.
- Do not mark payment successful unless verified.
- Log processing result.
- Alert finance/admin for critical mismatch.

## 30.3 Settlement Errors

Examples:

- Missing facility bank details
- Provider transfer failed
- Amount mismatch
- Duplicate settlement attempt

Rules:

- Mark settlement failed or on hold.
- Show failure reason to authorized users.
- Allow retry after issue is resolved.

---

# 31. Acceptance Criteria

## 31.1 Assessment Payments

- Food handler can view assessment fee.
- Food handler can initialize payment.
- Payment is verified server-side.
- Webhook processing is idempotent.
- Successful payment updates assessment status.
- Receipt is generated after successful payment.
- Failed payment can be retried.
- Assessment cannot proceed without payment where policy requires it.

## 31.2 Fee Schedules

- State can create fee schedule.
- State admin can approve fee schedule.
- Only active fee schedule is used for payment calculation.
- Historical fee schedule remains linked to old payments.
- Fee changes are audit logged.

## 31.3 Employer Subscriptions

- Employer can view plans.
- Employer can subscribe to a plan.
- Successful payment activates subscription.
- Subscription entitlements are applied.
- Expired subscription restricts premium features but does not block regulatory visibility.
- Employer can view invoices and receipts.

## 31.4 Facility Settlements

- Settlement eligibility is created only for valid completed assessments.
- Facility can view pending and paid settlements.
- Settlement batch can be created and processed.
- Paid settlement cannot be paid twice.
- Failed settlement can be retried.
- Facility can raise settlement dispute.

## 31.5 Refunds

- Refund request can be created.
- Authorized user can approve/reject refund.
- Refund creates ledger reversal entry.
- Refund updates payment/refund status.
- Partial refund works for bulk payments where applicable.

## 31.6 Reconciliation

- System can compare provider records with internal ledger.
- Matched and unmatched records are identified.
- Amount mismatches are flagged.
- Manual resolution requires reason and audit log.

## 31.7 Dashboards and Reports

- Food handler can view payment status and receipt.
- Employer can view billing dashboard.
- Facility can view settlement dashboard.
- State can view state finance dashboard.
- Federal can view national finance dashboard.
- Reports export to PDF/Excel/CSV.

## 31.8 Privacy and Security

- Finance users cannot see medical details.
- Provider secrets are protected.
- Webhook signatures are verified.
- All financial actions are audit logged.
- Ledger records are immutable.

---

# 32. Codex Implementation Instructions

Use this prompt for Codex:

```txt
Implement the Payments, Subscriptions & Settlements Module for FoodCert NG.

The module must support assessment payments by food handlers, employer subscriptions, state assessment fee schedules, payment provider abstraction, checkout initialization, webhook verification, server-side payment verification, receipts, invoices, immutable payment ledger, employer subscription entitlements, bulk employer assessment payments, facility settlement eligibility, settlement batches, state revenue reporting, federal finance oversight, refunds, reversals, chargebacks, settlement disputes, reconciliation, background jobs, role-based permissions, privacy-safe finance serializers, and audit logs.

Important rules:
- Assessment payment amount must come from the active state-approved fee schedule.
- Assessment cannot proceed without successful payment where policy requires prepayment.
- Webhooks must be signature-verified and idempotent.
- Provider callbacks must not be trusted without server-side verification.
- Payment records and ledger entries must not be deleted or destructively edited.
- Historical payments must retain the fee schedule and fee split used at payment time.
- Employer subscriptions control premium access but must not block regulatory visibility.
- Facility settlements must be traceable to payment allocation, assessment, facility, state, and settlement batch.
- Paid settlements must not be paid twice.
- Refunds must create reversal/refund ledger entries.
- Finance views must not expose lab results, diagnosis, doctor notes, declaration answers, or full NIN.
- State users only see their state financial records.
- Federal users see national finance oversight based on permission.
- All financial actions must be audit logged.

Build backend models, provider adapters, services, serializers, permissions, endpoints, webhook handlers, background jobs, tests, and frontend pages for the module.
```

---

# 33. MVP Build Order

1. PaymentProvider model and provider adapter interface
2. AssessmentFeeSchedule model and state fee configuration UI
3. PaymentTransaction model and payment initialization API
4. Provider payment verification and webhook handler
5. Payment receipt generation
6. Assessment payment integration with Medical Assessment Workflow
7. SubscriptionPlan model
8. EmployerSubscription model and billing UI
9. Employer invoices and receipts
10. Subscription entitlement enforcement
11. PaymentAllocation model and fee split service
12. SettlementRecord model
13. Settlement eligibility service
14. Settlement batch creation and processing
15. Facility settlement dashboard
16. State finance dashboard
17. Federal finance dashboard
18. Refund request workflow
19. Reconciliation dashboard
20. Payment expiry and verification background jobs
21. Subscription renewal/expiry background jobs
22. Settlement eligibility background job
23. Finance-safe serializers
24. Financial audit logs
25. Permission tests
26. Webhook idempotency tests
27. Payment privacy tests
28. Settlement duplicate-prevention tests
