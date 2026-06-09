# PRD: Stakeholder Management Module — FoodCert NG

## 1. Module Name

**Stakeholder Management Module**

## 2. Product Context

FoodCert NG is a national platform for food handler medical fitness certification. The platform serves several organization types, including Federal Ministry of Health and Social Welfare, State Ministries of Health and FCT Health authority, approved medical facilities, employers/food businesses, and the platform operator.

Each organization needs to manage internal offices, departments, units, branches, users, roles, permissions, invitations, and access scopes. Instead of rebuilding these features separately inside the Federal Ministry, State Ministry, Medical Facility, Employer, Inspector, and Reports modules, FoodCert NG should provide one shared **Stakeholder Management Module**.

This module becomes the foundational organization, user, role, permission, and invite layer for the entire platform.

---

# 3. Product Goal

To provide a unified, reusable organization and user-management system that allows every organization on FoodCert NG to manage its structure, users, roles, permissions, invitations, and scoped access without duplicating these features across individual modules.

---

# 4. Core Product Principle

FoodCert NG should treat every account-holding stakeholder as an **organization account**.

Each organization can have:

```txt
Organization
→ Offices / Directorates / Departments / Units / Branches
→ Users
→ Roles
→ Permissions
→ Invitations
→ Access Scope
```

The same stakeholder engine should power different organization experiences.

| Organization Type | UI Label for Units |
|---|---|
| Federal Ministry | Departments, Directorates, National Units |
| State Ministry | Directorates, Units, Desks, LGA Offices |
| Medical Facility | Departments, Clinical Unit, Lab Unit, Records Unit |
| Employer | Head Office, Branches, Regional Offices, Sites |
| Platform Operator | Support Unit, Finance, Compliance, Technical Admin |

---

# 5. Why This Module Is Needed

Without this shared module, each major module would have to separately implement users, invites, roles, permissions, offices, branches, departments, staff management, unit-level restrictions, access scoping, user suspension, and activity logs.

That would create duplicated code, inconsistent permissions, and high maintenance cost.

With a shared Stakeholder Management Module:

- State Ministries can manage units and officers.
- Employers can manage branches and branch managers.
- Medical facilities can manage departments and staff.
- Federal Ministry can manage national users and departments.
- Platform admins can manage organizations globally.
- Access control is consistent across the whole platform.

---

# 6. Module Objectives

The Stakeholder Management Module must allow authorized users to:

1. Create and manage organization profiles.
2. Define organization type.
3. Create and manage internal units, offices, departments, or branches.
4. Support nested organization units.
5. Invite users into organizations.
6. Assign users to roles.
7. Assign users to units/offices/departments/branches.
8. Apply unit-restricted access where needed.
9. Manage role templates by organization type.
10. Manage permissions linked to roles.
11. Support custom permission overrides where allowed.
12. Suspend, reactivate, or remove users from organizations.
13. Transfer users between units.
14. Maintain organization-scoped audit logs.
15. Support role-aware navigation.
16. Support organization-specific labels for units.
17. Provide APIs and frontend pages reusable across organization types.

---

# 7. Key Actors

## 7.1 Super Admin / Platform Operator

Can:

- Create organizations.
- Manage all organizations.
- Configure organization types.
- Configure global role templates.
- Manage all users.
- Assign platform-level roles.
- Override organization settings.
- Suspend organizations.
- View global audit logs.
- Configure permission templates.

## 7.2 Federal Ministry Admin

Can:

- Manage Federal Ministry organization profile.
- Create Federal Ministry departments/directorates.
- Invite federal users.
- Assign federal roles.
- Assign users to federal units.
- View national-level organization structures.
- View state organization summaries where permitted.

Cannot by default:

- Edit State Ministry internal users unless authorized.
- Manage medical facility users directly unless policy permits.
- Manage employer users directly unless policy permits.

## 7.3 State Ministry Admin

Can:

- Manage State Ministry organization profile.
- Create state units, directorates, desks, inspectorates, and LGA offices.
- Invite state users.
- Assign roles and units.
- Manage inspectors and LGA officers.
- Suspend/reactivate state users.
- View state-scoped stakeholder audit logs.

Cannot:

- Manage users outside their state.
- Edit Federal Ministry users.
- Edit employer/facility users unless specific regulatory action allows it.

## 7.4 Medical Facility Admin

Can:

- Manage facility profile within allowed fields.
- Create facility departments.
- Invite doctors.
- Invite lab staff.
- Invite medical records staff.
- Invite finance users.
- Assign staff to departments.
- Suspend/reactivate facility users.

Cannot:

- Approve its own facility accreditation.
- Assign State Ministry roles.
- Access another facility’s users.

## 7.5 Employer Admin / Business Owner

Can:

- Manage employer organization profile.
- Create branches and offices.
- Invite employer users.
- Invite branch managers.
- Invite compliance officers.
- Invite finance users.
- Invite food handlers or send food handler onboarding links.
- Assign food handlers to branches.
- Suspend internal employer users.

Cannot:

- Assign medical or regulatory roles.
- View other employers’ users.
- Modify medical records.

## 7.6 Branch Manager

Can, if permitted:

