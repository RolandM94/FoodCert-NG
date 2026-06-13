# PRD: Assessment Fees Settings, State Fee Configuration & Payment UI Consolidation — FoodCert NG

## 1. Document Purpose

This PRD defines how **Food Handler Assessment Fees** should be configured, governed, displayed, applied, collected, reconciled, and reported within FoodCert NG.

The core product decision is:

> **Assessment fees are set by the State Ministry of Health for its own state and applied uniformly to all approved medical facilities within that state.**

> **Platform service fees are set by the FoodCert platform owner, not by State Ministries. The platform fee is automatically added to the state-approved assessment fee at checkout as part of the final customer payable amount.**

The fee-setting interface should be located under the **State Ministry account**, not the Medical Facility account.

Recommended location:

```txt
State Ministry
├── Settings
│   └── Fees & Payments
```

Alternative operational shortcut:

```txt
State Ministry
├── Revenue / Payments
│   └── Assessment Fee Settings, read-only shortcut or deep link
```

The **Medical Facility account** should only see the active state-approved fee schedule as read-only and should not be able to set or override official assessment fees.

---

# 2. Guideline Alignment

The National Guideline for Food Handlers’ Medical Test establishes that approved medical facilities are mapped to their respective states, that pre-qualification and monitoring are handled by the relevant departments in State Ministries of Health, and that the **prices of food handlers’ medical assessments shall be standardised per state for all approved medical facilities**.

Therefore, the FoodCert NG platform should enforce a state-controlled fee schedule.

This means:

```txt
Fee Setter: State Ministry of Health
Fee Scope: Per State
Applies To: All approved medical facilities in that state
Medical Facility Role: View-only fee schedule; cannot set official assessment fee
Federal Ministry Role: National oversight and reporting, not day-to-day fee setting
Platform Admin Role: Owns platform service fee configuration and system support, not state policy fee setting
```

---

# 3. Product Decision

## 3.1 Who Sets Assessment Fees?

The **State Ministry of Health** sets the food handler assessment fee for its state.

The authorized state users are usually from:

```txt
Policy & Finance Unit
Revenue Unit
State Ministry Admin
Authorized State Finance Officer
```

The **FoodCert platform owner** sets the platform service fee. State Ministry users must not create, edit, or override the platform service fee.

## 3.2 Where Should Fee Settings Be Located?

Assessment fee settings should be located in:

```txt
State Ministry → Settings → Fees & Payments
```

This is the correct location because fee settings are state policy/finance configuration, not a medical facility setting.

## 3.3 Who Can View the Fee?

The active fee schedule should be visible to:

```txt
State Ministry users, based on permission
Approved Medical Facilities, read-only
Food Handlers, during assessment booking/payment
Employers, where employer pays on behalf of food handlers
Federal Ministry, oversight/reporting view
Platform Admin, support/audit view
```

Customer-facing payment screens should show the final payable amount as:

```txt
State-approved assessment fee
+ FoodCert platform fee
= Final amount payable by customer
```

## 3.4 Who Cannot Edit the Fee?

The following users must not edit the official assessment fee:

```txt
Medical Facility Admin
Doctor
Lab Staff
Employer Admin
Branch Manager
Food Handler
Inspector
```

---

# 4. Core Product Principle

Use this rule throughout the platform:

> **State controls the assessment price. Facilities provide the assessment service. Food handlers or employers pay through the platform. Facilities receive settlements according to state-approved payment and settlement rules.**

The assessment fee is not a facility-level commercial setting.

---

# 5. UI Consolidation Decision

## 5.1 Do Not Create a Standalone Fee Module

Do not create separate top-level modules called:

```txt
Assessment Fees
Fee Management
Pricing
Facility Fees
Medical Facility Pricing
```

Assessment fee configuration should be consolidated under State Ministry settings.

## 5.2 Recommended State Ministry Structure

