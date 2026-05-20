# 15_STAKEHOLDER_MANAGEMENT_INTEGRATION.md — Multi-Actor Organization, Branch, Unit, and Stakeholder Management

## Purpose

This document extends the FoodCert NG PRD and Codex build instructions to support real-world stakeholder structures across a national rollout. The platform must not treat organizations as flat containers. State Ministries, employers, medical facilities, and federal agencies all require internal units, branches, departments, approval desks, and scoped staff access.

This file should be implemented alongside:

- `02_USERS_ROLES_ORGANIZATIONS.md`
- `03_IDENTITY_FOOD_HANDLERS_EMPLOYERS.md`
- `04_MEDICAL_FACILITY_ACCREDITATION.md`
- `08_ILLNESS_RETURN_TO_WORK_INSPECTIONS.md`
- `09_DASHBOARDS_REPORTING_ANALYTICS.md`
- `10_FRONTEND_PAGES_AND_UX.md`
- `12_API_ENDPOINTS_AND_ACCEPTANCE_CRITERIA.md`
- `13_CODEX_MASTER_PROMPT.md`
- `14_UI_UX_USER_FLOWS.md`

---

# 1. Why This Is Needed

The national platform will serve complex organizations, not just individual users.

## State Ministry of Health

A State Ministry may include:

- Commissioner or Permanent Secretary
- Director of Public Health
- Food Safety Directorate
- Certificate Verification Desk
- Facility Accreditation Unit
- Policy and Finance Unit
- Inspectorate Department
- LGA inspection offices
- Monitoring and Evaluation officers

These actors should not all have the same dashboard or permissions.

## Employer / Food Business

A large employer may have:

- Head office
- Regional offices
- Multiple branches
- Branch managers
- Compliance officers
- Site supervisors
- Food handlers assigned to specific branches

A branch manager should only see their own branch unless given wider access.

## Medical Facility

A medical facility may include:

- Facility administrator
- Clinical assessment department
- Laboratory department
- Medical records department
- Doctors
- Lab staff
- Records officers
- Finance/settlement officer

Each department needs access only to relevant workflows.

---

# 2. New Core Model: OrganizationUnit

Add `OrganizationUnit` to the `organizations` app.

```python
class OrganizationUnit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "organizations.Organization",
        related_name="units",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    unit_type = models.CharField(
        max_length=50,
        choices=[
            ("headquarters", "Headquarters"),
            ("directorate", "Directorate"),
            ("department", "Department"),
            ("unit", "Unit"),
            ("branch", "Branch"),
            ("lab_department", "Laboratory Department"),
            ("clinical_department", "Clinical Department"),
            ("records_department", "Medical Records Department"),
            ("lga_office", "LGA Office"),
            ("regional_office", "Regional Office"),
            ("other", "Other"),
        ],
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.SET_NULL,
    )
    description = models.TextField(blank=True)
    state = models.ForeignKey("geography.State", null=True, blank=True, on_delete=models.SET_NULL)
    lga = models.ForeignKey("geography.LGA", null=True, blank=True, on_delete=models.SET_NULL)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## Unit Type Examples

| Organization Type | Typical Units |
|---|---|
| Federal Ministry | M&E Directorate, Policy Directorate, Certification Oversight Unit |
| State Ministry | Food Safety Directorate, Verification Desk, Accreditation Unit, Inspectorate, LGA Offices |
| Employer | Headquarters, Regional Office, Branch |
| Medical Facility | Clinical Department, Laboratory Department, Medical Records Department, Finance Unit |
| Platform Operator | Support Unit, Technical Operations, Finance, Compliance |

Recommended nesting limit for MVP: **3 levels**.

---

# 3. User Model Update

Update the existing `User` model to include organization unit assignment.

```python
class User(AbstractUser):
    organization = models.ForeignKey(
        "organizations.Organization",
        null=True,
        blank=True,
        related_name="users",
        on_delete=models.SET_NULL,
    )
    unit = models.ForeignKey(
        "organizations.OrganizationUnit",
        null=True,
        blank=True,
        related_name="members",
        on_delete=models.SET_NULL,
    )
    unit_restricted = models.BooleanField(default=False)