- View assigned branch.
- Invite food handlers to assigned branch.
- View branch users.
- Generate branch-level compliance views.
- Manage branch-specific worker onboarding.

Cannot if `unit_restricted = true`:

- View other branches.
- Invite users outside assigned branch.
- View employer-wide dashboards.

## 7.7 Organization User

A general user attached to an organization.

Can:

- Access modules permitted by assigned role.
- View their assigned unit.
- Update basic profile information.
- Accept invitations.

Cannot:

- Change own role unless permitted.
- Assign themselves permissions.
- Bypass unit restrictions.

---

# 8. Organization Types

The system must support the following organization types.

## 8.1 Federal Ministry

Represents the national oversight authority.

Examples:

- Federal Ministry of Health and Social Welfare

Common unit labels:

- Directorate
- Department
- Unit
- Programme Office
- M&E Unit
- Policy Unit

## 8.2 State Ministry

Represents each State Ministry of Health and the FCT Health authority.

Common unit labels:

- Directorate
- Unit
- Desk
- Inspectorate
- LGA Office
- State Office

Example units:

- Food Safety Directorate
- Certificate Verification Desk
- Facility Accreditation Unit
- Policy and Finance Unit
- Inspectorate Department
- Ikeja LGA Office

## 8.3 Medical Facility

Represents approved or applying medical facilities.

Common unit labels:

- Department
- Clinical Unit
- Laboratory Department
- Medical Records Unit
- Finance Unit
- Administration Unit

Example units:

- Clinical Assessment Department
- Laboratory Department
- Medical Records Department
- Finance / Settlement Unit

## 8.4 Employer / Food Business

Represents food businesses and employers.

Common unit labels:

- Head Office
- Branch
- Regional Office
- Site
- Outlet
- Store

Example units:

- Headquarters
- Ikeja Branch
- Lekki Branch
- Abuja Regional Office

## 8.5 Platform Operator

Represents the FoodCert NG system operator.

Common unit labels:

- Technical Operations
- Support
- Finance
- Compliance
- Admin

---

# 9. Organization Management

## 9.1 Organization Profile Fields

Each organization should have:

- Organization ID
- Organization name
- Organization type
- Parent organization, optional
- State, where applicable
- LGA, where applicable
- Address
- Phone
- Email
- Website, optional
- Contact person
- Status
- Created by
- Created at
- Updated at

## 9.2 Organization Statuses

- Draft
- Active
- Pending Approval
- Suspended
- Inactive
- Archived

## 9.3 Organization Rules

- Every account-holding stakeholder must belong to an organization.
- A user may belong to one or more organizations if multi-organization access is supported.
- Organization type determines available role templates.
- Organization type determines allowed unit labels.
- Organization status can affect access.
- Suspended organizations cannot invite new users.
- Archived organizations should not be deleted.

## 9.4 Parent-Child Organization Relationships

The system should support optional parent organization relationships.

Examples:

```txt
Federal Ministry of Health
  → State Ministry of Health

State Ministry of Health
  → LGA Office

Employer Head Office
  → Branches

Medical Facility
  → Departments
```

For MVP, parent-child relationships should be used carefully and should not replace `OrganizationUnit` for internal structure.

---

# 10. Organization Unit Management

## 10.1 Purpose

Organization units represent internal structures such as departments, offices, branches, directorates, desks, and units.

## 10.2 OrganizationUnit Model Concept

Use one flexible model:

```txt
OrganizationUnit
```

This model should power:

- Federal departments
- State directorates
- State LGA offices
- Facility departments
- Employer branches
- Platform operator teams

## 10.3 Unit Types

Supported unit types:

- Headquarters
- Directorate
- Department
- Unit
- Desk
- Office
- Branch
- Regional Office
- Site
- Outlet
- Store
- LGA Office
- Inspectorate
- Clinical Department
- Laboratory Department
- Medical Records Department
- Finance Unit
- Administration Unit
- Support Unit
- Technical Unit
- Other

## 10.4 Unit Fields

Each unit should include:

- Unit ID
- Organization
- Parent unit, optional
- Unit name
- Unit type
- Description
- State, optional
- LGA, optional
- Address, optional
- Phone, optional
- Email, optional
- Manager/user lead, optional
- Status
- Created by
- Created at
- Updated at

## 10.5 Unit Nesting

Units should support nesting.

Example State Ministry:

```txt
Lagos State Ministry of Health
  └── Food Safety Directorate
      ├── Certificate Verification Desk
      ├── Facility Accreditation Unit
      ├── Policy and Finance Unit
      └── Inspectorate Department
          ├── Ikeja LGA Office
          └── Surulere LGA Office
```

Example Employer:

```txt
MegaChow Foods Ltd
  ├── Headquarters
  ├── Ikeja Branch
  ├── Lekki Branch
  └── Abuja Regional Office
```

Example Facility:

```txt
Excel Diagnostics Ltd
  ├── Clinical Assessment Department
  ├── Laboratory Department
  ├── Medical Records Department
  └── Finance / Settlement Unit
```

## 10.6 Nesting Limit

Recommended MVP nesting limit:

```txt
3 levels
```

This prevents unnecessarily complex permission inheritance.

## 10.7 Unit Statuses