```txt
State Ministry
├── Dashboard
├── Stakeholder Management
├── Medical Facilities
├── Directory & Registry
├── Certificate Validation
├── Certificate Registry
├── Inspections
├── Reports
├── Revenue / Payments
└── Settings
    ├── State Profile
    ├── Policy Settings
    ├── Fees & Payments
    ├── Certificate Rules
    ├── Notification Settings
    └── Security / Audit
```

## 5.3 Fees & Payments Subsection

Inside **Settings → Fees & Payments**, use tabs or cards:

```txt
Fees & Payments
├── Assessment Fees
├── Certificate Fees, if applicable
├── Facility Accreditation Fees, if applicable
├── Re-accreditation Fees, if applicable
├── Settlement Rules
├── Effective Dates
├── Payment Gateway Settings, permission-based
└── Change History
```

## 5.4 Revenue / Payments Module Relationship

The **Revenue / Payments** module should focus on operations and reporting:

```txt
Revenue / Payments
├── Collections
├── Transactions
├── Settlements
├── Reconciliation
├── Refunds
├── Reports
└── Fee Schedule, read-only or shortcut to Settings
```

Revenue / Payments can show the active fee schedule, but the actual fee-editing screen should live under:

```txt
State Ministry → Settings → Fees & Payments
```

---

# 6. User Roles and Access Expectations

## 6.1 State Ministry Admin

Can:

```txt
View fee settings
Create draft fee schedule
Edit draft fee schedule
Submit for approval, if approval workflow is enabled
Approve fee schedule, if permitted
Publish fee schedule
Set effective date
Deactivate expired fee schedule
View fee history
Export fee settings
```

## 6.2 State Policy & Finance Unit

Can:

```txt
Configure assessment fees
Configure settlement split rules
Configure effective dates
Review collections and settlement impact
View payment reports
```

## 6.3 State Revenue / Finance Officer

Can:

```txt
View active fee schedule
View transaction collections
View settlements
View reconciliation reports
Export payment reports
```

May or may not edit fee settings depending on permission.

## 6.4 Medical Facility Admin

Can:

```txt
View active state assessment fee schedule
View amount payable by food handler
View facility settlement share, if permitted
View assessment payment status
View settlement reports
```

Cannot:

```txt
Create assessment fees
Edit assessment fees
Override assessment fees
Create facility-specific assessment price
```

## 6.5 Employer Admin

Can:

```txt
View payable assessment fee during booking/payment
Pay for one or more food handlers, if employer payment is supported
View payment receipts for payments made by employer
```

Cannot edit assessment fees.

## 6.6 Food Handler

Can:

```txt
View assessment fee before payment
Pay assessment fee
View receipt
View payment status
```

Cannot edit assessment fees.

## 6.7 Federal Ministry

Can:

```txt
View state fee schedules nationally
Compare fees across states
View national fee adoption reports
View aggregate revenue reports, if permitted
```

Cannot edit a state’s fee unless explicitly given national policy override permissions.

## 6.8 Platform Admin

Can:

```txt
Configure global system fee categories
Support payment gateway integration
Audit fee changes
Assist with failed configuration issues
```

Platform Admin should not be treated as the policy owner for state fees.
Platform Admin is the owner of FoodCert platform service fees.

---

# 7. Fee Types

## 7.1 Required Fee Type

The primary required fee is:

```txt
Food Handler Assessment Fee
```

## 7.2 Optional Fee Types

Depending on state policy, the system may also support:

```txt
Certificate Issuance Fee
Facility Accreditation Application Fee
Facility Re-accreditation Fee
Late Renewal Fee
Replacement Certificate Fee
Inspection Revisit Fee
```

These optional fees should be configurable but can be disabled by default.

## 7.3 Fee Category Model

Each fee should have:

```txt
Fee Name
Fee Code
Fee Description
Fee Type
Amount
Currency
Applies To
State
Effective Date
Expiry Date, optional
Status
Created By
Approved By
Published By
```

---

# 8. Assessment Fee Configuration Requirements

## 8.1 Assessment Fee Fields

