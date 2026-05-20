# 14_UI_UX_USER_FLOWS_STAKEHOLDER_ADDENDUM.md

## Purpose

This addendum updates `14_UI_UX_USER_FLOWS.md` to include stakeholder management, organization units, employer branches, medical facility departments, State Ministry internal units, unit-scoped invitations, and unit-aware dashboards.

Use this together with:

- `14_UI_UX_USER_FLOWS.md`
- `15_STAKEHOLDER_MANAGEMENT_INTEGRATION.md`

---

# 1. New Global UI/UX Principle: Organization-Aware Navigation

The frontend must not assume that a user only belongs to a flat organization. A user may belong to:

- An organization only
- An organization and a specific unit
- An organization and a branch
- An organization and a department
- An organization and an LGA office

The UI should show the user’s active scope in the top bar or profile area.

Example:

```txt
MegaChow Ltd / Branch — Ikeja
Lagos State MOH / Certificate Verification Desk
Excel Diagnostics Ltd / Laboratory Department
```

Where the user has wider access, allow scope filtering.

Where the user is `unit_restricted`, lock the scope filter to their assigned unit.

---

# 2. New Shared Component: Organization Scope Switcher

## Component Name

`OrganizationScopeSwitcher`

## Used By

- Employer head office users
- State Ministry users
- Medical facility admins
- Federal Ministry users
- Super Admins

## Function

Allows authorized users to filter dashboards and records by:

- Organization
- Unit
- Branch
- Department
- LGA office
- State
- LGA

## UX Rules

- If user has no unit restriction, allow switching between units they are allowed to access.
- If user is `unit_restricted`, show the assigned unit but disable switching.
- If user has federal access, allow state drill-down.
- If user has employer head office access, allow branch filtering.
- If user has facility admin access, allow department filtering.

---

# 3. New Shared Screen: Organization Unit Management

## Route Examples

```txt
/app/admin/organizations/:id/units
/app/state/units
/app/employer/branches
/app/facility/departments
```

## Page Layout

### Header

- Page title
- Organization name
- Create Unit / Create Branch / Create Department button

### Left Panel

Tree view of units.

Example:

```txt
Food Safety Directorate
  ├── Certificate Verification Desk
  ├── Facility Accreditation Unit
  └── Inspectorate
      ├── Ikeja LGA Office
      └── Surulere LGA Office
```

### Main Panel

Selected unit detail:

- Unit name
- Unit type
- Parent unit
- Address
- State
- LGA
- Phone
- Email
- Description
- Status
- Members
- Linked records

### Actions

- Edit Unit
- Add Child Unit
- Assign User
- Deactivate Unit
- View Members
- View Linked Records

## Empty State

```txt
No units created yet. Create your first unit to organize users, branches, departments, or offices.
```

---

# 4. New Shared Flow: Invite User to Organization/Unit

## Trigger Points

Invite modal should be available from:

- Organization users page
- Employer branch detail page
- Facility department detail page
- State Ministry unit detail page
- Super Admin organization detail page

## Invite Modal Fields

- Email
- Phone, optional
- Role
- Unit, optional
- Message, optional
- Expiry date, default 7 days

## Invite Modal Actions

- Send Invite
- Cancel

## Invite Statuses

- Pending
- Accepted
- Expired
- Revoked

## Invite List Columns

- Recipient
- Role
- Unit
- Invited by
- Status
- Expires at
- Actions

## Invite Row Actions

- Resend
- Revoke
- Copy Invite Link

## Acceptance Flow

1. User clicks invite link.
2. If not logged in, user registers or logs in.
3. System shows invitation summary:
   - Organization
   - Unit
   - Role
   - Invited by
4. User accepts.
5. User is assigned to organization, role, and unit.
6. User is redirected to the correct dashboard.

---

# 5. Employer UI/UX Update: Branch Management

## New Route

```txt
/app/employer/branches
```

## Employer Navigation Update

Add:

- Branches

Updated Employer navigation:

- Dashboard
- Business Profile
- Branches
- Food Handlers
- Certificates
- Vaccination Compliance
- Illness Reports
- Compliance Reports
- Inspections
- Subscription and Billing
- Notifications
- Settings

