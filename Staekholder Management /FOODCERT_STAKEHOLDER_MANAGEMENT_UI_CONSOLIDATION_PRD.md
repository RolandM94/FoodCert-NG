# PRD Update: Stakeholder Management Navigation & UI Consolidation — FoodCert NG

## 1. Purpose

This PRD is a focused update to the existing **Stakeholder Management Module**. It explains how FoodCert NG should consolidate related administrative functions that currently appear as separate navigation items — such as **Users**, **Invites**, **Units & Offices**, **Departments**, **Branches**, and **Roles** — into one clean parent module called **Stakeholder Management**.

The intended UI pattern is similar to the sample stakeholder management screen shared by the product owner, where one parent page contains organized tabs such as:

```txt
Stakeholders | Roles | Departments
```

For FoodCert NG, the same idea should apply across all organization workspaces:

- Federal Ministry of Health
- State Ministry of Health
- Medical Facilities
- Employers / Food Businesses
- Platform Admin / Super Admin

---

## 2. Problem Statement

The current navigation risks making related stakeholder administration functions look like separate modules.

Example fragmented navigation:

```txt
Dashboard
Units & Offices
Facilities
Forms
Accreditation
Users
Invites
```

This is confusing because **Users**, **Invites**, and **Units & Offices** are not independent business modules. They are all part of managing stakeholders inside an organization.

The correct structure should be:

```txt
Dashboard
Stakeholder Management
Facilities
Forms
Accreditation
Reports
Settings
```

Then inside **Stakeholder Management**, the user should see organized tabs:

```txt
Overview
Stakeholders
Roles & Permissions
Units / Offices / Departments / Branches
Invites
Audit Logs
```

---

## 3. Product Decision

FoodCert NG should implement **one Stakeholder Management parent module**.

This parent module should contain:

1. Organization account/profile overview
2. Stakeholders / users / staff / officers
3. Roles and permissions
4. Units / offices / departments / branches
5. Invites
6. Audit logs

The backend should use one shared stakeholder engine. The frontend should adapt labels based on the active organization type.

---

## 4. Product Goal

To create a clean, unified, reusable stakeholder management experience where each organization can manage its internal structure, users, roles, permissions, invitations, and access scope from one place.

---

## 5. Core Objectives

This update must:

1. Remove Users, Invites, Units & Offices, Branches, Departments, and Staff as scattered top-level module links.
2. Create one parent navigation item: **Stakeholder Management**.
3. Provide tabbed sub-navigation inside Stakeholder Management.
4. Reuse existing Stakeholder Management backend models and APIs.
5. Adapt labels based on organization type.
6. Preserve organization, unit, branch, department, state, and LGA scoping.
7. Preserve all role and permission enforcement.
8. Prevent duplicated user, invite, branch, department, and role implementations across modules.
9. Improve UI clarity for national rollout.
10. Make Codex implementation simpler by enforcing one stakeholder service layer.

---

## 6. Target Navigation

### 6.1 State Ministry Workspace

Replace scattered items such as:

```txt
Dashboard
Units & Offices
Facilities
Forms
Accreditation
Users
Invites
```

With:

```txt
Dashboard
Stakeholder Management
Facilities
Forms
Accreditation
Certificate Validation
Inspections
Reports
Settings
```

Inside Stakeholder Management:

```txt
Overview
Officers
Roles & Permissions
Units & Offices
Invites
Audit Logs
```

### 6.2 Employer Workspace

Use:

```txt
Dashboard
Stakeholder Management
Food Handlers
Certificates
Vaccination Compliance
Illness Reports
Inspections
Billing
Reports
Settings
```

Inside Stakeholder Management:

```txt
Overview
Team Members
Roles & Permissions
Branches / Outlets
Invites
Audit Logs
```

### 6.3 Medical Facility Workspace

Use:

```txt
Dashboard
Stakeholder Management
Accreditation
Appointments
Assessments
Lab Requests
Certificates
Settlements
Reports
Settings
```

Inside Stakeholder Management:

```txt
Overview
Staff
Roles & Permissions
Departments
Invites
Audit Logs
```