The Assessment Fee configuration screen should include:

```txt
State
Fee Name
Fee Type
Assessment Category
Amount
Currency
Applies to Facility Type, optional
Applies to Food Handler Category, optional
Payment Required Before Assessment
Payment Required Before Certificate Issuance
Effective Start Date
Effective End Date, optional
Status
Internal Notes
Public Description
```

## 8.2 Fee Statuses

Recommended statuses:

```txt
Draft
Pending Approval
Approved
Scheduled
Active
Expired
Archived
Rejected
```

## 8.3 Effective Date Rules

- Only one active assessment fee schedule should exist per state for a given assessment category and scope.
- A new fee can be scheduled for the future.
- Existing active fee should remain active until the new effective date.
- Backdating should require special permission.
- Expired fees should remain in history for audit and reconciliation.

## 8.4 Fee Uniformity Rule

For the standard food handler assessment:

```txt
All approved medical facilities in the same state must use the same active assessment fee.
```

Facility-specific pricing should not be allowed unless a formal policy exception exists.

## 8.5 Facility Type Variation, Optional

If a state policy allows variation by facility or service type, it must be controlled by state configuration, not by the facility.

Example:

```txt
Basic Assessment Fee
Enhanced Assessment Fee
Additional Clinically Indicated Test Fee
```

However, the MVP should keep a simple uniform fee per state.

---

# 9. Payment and Assessment Workflow Integration

## 9.1 Food Handler Self-Payment Flow

```txt
Food handler selects approved medical facility
→ Platform identifies food handler’s state
→ Platform fetches active state assessment fee
→ Food handler reviews fee
→ Food handler pays through platform
→ Payment success creates assessment payment record
→ Medical facility can proceed with assessment
→ Settlement is processed according to state rules
```

## 9.2 Employer-Sponsored Payment Flow

```txt
Employer selects food handlers for assessment
→ Platform calculates total payable based on state fee
→ Employer pays for selected food handlers
→ Payment records are linked to each food handler assessment
→ Medical facility sees paid assessment appointments
→ Receipts are available to employer and food handlers
```

## 9.3 Medical Facility Workflow

```txt
Facility receives appointment / assessment request
→ Facility sees payment status
→ Facility sees active state fee schedule, read-only
→ Facility conducts assessment only when payment rule is satisfied
→ Facility submits assessment result
→ Settlement record is generated
```

## 9.4 Certificate Workflow

If certificate issuance requires payment or payment verification:

```txt
Assessment completed
→ Payment verified
→ State validates/approves certificate issuance
→ Certificate generated
```

---

# 10. Settlement Rules

## 10.1 Settlement Configuration Location

Settlement rules should also be configured under:

```txt
State Ministry → Settings → Fees & Payments → Settlement Rules
```

## 10.2 Settlement Split Examples

Depending on policy, the assessment fee may be split across:

```txt
Medical Facility Share
State Ministry / Regulatory Share
Payment Gateway Charge
Other Statutory Charges, if applicable
```

The FoodCert platform service charge is configured separately by the platform owner and added at checkout. It is not part of the state-managed assessment fee split.

## 10.3 Settlement Rule Fields

```txt
State
Fee Type
Facility Share Type, fixed or percentage
Facility Share Value
State Share Type, fixed or percentage
State Share Value
Gateway Fee Handling
Effective Date
Status
```

## 10.4 Settlement Rule Validation

- Percentage splits must not exceed 100%.
- Fixed charges must not exceed total fee.
- Gateway charges must be clearly defined.
- Changes must be effective-dated and audit logged.
- Settlement rule must match active fee schedule.

---

# 11. Medical Facility Read-Only Fee View

Medical Facility accounts should have a read-only page or card:

```txt
Medical Facility
├── Settlements
├── Assessment Payments
└── Active State Fee Schedule
```

## 11.1 Read-Only Fee Schedule Fields

```txt
State
Assessment Fee
Currency
Effective Date
Payment Rule
Settlement Rule Summary, permission-based
Last Updated
Configured By State Ministry
```

