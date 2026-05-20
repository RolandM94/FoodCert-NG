# Chunk 00c — Stakeholder Management and Multi-Actor Organization Supplement

## Goal

Extend the core design with organizational substructures (departments, units, branches)
so that the platform supports the real-world stakeholder complexity of a national rollout
across 36 States + FCT, where each organization contains multiple actors with distinct
duties, scopes, and reporting lines.

---

## 1 — The Problem

The current design models organizations as flat containers:

```
Organization "Lagos State MOH"
  ├── User (role: State Ministry Admin)  ← one person does everything?
  └── User (role: Inspector)

Organization "MegaChow Ltd"
  └── User (role: Employer)              ← one person for 50 branches?
```

In reality:

- **Lagos State MOH** has a Commissioner, Director of Public Health, Head of Food Safety,
  Verification Officers (who review certificate queues), Policy Officers (who set fees),
  and dozens of Inspectors. These people are not interchangeable — a Verification Officer
  should not be managing facility accreditation.

- **MegaChow Ltd** has 50 restaurant branches across 5 states. Each branch has a Site Manager
  who needs to monitor only their own staff. The Head Office Compliance Officer needs to
  see everything. Food handlers at Ikeja branch are not the concern of the Surulere branch
  manager.

- **Excel Diagnostics Ltd** (a private facility) has a Main Lab department, a Clinical
  Assessment department, and a Medical Records department. Staff in each department
  have different access needs.

---

## 2 — New Model: OrganizationUnit

```python
class OrganizationUnit(models.Model):
    id = UUIDField(primary_key=True)
    organization = ForeignKey(Organization, related_name="units")
    name = CharField()
    unit_type = CharField(
        choices=[
            "headquarters",
            "directorate",
            "department",
            "unit",
            "branch",
            "lab_department",
            "clinical_department",
            "records_department",
            "other",
        ],
    )
    parent = ForeignKey("self", null=True, blank=True, related_name="children")
    description = TextField(blank=True)
    state = ForeignKey(State, null=True, blank=True)
    lga = ForeignKey(LGA, null=True, blank=True)
    address = TextField(blank=True)
    phone = CharField(blank=True)
    email = EmailField(blank=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### Unit Type Examples by Organization Type

| Organization Type | Typical Units |
|------------------|---------------|
| `state_ministry` | Food Safety Directorate, Verification Desk, Policy & Finance Unit, Inspectorate, LGA Offices |
| `employer` | Headquarters, Branch — Ikeja, Branch — Surulere, Branch — Lekki |
| `medical_facility` | Clinical Assessment Dept, Laboratory Dept, Medical Records Dept |
| `federal_ministry` | M&E Directorate, Policy Directorate, Certification Oversight Unit |

### Nesting

`parent` is self-referential. A state ministry can model:

```
Food Safety Directorate (directorate)
  ├── Verification Desk (unit)
  ├── Accreditation Unit (unit)
  └── Inspectorate (department)
        ├── LGA Office — Ikeja (unit)
        ├── LGA Office — Surulere (unit)
        └── LGA Office — Eti-Osa (unit)
```

---

## 3 — Updated Models

### User (overrides Chunk 02 User model)

Add two fields:

```python
class User(AbstractUser):
    # ... existing fields unchanged ...
    unit = ForeignKey(OrganizationUnit, null=True, blank=True, related_name="members")
    # ... rest unchanged ...
```

When a user belongs to an organization, `unit` optionally pins them to a specific
sub-unit. If `unit` is null while `organization` is set, the user is an organization-level
actor (e.g., the owner or a floating admin).

### FoodHandlerProfile (overrides Chunk 03 FoodHandlerProfile model)

Add one field:

```python
class FoodHandlerProfile(models.Model):
    # ... existing fields unchanged ...
    business_branch = ForeignKey(OrganizationUnit, null=True, blank=True)
    # ... rest unchanged ...
```

This links a food handler to the specific branch or location within their employer's
organization. `employer` still points to the parent `Employer` record; `business_branch`
narrows it to the physical site.

### Inspection (overrides Chunk 08 Inspection model)

Add one field:

```python
class Inspection(models.Model):
    # ... existing fields unchanged ...
    branch = ForeignKey(OrganizationUnit, null=True, blank=True)
    # ... rest unchanged ...