- Active
- Inactive
- Suspended
- Closed
- Archived

## 10.8 Unit Rules

- Units should be soft-deleted by setting status inactive/archived.
- Users assigned to inactive units should be flagged for reassignment.
- Branch units must belong to employer organizations.
- Clinical/lab/records departments must belong to medical facility organizations.
- LGA offices should belong to State Ministry organizations.
- Unit movement should be audit logged.
- Unit name should be unique within the same parent and organization.

---

# 11. User Membership Management

## 11.1 Purpose

A user can be attached to an organization with a role, optional unit, and access scope.

## 11.2 Membership Model Concept

Instead of storing only one role directly on the user, use an organization membership model.

```txt
User
→ OrganizationMembership
→ Organization
→ Role
→ Unit
→ Scope
```

This supports future cases where one user may belong to multiple organizations.

## 11.3 Membership Fields

Each membership should include:

- Membership ID
- User
- Organization
- Role
- Unit, optional
- Unit restricted: true/false
- Status
- Joined at
- Invited by
- Last active at
- Created at
- Updated at

## 11.4 Membership Statuses

- Invited
- Active
- Suspended
- Removed
- Expired
- Pending Verification

## 11.5 Membership Rules

- A user can have only one active membership per organization unless multi-role memberships are enabled.
- A user can have a role without a unit.
- A user can be assigned to a unit and restricted to it.
- If `unit_restricted = true`, the user can only access records linked to that unit.
- If `unit_restricted = false`, the user may access organization-wide records based on role permissions.
- Suspended users cannot access the organization workspace.
- Removed users should retain historical audit attribution.

---

# 12. User Management Features

Authorized organization admins should be able to:

- View organization users.
- Search users.
- Filter users by role.
- Filter users by unit.
- Filter users by status.
- Invite users.
- Assign roles.
- Assign units.
- Restrict user to unit.
- Suspend user.
- Reactivate user.
- Remove user from organization.
- Transfer user to another unit.
- View user activity.
- View user audit trail.

## 12.1 User Table Columns

- Name
- Email
- Phone
- Role
- Unit
- Unit restricted
- Status
- Last login
- Joined date
- Actions

## 12.2 User Actions

- View profile
- Edit role
- Change unit
- Toggle unit restriction
- Suspend
- Reactivate
- Remove
- Resend invite
- View audit log

---

# 13. Role Management

## 13.1 Purpose

Roles group permissions based on responsibilities.

## 13.2 Role Types

The system should support:

1. System-defined role templates
2. Organization-specific custom roles, future/optional
3. Permission overrides, where allowed

## 13.3 Role Fields

- Role ID
- Name
- Code
- Organization type
- Description
- Is system role
- Is custom role
- Permissions
- Status
- Created by
- Created at
- Updated at

## 13.4 Role Statuses

- Active
- Inactive
- Deprecated

## 13.5 Role Rules

- System roles cannot be deleted.
- Deprecated roles cannot be newly assigned.
- Custom roles should be restricted by organization type.
- Roles must map to permission codes.
- Role changes must be audit logged.
- Users should not be able to assign roles higher than their own authority level.
- Super Admin can manage global role templates.
- Organization Admin can assign roles allowed for their organization type.

---

# 14. Role Templates by Organization Type

## 14.1 Federal Ministry Role Templates

Suggested roles:

- Federal Admin
- National Food Safety Programme Officer
- National M&E Officer
- National Policy Officer
- National Finance/Oversight Officer
- Federal Viewer
- Executive Viewer

## 14.2 State Ministry Role Templates

Suggested roles:

- State Admin
- Food Safety Directorate Officer
- Certificate Verification Officer
- Facility Accreditation Officer
- Policy and Finance Officer
- Inspectorate Coordinator
- Inspector / Environmental Health Officer
- LGA Office Officer
- State Viewer

## 14.3 Medical Facility Role Templates

Suggested roles:

- Facility Admin
- Doctor
- Lab Staff
- Medical Records Staff
- Finance / Settlement User
- Facility Viewer

## 14.4 Employer Role Templates

Suggested roles:

- Employer Admin / Business Owner
- Compliance Officer
- Branch Manager
- Finance User
- Employer Viewer

## 14.5 Platform Operator Role Templates

Suggested roles:

- Super Admin
- Platform Admin
- Support Agent
- Finance Operator
- Compliance Operator
- Technical Operator
- Auditor

---

# 15. Permission Management

## 15.1 Purpose

Permissions define exactly what users can do.

## 15.2 Permission Format

Use clear permission codes:

```txt
module.action
```

Examples:

```txt
organization.view
organization.update
unit.create
unit.update
user.invite
user.suspend
role.assign
certificate.validate
facility.accredit
inspection.assign
payment.view
settlement.view
report.export
```

## 15.3 Permission Categories

Permission categories should include:

- Organization
- Unit
- User
- Role
- Invite
- Employer
- Facility
- Assessment
- Certificate
- Inspection
- Payment
- Subscription
- Settlement
- Report
- Policy
- Audit

## 15.4 Permission Rules