### 6.4 Federal Ministry Workspace

Use:

```txt
Dashboard
Stakeholder Management
States
National Registry
Policy
M&E
Reports
Data Quality
Settings
```

Inside Stakeholder Management:

```txt
Overview
Federal Users
Roles & Permissions
Departments / Directorates
Invites
Audit Logs
```

### 6.5 Platform Admin Workspace

Use:

```txt
Dashboard
Organizations
Stakeholder Management
Roles & Permissions
System Settings
Audit Logs
Reports
```

Inside Stakeholder Management:

```txt
Overview
Platform Users
Roles & Permissions
Teams / Units
Invites
Audit Logs
```

---

## 7. Organization-Specific Labels

The same underlying pages should use different user-facing labels depending on organization type.

| Organization Type | User Tab Label | Unit Tab Label | Primary Invite Button |
|---|---|---|---|
| Federal Ministry | Federal Users | Departments / Directorates | Invite Federal User |
| State Ministry | Officers | Units & Offices | Invite Officer |
| Medical Facility | Staff | Departments | Invite Staff |
| Employer | Team Members | Branches / Outlets | Invite Team Member |
| Platform Operator | Platform Users | Teams / Units | Invite Platform User |

The backend entities remain the same:

```txt
Organization
OrganizationUnit
OrganizationMembership
Role
Permission
UserInvite
AuditLog
```

---

## 8. Stakeholder Management Page Structure

### 8.1 Parent Route

Recommended shared route:

```txt
/app/stakeholder-management
```

Role-specific aliases can route to the same module:

```txt
/app/state/stakeholder-management
/app/employer/stakeholder-management
/app/facility/stakeholder-management
/app/federal/stakeholder-management
/app/admin/stakeholder-management
```

### 8.2 Header

The page header should show:

- Page title: Stakeholder Management
- Active organization name
- Organization type badge
- State/LGA badge, where applicable
- Primary action based on selected tab

Example:

```txt
Stakeholder Management
Lagos State Ministry of Health · State Ministry · Lagos
```

### 8.3 Tabs

Base tabs:

```txt
Overview | Stakeholders | Roles & Permissions | Units & Offices | Invites | Audit Logs
```

The labels must adapt by organization type.

State Ministry example:

```txt
Overview | Officers | Roles & Permissions | Units & Offices | Invites | Audit Logs
```

Employer example:

```txt
Overview | Team Members | Roles & Permissions | Branches / Outlets | Invites | Audit Logs
```

Medical Facility example:

```txt
Overview | Staff | Roles & Permissions | Departments | Invites | Audit Logs
```

---

## 9. Overview Tab

### 9.1 Purpose

The Overview tab gives a summary of the organization’s stakeholder structure.

### 9.2 Summary Cards

Show:

- Total users
- Active users
- Pending invites
- Suspended users
- Total units/offices/departments/branches
- Active units
- Roles in use
- Users without unit assignment
- Users with unit restriction
- Recent stakeholder changes

### 9.3 Sections

#### A. Organization Summary

- Organization name
- Organization type
- Status
- State/LGA
- Contact person
- Last updated

#### B. Stakeholder Summary

- Users by role
- Users by unit
- Pending invites
- Suspended users

#### C. Structure Summary

- Unit tree preview
- Branch/department count
- Units without assigned manager

#### D. Recent Activity

- Last invites sent
- Last role changes
- Last unit changes
- Last user suspension/reactivation

---

## 10. Stakeholders / Users Tab

### 10.1 Purpose

This tab manages organization members.

The tab label should change by organization type:

- State Ministry: Officers
- Employer: Team Members
- Medical Facility: Staff
- Federal Ministry: Federal Users
- Platform Admin: Platform Users

### 10.2 Table Columns

Recommended columns:

- Name
- Email
- Phone
- Role
- Unit / Department / Branch / Office
- Unit restricted
- Status
- Last login
- Joined date
- Actions

### 10.3 Filters

- Role
- Unit
- Status
- Unit restricted
- Date joined
- Search by name/email/phone

### 10.4 Dropdown Segments

Similar to the sample UI, the Stakeholders tab should support a dropdown filter.

