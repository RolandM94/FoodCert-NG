# PRD: Employers Module — FoodCert NG

## 1. Module Name

**Employers / Food Business Owner Management Module**

## 2. Product Context

The Employers Module is a core component of **FoodCert NG**, the national food handler medical fitness certification platform. It enables food business owners and employers to register their businesses, manage branches, onboard food handlers, monitor certification and vaccination compliance, report illnesses, respond to inspections, maintain required records, and pay employer subscription fees.

The module must support the reality that employers may range from a single street food vendor to a large multi-branch food business operating across multiple states. The stakeholder management supplement requires organizations to support branches and sub-units using `OrganizationUnit`.

The module must also align with the National Guidelines for Food Handlers’ Medical Test 2024, which places obligations on food business owners to maintain food handler health standards, keep vaccination documentation, prevent sick handlers from handling food, and preserve confidentiality of health information.

---

# 3. Product Goal

To provide employers with a complete digital workspace for ensuring that every food handler under their business is medically certified, vaccination-compliant, fit to handle food, properly assigned to a branch/location, and inspection-ready.

---

# 4. Core Objectives

The Employers Module must allow employers to:

1. Register and manage food business profiles.
2. Create and manage business branches.
3. Invite and onboard food handlers.
4. Assign food handlers to branches.
5. Track staff certification status.
6. Track vaccination compliance.
7. Report illness or suspected illness.
8. Ensure temporarily unfit handlers are excluded from food handling.
9. Download compliance reports.
10. Respond to inspection findings.
11. Pay subscription fees.
12. Manage employer users and branch managers.
13. Restrict branch managers to only their own branch where required.
14. Maintain privacy by showing only operational fitness categories, not detailed medical records.

---

# 5. Employer User Types

## 5.1 Employer Owner / Head Office Admin

This is the main business account owner or head office administrator.

Can:

- Register the business.
- Manage business profile.
- Create and manage branches.
- Add food handlers.
- Invite branch managers.
- View all branches.
- View all food handlers.
- View all compliance reports.
- Manage subscription and billing.
- Respond to inspections.
- Generate employer-wide compliance reports.

## 5.2 Employer Compliance Officer

Usually responsible for internal regulatory compliance.

Can:

- View certification status.
- View vaccination status.
- Generate compliance reports.
- Track expiring certificates.
- Report illness.
- Respond to inspection findings.
- View branch-level compliance.

May not:

- Manage billing unless permission is granted.
- Change business ownership details unless permission is granted.

## 5.3 Branch Manager

A branch-scoped employer user.

Can:

- View only food handlers assigned to their branch.
- Invite food handlers to their branch.
- Track certificates for branch staff.
- Report illness for branch staff.
- Generate branch compliance reports.
- Respond to branch-specific inspections.

Cannot:

- View other branches if `unit_restricted = true`.
- Manage employer-wide subscription.
- View detailed medical records.

## 5.4 Employer Finance User

Optional role or permission set.

Can:

- View subscription invoices.
- Pay subscription fees.
- Download receipts.
- View billing history.

Cannot:

- View medical data.
- Edit food handler medical status.

---

# 6. Employer Module Scope

## 6.1 In Scope

The module must include:

- Employer registration
- Business profile management
- Branch management
- Employer user invitations
- Branch manager assignment
- Food handler invitation
- Food handler branch assignment
- Food handler compliance table
- Certificate status monitoring
- Vaccination status monitoring
- Illness reporting
- Return-to-work visibility
- Subscription and billing
- Compliance report generation
- Inspection history
- Inspection response
- Dashboard analytics
- Notifications and reminders

## 6.2 Out of Scope for MVP

For the MVP, the following may be deferred:

- Payroll integration
- HR system integration
- Biometric attendance integration
- Advanced enterprise API access
- Offline branch compliance mode
- AI compliance recommendations
- Automated sanctions/payment of fines
- Multi-country support

---

# 7. Employer Registration Workflow

## 7.1 Workflow Summary

```txt
User creates employer account
→ Creates business profile
→ Selects establishment category
→ Chooses subscription plan
→ Pays subscription fee
→ Creates branches, if applicable
→ Invites food handlers and branch managers
→ Starts compliance monitoring
```

## 7.2 Employer Account Creation

### Required Fields

- First name
- Last name
- Email
- Phone number
- Password
- Confirm password