```

## Meaning

- `organization` determines the main organization the user belongs to.
- `unit` optionally narrows the user to a branch, department, directorate, or office.
- `unit_restricted = true` means the user must only see records linked to their unit, except where explicit permission override exists.

Effective access should be computed as:

```txt
Role + Organization + Unit + unit_restricted flag + explicit permissions
```

---

# 4. Food Handler Profile Update

Add `business_branch` to `FoodHandlerProfile`.

```python
class FoodHandlerProfile(models.Model):
    employer = models.ForeignKey("employers.Employer", null=True, blank=True, on_delete=models.SET_NULL)
    business_branch = models.ForeignKey(
        "organizations.OrganizationUnit",
        null=True,
        blank=True,
        related_name="food_handlers",
        on_delete=models.SET_NULL,
    )
```

## Rules

- `business_branch` must belong to the same organization as the employer.
- `business_branch.unit_type` should usually be `branch`.
- If the food handler was invited by a branch manager, auto-assign their `business_branch`.
- If a food handler changes employer, require branch reassignment.
- A certificate remains valid after change of employer until expiry, but employer compliance visibility changes.

---

# 5. Inspection Model Update

Add `branch` to `Inspection`.

```python
class Inspection(models.Model):
    employer = models.ForeignKey("employers.Employer", on_delete=models.CASCADE)
    branch = models.ForeignKey(
        "organizations.OrganizationUnit",
        null=True,
        blank=True,
        related_name="inspections",
        on_delete=models.SET_NULL,
    )
```

## Rules

- If `branch` is set, the inspection targets a specific site.
- If `branch` is null, the inspection applies to the whole employer.
- Inspectors assigned to an LGA Office should see inspections in their LGA by default.
- State admins can view all inspections in their state.

---

# 6. New Model: UserInvite

Add `UserInvite` to support organization and unit-based invitations.

```python
class UserInvite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE)
    unit = models.ForeignKey(
        "organizations.OrganizationUnit",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    invited_by = models.ForeignKey(
        "accounts.User",
        related_name="sent_invites",
        on_delete=models.CASCADE,
    )
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    role = models.CharField(max_length=50, choices=RoleChoices.choices)
    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=30,
        choices=[
            ("pending", "Pending"),
            ("accepted", "Accepted"),
            ("expired", "Expired"),
            ("revoked", "Revoked"),
        ],
        default="pending",
    )
    token = models.CharField(max_length=255, unique=True)
    accepted_by = models.ForeignKey(
        "accounts.User",
        null=True,
        blank=True,
        related_name="accepted_invites",
        on_delete=models.SET_NULL,
    )
    accepted_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## Invite Lifecycle

```txt
Admin sends invite
  ↓
Pending
  ├── accepted by recipient → Accepted
  ├── expires_at passed → Expired
  └── revoked by admin → Revoked
```

## Who Can Invite Whom

| Inviter Role | Can Invite |
|---|---|
| Super Admin | Any role in any organization |
| Federal Admin | Federal users, State Ministry users, selected national roles |
| State Ministry Admin | State Ministry users, inspectors within their state |
| Medical Facility Admin | Facility Admin, Doctor, Lab Staff, Medical Records Staff |
| Employer | Employer users, branch managers, food handlers |
| Branch Manager | Food handlers for their branch only, if permitted |

---

# 7. State Ministry Multi-Actor Mapping

No additional global role is required for every internal title. Use existing role + organization unit + permissions.

| Unit | Unit Type | Typical Duties |
|---|---|---|
| Food Safety Directorate | directorate | Overall state food safety oversight |
| Certificate Verification Desk | unit | Review certificate validation queue |
| Facility Accreditation Unit | unit | Review and recommend facility approvals |
| Policy and Finance Unit | unit | Configure assessment fees, review revenue reports |
| Inspectorate Department | department | Assign and review inspections |
| LGA Office | lga_office | Local inspection coordination |

For MVP, unit scoping can be implemented as:

- Default dashboard filter
- Queue routing
- Suggested permission filtering
- Optional hard restriction when `unit_restricted = true`

---

# 8. Multi-Site Employer / Branch Management

## Employer Setup Flow

1. Employer registers organization.
2. Employer creates headquarters unit.
3. Employer creates branch units for each site.
4. Employer invites branch managers and assigns them to branches.
5. Food handlers are assigned to branches.
6. Employer dashboard supports branch filters.