#### State Ministry Dropdown

```txt
All Officers
State Team Members
Inspectors
LGA Officers
Pending Invites
Suspended Users
```

#### Employer Dropdown

```txt
All Team Members
Branch Managers
Compliance Officers
Finance Users
Pending Invites
Suspended Users
```

#### Medical Facility Dropdown

```txt
All Staff
Doctors
Lab Staff
Medical Records Staff
Finance Staff
Pending Invites
Suspended Users
```

#### Federal Ministry Dropdown

```txt
All Federal Users
M&E Officers
Policy Officers
Finance/Oversight Users
Executive Viewers
Pending Invites
Suspended Users
```

### 10.5 Actions

- Invite user
- View user
- Change role
- Change unit
- Toggle unit restriction
- Suspend user
- Reactivate user
- Remove user
- View audit trail

---

## 11. Roles & Permissions Tab

### 11.1 Purpose

This tab allows authorized admins to view and manage available roles and permissions.

### 11.2 Role List Columns

- Role name
- Role code
- Description
- Organization type
- Number of users
- Permissions count
- Status
- Actions

### 11.3 Role Detail View

Show:

- Role description
- Assigned users
- Permission groups
- Module access
- Sensitive permissions
- Last updated
- Audit history

### 11.4 Permission Grouping

Group permissions by module:

```txt
Organization
Users
Invites
Units
Facilities
Employers
Assessments
Certificates
Inspections
Payments
Reports
Settings
Audit Logs
```

### 11.5 MVP Rule

For MVP, implement:

- View role templates
- Assign roles
- View permissions
- Permission-based navigation

Custom role creation can be feature-flagged or deferred.

---

## 12. Units / Offices / Departments / Branches Tab

### 12.1 Purpose

This tab manages the internal structure of an organization.

| Organization Type | Tab Label |
|---|---|
| Federal Ministry | Departments / Directorates |
| State Ministry | Units & Offices |
| Medical Facility | Departments |
| Employer | Branches / Outlets |
| Platform Operator | Teams / Units |

### 12.2 Layout

Use a two-panel layout where possible.

#### Left Panel

Tree/list of units.

Example:

```txt
Food Safety Directorate
  ├── Certificate Verification Desk
  ├── Facility Accreditation Unit
  └── Inspectorate
      ├── Ikeja LGA Office
      └── Surulere LGA Office
```

#### Right Panel

Selected unit detail:

- Unit name
- Unit type
- Parent unit
- State
- LGA
- Address
- Manager
- Status
- Members count
- Linked records count
- Actions

### 12.3 Unit Actions

- Create unit
- Edit unit
- Add child unit
- Assign manager
- Assign users
- Deactivate unit
- View members
- View linked records

### 12.4 Primary Button Labels

| Organization Type | Button Label |
|---|---|
| State Ministry | Add Unit / Office |
| Employer | Add Branch |
| Medical Facility | Add Department |
| Federal Ministry | Add Department |
| Platform Admin | Add Team |

---

## 13. Invites Tab

### 13.1 Purpose

The Invites tab manages pending, accepted, expired, and revoked invitations.

### 13.2 Invite Table Columns

- Recipient email/phone
- Role
- Unit / Department / Branch / Office
- Unit restricted
- Invited by
- Status
- Expires at
- Accepted at
- Actions

### 13.3 Invite Filters

- Status
- Role
- Unit
- Invited by
- Expiry date

### 13.4 Invite Actions

- Create invite
- Resend invite
- Revoke invite
- Copy invite link
- View invite details

### 13.5 Invite Modal Fields

- Email
- Phone, optional
- Role
- Unit / Department / Branch / Office, optional
- Unit restricted toggle
- Message, optional
- Expiry date, default 7 days

### 13.6 Invite Acceptance Page

The invited user should see:

- Organization name
- Role
- Unit/branch/department
- Invited by
- Expiry date
- Accept button
- Decline button

---

## 14. Audit Logs Tab

### 14.1 Purpose

The Audit Logs tab provides a trace of stakeholder management actions.

### 14.2 Audit Table Columns