### Validation Rules

- Email must be unique.
- Phone number must be unique or verified.
- Password must meet security rules.
- OTP verification should be supported.

## 7.3 Business Profile Creation

### Required Fields

- Business name
- Business registration number, optional for informal/small businesses
- Establishment category
- Business type
- Contact person
- Phone number
- Email
- Head office address
- State
- LGA
- Ward, optional
- Number of food handlers, estimated
- Number of branches, estimated

### Establishment Categories

The system should support:

- Restaurants and cafes
- Bakeries and pastry shops
- Abattoirs, slaughter slabs, and butcher shops
- Grocery stores and supermarkets
- Food trucks and street vendors
- Catering services
- School cafeterias
- Hospital kitchens
- Bars and pubs
- Food processing plants
- Hotels and resorts
- Corporate dining facilities
- Food markets and stalls
- Airport and train station food outlets
- Farms and livestock feed processing plants
- Daycare centres
- Airline catering vendors
- Train catering vendors
- Cruise/sea vessel catering vendors
- Emergency food service operators
- Other

## 7.4 Business Verification

For MVP, business verification may be simple:

- Business profile submitted
- Employer email/phone verified
- Employer status becomes `active`

Later, support:

- CAC verification
- State food business permit verification
- Local government permit upload
- Manual review by State Ministry

---

# 8. Branch Management

## 8.1 Purpose

Employers may operate several physical locations. The platform must allow businesses to create branches and assign food handlers to specific branches.

This should use the `OrganizationUnit` model with `unit_type = branch`.

## 8.2 Branch Creation

### Required Fields

- Branch name
- Branch address
- State
- LGA
- Phone number
- Email, optional
- Branch manager, optional
- Status

### Optional Fields

- Ward
- GPS coordinates
- Operating hours
- Food handler capacity
- Inspection contact person
- Parent region/office

## 8.3 Branch Statuses

- Active
- Inactive
- Suspended
- Closed

## 8.4 Branch List Page

### Columns

- Branch name
- State
- LGA
- Address
- Branch manager
- Number of food handlers
- Compliance percentage
- Certificate issues
- Inspection status
- Status
- Actions

### Actions

- View branch
- Edit branch
- Assign manager
- Add food handler
- View compliance report
- View inspections
- Deactivate branch

## 8.5 Branch Detail Page

Tabs:

1. Overview
2. Food Handlers
3. Certificates
4. Vaccinations
5. Illness Reports
6. Inspections
7. Branch Users
8. Compliance Reports

## 8.6 Branch Scope Rules

### Head Office User

Can:

- View all branches.
- Filter dashboard by branch.
- Move food handlers between branches.
- Invite branch managers.
- Generate employer-wide and branch-specific reports.

### Branch Manager

If `unit_restricted = true`, can only:

- View their assigned branch.
- View food handlers in their branch.
- Invite food handlers to their branch.
- Generate branch-only compliance reports.
- Report illness for branch food handlers.
- Respond to branch inspections.

Cannot:

- View other branches.
- View employer-wide reports.
- Manage employer subscription.
- Access detailed medical records.

---

# 9. Employer User Management

## 9.1 Invite Employer User

Employer admins should be able to invite internal users.

### Invite Fields

- Email
- Phone, optional
- Role
- Unit/branch, optional
- Message, optional
- Expiry date, default 7 days

## 9.2 Employer User Types

Supported employer-side access levels:

- Owner/Admin
- Compliance Officer
- Branch Manager
- Finance User
- Viewer

## 9.3 Invite Statuses

- Pending
- Accepted
- Expired
- Revoked

## 9.4 Invite Acceptance Workflow

```txt
Employer sends invite
→ Recipient clicks link
→ Recipient registers or logs in
→ System displays invite details
→ Recipient accepts
→ User is attached to employer organization, role, and unit/branch
→ User lands on employer dashboard
```

## 9.5 Access Rules

- Only owner/admin can invite head office users.
- Head office admin can invite branch managers.
- Branch manager can invite food handlers only to their own branch if permitted.
- Expired invites cannot be accepted.
- Revoked invites cannot be accepted.
- Invite acceptance must create audit log.

---

# 10. Food Handler Onboarding by Employer

## 10.1 Onboarding Options

Employers should be able to onboard food handlers through:

1. Manual add
2. Invite by phone/email
3. Bulk upload CSV/Excel
4. Share branch registration link
5. Link existing certified food handler

## 10.2 Manual Add Fields

- Full name
- Phone number
- Email, optional
- Food handler category
- Branch
- Job title, optional
- Staff ID, optional

## 10.3 Invite Food Handler

Employer sends invite to food handler.

Invite should include:

- Employer name
- Branch, if applicable
- Food handler category, if pre-selected
- Registration link
- Message

When accepted:

- Food handler account is created or linked.
- Food handler is attached to employer.
- Food handler is assigned to branch if invite included branch.

## 10.4 Bulk Upload

### Accepted File Types

- CSV
- Excel

### Required Columns

- Full name
- Phone number
- Email, optional
- Food handler category
- Branch name
- Staff ID, optional

### Bulk Upload Behaviour

- Validate file before import.
- Show import preview.
- Flag missing required fields.
- Flag invalid branches.
- Flag duplicate phone numbers.
- Allow user to fix errors before final import.
- Send invites after successful import.

## 10.5 Link Existing Food Handler

Some food handlers may already have certificates.

Employer should be able to:

- Search by phone number, certificate number, or food handler ID.
- Request link to the food handler.
- Food handler approves employer link request.
- Employer can then see operational fitness status.

---

# 11. Employer Food Handler Management

## 11.1 Food Handler List

### Columns

- Name
- Passport photo
- Staff ID
- Branch
- Food handler category
- Fitness status
- Certificate status
- Certificate expiry date
- Vaccination status
- Last assessment date
- Return-to-work status
- Actions

## 11.2 Filters

- Branch
- Food handler category
- Fitness status
- Certificate status
- Vaccination status
- Expiry window
- Illness status

## 11.3 Actions

- View operational status
- View certificate
- Download certificate
- Send renewal reminder
- Report illness
- Reassign branch
- Remove from employer
- View compliance history

## 11.4 Employer Visibility Rules

Employers can see:

- Name
- Passport photo
- Branch
- Food handler category
- Certificate status
- Fitness category
- Expiry date
- Vaccination compliance status
- Return-to-work status
- Certificate PDF
- Public certificate details

Employers cannot see:

- Lab results
- Doctor notes
- Diagnosis
- Detailed declaration answers
- Full NIN
- Sensitive medical history

---

# 12. Fitness Status Categories

Employers should see only operational fitness categories.

## 12.1 Employer-Visible Statuses

- Fit to Handle Food
- Certification Pending
- Certificate Expired
- Certificate Expiring Soon
- Temporarily Not Fit
- Excluded from Food Handling
- Return-to-Work Clearance Pending
- Cleared to Return to Work
- Vaccination Due
- Medical Review Required
- Not Linked
- Invite Pending

## 12.2 Status Logic

| Status | Meaning | Employer Action |
|---|---|---|
| Fit to Handle Food | Certificate active and valid | No action |
| Certification Pending | Assessment in progress | Monitor |
| Certificate Expired | Certificate no longer valid | Send renewal reminder |
| Temporarily Not Fit | Doctor has temporarily restricted handler | Do not assign to food handling |
| Excluded from Food Handling | Illness or medical risk reported | Remove from food handling duties |
| Return-to-Work Clearance Pending | Awaiting medical clearance | Do not assign yet |
| Cleared to Return to Work | Doctor has cleared handler | May resume duties |
| Vaccination Due | Vaccine due or incomplete | Send reminder |
| Medical Review Required | Doctor/facility review required | Monitor |
| Invite Pending | Worker has not accepted invite | Resend invite |

---

# 13. Certificate Monitoring

## 13.1 Certificate Dashboard

Employers need a certificate compliance view.

### Metrics

- Total food handlers
- Active certificates
- Expired certificates
- Expiring in 30 days
- Expiring in 7 days
- Certification pending
- Revoked certificates
- Suspended certificates
- No certificate

## 13.2 Certificate List

### Columns

- Food handler
- Branch
- Certificate number
- Issuing State Ministry
- Facility
- Issue date
- Expiry date
- Certificate status
- Actions

## 13.3 Actions

- View certificate
- Download certificate
- Verify certificate
- Send renewal reminder
- Export certificate list

## 13.4 Renewal Reminder

Employers should be able to send reminders to food handlers whose certificates are:

- Expiring in 30 days
- Expiring in 7 days
- Already expired

The system should also send automatic notifications.

---

# 14. Vaccination Compliance

## 14.1 Purpose

Employers are required to maintain up-to-date vaccination evidence for food handlers.

## 14.2 Vaccination Dashboard

Metrics:

- Typhoid valid
- Typhoid expired
- Typhoid due soon
- Hepatitis A dose 1 completed
- Hepatitis A dose 2 pending
- Hepatitis A complete
- Vaccination record missing
- Other vaccine due

## 14.3 Vaccination Table

Columns:

- Food handler
- Branch
- Typhoid status
- Typhoid expiry date
- Hepatitis A dose 1
- Hepatitis A dose 2
- Next due date
- Actions

## 14.4 Employer Actions

- Send vaccination reminder
- View vaccination compliance status
- Export vaccination report

Employers should not see sensitive clinical notes attached to vaccination review.

---

# 15. Illness Reporting

## 15.1 Purpose

Employers must be able to report illness or suspected illness among food handlers and ensure affected staff are excluded from food handling duties.

## 15.2 Report Illness Form

Fields:

- Food handler
- Branch
- Symptoms observed/reported
- Symptom start date
- Date reported
- Notes
- Immediate exclusion confirmed: Yes/No

Symptoms:

- Jaundice
- Diarrhoea
- Vomiting
- Fever
- Sore throat with fever
- Infected skin lesions
- Discharge from ear, eye, or nose
- Cough or flu
- Other

## 15.3 Illness Report Workflow

```txt
Employer reports illness
→ Food handler marked Medical Review Required or Excluded
→ Employer instructed not to assign food handling duties
→ Food handler notified
→ Doctor/facility review starts
→ Return-to-work workflow triggered if needed
→ Employer sees return-to-work status
```

## 15.4 Illness Report Statuses

- Submitted
- Under Medical Review
- Excluded from Food Handling
- Clearance Pending
- Cleared to Return to Work
- Closed

## 15.5 Employer View

Employers should see:

- Food handler name
- Branch
- Operational exclusion status
- Date reported
- Return-to-work status
- Clearance date, if cleared

Employers should not see:

- Diagnosis
- Detailed lab results
- Doctor notes

---

# 16. Return-to-Work Visibility

## 16.1 Employer View

Employers should see whether a food handler is:

- Excluded
- Awaiting review
- Awaiting test result
- Awaiting clearance
- Cleared to return
- Not cleared

## 16.2 Employer Actions

- View return-to-work status
- Receive clearance notification
- Download return-to-work clearance, where permitted
- Keep worker excluded until cleared

## 16.3 Important Rule

The employer must not manually override a medical exclusion. Only authorized medical or regulatory users can clear the food handler.

---

# 17. Employer Subscription and Billing

## 17.1 Purpose

Employers pay subscription fees for access to the employer compliance tools.

## 17.2 Subscription Plans

Suggested plans:

### Basic

For small businesses.

Includes:

- One business profile
- Limited food handlers
- Basic certificate tracking
- Basic compliance dashboard
- Renewal alerts

### Standard

For growing/mid-sized businesses.

Includes:

- Multiple branches
- More food handlers
- Bulk upload
- Vaccination compliance
- Illness reporting
- Compliance reports
- Inspection history

### Enterprise

For large food businesses.

Includes:

- High-volume food handlers
- Multi-state branch management
- Advanced analytics
- API access, future
- Custom reports
- Dedicated support

## 17.3 Subscription Fields

- Plan
- Billing cycle: monthly/yearly
- Start date
- Expiry date
- Status
- Last payment date
- Next billing date

## 17.4 Subscription Statuses

- Trial
- Active
- Past Due
- Suspended
- Cancelled
- Expired

## 17.5 Subscription Access Rules

If subscription is active:

- Full access to plan features.

If subscription expires:

- Employer can still view basic compliance status.
- Employer continues receiving regulatory notices.
- Employer cannot add new food handlers beyond allowed free access.
- Employer cannot generate premium reports.
- Employer cannot access advanced analytics.
- Regulatory users can still see employer compliance.

## 17.6 Billing Pages

Employer billing section should include:

- Current plan
- Usage
- Upgrade/downgrade
- Invoices
- Payment history
- Receipts
- Payment method
- Renewal date