- Permissions should be backend-enforced.
- Frontend should only hide or show UI based on permissions but should not be trusted.
- Permission checks should consider organization and unit scope.
- Sensitive permissions should be auditable.
- Some permissions should be system-only.

## 15.5 Effective Access Formula

Access must be calculated using:

```txt
Role + Organization + Unit + Unit Restriction + Permission + Data Scope
```

Example:

A branch manager with:

```txt
role = Branch Manager
organization = MegaChow Foods Ltd
unit = Ikeja Branch
unit_restricted = true
```

Can access:

- Ikeja branch food handlers
- Ikeja branch certificates
- Ikeja branch inspections
- Ikeja branch reports

Cannot access:

- Lekki branch records
- Employer-wide finance
- Medical records

---

# 16. Suggested Permission Matrix

## 16.1 Organization and Unit Permissions

| Permission | Description |
|---|---|
| organization.view | View organization profile |
| organization.update | Update organization profile |
| organization.suspend | Suspend organization |
| unit.view | View organization units |
| unit.create | Create units |
| unit.update | Update units |
| unit.deactivate | Deactivate units |
| unit.assign_user | Assign users to units |
| unit.view_members | View unit members |

## 16.2 User and Invite Permissions

| Permission | Description |
|---|---|
| user.view | View users |
| user.invite | Invite users |
| user.update | Update user membership |
| user.suspend | Suspend users |
| user.reactivate | Reactivate users |
| user.remove | Remove users |
| invite.view | View invites |
| invite.create | Create invites |
| invite.resend | Resend invites |
| invite.revoke | Revoke invites |

## 16.3 Role and Permission Permissions

| Permission | Description |
|---|---|
| role.view | View roles |
| role.assign | Assign roles |
| role.create_custom | Create custom roles |
| role.update_custom | Update custom roles |
| permission.view | View permissions |
| permission.override | Apply permission overrides |

## 16.4 Module-Specific Permission Examples

| Permission | Description |
|---|---|
| employer.manage_branch | Manage employer branches |
| employer.view_compliance | View employer compliance |
| facility.manage_department | Manage facility departments |
| facility.invite_staff | Invite facility staff |
| certificate.verify | Verify certificate |
| certificate.validate | Approve certificate issuance |
| inspection.conduct | Conduct inspection |
| inspection.assign | Assign inspection |
| payment.view | View payment status |
| settlement.view | View settlement reports |
| report.export | Export reports |

---

# 17. Invitation Management

## 17.1 Purpose

Invitations allow organizations to add users to the platform under their organization, role, and unit.

## 17.2 Invitation Flow

```txt
Admin opens invite user form
→ Selects role
→ Selects unit/branch/department, optional
→ Sets unit restriction, optional
→ Enters email/phone
→ Sends invite
→ User receives invite link
→ User registers or logs in
→ User reviews invite details
→ User accepts
→ Membership is created
→ User lands on role-specific dashboard
```

## 17.3 Invite Fields

- Invite ID
- Organization
- Unit, optional
- Role
- Email
- Phone, optional
- Invited by
- Message
- Token
- Status
- Expires at
- Accepted by
- Accepted at
- Created at
- Updated at

## 17.4 Invite Statuses

- Pending
- Accepted
- Expired
- Revoked
- Failed

## 17.5 Invite Rules

- Invite tokens must be unique.
- Invite tokens must be one-time use.
- Invite tokens must expire.
- Default expiry should be 7 days.
- Admin can resend pending invite.
- Admin can revoke pending invite.
- Expired invite cannot be accepted.
- Revoked invite cannot be accepted.
- Invite acceptance must create audit log.
- User must be assigned to organization and role on acceptance.
- If unit was set, user must be assigned to that unit.
- If unit restriction was set, user must be restricted to that unit.

## 17.6 Invite Acceptance UX

Invite acceptance page should show:

- Organization name
- Organization type
- Role
- Unit/branch/department, if any
- Invited by
- Expiry date
- Accept button
- Decline button

If user is not registered:

- Create account first.
- Then accept invite.

If user is already logged in:

- Confirm acceptance.

---

# 18. Access Scoping

## 18.1 Scope Types

The module should support:

- Global scope
- National scope
- State scope
- Organization scope
- Unit scope
- LGA scope
- Branch scope
- Department scope
- Own-record scope

## 18.2 Scope Examples

| User | Scope |
|---|---|
| Super Admin | Global |
| Federal Admin | National |
| State Admin | State |
| State LGA Officer | LGA |
| Facility Admin | Facility organization |
| Lab Staff | Facility lab department |
| Employer Admin | Employer organization |
| Branch Manager | Employer branch |
| Food Handler | Own record |

## 18.3 Unit Restriction

If `unit_restricted = true`:

- User dashboard defaults to assigned unit.
- User cannot switch to other units.
- API queries must filter records by assigned unit.
- Reports must show only assigned unit.
- Exports must respect unit scope.

## 18.4 Non-Restricted Unit Assignment

If `unit_restricted = false`:

- Unit may be used as default dashboard filter.
- User can view broader organization data if role permits.
- User can switch units if role allows.

---

# 19. Role-Based Navigation

## 19.1 Purpose

Navigation should be generated based on role, permissions, and organization type.

## 19.2 Examples