- Date/time
- Actor
- Action
- Target
- Role
- Unit
- Details
- IP address
- Actions

### 14.3 Audit Filters

- Date range
- Actor
- Action type
- Target user
- Role
- Unit

### 14.4 Logged Events

- User invited
- Invite accepted
- Invite revoked
- Invite resent
- Role changed
- Unit changed
- Unit restriction changed
- User suspended
- User reactivated
- User removed
- Unit created
- Unit updated
- Unit deactivated
- Permission override granted
- Permission override revoked

---

## 15. Backend Implementation Rules

### 15.1 No Separate Backend Modules

Do not create separate backend modules for:

- State users
- Facility staff
- Employer team members
- Employer branches
- Facility departments
- State units
- Invites

All of these should use:

```txt
Organization
OrganizationUnit
OrganizationMembership
Role
Permission
UserInvite
AuditLog
```

### 15.2 Organization Context

Every Stakeholder Management request must have an active organization context.

Possible sources:

- Current user active organization
- Route organization ID
- Workspace context
- Membership context

### 15.3 Label Resolution

The system should provide organization-specific labels.

Example response:

```json
{
  "organization_type": "state_ministry",
  "labels": {
    "stakeholders": "Officers",
    "unit": "Unit / Office",
    "units": "Units & Offices",
    "invite_button": "Invite Officer"
  }
}
```

### 15.4 Access Control

All endpoints must check:

```txt
User membership
Role
Permission
Organization scope
Unit scope
Unit restriction
```

### 15.5 Unit Restriction

If user is unit restricted:

- List queries must be filtered to assigned unit.
- User cannot create records outside assigned unit unless permission allows.
- User cannot invite users into other units.
- User cannot view other unit members.

---

## 16. Frontend Implementation Rules

### 16.1 One Parent Navigation Item

The sidebar/top navigation should show one parent item:

```txt
Stakeholder Management
```

Do not show these as disconnected top-level modules:

```txt
Users
Invites
Units & Offices
Branches
Departments
```

### 16.2 Internal Tabs

Inside Stakeholder Management, show tabs:

```txt
Overview
Stakeholders
Roles & Permissions
Units & Offices
Invites
Audit Logs
```

### 16.3 Permission-Based Tab Visibility

Hide tabs when user lacks permission.

Examples:

- User without `role.view` should not see Roles & Permissions.
- User without `invite.view` should not see Invites.
- User without `unit.view` should not see Units/Branches/Departments.
- User without `audit.view` should not see Audit Logs.

Backend must still enforce all permissions.

---

## 17. API Requirements

### 17.1 Context API

Add or expose:

```txt
GET /api/stakeholder-management/context
```

Returns:

```json
{
  "organization": {
    "id": "uuid",
    "name": "Lagos State Ministry of Health",
    "organization_type": "state_ministry",
    "state": "Lagos"
  },
  "labels": {
    "module_title": "Stakeholder Management",
    "stakeholders": "Officers",
    "units": "Units & Offices",
    "invite_button": "Invite Officer"
  },
  "permissions": {
    "can_view_users": true,
    "can_invite_users": true,
    "can_view_roles": true,
    "can_view_units": true,
    "can_view_invites": true,
    "can_view_audit_logs": false
  }
}
```

### 17.2 Existing APIs to Reuse

```txt
GET    /api/organizations/:organization_id/memberships
GET    /api/organizations/:organization_id/units
GET    /api/organizations/:organization_id/invites
GET    /api/roles
GET    /api/permissions
GET    /api/organizations/:organization_id/audit-logs
```

### 17.3 No Duplicate Endpoints

Avoid creating:

```txt
/api/state/users
/api/employer/users
/api/facility/staff
```

unless they are thin aliases to the shared stakeholder APIs.

---

## 18. Frontend Routes

### 18.1 Shared Routes

```txt
/app/stakeholder-management
/app/stakeholder-management/overview
/app/stakeholder-management/stakeholders
/app/stakeholder-management/roles
/app/stakeholder-management/units
/app/stakeholder-management/invites
/app/stakeholder-management/audit
```

### 18.2 Role-Specific Route Aliases