```

An inspection can now target a specific branch, not just a whole employer.
If `branch` is null, the inspection applies to the entire business.

---

## 4 — Expanded User Invite Workflow (overrides Chunk 02)

### Invite Model (new)

```python
class UserInvite(models.Model):
    id = UUIDField(primary_key=True)
    organization = ForeignKey(Organization)
    unit = ForeignKey(OrganizationUnit, null=True, blank=True)
    invited_by = ForeignKey(User, related_name="sent_invites")
    email = EmailField()
    phone = CharField(blank=True)
    role = CharField(choices=RoleChoices)
    message = TextField(blank=True)
    status = CharField(
        choices=["pending", "accepted", "expired", "revoked"],
        default="pending",
    )
    token = CharField(unique=True)
    accepted_by = ForeignKey(User, null=True, blank=True, related_name="accepted_invites")
    accepted_at = DateTimeField(null=True, blank=True)
    expires_at = DateTimeField()
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### Invite Lifecycle

```
[Admin sends invite]
  │
  ▼
pending ─── expires_at passed ──► expired
  │
  │ (recipient clicks link, registers/logs in)
  ▼
accepted ──► User auto-linked to organization, role, and optional unit
  │
  │ (admin manually revokes before acceptance)
  ▼
revoked
```

### Rules

1. Only users with `State Ministry Admin`, `Medical Facility Admin`, or `Employer`
   roles can send invites (within their organization scope).
2. An invite specifies: **email**, **role**, **unit** (optional), **message**.
3. If a `unit` is set, the invited user is scoped to that unit upon acceptance.
4. The token is a one-time-use, time-limited signed value (default 7 days expiry).
5. Expired invites cannot be accepted — a new invite must be sent.
6. An invitation acceptance audit log entry is created.
7. A notification is sent to the inviter when the invite is accepted.

### Who Can Invite Whom

| Inviter Role | Can Invite Roles |
|-------------|-----------------|
| State Ministry Admin | State Ministry Admin, Inspector |
| Medical Facility Admin | Doctor, Lab Staff, Facility Admin |
| Employer | Employer (branch manager) — limited scope |
| Super Admin / Federal Admin | Any role in any org |

---

## 5 — State MOH Multi-Actor Mapping

No new Django roles are added. The existing `State Ministry Admin` role is used.
Instead, `OrganizationUnit` distinguishes duties:

| Unit Name | unit_type | Typical Duties |
|-----------|-----------|---------------|
| Food Safety Directorate | directorate | Overall oversight, facility accreditation reviews |
| Verification Desk | unit | Review certificate queues, approve/reject issuance |
| Policy & Finance Unit | unit | Configure assessment fees, policy flags, settlement oversight |
| Inspectorate | department | Manage inspectors, assign inspections, review reports |
| LGA Offices (per LGA) | unit | Local inspections, local facility liaison |

### Permission Scope by Unit

Access control is computed as:
- **Role** determines what actions the user can perform.
- **Organization** determines which records are visible.
- **Unit** (optional) narrows visibility and action scope further.

Example: A Verification Desk officer can approve certificates, but only for their
state's queue. A Food Safety Directorate officer can review accreditations for their
state. An Inspector assigned to Ikeja LGA Office sees inspections assigned to their
LGA first, but can search statewide.

Unit-scoping is advisory (filtering, default views, queue routing) rather than
hard-gating, unless `unit` is paired with a `unit_restricted` flag on User.

---

## 6 — Multi-Site Employer (Branches)

### Setup Flow

1. Employer creates their organization and gets the `Employer` profile (Chunk 03).
2. Employer creates `OrganizationUnit` records of type `branch` for each physical site.
3. Each branch gets an address, state/LGA, and optionally a branch manager (User
   assigned to that unit with role `Employer`).
4. Food handlers are linked to a `business_branch` (OrganizationUnit).

### Scope Enforcement

- **Branch manager** (Employer user with `unit = "Branch — Ikeja"`):
  Sees only food handlers belonging to that branch. Dashboard filtered to that branch.
- **Head Office** (Employer user with no unit, or unit = "Headquarters"):
  Sees all branches. Dashboard filterable by branch.