### State Certificate Verification Officer

Navigation:

- Dashboard
- Certificate Validation Queue
- Certificate Registry
- Reports
- Notifications

### State Facility Accreditation Officer

Navigation:

- Dashboard
- Facility Applications
- Approved Facilities
- Re-accreditation
- Reports

### Employer Branch Manager

Navigation:

- Branch Dashboard
- Food Handlers
- Certificates
- Vaccination Compliance
- Illness Reports
- Inspections
- Reports

### Facility Lab Staff

Navigation:

- Lab Dashboard
- Lab Requests
- Result Entry
- Submitted Results

### Facility Doctor

Navigation:

- Doctor Dashboard
- Assigned Assessments
- Declaration Review
- Physical Exam
- Lab Result Review
- Vaccination Review
- Fitness Decision

---

# 20. Frontend UX Requirements

## 20.1 Stakeholder Management Main Pages

The module should provide these reusable pages:

- Organization Profile
- Units / Offices / Branches / Departments
- Users
- Roles
- Permissions
- Invites
- Audit Logs

## 20.2 Organization Profile Page

Displays:

- Organization name
- Organization type
- Contact details
- Address
- State/LGA
- Status
- Created date
- Update actions

## 20.3 Units Page

Features:

- Unit tree view
- Create unit
- Edit unit
- Deactivate unit
- View unit members
- Assign users
- View linked records

## 20.4 Users Page

Features:

- User table
- Invite user button
- Role filter
- Unit filter
- Status filter
- Search
- User detail drawer
- Role assignment
- Unit assignment
- Suspension/reactivation

## 20.5 Roles Page

Features:

- Role list
- Role description
- Permission list
- Role assignment rules
- Custom role creation, if enabled
- Role deprecation

## 20.6 Invites Page

Features:

- Pending invites
- Accepted invites
- Expired invites
- Revoked invites
- Resend invite
- Revoke invite
- Copy invite link

## 20.7 Audit Logs Page

Features:

- User activity log
- Role change log
- Invite log
- Unit change log
- Permission change log
- Filter by date/user/action

---

# 21. Organization-Specific UX Labels

The same underlying pages should use labels appropriate to organization type.

## 21.1 State Ministry

Use:

- Units and Offices
- Officers
- Roles
- Invites

## 21.2 Employer

Use:

- Branches
- Users
- Branch Managers
- Invites

## 21.3 Medical Facility

Use:

- Departments
- Staff
- Doctors
- Lab Staff
- Invites

## 21.4 Federal Ministry

Use:

- Departments and Directorates
- Federal Users
- Roles
- Invites

## 21.5 Platform Operator

Use:

- Organizations
- Teams
- Users
- Roles
- Permissions

---

# 22. Data Model Requirements

## 22.1 Organization

```python
class Organization(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)
    organization_type = models.CharField(max_length=50)
    parent = models.ForeignKey("self", null=True, blank=True, related_name="children", on_delete=models.SET_NULL)
    state = models.ForeignKey("geography.State", null=True, blank=True, on_delete=models.SET_NULL)
    lga = models.ForeignKey("geography.LGA", null=True, blank=True, on_delete=models.SET_NULL)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    contact_person_name = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=50)
    created_by = models.ForeignKey("accounts.User", null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 22.2 OrganizationUnit

```python
class OrganizationUnit(models.Model):
    id = models.UUIDField(primary_key=True)
    organization = models.ForeignKey("organizations.Organization", related_name="units", on_delete=models.CASCADE)
    parent = models.ForeignKey("self", null=True, blank=True, related_name="children", on_delete=models.SET_NULL)
    name = models.CharField(max_length=255)
    unit_type = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    state = models.ForeignKey("geography.State", null=True, blank=True, on_delete=models.SET_NULL)
    lga = models.ForeignKey("geography.LGA", null=True, blank=True, on_delete=models.SET_NULL)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    manager = models.ForeignKey("accounts.User", null=True, blank=True, related_name="managed_units", on_delete=models.SET_NULL)
    status = models.CharField(max_length=50)
    created_by = models.ForeignKey("accounts.User", null=True, blank=True, related_name="units_created", on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 22.3 Role

```python
class Role(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100, unique=True)
    organization_type = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    is_system_role = models.BooleanField(default=True)
    is_custom_role = models.BooleanField(default=False)
    status = models.CharField(max_length=50)
    created_by = models.ForeignKey("accounts.User", null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 22.4 Permission

```python
class Permission(models.Model):
    id = models.UUIDField(primary_key=True)
    code = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=255)
    module = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_sensitive = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 22.5 RolePermission

```python
class RolePermission(models.Model):
    id = models.UUIDField(primary_key=True)
    role = models.ForeignKey("stakeholders.Role", on_delete=models.CASCADE)
    permission = models.ForeignKey("stakeholders.Permission", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 22.6 OrganizationMembership

```python
class OrganizationMembership(models.Model):
    id = models.UUIDField(primary_key=True)
    user = models.ForeignKey("accounts.User", related_name="memberships", on_delete=models.CASCADE)
    organization = models.ForeignKey("organizations.Organization", related_name="memberships", on_delete=models.CASCADE)
    role = models.ForeignKey("stakeholders.Role", on_delete=models.PROTECT)
    unit = models.ForeignKey("organizations.OrganizationUnit", null=True, blank=True, on_delete=models.SET_NULL)
    unit_restricted = models.BooleanField(default=False)
    status = models.CharField(max_length=50)
    invited_by = models.ForeignKey("accounts.User", null=True, blank=True, related_name="memberships_invited", on_delete=models.SET_NULL)
    joined_at = models.DateTimeField(null=True, blank=True)
    last_active_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 22.7 UserInvite