These should route to the same components:

```txt
/app/state/stakeholder-management
/app/employer/stakeholder-management
/app/facility/stakeholder-management
/app/federal/stakeholder-management
/app/admin/stakeholder-management
```

### 18.3 Query Parameter Tabs

Tabs may also be controlled by query params:

```txt
/app/state/stakeholder-management?tab=officers
/app/state/stakeholder-management?tab=roles
/app/state/stakeholder-management?tab=units
/app/state/stakeholder-management?tab=invites
```

---

## 19. Components to Build or Refactor

### 19.1 New Components

- StakeholderManagementLayout
- StakeholderManagementTabs
- StakeholderOverviewCards
- StakeholderTable
- StakeholderTypeDropdown
- RolePermissionTable
- UnitStructurePanel
- UnitTreeView
- InviteTable
- InviteUserModal
- StakeholderAuditTable
- OrganizationContextBadge
- StakeholderModuleHeader

### 19.2 Components to Refactor

If these currently exist as separate components, refactor them into shared Stakeholder Management components:

- UsersTable
- InvitesTable
- UnitsAndOfficesTable
- BranchesTable
- DepartmentsTable
- RolesTable

---

## 20. Permissions Required

Recommended permission codes:

```txt
stakeholder.view
stakeholder.overview.view
stakeholder.user.view
stakeholder.user.invite
stakeholder.user.update
stakeholder.user.suspend
stakeholder.role.view
stakeholder.role.assign
stakeholder.unit.view
stakeholder.unit.create
stakeholder.unit.update
stakeholder.unit.deactivate
stakeholder.invite.view
stakeholder.invite.create
stakeholder.invite.resend
stakeholder.invite.revoke
stakeholder.audit.view
```

These can map internally to existing permission names if already defined.

---

## 21. Migration From Current UI

### 21.1 Current State

Current navigation may show:

```txt
Units & Offices
Users
Invites
```

as separate items.

### 21.2 Target State

Replace with:

```txt
Stakeholder Management
```

Inside it:

```txt
Overview
Officers / Team Members / Staff
Roles & Permissions
Units & Offices / Branches / Departments
Invites
Audit Logs
```

### 21.3 Migration Steps

1. Add Stakeholder Management parent route.
2. Move Users page into Stakeholder Management tab.
3. Move Invites page into Stakeholder Management tab.
4. Move Units & Offices page into Stakeholder Management tab.
5. Add Roles & Permissions tab.
6. Add Overview tab.
7. Hide old top-level navigation items.
8. Add redirects from old URLs to new tab URLs.
9. Ensure existing API calls still work through shared services.
10. Refactor duplicated UI components into shared components.

### 21.4 Redirects

Recommended redirects:

```txt
/app/state/users → /app/state/stakeholder-management?tab=officers
/app/state/invites → /app/state/stakeholder-management?tab=invites
/app/state/units → /app/state/stakeholder-management?tab=units

/app/employer/users → /app/employer/stakeholder-management?tab=team-members
/app/employer/invites → /app/employer/stakeholder-management?tab=invites
/app/employer/branches → /app/employer/stakeholder-management?tab=branches

/app/facility/staff → /app/facility/stakeholder-management?tab=staff
/app/facility/invites → /app/facility/stakeholder-management?tab=invites
/app/facility/departments → /app/facility/stakeholder-management?tab=departments
```

---

## 22. Implementation Chunks for Codex

## Chunk 1: Navigation Consolidation

### Goal

Replace fragmented top-level navigation with one Stakeholder Management parent item.

### Backend Tasks

- Ensure the navigation API can return Stakeholder Management as a parent module.
- Add permission mapping for stakeholder management visibility.
- Ensure existing user/unit/invite permissions map to new parent visibility.

### Frontend Tasks

- Update sidebar/top navigation.
- Remove Users, Invites, Units & Offices as separate top-level items.
- Add Stakeholder Management nav item.
- Add active state handling.
- Add redirects from old routes.

### Acceptance Criteria

- Stakeholder Management appears as one parent module.
- Users, Invites, Units & Offices no longer appear as separate top-level modules.
- Old routes redirect correctly.
- Navigation respects permissions.