---

# 18. Inspection Management

## 18.1 Employer Inspection History

Employers should be able to view inspections conducted on their business or branch.

### Table Columns

- Inspection date
- Inspector
- Branch
- Compliance score
- Findings summary
- Enforcement action
- Status
- Follow-up due date
- Actions

## 18.2 Inspection Detail

Show:

- Inspection metadata
- Branch inspected
- Checklist responses
- Findings
- Evidence files, where visible
- Enforcement notice
- Required corrective actions
- Deadline
- Response history

## 18.3 Employer Response to Inspection

Employer can:

- Acknowledge notice
- Submit corrective action
- Upload evidence
- Add comments
- Request review
- Mark action completed

## 18.4 Inspection Statuses

- Draft
- Submitted
- Notice Issued
- Employer Response Pending
- Corrective Action Submitted
- Under Review
- Closed
- Escalated

---

# 19. Compliance Reports

## 19.1 Report Types

Employers should generate:

- Employer-wide compliance report
- Branch compliance report
- Certificate expiry report
- Vaccination compliance report
- Illness/exclusion report
- Return-to-work report
- Inspection readiness report
- Food handler roster report

## 19.2 Report Filters

- Date range
- Branch
- State
- LGA
- Food handler category
- Certificate status
- Fitness status
- Vaccination status
- Inspection status

## 19.3 Export Formats

- PDF
- Excel
- CSV

## 19.4 Report Privacy

Reports must not include:

- Lab results
- Diagnosis
- Doctor notes
- Full NIN
- Declaration answers

---

# 20. Employer Dashboard

## 20.1 Dashboard Cards

Show:

- Total food handlers
- Fit to handle food
- Certification pending
- Certificates expired
- Certificates expiring soon
- Temporarily not fit
- Excluded from food handling
- Vaccination due
- Active branches
- Open inspection notices
- Subscription status
- Overall compliance percentage

## 20.2 Dashboard Charts

Suggested charts:

- Compliance by branch
- Certificate status distribution
- Expiring certificates over time
- Vaccination compliance by branch
- Illness reports trend
- Inspection outcomes

## 20.3 Dashboard Filters

- Branch
- State
- LGA
- Food handler category
- Certificate status
- Date range

If user is branch-restricted:

- Pre-filter dashboard to assigned branch.
- Disable branch switching.

---

# 21. Notifications

## 21.1 Employer Notifications

Notify employer when:

- Food handler accepts invite
- Food handler certificate is issued
- Food handler certificate is expiring
- Food handler certificate expires
- Food handler becomes temporarily not fit
- Food handler is excluded from handling food
- Food handler is cleared to return to work
- Vaccination is due
- Inspection notice is issued
- Corrective action deadline is approaching
- Subscription is expiring
- Subscription payment fails
- Branch manager accepts invite

## 21.2 Notification Channels

- In-app
- Email
- SMS
- WhatsApp, optional future

---

# 22. Data Model Requirements

## 22.1 Employer

```python
class Employer(models.Model):
    id = models.UUIDField(primary_key=True)
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    business_registration_number = models.CharField(max_length=100, blank=True)
    establishment_category = models.CharField(max_length=100)
    business_type = models.CharField(max_length=100, blank=True)
    contact_person_name = models.CharField(max_length=255)
    contact_person_phone = models.CharField(max_length=50)
    contact_person_email = models.EmailField(blank=True)
    address = models.TextField()
    state = models.ForeignKey("geography.State", on_delete=models.SET_NULL, null=True)
    lga = models.ForeignKey("geography.LGA", on_delete=models.SET_NULL, null=True)
    ward = models.CharField(max_length=100, blank=True)
    compliance_status = models.CharField(max_length=50)
    subscription_status = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 22.2 Employer Branch

Use `OrganizationUnit`.

```python
OrganizationUnit {
    organization = employer.organization
    unit_type = "branch"
}
```

## 22.3 Food Handler Branch Link

```python
class FoodHandlerProfile(models.Model):
    employer = models.ForeignKey("employers.Employer", null=True, blank=True)
    business_branch = models.ForeignKey("organizations.OrganizationUnit", null=True, blank=True)