```python
class UserInvite(models.Model):
    id = models.UUIDField(primary_key=True)
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE)
    unit = models.ForeignKey("organizations.OrganizationUnit", null=True, blank=True, on_delete=models.SET_NULL)
    role = models.ForeignKey("stakeholders.Role", on_delete=models.PROTECT)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    invited_by = models.ForeignKey("accounts.User", related_name="sent_invites", on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    unit_restricted = models.BooleanField(default=False)
    token = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50)
    accepted_by = models.ForeignKey("accounts.User", null=True, blank=True, related_name="accepted_invites", on_delete=models.SET_NULL)
    accepted_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 22.8 PermissionOverride

```python
class PermissionOverride(models.Model):
    id = models.UUIDField(primary_key=True)
    membership = models.ForeignKey("stakeholders.OrganizationMembership", on_delete=models.CASCADE)
    permission = models.ForeignKey("stakeholders.Permission", on_delete=models.CASCADE)
    effect = models.CharField(max_length=20)  # allow or deny
    reason = models.TextField(blank=True)
    granted_by = models.ForeignKey("accounts.User", null=True, blank=True, on_delete=models.SET_NULL)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

# 23. API Requirements

## 23.1 Organization APIs

```txt
GET    /api/organizations
POST   /api/organizations
GET    /api/organizations/:id
PATCH  /api/organizations/:id
PATCH  /api/organizations/:id/suspend
PATCH  /api/organizations/:id/reactivate
```

## 23.2 Organization Unit APIs

```txt
GET    /api/organizations/:organization_id/units
POST   /api/organizations/:organization_id/units
GET    /api/organizations/:organization_id/units/:unit_id
PATCH  /api/organizations/:organization_id/units/:unit_id
DELETE /api/organizations/:organization_id/units/:unit_id
GET    /api/organizations/:organization_id/units/:unit_id/members
POST   /api/organizations/:organization_id/units/:unit_id/assign-user
```

Delete should soft-delete/deactivate the unit.

## 23.3 Membership APIs

```txt
GET   /api/organizations/:organization_id/memberships
GET   /api/organizations/:organization_id/memberships/:membership_id
PATCH /api/organizations/:organization_id/memberships/:membership_id
PATCH /api/organizations/:organization_id/memberships/:membership_id/suspend
PATCH /api/organizations/:organization_id/memberships/:membership_id/reactivate
PATCH /api/organizations/:organization_id/memberships/:membership_id/remove
PATCH /api/organizations/:organization_id/memberships/:membership_id/change-role
PATCH /api/organizations/:organization_id/memberships/:membership_id/change-unit
PATCH /api/organizations/:organization_id/memberships/:membership_id/toggle-unit-restriction
```

## 23.4 Invite APIs

```txt
GET    /api/organizations/:organization_id/invites
POST   /api/organizations/:organization_id/invites
GET    /api/organizations/:organization_id/invites/:invite_id
POST   /api/organizations/:organization_id/invites/:invite_id/resend
POST   /api/organizations/:organization_id/invites/:invite_id/revoke
POST   /api/invites/:token/accept
POST   /api/invites/:token/decline
GET    /api/invites/:token/preview
```

## 23.5 Role and Permission APIs

```txt
GET    /api/roles
POST   /api/roles
GET    /api/roles/:id
PATCH  /api/roles/:id
GET    /api/permissions
GET    /api/roles/:id/permissions
POST   /api/roles/:id/permissions
DELETE /api/roles/:id/permissions/:permission_id
GET    /api/organization-types/:type/roles
```

## 23.6 Permission Check APIs

```txt
GET  /api/me/memberships
GET  /api/me/effective-permissions
GET  /api/me/navigation
POST /api/permissions/check
```

## 23.7 Audit APIs

```txt
GET /api/organizations/:organization_id/audit-logs
GET /api/stakeholders/audit-logs
```

---

# 24. Frontend Routes

## 24.1 Shared Stakeholder Routes

```txt
/app/stakeholders/organizations
/app/stakeholders/organizations/[id]
/app/stakeholders/organizations/[id]/units
/app/stakeholders/organizations/[id]/users
/app/stakeholders/organizations/[id]/roles
/app/stakeholders/organizations/[id]/invites
/app/stakeholders/organizations/[id]/audit
```

## 24.2 Organization-Specific Routes

These routes can use the same components with different labels.

### Federal Ministry

```txt
/app/federal/stakeholders/departments
/app/federal/stakeholders/users
/app/federal/stakeholders/roles
/app/federal/stakeholders/invites
```

### State Ministry

```txt
/app/state/stakeholders/units
/app/state/stakeholders/offices
/app/state/stakeholders/users
/app/state/stakeholders/roles
/app/state/stakeholders/invites
```