---

## Chunk 2: Stakeholder Management Layout and Context

### Goal

Create the parent page layout, header, context badge, and tab structure.

### Backend Tasks

- Add `/api/stakeholder-management/context`.
- Return active organization, organization type, labels, and permissions.
- Reuse membership/organization context.

### Frontend Tasks

- Create `StakeholderManagementLayout`.
- Create `StakeholderModuleHeader`.
- Create `OrganizationContextBadge`.
- Create `StakeholderManagementTabs`.
- Add tabs: Overview, Stakeholders, Roles & Permissions, Units/Offices/Branches/Departments, Invites, Audit Logs.

### Acceptance Criteria

- Stakeholder Management page loads.
- Header shows active organization.
- Labels change by organization type.
- Tabs show/hide by permission.

---

## Chunk 3: Overview Tab

### Goal

Create a summary dashboard for stakeholder management.

### Backend Tasks

- Add or reuse summary endpoint:

```txt
GET /api/stakeholder-management/summary
```

- Return total users, active users, pending invites, suspended users, total units, active units, roles in use, users without unit, and recent activity.

### Frontend Tasks

- Create `StakeholderOverviewCards`.
- Create recent activity list.
- Create structure summary panel.
- Add organization profile summary.

### Acceptance Criteria

- Overview tab shows stakeholder summary.
- Summary respects organization scope.
- Recent activity displays.
- Empty states work.

---

## Chunk 4: Stakeholders Tab

### Goal

Move users/team/staff/officers into the Stakeholders tab.

### Backend Tasks

- Reuse:

```txt
GET /api/organizations/:organization_id/memberships
PATCH /api/organizations/:organization_id/memberships/:id
```

- Add filters for role, unit, and status.
- Ensure scope enforcement.

### Frontend Tasks

- Create/refactor `StakeholderTable`.
- Create `StakeholderTypeDropdown`.
- Add filters, search, sort, pagination.
- Add row actions.
- Add invite button.
- Use organization-specific labels.

### Acceptance Criteria

- Users display inside Stakeholder Management.
- Dropdown segments work.
- Role/unit/status filters work.
- Row actions work according to permission.
- Unit-restricted users cannot view other units.

---

## Chunk 5: Roles & Permissions Tab

### Goal

Move roles into Stakeholder Management and show role permissions.

### Backend Tasks

- Reuse role APIs.
- Filter roles by organization type.
- Return role permission groups.
- Return assigned user counts.

### Frontend Tasks

- Create `RolePermissionTable`.
- Create role detail drawer.
- Show permissions grouped by module.
- Add assign role action if permitted.

### Acceptance Criteria

- Roles display by organization type.
- Permissions are visible.
- User counts are correct.
- Unauthorized users cannot view roles tab.

---

## Chunk 6: Units / Offices / Branches / Departments Tab

### Goal

Move units, offices, departments, and branches into one structure tab.

### Backend Tasks

- Reuse:

```txt
GET /api/organizations/:organization_id/units
POST /api/organizations/:organization_id/units
PATCH /api/organizations/:organization_id/units/:id
```

- Add unit tree response.
- Enforce organization scope.

### Frontend Tasks

- Create `UnitStructurePanel`.
- Create `UnitTreeView`.
- Create unit detail panel.
- Add create/edit/deactivate actions.
- Apply organization-specific labels.

### Acceptance Criteria

- State sees Units & Offices.
- Employer sees Branches / Outlets.
- Facility sees Departments.
- Federal sees Departments / Directorates.
- Unit tree/table works.
- Unit actions respect permissions.

---

## Chunk 7: Invites Tab

### Goal

Move pending/accepted/expired/revoked invites into Stakeholder Management.

### Backend Tasks

- Reuse invite APIs.
- Add filters by status, role, and unit.
- Ensure invite creation accepts role, unit, unit_restricted, and expiry date.

### Frontend Tasks

- Create `InviteTable`.
- Create `InviteUserModal`.
- Add resend/revoke/copy-link actions.
- Add status badges.
- Add invite filters.