## 11.2 Facility Restrictions

Medical facilities must not see edit actions such as:

```txt
Edit Fee
Create Fee
Override Fee
Set Facility Price
Publish Fee
```

---

# 12. Federal Oversight View

Federal Ministry users may need national visibility.

Recommended placement:

```txt
Federal Ministry
├── Reports
│   └── State Fee Schedule Report
├── Revenue Oversight
│   └── Assessment Fee Comparison
└── Settings, national policy only
```

Federal view should show:

```txt
State
Active Assessment Fee
Effective Date
Last Updated
Facilities Covered
Assessment Volume
Revenue Collected
Status
```

Federal users should not edit state fees unless a special permission exists.

---

# 13. UI Requirements

## 13.1 State Fee Settings Page Header

```txt
Fees & Payments
Configure assessment fees, payment rules, and settlement settings for your state.
```

Primary actions:

```txt
Create Fee Schedule
Create New Version
Export History
```

## 13.2 Assessment Fees Tab

### KPI Cards

```txt
Active Assessment Fee
Effective Date
Approved Facilities Covered
Assessment Payments This Month
Pending Fee Changes
```

### Fee Table Columns

```txt
Fee Name
Fee Type
Amount
Currency
Applies To
Effective Start
Effective End
Status
Created By
Approved By
Actions
```

### Actions

```txt
View
Edit Draft
Submit for Approval
Approve
Reject
Publish
Schedule
Archive
View History
```

Actions should be permission-based.

## 13.3 Create / Edit Fee Schedule Form

Fields:

```txt
Fee Name
Fee Type
Amount
Currency
Assessment Category
Applies To
Payment Rule
Effective Start Date
Effective End Date
Public Description
Internal Notes
```

Validation:

```txt
Amount must be greater than zero
Currency required
Effective date required
Only one active fee for same state/category/scope
Cannot edit active fee directly; create new version instead
```

## 13.4 Settlement Rules Tab

Columns:

```txt
Rule Name
Fee Type
Facility Share
State Share
Platform Charge
Gateway Fee Handling
Effective Date
Status
Actions
```

## 13.5 Change History Tab

Columns:

```txt
Date
Action
Fee Type
Old Amount
New Amount
Changed By
Approved By
Effective Date
Reason
```

---

# 14. Data Model Requirements

## 14.1 StateFeeSchedule

```txt
id
state_id
fee_name
fee_code
fee_type
assessment_category
amount
currency
applies_to_facility_type
applies_to_food_handler_category
payment_required_before_assessment
payment_required_before_certificate
public_description
internal_notes
status
effective_start_date
effective_end_date
created_by
approved_by
approved_at
published_by
published_at
rejected_by
rejected_at
rejection_reason
created_at
updated_at
```

## 14.2 FeeScheduleVersion

```txt
id
fee_schedule_id
version_number
amount
currency
settings_json
status
effective_start_date
effective_end_date
created_by
approved_by
published_by
created_at
```

## 14.3 SettlementRule

```txt
id
state_id
fee_schedule_id
rule_name
facility_share_type
facility_share_value
state_share_type
state_share_value
platform_charge_type
platform_charge_value
gateway_fee_handling
status
effective_start_date
effective_end_date
created_by
approved_by
published_by
created_at
updated_at
```

## 14.4 AssessmentPayment

```txt
id
food_handler_id
employer_id, optional
medical_facility_id
state_id
assessment_id, optional
appointment_id, optional
fee_schedule_id
fee_version_id
amount
currency
payment_status
payment_reference
gateway_reference
paid_by_user_id
paid_by_type
paid_at
receipt_url
created_at
updated_at
```

## 14.5 FacilitySettlement

```txt
id
assessment_payment_id
medical_facility_id
state_id
settlement_rule_id
gross_amount
facility_share
state_share
platform_charge
gateway_charge
net_settlement_amount
settlement_status
settlement_reference
settled_at
created_at
updated_at
```