```

## 22.4 Employer Subscription

```python
class EmployerSubscription(models.Model):
    id = models.UUIDField(primary_key=True)
    employer = models.ForeignKey("employers.Employer", on_delete=models.CASCADE)
    plan = models.ForeignKey("subscriptions.EmployerSubscriptionPlan", on_delete=models.PROTECT)
    billing_cycle = models.CharField(max_length=20)
    status = models.CharField(max_length=50)
    starts_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    cancelled_at = models.DateTimeField(null=True, blank=True)
    last_payment_transaction = models.ForeignKey("payments.PaymentTransaction", null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 22.5 Employer Illness Report

```python
class IllnessReport(models.Model):
    id = models.UUIDField(primary_key=True)
    food_handler = models.ForeignKey("food_handlers.FoodHandlerProfile", on_delete=models.CASCADE)
    employer = models.ForeignKey("employers.Employer", on_delete=models.CASCADE)
    branch = models.ForeignKey("organizations.OrganizationUnit", null=True, blank=True, on_delete=models.SET_NULL)
    reported_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    symptoms = models.JSONField(default=dict)
    symptom_start_date = models.DateField(null=True, blank=True)
    reported_at = models.DateTimeField(auto_now_add=True)
    exclusion_confirmed = models.BooleanField(default=False)
    status = models.CharField(max_length=50)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

---

# 23. API Requirements

## 23.1 Employer Profile

```txt
POST   /api/employers
GET    /api/employers/me
PATCH  /api/employers/:id
GET    /api/employers/:id
```

## 23.2 Branches

```txt
GET    /api/employers/:id/branches
POST   /api/employers/:id/branches
GET    /api/employers/:id/branches/:branch_id
PATCH  /api/employers/:id/branches/:branch_id
DELETE /api/employers/:id/branches/:branch_id
```

## 23.3 Employer Users and Invites

```txt
GET    /api/employers/:id/users
POST   /api/employers/:id/invites
GET    /api/employers/:id/invites
DELETE /api/employers/:id/invites/:invite_id
POST   /api/invites/:token/accept
```

## 23.4 Food Handlers

```txt
GET    /api/employers/:id/food-handlers
POST   /api/employers/:id/food-handlers/invite
POST   /api/employers/:id/food-handlers/bulk-upload
PATCH  /api/employers/:id/food-handlers/:food_handler_id/branch
DELETE /api/employers/:id/food-handlers/:food_handler_id
```

## 23.5 Compliance

```txt
GET /api/employers/:id/dashboard
GET /api/employers/:id/compliance-summary
GET /api/employers/:id/certificates
GET /api/employers/:id/vaccinations
GET /api/employers/:id/reports/compliance
GET /api/employers/:id/reports/certificates
GET /api/employers/:id/reports/vaccinations
```

## 23.6 Illness Reports

```txt
POST /api/employers/:id/illness-reports
GET  /api/employers/:id/illness-reports
GET  /api/employers/:id/illness-reports/:report_id
```

## 23.7 Inspections

```txt
GET  /api/employers/:id/inspections
GET  /api/employers/:id/inspections/:inspection_id
POST /api/employers/:id/inspections/:inspection_id/responses
```

## 23.8 Billing

```txt
GET  /api/employers/:id/subscription
POST /api/employers/:id/subscription/checkout
PATCH /api/employers/:id/subscription/change-plan
GET  /api/employers/:id/invoices
GET  /api/employers/:id/payments
```

---

# 24. Frontend Pages

## 24.1 Employer Routes

```txt
/app/employer/dashboard
/app/employer/business-profile
/app/employer/branches
/app/employer/branches/[id]
/app/employer/food-handlers
/app/employer/food-handlers/import
/app/employer/certificates
/app/employer/vaccinations
/app/employer/illness-reports
/app/employer/compliance-reports
/app/employer/inspections
/app/employer/inspections/[id]
/app/employer/billing
/app/employer/users
/app/employer/invites
/app/employer/settings
```

## 24.2 Core Components

- EmployerDashboardCards
- BranchSelector
- BranchManagementTable
- BranchDetailTabs
- FoodHandlerComplianceTable
- FitnessStatusBadge
- CertificateStatusBadge
- VaccinationStatusBadge
- InviteFoodHandlerModal
- InviteEmployerUserModal
- BulkUploadFoodHandlers
- ComplianceReportBuilder
- IllnessReportForm
- InspectionResponseForm
- SubscriptionPlanCards
- BillingHistoryTable

---

# 25. Permissions and Access Control

## 25.1 Employer Admin

Can:

- Manage employer profile
- Manage branches
- Manage employer users
- Manage food handlers
- Manage billing
- View all compliance data
- Generate reports

## 25.2 Compliance Officer

Can:

- View all compliance data
- Manage food handlers
- Report illness
- Generate reports
- Respond to inspections

Cannot by default:

- Manage billing
- Delete branches
- Change business ownership details

## 25.3 Branch Manager

Can:

- View assigned branch only
- Invite food handlers to assigned branch
- Report illness for branch food handlers
- Generate branch compliance report
- Respond to branch inspections

Cannot:

- View other branches
- Manage employer subscription
- View detailed medical records

## 25.4 Finance User

Can:

- View billing
- Pay invoices
- Download receipts

Cannot:

- View food handler medical details
- Report illness
- Manage certificates

---

# 26. Audit Logs

Create audit logs for:

- Employer registration
- Business profile update
- Branch creation/update/deactivation
- User invite sent
- User invite accepted
- Food handler invited
- Food handler linked to employer
- Food handler branch reassigned
- Illness report submitted
- Compliance report generated
- Certificate downloaded
- Subscription payment made
- Subscription plan changed
- Inspection response submitted

---

# 27. Acceptance Criteria

## Employer Registration

- Employer can register a business.
- Employer can select establishment category.
- Employer can create business profile.
- Employer can access dashboard after completing required setup.

## Branch Management

- Employer can create branches.
- Employer can assign branch managers.
- Employer can assign food handlers to branches.
- Branch manager can be restricted to one branch.
- Head office can view all branches.

## Food Handler Management

- Employer can invite food handlers.
- Employer can bulk upload food handlers.
- Employer can link existing food handlers.
- Employer can view food handler operational fitness status.
- Employer cannot view sensitive medical details.

## Compliance Dashboard

- Dashboard shows total food handlers.
- Dashboard shows valid, expired, and pending certificates.
- Dashboard shows vaccination due status.
- Dashboard can be filtered by branch.
- Branch manager dashboard defaults to assigned branch.

## Illness Reporting

- Employer can report illness for a food handler.
- Food handler is marked for medical review or exclusion.
- Employer sees return-to-work status.
- Employer cannot override medical exclusion.

## Subscription

- Employer can select a plan.
- Employer can pay subscription fee.
- Employer can view invoices and receipts.
- Expired subscription restricts premium features but does not block regulatory notices.

## Inspection

- Employer can view inspection history.
- Employer can respond to inspection findings.
- Branch inspection is visible to the correct branch manager and head office.

## Privacy

- Employer cannot see lab results.
- Employer cannot see doctor notes.
- Employer cannot see diagnosis.
- Employer cannot see declaration answers.
- Employer cannot see full NIN.
- Public verification privacy remains unchanged.

---

# 28. Codex Implementation Instructions

Give Codex this instruction for the Employers Module:

```txt
Implement the Employers Module for FoodCert NG.

The module must support employer registration, business profile management, branch management using OrganizationUnit, employer user invites, branch manager scoping, food handler invitations, food handler bulk upload, food handler branch assignment, certificate compliance tracking, vaccination compliance tracking, illness reporting, inspection history, inspection response, employer subscription billing, and compliance reports.

Important rules:
- Employers must not see detailed medical records.
- Employers see only operational fitness status categories.
- Branch managers with unit_restricted=true must only see their assigned branch.
- Head office employer users can view all branches.
- Food handlers can be assigned to business_branch.
- Inspections can be branch-specific.
- Employer subscription status controls premium features but must not block regulatory visibility or critical notices.
- All sensitive actions must be audit logged.

Build backend models, serializers, permissions, services, endpoints, tests, and frontend pages for the module.
```

---

# 29. MVP Build Order for Employers Module

1. Employer model and profile API
2. Employer registration page
3. Employer dashboard shell
4. Branch management with `OrganizationUnit`
5. Employer user invite workflow
6. Food handler invite workflow
7. Food handler list and branch assignment
8. Certificate compliance table
9. Vaccination compliance table
10. Illness reporting
11. Subscription plan and billing
12. Compliance report export
13. Inspection history and response
14. Branch manager permission tests
15. Employer privacy tests