### Acceptance Criteria

- Invites display inside Stakeholder Management.
- Invite modal works.
- Invites can be resent/revoked.
- Invite labels adapt by organization type.
- Invite permissions are enforced.

---

## Chunk 8: Audit Logs Tab

### Goal

Add stakeholder audit history.

### Backend Tasks

- Reuse or add:

```txt
GET /api/organizations/:organization_id/audit-logs
```

- Filter audit events by stakeholder actions.

### Frontend Tasks

- Create `StakeholderAuditTable`.
- Add filters by actor, action, date, and target.
- Add detail drawer.

### Acceptance Criteria

- Audit logs display.
- Logs are organization-scoped.
- Sensitive actions are included.
- Unauthorized users cannot view audit tab.

---

## Chunk 9: Route Migration and Cleanup

### Goal

Remove duplicate routes and redirect old URLs.

### Backend Tasks

- Keep old APIs if already used, but ensure they call shared services.
- Avoid duplicate service logic.

### Frontend Tasks

- Add redirects from old routes.
- Remove old standalone nav links.
- Refactor duplicated user/unit/invite pages.
- Update breadcrumbs.
- Update page titles.

### Acceptance Criteria

- Old routes redirect to new Stakeholder Management tabs.
- No broken links.
- Breadcrumbs show Stakeholder Management.
- Duplicated pages are removed or converted to aliases.

---

## Chunk 10: Tests and QA

### Backend Tests

- Context API returns correct labels.
- Permissions show/hide correct tabs.
- Membership list is scoped.
- Unit list is scoped.
- Invite list is scoped.
- Unit-restricted users cannot access other units.
- Old route aliases call shared service.
- Audit logs are created.

### Frontend Tests

- Stakeholder Management nav appears.
- Tabs render correctly.
- Labels change by organization type.
- Users tab works.
- Roles tab works.
- Units tab works.
- Invites tab works.
- Audit tab works.
- Old routes redirect correctly.

### Acceptance Criteria

- All tests pass.
- No permission regression.
- No stakeholder function exists as disconnected top-level UI.
- UI matches clean tabbed stakeholder management pattern.

---

## 23. Codex Implementation Prompt

Use this prompt for Codex:

```txt
Implement the Stakeholder Management UI consolidation update for FoodCert NG.

The goal is to replace fragmented top-level navigation items such as Users, Invites, Units & Offices, Branches, Departments, and Staff with one parent module called Stakeholder Management.

Inside Stakeholder Management, implement tabs:
- Overview
- Stakeholders
- Roles & Permissions
- Units / Offices / Branches / Departments
- Invites
- Audit Logs

The labels must adapt by organization type:
- State Ministry: Officers, Units & Offices
- Employer: Team Members, Branches / Outlets
- Medical Facility: Staff, Departments
- Federal Ministry: Federal Users, Departments / Directorates
- Platform Admin: Platform Users, Teams / Units

Reuse the existing Stakeholder Management backend models and services:
Organization, OrganizationUnit, OrganizationMembership, Role, Permission, UserInvite, AuditLog.

Do not create separate backend modules for State Users, Employer Users, Facility Staff, Branches, Departments, or Invites. If route aliases are needed, they should call the shared stakeholder services.

Implement a context endpoint that returns active organization, organization type, labels, and permissions.

Update frontend navigation so only Stakeholder Management appears as the parent nav item. Move Users, Invites, Units & Offices, Branches, Departments, and Roles into tabs under Stakeholder Management. Add redirects from old URLs to the correct new tabs.

All tabs must respect backend permissions and organization/unit scope. Unit-restricted users must not see records outside their assigned unit.

Build reusable frontend components, route aliases, redirects, tests, and audit log integration.
```

---

## 24. MVP Build Order

1. Navigation consolidation
2. Stakeholder context endpoint
3. Stakeholder Management parent layout
4. Overview tab
5. Stakeholders tab
6. Roles & Permissions tab
7. Units/Branches/Departments tab
8. Invites tab
9. Audit Logs tab
10. Route redirects and cleanup
11. Permissions and scope tests
12. Frontend QA