- **Food handler** (no change): Belongs to an employer and optionally a branch.

### Invite Flow for Branches

When a head office admin invites a branch manager:
1. Invite specifies `unit = "Branch — Ikeja"`, `role = "Employer"`.
2. Branch manager accepts, is auto-scoped to that branch.
3. Branch manager can then invite food handlers — and those handlers
   auto-inherit `business_branch = "Branch — Ikeja"`.

---

## 7 — Private Facility Department Structuring

A multi-department facility (e.g., a large private hospital) creates units:

```
Medical Facility "Excel Diagnostics Ltd"
  ├── Clinical Assessment Dept (unit_type: clinical_department)
  │     ├── Doctor A
  │     └── Doctor B
  ├── Laboratory Dept (unit_type: lab_department)
  │     ├── Lab Staff A
  │     └── Lab Staff B
  └── Medical Records Dept (unit_type: records_department)
        └── Records Staff A
```

Users in each department see only their relevant workflows:
- Clinical Assessment Dept users see declarations, physical exams, fitness decisions.
- Laboratory Dept users see test requests and results.
- Medical Records Dept users see completed assessments and certificates.

Scoping is done by filtering the views/API queries to the user's unit.

---

## 8 — API Endpoint Additions

### Organization Units

```
GET    /api/organizations/:id/units
POST   /api/organizations/:id/units
GET    /api/organizations/:id/units/:unit_id
PATCH  /api/organizations/:id/units/:unit_id
DELETE /api/organizations/:id/units/:unit_id   (soft-delete: set is_active=False)
```

### User Invites (expanded)

```
GET    /api/organizations/:id/invites
POST   /api/organizations/:id/invites
DELETE /api/organizations/:id/invites/:invite_id   (revoke)
POST   /api/invites/:token/accept
```

### User Unit Assignment

```
PATCH  /api/users/:id/unit
```

Allowed only by organization admins within their own org scope.

---

## 9 — Dashboard Filter Impacts (overrides Chunk 09)

| Dashboard | New Filter |
|-----------|-----------|
| Employer | Branch (OrganizationUnit where unit_type=branch) |
| State MOH | LGA Office, Facility type, Inspector unit |
| Facility | Department (Clinical / Lab / Records) |
| Federal MOH | State → drill-down to LGA → drill-down to facility |

State and employer dashboards should default to the user's `unit` scope
when the user has a unit assigned.

---

## 10 — Cross-Chunk Impact Table

| Chunk | Impact |
|-------|--------|
| **00b** (Models Registry) | Add OrganizationUnit model |
| **01** (Foundation) | Include `units` app or add to `organizations` app |
| **02** (Users/Roles/Orgs) | User model gains `unit` FK. Add UserInvite model. Expand invite workflow. Add unit endpoints. |
| **03** (Food Handlers/Employers) | FoodHandlerProfile gains `business_branch` FK. Employer can create/manage branches. |
| **04** (Facility Accreditation) | No structural change. Facilities can optionally create departments after accreditation. |
| **06** (Medical Assessment) | No structural change. Doctor and lab staff workflows unchanged. |
| **08** (Illness/Inspections) | Inspection gains `branch` FK. Inspector can target specific branch. |
| **09** (Dashboards/Reports) | Add branch/unit filters to dashboards. Scope defaults to user's unit. |
| **10** (Frontend) | Add unit/branch management pages to employer, facility, and state admin views. |
| **12** (API Endpoints) | Add unit endpoints, invite lifecycle endpoints. |
| **13** (Codex Master Prompt) | Mention multi-actor org structure in build prompt. |

---

## 11 — Acceptance Criteria

- An organization can have multiple units/departments/branches.
- A unit can have a parent unit (nesting up to 3 levels recommended).
- A user can be assigned to a unit within their organization.
- Invites can specify a target unit.
- Food handlers can be assigned to a business branch.
- Inspections can target a specific branch.
- Branch-scoped employer users see only their branch's food handlers.
- State MOH users in the Verification Desk unit see only the certificate queue
  (not facility accreditation, not policy config) — scoping is advisory unless
  `unit_restricted` flag is on.
- Dashboard defaults to the user's unit where applicable.
- Removing a unit does not delete users — it unassigns them from the unit.