## Branch Manager Scope

If user has:

```txt
role = Employer
unit = Branch — Ikeja
unit_restricted = true
```

Then they should only see:

- Food handlers in Branch — Ikeja
- Certificates for Branch — Ikeja staff
- Illness reports for Branch — Ikeja staff
- Compliance reports for Branch — Ikeja
- Inspections targeting Branch — Ikeja

Head office users should see all branches.

---

# 9. Medical Facility Department Management

Medical facilities should be able to create internal departments.

| Department | Unit Type | User Types |
|---|---|---|
| Clinical Assessment Department | clinical_department | Doctors |
| Laboratory Department | lab_department | Lab Staff |
| Medical Records Department | records_department | Records Staff |
| Finance/Settlement Unit | unit | Facility finance users |

## Department Scoping

- Doctors in clinical department see assigned assessments, declarations, examinations, and fitness decisions.
- Lab staff in lab department see lab requests and result entry.
- Medical records staff see completed assessment records and certificates.
- Finance users see payment and settlement reports.

---

# 10. API Endpoint Additions

## Organization Units

```txt
GET    /api/organizations/:id/units
POST   /api/organizations/:id/units
GET    /api/organizations/:id/units/:unit_id
PATCH  /api/organizations/:id/units/:unit_id
DELETE /api/organizations/:id/units/:unit_id
```

Delete should be soft-delete by setting `is_active = False`.

## User Invites

```txt
GET    /api/organizations/:id/invites
POST   /api/organizations/:id/invites
GET    /api/organizations/:id/invites/:invite_id
DELETE /api/organizations/:id/invites/:invite_id
POST   /api/invites/:token/accept
```

Delete should revoke the invite.

## User Unit Assignment

```txt
PATCH  /api/users/:id/unit
```

## Branch Assignment

```txt
PATCH /api/food-handlers/:id/business-branch
```

---

# 11. Dashboard and Reporting Impact

## Employer Dashboard

Add filters:

- Branch
- State
- LGA
- Food handler category
- Certificate status
- Fitness status

Branch managers should default to their own branch.

## State Ministry Dashboard

Add filters:

- Directorate/unit
- LGA Office
- Facility type
- Inspector unit
- LGA
- State zone, if configured

## Medical Facility Dashboard

Add filters:

- Department
- Doctor
- Lab status
- Assessment status
- Settlement status

## Federal Dashboard

Add drill-down:

```txt
National → State → LGA → Facility/Employer → Branch
```

---

# 12. UI/UX Additions

## Organization Unit Management Page

Available to:

- Super Admin
- Federal Admin, where allowed
- State Ministry Admin
- Employer Admin
- Medical Facility Admin

Features:

- Unit tree view
- Create unit
- Edit unit
- Deactivate unit
- Assign users
- View members
- View linked records

## Employer Branch Management Page

Route:

```txt
/app/employer/branches
```

Features:

- Create branch
- Edit branch
- Assign branch manager
- View branch compliance
- View branch food handlers
- Export branch report

## Facility Department Management Page

Route:

```txt
/app/facility/departments
```

Features:

- Create department
- Assign staff
- View department workload
- View department performance

## State Ministry Unit Management Page

Route:

```txt
/app/state/units
```

Features:

- Create directorate/unit/LGA office
- Assign officers
- Route certificate queue to Verification Desk
- Route accreditation applications to Accreditation Unit
- Route inspections to Inspectorate or LGA Office

## Invite User Modal

Fields:

- Email
- Phone, optional
- Role
- Unit, optional
- Message
- Expiry date, default 7 days

Actions:

- Send Invite
- Resend Invite
- Revoke Invite

---

# 13. Cross-Chunk Required Updates

## Update `02_USERS_ROLES_ORGANIZATIONS.md`

Add:

- `OrganizationUnit` model
- `User.unit`
- `User.unit_restricted`
- `UserInvite` model
- Unit-based invite workflow
- Unit-aware permission rules

## Update `03_IDENTITY_FOOD_HANDLERS_EMPLOYERS.md`

Add:

- `FoodHandlerProfile.business_branch`
- Employer branch management
- Branch-scoped employer dashboard
- Branch manager permissions

