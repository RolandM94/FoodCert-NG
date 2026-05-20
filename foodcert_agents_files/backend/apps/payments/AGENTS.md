# payments/AGENTS.md — Payments, Subscriptions, and Settlements Instructions

## Scope

This area manages:
- Food handler assessment payments
- Employer subscriptions
- Medical facility settlements
- State fee and platform fee allocation
- Payment provider abstraction
- Receipts
- Reconciliation
- Refunds and failed payments

## Key Product Rules

- Food handlers pay assessment fees through the platform.
- Employers pay subscription fees.
- Medical facilities receive settlements through the platform.
- Assessment should not be activated until payment is successful unless policy explicitly allows it.
- Payment amounts must be calculated on the backend.
- Payment provider-specific logic must be abstracted.

## Provider Abstraction

Create a payment provider interface with methods like:
- initialize_payment()
- verify_payment()
- refund_payment()
- create_transfer_recipient()
- initiate_transfer()
- verify_transfer()

Do not put Paystack, Flutterwave, Remita, or other provider-specific logic directly in views.

## Assessment Payments

Payment flow:
1. Food handler selects state and approved facility.
2. Backend calculates applicable state-approved assessment fee.
3. Backend creates payment transaction with internal reference.
4. Payment provider checkout is initialized.
5. Provider webhook or verification confirms payment.
6. Assessment becomes active.
7. Receipt is generated.
8. Settlement eligibility is created after assessment completion and State validation.

## Assessment Fee Rules

Assessment fee should support:
- Gross assessment amount
- Facility amount
- State amount
- Platform amount
- Effective date range
- State-specific configuration
- Facility-type-specific configuration

## Employer Subscriptions

Employer subscription plan should support:
- Plan name
- Monthly price
- Yearly price
- Max food handlers
- Max locations
- Features
- Status

Subscription statuses:
- trial
- active
- past_due
- suspended
- cancelled
- expired

If subscription expires:
- Employer should still receive regulatory notices.
- Employer should not lose access to already-issued certificate status.
- Employer may be restricted from adding new food handlers or exporting premium reports.

## Settlements

Settlement flow:
1. Payment successful.
2. Assessment completed.
3. Doctor decision submitted.
4. State validation completed.
5. Certificate issued or report finalized.
6. Settlement becomes eligible.
7. Facility amount, State amount, and platform amount are calculated.
8. Settlement is marked pending.
9. Payout is processed.
10. Settlement is marked paid or failed.

## Audit Requirements

Audit:
- Payment initialized
- Payment confirmed
- Payment failed
- Refund initiated
- Subscription activated
- Subscription suspended
- Settlement created
- Settlement paid
- Settlement failed

## Do Not Do

- Do not trust frontend amounts.
- Do not issue certificate before payment is confirmed.
- Do not settle facility before assessment completion and State validation.
- Do not hardcode one payment provider.
- Do not process webhooks without signature verification.