## 14.6 FeeAuditLog

```txt
id
actor_id
state_id
action
entity_type
entity_id
old_value_json
new_value_json
reason
ip_address
user_agent
created_at
```

---

# 15. API Requirements

## 15.1 State Fee Settings APIs

```txt
GET    /api/state/settings/fees
POST   /api/state/settings/fees
GET    /api/state/settings/fees/:id
PATCH  /api/state/settings/fees/:id
POST   /api/state/settings/fees/:id/submit
POST   /api/state/settings/fees/:id/approve
POST   /api/state/settings/fees/:id/reject
POST   /api/state/settings/fees/:id/publish
POST   /api/state/settings/fees/:id/archive
GET    /api/state/settings/fees/:id/history
```

## 15.2 Active Fee Lookup APIs

```txt
GET /api/fees/active-assessment-fee?state_id={stateId}
GET /api/fees/active-assessment-fee?facility_id={facilityId}
GET /api/fees/active-assessment-fee?food_handler_id={foodHandlerId}
```

## 15.3 Settlement Rule APIs

```txt
GET    /api/state/settings/settlement-rules
POST   /api/state/settings/settlement-rules
GET    /api/state/settings/settlement-rules/:id
PATCH  /api/state/settings/settlement-rules/:id
POST   /api/state/settings/settlement-rules/:id/approve
POST   /api/state/settings/settlement-rules/:id/publish
POST   /api/state/settings/settlement-rules/:id/archive
```

## 15.4 Payment APIs

```txt
POST /api/payments/assessment/initiate
POST /api/payments/assessment/verify
GET  /api/payments/assessment/:id
GET  /api/payments/assessment/:id/receipt
```

## 15.5 Medical Facility Read-Only APIs

```txt
GET /api/facility/fee-schedule/active
GET /api/facility/settlements
GET /api/facility/assessment-payments
```

## 15.6 Federal Oversight APIs

```txt
GET /api/federal/reports/state-fee-schedules
GET /api/federal/reports/assessment-fee-comparison
GET /api/federal/reports/assessment-revenue-summary
```

---

# 16. Permissions

## 16.1 Fee Settings Permissions

```txt
fees.view
fees.create
fees.update_draft
fees.submit_for_approval
fees.approve
fees.reject
fees.publish
fees.archive
fees.view_history
fees.export_history
```

## 16.2 Settlement Permissions

```txt
settlement_rules.view
settlement_rules.create
settlement_rules.update_draft
settlement_rules.approve
settlement_rules.publish
settlement_rules.archive
```

## 16.3 Payment Permissions

```txt
assessment_payment.initiate
assessment_payment.verify
assessment_payment.view
assessment_payment.view_receipt
assessment_payment.refund
```

## 16.4 Facility Permissions

```txt
facility_fee_schedule.view
facility_settlements.view
facility_assessment_payments.view
```

## 16.5 Federal Oversight Permissions

```txt
federal_fee_schedules.view
federal_fee_reports.export
```

## 16.6 Permission Rules

- Only state-authorized users can create or update state fee schedules.
- Only users with approval permission can approve fee schedules.
- Active fee schedules cannot be edited directly; a new version must be created.
- Medical facilities can only view fee schedules for their mapped state.
- Food handlers and employers can only view the fee at the point of payment.
- Federal users can view fee schedules across states but cannot edit state fees without special permission.
- All fee changes must be audit logged.

---

# 17. Validation and Business Rules

## 17.1 Fee Schedule Rules

```txt
Amount must be greater than zero.
Currency is required.
State is required.
Effective start date is required.
Only one active fee schedule per state/category/scope.
A future fee schedule can be scheduled.
Active fee cannot be edited directly.
Expired fee cannot be reused.
Archived fee cannot be assigned to new payments.
```

## 17.2 Payment Rules