## Update `04_MEDICAL_FACILITY_ACCREDITATION.md`

Add:

- Facility department management after facility approval
- Clinical, lab, records, and finance units

## Update `08_ILLNESS_RETURN_TO_WORK_INSPECTIONS.md`

Add:

- `Inspection.branch`
- Branch-specific inspection workflow
- LGA office inspector assignment

## Update `09_DASHBOARDS_REPORTING_ANALYTICS.md`

Add:

- Branch filters
- Unit filters
- Department filters
- Federal drill-down to branch/facility level

## Update `10_FRONTEND_PAGES_AND_UX.md`

Add:

- Unit management pages
- Branch management pages
- Department management pages
- Invite user modal
- Role + unit scoped navigation

## Update `12_API_ENDPOINTS_AND_ACCEPTANCE_CRITERIA.md`

Add:

- Organization unit endpoints
- Invite endpoints
- User unit assignment endpoint
- Branch assignment endpoint
- Acceptance criteria listed below

## Update `13_CODEX_MASTER_PROMPT.md`

Add this instruction:

```txt
The application must support multi-actor organization structures. Organizations are not flat. Implement OrganizationUnit for directorates, departments, branches, LGA offices, laboratory departments, clinical departments, and records departments. Users can belong to an organization and optionally to a unit. Invites can assign a user to a role and unit. Employer food handlers can be assigned to business branches. Inspections can target a specific branch. Dashboards must default to the user's unit scope where applicable.
```

---

# 14. Acceptance Criteria

## Organization Units

- An organization can create multiple units.
- Units can be nested up to 3 levels.
- Units can be deactivated without deleting users.
- A user can be assigned to an organization unit.
- A unit can be assigned to a state and LGA where relevant.

## Invites

- Admin can invite a user to an organization.
- Admin can optionally assign the invite to a unit.
- Invite token expires after configured duration.
- Accepted invite assigns role, organization, and unit.
- Expired or revoked invite cannot be accepted.
- Invite acceptance creates audit log.

## Employer Branches

- Employer can create branch units.
- Food handlers can be assigned to branches.
- Branch managers can be restricted to their branch.
- Head office users can view all branches.
- Employer dashboard can filter by branch.

## Medical Facility Departments

- Facility can create departments.
- Doctors can be assigned to clinical department.
- Lab staff can be assigned to laboratory department.
- Records staff can be assigned to medical records department.
- Facility dashboard can filter by department.

## State Ministry Units

- State Ministry can create directorates, units, departments, and LGA offices.
- Certificate queue can be routed to Verification Desk.
- Accreditation applications can be routed to Accreditation Unit.
- Inspections can be routed to Inspectorate or LGA Office.
- Dashboards default to user unit scope where applicable.

## Inspections

- Inspection can target employer-wide or branch-specific scope.
- Branch-specific inspection shows branch food handlers and certificates.
- Inspector LGA office can default inspection list to its LGA.

## Privacy

- Unit scoping must not weaken medical data privacy.
- Branch managers still cannot see detailed medical records.
- Public verification remains unchanged and limited.

---

# 15. Codex Implementation Order for This Supplement

Implement this supplement after the foundation roles and organizations are created, but before employer/facility dashboards are finalized.

Recommended order:

1. Add `OrganizationUnit` model.
2. Add `User.unit` and `User.unit_restricted`.
3. Add `UserInvite` model.
4. Add organization unit endpoints.
5. Add invite endpoints.
6. Update permissions to account for organization and unit scope.
7. Add `FoodHandlerProfile.business_branch`.
8. Add branch management UI.
9. Add `Inspection.branch`.
10. Add dashboard filters.
11. Add facility department management UI.
12. Add state unit management UI.
13. Add tests for unit scoping.

---

# 16. Tests to Add

Add tests for:

- Creating organization units
- Nesting units
- Soft-deleting units
- Assigning users to units
- Accepting invites with units
- Branch manager seeing only branch food handlers
- Head office seeing all branches
- Facility lab staff seeing lab requests only
- State verification desk seeing certificate validation queue
- Inspection targeting a branch
- Dashboard defaulting to user unit
- Public verification unaffected by organization unit logic