## Branch List Page

### Header Actions

- Create Branch
- Import Branches

### Table Columns

- Branch name
- State
- LGA
- Address
- Branch manager
- Food handlers
- Compliance %
- Certificate issues
- Status
- Actions

### Filters

- State
- LGA
- Compliance status
- Branch status

### Row Actions

- View Branch
- Edit
- Assign Manager
- View Food Handlers
- View Compliance Report
- Deactivate

## Create/Edit Branch Form

Fields:

- Branch name
- Address
- State
- LGA
- Phone
- Email
- Parent unit, optional
- Branch manager, optional
- Status

## Branch Detail Page

Tabs:

1. Overview
2. Food Handlers
3. Certificates
4. Illness Reports
5. Inspections
6. Compliance Reports
7. Branch Users

## Branch Manager Experience

If branch manager has:

```txt
role = Employer
unit = Branch — Ikeja
unit_restricted = true
```

Then:

- Dashboard automatically filters to Branch — Ikeja.
- Branch filter is visible but locked.
- They cannot view other branches.
- They can invite food handlers only to Branch — Ikeja.
- They can report illness only for Branch — Ikeja workers.
- They can generate only Branch — Ikeja compliance reports.

## Food Handler Assignment UI

When employer adds a food handler, add field:

- Business branch

If the current user is a restricted branch manager:

- Pre-fill business branch with their branch.
- Disable branch selection.

---

# 6. Medical Facility UI/UX Update: Department Management

## New Route

```txt
/app/facility/departments
```

## Facility Navigation Update

Add:

- Departments

Updated Facility navigation:

- Dashboard
- Facility Profile
- Accreditation
- Departments
- Appointments
- Assessments
- Doctors
- Lab Staff
- Lab Requests
- Certificates
- Settlements
- Reports
- Settings

## Department List Page

Columns:

- Department name
- Department type
- Members
- Pending tasks
- Completed tasks
- Status
- Actions

Department types:

- Clinical Assessment Department
- Laboratory Department
- Medical Records Department
- Finance/Settlement Unit
- Other

## Department Detail Page

Tabs:

1. Overview
2. Members
3. Workload
4. Reports

## Department-Specific UX

### Clinical Department

Show:

- Assigned doctors
- Pending declaration reviews
- Pending physical exams
- Fitness decisions pending

### Laboratory Department

Show:

- Lab staff
- New lab requests
- Samples collected
- Results pending upload
- Repeat tests required

### Medical Records Department

Show:

- Completed assessments
- Certificates issued
- Certificate corrections/replacement requests
- Records requiring review

### Finance/Settlement Unit

Show:

- Pending settlements
- Settled payments
- Failed settlements
- Facility revenue reports

---

# 7. State Ministry UI/UX Update: Internal Unit Management

## New Route

```txt
/app/state/units
```

## State Ministry Navigation Update

Add:

- Units and Offices

Updated State Ministry navigation:

- State Dashboard
- Units and Offices
- Facilities
- Accreditation Applications
- Assessment Fees
- Certificate Validation Queue
- Certificate Registry
- Employers
- Food Handlers
- Inspectors
- Inspections
- Reports
- State Settings

## State Unit Tree Examples

```txt
Food Safety Directorate
  ├── Certificate Verification Desk
  ├── Facility Accreditation Unit
  ├── Policy and Finance Unit
  └── Inspectorate
      ├── Ikeja LGA Office
      └── Surulere LGA Office
```

## Unit Detail Page

Tabs:

1. Overview
2. Officers
3. Assigned Queues
4. Reports
5. Audit

## Queue Routing UX

State Admin should be able to route workflows:

| Workflow | Suggested Unit |
|---|---|
| Certificate validation | Certificate Verification Desk |
| Facility accreditation | Facility Accreditation Unit |
| Fee configuration | Policy and Finance Unit |
| Inspection assignment | Inspectorate |
| LGA inspections | LGA Office |

## Verification Desk User Experience

Dashboard should show:

- Certificate validation queue
- Pending clarifications
- Approved today
- Rejected today
- Average validation time

Navigation should focus on:

- Certificate Validation Queue
- Certificate Registry
- Reports

Do not show facility accreditation or fee configuration unless permitted.

## Accreditation Unit User Experience

Dashboard should show:

- Facility applications pending review
- Facilities approved
- Facilities rejected
- Re-accreditation due
- Suspended facilities

Navigation should focus on:

- Accreditation Applications
- Facilities
- Reports

## Policy and Finance Unit User Experience

Dashboard should show:

- Assessment fee configuration
- Revenue summaries
- Settlement summaries
- Payment reconciliation

Navigation should focus on:

- Assessment Fees
- Revenue Reports
- Settlement Reports

## Inspectorate User Experience

Dashboard should show:

- Inspections assigned
- Inspections submitted
- Notices issued
- Follow-ups due
- Inspector performance

Navigation should focus on:

- Inspectors
- Inspections
- Notices
- Reports

---

# 8. Inspector UI/UX Update: LGA Office and Branch-Specific Inspections

## Inspector Scope Display

Inspector dashboard should show:

```txt
Assigned Office: Ikeja LGA Office
Coverage: Ikeja LGA
```

## Inspection Target Selection

When starting an inspection, inspector selects:

1. Employer/business
2. Branch, optional
3. Inspection type
4. Inspection checklist

If branch is selected:

- Show branch-specific food handlers.
- Show branch certificates.
- Show branch compliance history.
- Inspection report is linked to that branch.

## Branch-Specific Inspection Result

The inspection result should show:

- Employer name
- Branch name
- Branch address
- Branch manager
- Food handlers inspected
- Certificates verified
- Compliance score
- Findings
- Enforcement action

---

# 9. Federal Ministry UI/UX Update: Drill-Down Reporting

## National Dashboard Drill-Down

Federal dashboard should support this hierarchy:

```txt
National → State → LGA → Facility/Employer → Branch/Department
```

## State Comparison Table

Add columns:

- Number of active units/offices
- Facilities by department readiness, where available
- Employer branches registered
- Branch-level compliance coverage
- LGA inspection coverage

## Drill-Down Rules

- Federal users should view aggregate data nationally.
- Individual records should only be visible where authorized.
- Medical details remain restricted.

---

# 10. Super Admin UI/UX Update: Organization Structure Management

## Organization Detail Page

Add tab:

- Units

Tabs:

1. Overview
2. Users
3. Units
4. Invites
5. Settings
6. Audit Logs

## Super Admin Unit Controls

Super Admin can:

- Create unit
- Edit unit
- Deactivate unit
- Assign users
- Move users between units
- View all unit-scoped records
- Override unit restrictions where necessary

---

# 11. Updated Route List

Add these routes:

```txt
/app/admin/organizations/[id]/units
/app/admin/organizations/[id]/invites

/app/state/units
/app/state/units/[id]
/app/state/invites

/app/employer/branches
/app/employer/branches/[id]
/app/employer/invites

/app/facility/departments
/app/facility/departments/[id]
/app/facility/invites
```

---

# 12. Updated Component Checklist

Add these components:

- OrganizationUnitTree
- OrganizationUnitForm
- OrganizationUnitDetail
- UnitScopeBadge
- OrganizationScopeSwitcher
- InviteUserModal
- InviteStatusBadge
- BranchSelector
- BranchComplianceCard
- DepartmentWorkloadCard
- UnitMemberTable
- UnitScopedDashboardFilter
- QueueRoutingPanel

---

# 13. Updated Definition of Done

The UI/UX implementation now requires:

- Users can see their active organization and unit scope.
- Organization admins can create and manage units.
- Employers can create and manage branches.
- Facility admins can create and manage departments.
- State admins can create and manage directorates, units, and LGA offices.
- Invites can include role and unit.
- Branch managers are restricted to branch views where `unit_restricted = true`.
- Dashboards default to the user’s unit scope.
- Inspections can target a specific branch.
- Public verification remains unchanged and does not expose medical data.