```txt
Assessment payment must use the active fee schedule at the time of payment.
Payment record must store fee schedule ID and version ID.
Later fee changes must not change historical payment records.
Payment must be verified before assessment if payment_required_before_assessment is true.
Receipt must show fee amount and state fee schedule reference.
```

## 17.3 Settlement Rules

```txt
Settlement must use the rule active at the time of payment or assessment completion, based on configured policy.
Settlement calculation must be reproducible.
Settlement record must store settlement rule ID.
Settlement changes must not alter completed settlements.
```

---

# 18. Reporting Requirements

## 18.1 State Reports

```txt
Assessment Fee Schedule Report
Assessment Payment Collections Report
Medical Facility Collections Report
Settlement Report
Outstanding Payments Report
Fee Change History Report
Revenue by LGA Report
Revenue by Facility Report
```

## 18.2 Federal Reports

```txt
State Fee Schedule Comparison
National Assessment Revenue Summary
Assessment Fee Adoption Report
Fee Change Monitoring Report
State Collections Comparison
```

## 18.3 Medical Facility Reports

```txt
Assessment Payments Received
Pending Settlements
Settled Payments
Assessment Volume vs Settlement Report
```

---

# 19. Notifications

Notify relevant users when:

```txt
Draft fee schedule is created
Fee schedule submitted for approval
Fee schedule approved
Fee schedule rejected
Fee schedule published
New fee becomes active
Fee schedule is about to expire
Settlement rule changes
Payment is successful
Payment fails
Settlement is processed
```

Notification recipients:

```txt
State Policy & Finance Unit
State Revenue Officers
Medical Facilities, for active fee changes
Food handlers/employers, for payment receipts
Platform Admin, for payment gateway failures
```

---

# 20. Audit and Compliance

Fee settings are financially sensitive.

Audit log must capture:

```txt
Fee created
Fee edited
Fee submitted
Fee approved
Fee rejected
Fee published
Fee archived
Settlement rule created
Settlement rule changed
Payment initiated
Payment verified
Refund initiated
Settlement calculated
Settlement paid
Report exported
```

Each audit record should capture:

```txt
Actor
Role
Organization
State
Action
Old value
New value
Reason
Timestamp
IP address
User agent
```

---

# 21. Acceptance Criteria

## 21.1 State Fee Configuration

- State authorized users can create assessment fee schedule.
- Fee schedule is scoped to the state.
- Fee amount, effective dates, and payment rules can be configured.
- Active fee cannot be edited directly.
- Fee changes require new version or approval flow.
- Change history is visible.

## 21.2 UI Consolidation

- Fee settings are located under State Ministry Settings → Fees & Payments.
- Revenue / Payments module shows transactions, settlements, and read-only fee schedule shortcut.
- Medical Facility does not have fee editing screens.
- No standalone top-level Assessment Fees module exists.

## 21.3 Payment Application

- Food handler payment uses active state fee.
- Employer bulk payment uses active state fee per food handler.
- Payment records store fee schedule and version.
- Receipt shows paid amount and payment reference.

## 21.4 Facility View

- Medical facility can view active fee schedule.
- Medical facility cannot edit or override assessment fees.
- Facility can view payment and settlement records.

## 21.5 Federal Oversight

- Federal users can view fee schedules across states.
- Federal users cannot edit state fees unless given special permission.
- Federal reports show state fee comparison.

## 21.6 Security and Audit

- Fee changes are permission-controlled.
- Fee changes are audit logged.
- Payment and settlement events are audit logged.
- Exports are permission-controlled.

---

# 22. Implementation Chunks for Codex

## Chunk 1: Fee Settings Navigation and UI Consolidation

### Goal

Place assessment fee settings under State Ministry Settings → Fees & Payments and remove duplicate fee menus.

### Tasks

- Add Fees & Payments under State Ministry Settings.
- Add Assessment Fees tab.
- Add Settlement Rules tab.
- Add Change History tab.
- Ensure Revenue / Payments has read-only shortcut only.
- Ensure Medical Facility has read-only fee schedule only.
- Remove or redirect standalone Assessment Fees/Fee Management routes.