### Medical Facility

```txt
/app/facility/stakeholders/departments
/app/facility/stakeholders/staff
/app/facility/stakeholders/roles
/app/facility/stakeholders/invites
```

### Employer

```txt
/app/employer/stakeholders/branches
/app/employer/stakeholders/users
/app/employer/stakeholders/roles
/app/employer/stakeholders/invites
```

### Platform Admin

```txt
/app/admin/organizations
/app/admin/organizations/[id]
/app/admin/roles
/app/admin/permissions
/app/admin/invites
```

---

# 25. Core Frontend Components

Build reusable components:

- OrganizationProfileForm
- OrganizationStatusBadge
- OrganizationTypeBadge
- OrganizationUnitTree
- OrganizationUnitForm
- OrganizationUnitDetailPanel
- UnitStatusBadge
- UnitMemberTable
- UserMembershipTable
- UserMembershipDetailDrawer
- InviteUserModal
- InvitePreviewPage
- InviteStatusBadge
- RoleSelector
- UnitSelector
- PermissionList
- RolePermissionMatrix
- PermissionOverridePanel
- EffectivePermissionViewer
- UnitRestrictionToggle
- OrganizationScopeSwitcher
- RoleBasedNavigationPreview
- StakeholderAuditTimeline
- OrganizationActivityLog
- UserStatusBadge
- MembershipStatusBadge

---

# 26. Permission and Scope Services

## 26.1 Required Services

Backend should implement service-layer classes:

- OrganizationService
- OrganizationUnitService
- MembershipService
- InviteService
- RoleService
- PermissionService
- EffectiveAccessService
- NavigationService
- StakeholderAuditService

## 26.2 EffectiveAccessService

This service should calculate what a user can access.

Inputs:

- User
- Organization
- Role
- Unit
- Unit restriction
- Permission overrides
- Requested resource
- Requested action

Output:

```json
{
  "allowed": true,
  "reason": "permission_granted",
  "scope": "unit",
  "unit_id": "uuid"
}
```

## 26.3 NavigationService

This service should generate user navigation based on:

- Active organization
- Organization type
- Role
- Permissions
- Unit scope

---

# 27. Cross-Module Usage

## 27.1 Employer Module Usage

Employer Module uses Stakeholder Management for:

- Branches
- Employer users
- Branch managers
- Compliance officers
- Finance users
- Food handler invites
- Branch-scoped access

## 27.2 Medical Facility Module Usage

Medical Facility Module uses Stakeholder Management for:

- Departments
- Doctors
- Lab staff
- Records staff
- Finance users
- Department-scoped access

## 27.3 State Ministry Module Usage

State Ministry Module uses Stakeholder Management for:

- State directorates
- Certificate Verification Desk
- Accreditation Unit
- Policy and Finance Unit
- Inspectorate
- LGA offices
- State users and officers

## 27.4 Federal Ministry Module Usage

Federal Ministry Module uses Stakeholder Management for:

- Federal departments
- National users
- Federal roles
- National oversight users

## 27.5 Inspector Module Usage

Inspector Module uses Stakeholder Management for:

- Inspector assignment to State Ministry
- LGA office scoping
- Inspectorate unit membership
- Inspector permissions

## 27.6 Reports Module Usage

Reports Module uses Stakeholder Management for:

- Unit filters
- Branch filters
- Department filters
- User scope filtering
- Report access control

---

# 28. Privacy and Security Requirements

## 28.1 Core Security Rules

- All permission checks must be backend-enforced.
- Frontend hiding is not enough.
- Unit scoping must be applied to API querysets.
- Sensitive role changes must be audit logged.
- Permission overrides must expire where possible.
- Invite tokens must be securely generated.
- Invite tokens must not expose sensitive information.
- Removed users should not lose audit history.
- Suspended users cannot access organization workspace.
- Users cannot assign themselves higher privileges.

## 28.2 Medical Privacy Reminder

Stakeholder access must not weaken medical privacy.

Even if a user is an organization admin, they should not automatically see:

- Lab results
- Doctor notes
- Diagnosis
- Health declaration answers
- Full NIN

Medical access must still be governed by role-specific permissions and module-level privacy rules.

---

# 29. Audit Logs

Create audit logs for:

- Organization created
- Organization updated
- Organization suspended/reactivated
- Unit created
- Unit updated
- Unit deactivated
- Unit moved
- User invited
- Invite resent
- Invite revoked
- Invite accepted
- User role changed
- User unit changed
- Unit restriction changed
- User suspended
- User reactivated
- User removed
- Role created
- Role updated
- Role deprecated
- Permission added to role
- Permission removed from role
- Permission override granted
- Permission override revoked
- Effective permission check failed for sensitive action

Audit metadata should include:

- Actor
- Action
- Organization
- Unit
- Target user
- Target role
- Timestamp
- IP address
- User agent
- Before/after values where applicable

---

# 30. Notifications

## 30.1 Invite Notifications

Notify user when:

- Invite is sent.
- Invite is resent.
- Invite is revoked.
- Invite is about to expire.
- Invite is accepted.