### Acceptance Criteria

- State users configure fees only under Settings → Fees & Payments.
- Medical facilities cannot access fee edit screen.
- No duplicate fee-setting module exists.
- Old routes redirect correctly.

Suggested redirects:

```txt
/state/assessment-fees → /state/settings/fees-payments?tab=assessment-fees
/state/fee-management → /state/settings/fees-payments?tab=assessment-fees
/facility/fee-settings → /facility/fee-schedule
```

---

## Chunk 2: Fee Schedule Data Models

### Goal

Create state fee schedule models.

### Tasks

- Implement `StateFeeSchedule`.
- Implement `FeeScheduleVersion`.
- Add fee statuses.
- Add effective date fields.
- Add fee type/category fields.
- Add audit log model or connect to existing audit log.

### Acceptance Criteria

- Fee schedule can be stored by state.
- Fee versions can be stored.
- Historical versions remain accessible.
- Audit log records changes.

---

## Chunk 3: Fee Settings APIs

### Goal

Create backend APIs for managing fee schedules.

### Tasks

- Add list, create, detail, update draft APIs.
- Add submit, approve, reject, publish, archive actions.
- Add fee history endpoint.
- Add active fee lookup endpoint.
- Enforce state scope.

### Acceptance Criteria

- State users can manage fees through API.
- Active fee lookup returns correct fee.
- Only authorized users can modify fees.
- Medical facilities cannot modify fees.

---

## Chunk 4: Assessment Fees UI

### Goal

Build the State Assessment Fees configuration interface.

### Tasks

- Create `FeesPaymentsSettingsPage`.
- Create `AssessmentFeesTab`.
- Create fee table.
- Create fee form drawer/modal.
- Add status badges.
- Add action buttons.
- Add validation messages.

### Acceptance Criteria

- User can create draft fee.
- User can submit/approve/publish based on permission.
- Active fee is clearly shown.
- Future scheduled fee is clearly shown.
- Validation prevents duplicate active fee.

---

## Chunk 5: Settlement Rules

### Goal

Implement settlement rule configuration.

### Tasks

- Implement `SettlementRule` model.
- Add settlement rule APIs.
- Build Settlement Rules UI tab.
- Validate split totals.
- Link settlement rule to fee schedule.

### Acceptance Criteria

- State can configure settlement rule.
- Rule can be effective-dated.
- Invalid splits are rejected.
- Rule is audit logged.

---

## Chunk 6: Payment Workflow Integration

### Goal

Apply active state assessment fee during payment.

### Tasks

- Update assessment payment initiation.
- Fetch active fee by state/facility/food handler.
- Store fee schedule ID and version ID on payment.
- Generate receipt.
- Enforce payment-before-assessment rule where configured.

### Acceptance Criteria

- Payment amount matches active state fee.
- Historical payment amount does not change after fee updates.
- Receipt shows correct amount.
- Assessment cannot proceed before payment if configured.

---

## Chunk 7: Medical Facility Read-Only Fee Schedule

### Goal

Show active state fee schedule to medical facilities without edit access.

### Tasks

- Add facility fee schedule page/card.
- Add read-only active fee API.
- Show payment rule and effective date.
- Hide all edit actions.

### Acceptance Criteria

- Facility can view fee schedule.
- Facility cannot edit fee.
- Facility sees only mapped state fee.

---

## Chunk 8: Revenue / Payments Integration

### Goal

Connect fees to collections, settlements, and reconciliation.

### Tasks

- Show fee schedule reference in transaction records.
- Add collections table columns for fee schedule/version.
- Add settlement calculation using active settlement rule.
- Add reconciliation reports.
- Add read-only active fee schedule shortcut.

### Acceptance Criteria

- Transactions show linked fee schedule.
- Settlements calculate correctly.
- Revenue reports include assessment fee collections.
- Fee settings are not edited from Revenue module.

---

## Chunk 9: Federal Oversight Reports

### Goal

Allow Federal users to view state fee schedules and comparisons.

### Tasks

- Add federal fee schedule report.
- Add state comparison table.
- Add filters by state, fee status, effective date.
- Add export permission.

### Acceptance Criteria

- Federal users can compare fees across states.
- Federal users cannot edit state fee schedules by default.
- Reports respect permissions.

---

## Chunk 10: Permissions, Audit, and Tests

### Goal

Secure fee settings and financial actions.

### Tasks

- Implement permissions.
- Add backend scope checks.
- Add audit logging.
- Add unit tests for fee lifecycle.
- Add tests for active fee lookup.
- Add tests for payment amount locking.
- Add tests for facility read-only restrictions.

### Acceptance Criteria

- Unauthorized users cannot edit fees.
- Facility cannot override fee.
- Active fee lookup works.
- Historical payments remain unchanged after fee update.
- All fee changes are audited.

---

## Chunk 11: Final UI QA

### Goal

Confirm the user experience is clean and consolidated.

### QA Checklist

- State fee settings live under Settings → Fees & Payments.
- Assessment Fees tab works.
- Settlement Rules tab works.
- Change History tab works.
- Revenue module remains operational/reporting-focused.
- Facility view is read-only.
- Food handler payment displays correct fee.
- Employer bulk payment displays correct total.
- Federal oversight report works.
- Permissions and audit logs work.
- Mobile layout works.

---

# 23. Codex Implementation Prompt

Use this prompt for Codex:

```txt
Build the FoodCert NG Assessment Fees Settings and Payment Configuration workflow.

Core product rule:
Assessment fees are set by the State Ministry of Health for its own state. The fee applies uniformly to all approved medical facilities in that state. Medical facilities must not set or override the official assessment fee.

Place fee settings under:
State Ministry → Settings → Fees & Payments

Do not create a separate top-level Assessment Fees or Fee Management module.

State Settings → Fees & Payments should include:
- Assessment Fees
- Settlement Rules
- Change History

Revenue / Payments should show collections, transactions, settlements, reconciliation, reports, and a read-only shortcut to the active fee schedule. It should not be the primary fee-editing location.

Medical Facility accounts should have read-only access to the active state fee schedule and settlement/payment records. They must not see edit, create, approve, publish, or override fee actions.

Implement:
- StateFeeSchedule
- FeeScheduleVersion
- SettlementRule
- AssessmentPayment
- FacilitySettlement
- FeeAuditLog

Support fee lifecycle statuses:
Draft, Pending Approval, Approved, Scheduled, Active, Expired, Archived, Rejected.

Support permissions:
fees.view, fees.create, fees.update_draft, fees.submit_for_approval, fees.approve, fees.reject, fees.publish, fees.archive, fees.view_history, fees.export_history, settlement_rules.view, settlement_rules.create, settlement_rules.approve, settlement_rules.publish, assessment_payment.initiate, assessment_payment.verify, facility_fee_schedule.view.

Rules:
- Only authorized State users can create or update fees.
- Only one active fee schedule per state/category/scope.
- Active fees cannot be edited directly; create a new version instead.
- Payment must use the active fee at time of payment.
- Payment records must store fee schedule ID and version ID.
- Historical payment records must not change when fee changes.
- Settlement rules must be effective-dated and audit logged.
- Facility users can only view the active fee schedule for their mapped state.
- Federal users can view state fee schedules nationally but cannot edit by default.

Use Next.js + React + TypeScript + Tailwind CSS and follow the FoodCert NG application-wide design system. Backend permissions and scoping remain the source of truth.
```

---

# 24. MVP Build Order

1. Fee settings navigation and UI consolidation
2. Fee schedule data models
3. Fee settings APIs
4. Assessment Fees UI
5. Settlement Rules
6. Payment workflow integration
7. Medical facility read-only fee schedule
8. Revenue / Payments integration
9. Federal oversight reports
10. Permissions, audit, and tests
11. Final UI QA