## 30.2 Admin Notifications

Notify admin when:

- Invite accepted.
- User joins organization.
- User role changed.
- User suspended/reactivated.
- Permission override granted.
- Unit created/deactivated.

## 30.3 User Notifications

Notify user when:

- Their role changes.
- Their unit changes.
- Their access is suspended.
- They are removed from organization.
- Their invite is accepted successfully.

---

# 31. Background Jobs

## 31.1 Invite Expiry Job

Runs periodically.

Tasks:

- Find expired pending invites.
- Mark them expired.
- Notify inviter where required.

## 31.2 Stale User Review Job

Optional/future.

Tasks:

- Identify inactive users.
- Notify organization admins.
- Suggest access review.

## 31.3 Permission Override Expiry Job

Tasks:

- Expire temporary permission overrides.
- Notify affected user and admin.
- Log expiry.

---

# 32. Acceptance Criteria

## 32.1 Organization Management

- Super Admin can create organizations.
- Organization profile can be updated by authorized users.
- Organization type determines available unit labels and role templates.
- Suspended organizations cannot invite users.
- Organization changes are audit logged.

## 32.2 Unit Management

- Authorized users can create organization units.
- Units can be nested up to configured depth.
- Units can be edited.
- Units can be deactivated.
- Users can be assigned to units.
- Unit changes are audit logged.
- Unit-restricted users cannot access other units.

## 32.3 User Management

- Authorized users can view organization users.
- Authorized users can assign roles.
- Authorized users can assign units.
- Authorized users can suspend/reactivate users.
- Removed users lose access but audit history remains.
- User management actions are audit logged.

## 32.4 Role and Permission Management

- System roles are available by organization type.
- Users can only assign roles permitted for their organization type.
- Permissions are backend-enforced.
- Role changes immediately affect access.
- Sensitive permission changes are audit logged.

## 32.5 Invite Management

- Authorized users can send invites.
- Invites can include role and unit.
- Invites can set unit restriction.
- Invites expire after configured duration.
- Pending invites can be resent.
- Pending invites can be revoked.
- Accepted invites create organization membership.
- Expired/revoked invites cannot be accepted.

## 32.6 Scope Enforcement

- Branch manager with unit restriction sees only assigned branch.
- Facility lab staff sees lab department workflows only.
- State LGA officer sees LGA-scoped records.
- Federal user sees national scope only if role permits.
- API querysets enforce scope server-side.

## 32.7 Cross-Module Reuse

- Employer branches use OrganizationUnit.
- Facility departments use OrganizationUnit.
- State Ministry offices use OrganizationUnit.
- Federal departments use OrganizationUnit.
- Reports can filter by organization unit.
- Inspector module can use inspector LGA office assignment.

---

# 33. Testing Requirements

Add tests for:

- Organization creation
- Organization update
- Organization suspension
- Unit creation
- Unit nesting
- Unit soft delete
- User invite creation
- Invite acceptance
- Expired invite rejection
- Revoked invite rejection
- Membership creation
- Role assignment
- Unit assignment
- Unit restriction enforcement
- Permission checks
- Permission override
- Branch manager scope
- Facility department scope
- State LGA office scope
- Federal national scope
- Audit log creation
- Navigation generation by role
- API queryset scope filtering

---

# 34. Codex Implementation Instructions

Use this prompt for Codex:

```txt
Implement the Stakeholder Management Module for FoodCert NG.

The module must provide shared organization management, organization unit management, user membership management, role and permission management, invitation workflows, unit-scoped access, effective permission calculation, role-based navigation, audit logs, and reusable frontend pages.

Important rules:
- Every stakeholder is an organization account.
- The same OrganizationUnit model must support Federal Ministry departments, State Ministry units/offices, Medical Facility departments, Employer branches, and Platform Operator teams.
- Users join organizations through OrganizationMembership.
- Membership includes role, optional unit, and unit_restricted flag.
- Invites must assign organization, role, optional unit, and optional unit restriction.
- Access must be calculated using Role + Organization + Unit + Unit Restriction + Permission + Data Scope.
- Unit scoping must be enforced on the backend, not only in the frontend.
- Stakeholder management must be reused by Employer, Medical Facility, State Ministry, Federal Ministry, Inspector, Reports, and Admin modules.
- Role labels and unit labels should adapt to organization type.
- Medical privacy must not be weakened by organization admin access.
- All sensitive actions must be audit logged.

Build backend models, serializers, permissions, services, endpoints, tests, and frontend pages for this module.
```

---

# 35. MVP Build Order

1. Organization model and APIs
2. Organization type constants
3. OrganizationUnit model and APIs
4. Role model
5. Permission model
6. RolePermission model
7. Seed default role templates by organization type
8. OrganizationMembership model
9. Membership APIs
10. UserInvite model
11. Invite create/resend/revoke/accept APIs
12. Effective permission service
13. Unit scope filtering utilities
14. Role-based navigation service
15. Organization profile frontend
16. Unit tree frontend
17. Users/memberships frontend
18. Invite user modal and invite pages
19. Roles and permissions frontend
20. Audit logging
21. Background invite expiry job
22. Permission tests
23. Unit scope tests
24. Cross-module integration examples
