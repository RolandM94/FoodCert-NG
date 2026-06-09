# Stakeholder Management Module — Implementation Chunk Breakdown

> Based on `FOODCERT_STAKEHOLDER_MANAGEMENT_MODULE_PRD.md`
> Existing codebase: Django REST Framework backend + Next.js frontend
> Key existing apps: `apps/accounts` (User, UserInvite), `apps/organizations` (Organization, OrganizationUnit)

---

## Summary of Existing vs. Needed

| Concept | Already Exists? | Gap |
|---|---|---|
| Organization | `organizations.Organization` | Missing: `parent`, `contact_person_name`, `website`, `created_by`, additional status values |
| OrganizationUnit | `organizations.OrganizationUnit` | Missing: `manager`, `created_by`, `status` enum, more `unit_type` values |
| User | `accounts.User` | Has flat `role` CharField — must migrate to membership-based model |
| UserInvite | `accounts.UserInvite` | Missing: `unit_restricted`, `message`; align status values |
| Role model | **NO** | Must create |
| Permission model | **NO** | Must create |
| RolePermission | **NO** | Must create |
| OrganizationMembership | **NO** (User has direct FK to org/unit) | **Central piece** — must create |
| PermissionOverride | **NO** | Must create |

---

## Chunk 0: Foundation — Align Existing Models with PRD

**Status:** Implemented and verified.

**Purpose:** Evolve existing models to support membership-based RBAC. This is the prerequisite for everything else.

### 0.1 Extend Organization Model
**File:** `backend/apps/organizations/models.py`

- Add `parent` — FK to self (optional, for parent-child org relationships)
- Add `contact_person_name`, `website`
- Add `created_by` — FK to `accounts.User`
- Update `OrganizationStatus` enum to include: `DRAFT`, `ACTIVE`, `PENDING_APPROVAL`, `SUSPENDED`, `INACTIVE`, `ARCHIVED`
- Create + run migration

### 0.2 Extend OrganizationUnit Model
**File:** `backend/apps/organizations/models.py`

- Add `manager` — FK to `accounts.User` (optional)
- Add `created_by` — FK to `accounts.User`
- Replace `is_active` BooleanField with `status` CharField using enum: `ACTIVE`, `INACTIVE`, `SUSPENDED`, `CLOSED`, `ARCHIVED`
- Extend `OrganizationUnitType` to include all PRD types: `DESK`, `OFFICE`, `BRANCH`, `REGIONAL_OFFICE`, `SITE`, `OUTLET`, `STORE`, `LGA_OFFICE`, `INSPECTORATE`, `CLINICAL_DEPARTMENT`, `LAB_DEPARTMENT`, `MEDICAL_RECORDS_DEPARTMENT`, `FINANCE_UNIT`, `ADMINISTRATION_UNIT`, `SUPPORT_UNIT`, `TECHNICAL_UNIT`, `OTHER`
- Create + run migration

### 0.3 Extend UserInvite Model
**File:** `backend/apps/accounts/models.py`

- Add `unit_restricted` BooleanField (default=False)
- Add `message` TextField
- Add `unit_restricted` to existing serializer and views
- Align `InviteStatus` with PRD: `PENDING`, `ACCEPTED`, `EXPIRED`, `REVOKED`, `FAILED`
- Create + run migration

### 0.4 Create Role Model
**File:** `backend/apps/organizations/models.py` (or new `backend/apps/stakeholders/` app)

```python
class Role(BaseModel):
    name = CharField(max_length=255)
    code = CharField(max_length=100, unique=True)
    organization_type = CharField(max_length=50, blank=True)  # nullable = system-wide
    description = TextField(blank=True)
    is_system_role = BooleanField(default=True)
    is_custom_role = BooleanField(default=False)
    status = CharField(max_length=50)  # ACTIVE, INACTIVE, DEPRECATED
    created_by = FK(User, null=True, SET_NULL)
```

### 0.5 Create Permission Model
**File:** `backend/apps/organizations/models.py`

```python
class Permission(BaseModel):
    code = CharField(max_length=150, unique=True)
    name = CharField(max_length=255)
    module = CharField(max_length=100)
    description = TextField(blank=True)
    is_sensitive = BooleanField(default=False)
```

### 0.6 Create RolePermission Join Model
**File:** `backend/apps/organizations/models.py`

```python
class RolePermission(BaseModel):
    role = FK(Role, CASCADE, related_name='role_permissions')
    permission = FK(Permission, CASCADE)
    class Meta:
        unique_together = ('role', 'permission')
```

### 0.7 Create OrganizationMembership Model
**File:** `backend/apps/organizations/models.py`

```python
class OrganizationMembership(BaseModel):
    user = FK(User, CASCADE, related_name='memberships')
    organization = FK(Organization, CASCADE, related_name='memberships')
    role = FK(Role, PROTECT)
    unit = FK(OrganizationUnit, null=True, SET_NULL)
    unit_restricted = BooleanField(default=False)
    status = CharField(max_length=50)  # INVITED, ACTIVE, SUSPENDED, REMOVED, EXPIRED, PENDING_VERIFICATION
    invited_by = FK(User, null=True, SET_NULL, related_name='memberships_invited')
    joined_at = DateTimeField(null=True)
    last_active_at = DateTimeField(null=True)
    class Meta:
        constraints = [UniqueConstraint(fields=['user', 'organization'], condition=Q(status='ACTIVE'), name='unique_active_membership')]
```

### 0.8 Create PermissionOverride Model
**File:** `backend/apps/organizations/models.py`

```python
class PermissionOverride(BaseModel):
    membership = FK(OrganizationMembership, CASCADE)
    permission = FK(Permission, CASCADE)
    effect = CharField(max_length=20)  # 'allow' or 'deny'
    reason = TextField(blank=True)
    granted_by = FK(User, null=True, SET_NULL)
    expires_at = DateTimeField(null=True)
```

### 0.9 Data Migration: Backfill Memberships
**File:** `backend/apps/organizations/migrations/0xxx_backfill_memberships.py`

- For every `User` with `organization_id` set, create an `OrganizationMembership` row
- Map `User.role` → corresponding `Role` record (create roles first in Chunk 1, or backfill after)
- Map `User.unit_id` → `membership.unit`
- Map `User.unit_restricted` → `membership.unit_restricted`
- Set status to `ACTIVE`

### 0.10 Deprecate Direct User FKs
**File:** `backend/apps/accounts/models.py`

- Mark `User.role`, `User.organization`, `User.unit`, `User.unit_restricted` as deprecated
- Add property methods on User that delegate to active membership:
  - `User.current_organization` → active membership's organization
  - `User.current_role` → active membership's role
  - `User.current_unit` → active membership's unit
  - `User.is_unit_restricted` → active membership's unit_restricted
- Update all existing code to use membership path (propertys as stepping stone)

**Dependencies:** None (this is the foundation)
**Estimated files:** ~8 files modified, ~5 new migrations

---

## Chunk 1: Role Templates & Permission Seeds

**Status:** Implemented and verified.

**Purpose:** Seed all permission codes and role templates into the database so the system is usable.

### 1.1 Organization Type Constants
**File:** `backend/apps/organizations/constants.py`

- Define `OrganizationType` enum: `PLATFORM_OPERATOR`, `FEDERAL_MINISTRY`, `STATE_MINISTRY`, `MEDICAL_FACILITY`, `EMPLOYER`
- Define organization-type → unit-label mapping:
  ```python
  UNIT_LABELS = {
      'federal_ministry': {'plural': 'Departments & Directorates', 'singular': 'Department'},
      'state_ministry': {'plural': 'Units & Offices', 'singular': 'Unit'},
      'medical_facility': {'plural': 'Departments', 'singular': 'Department'},
      'employer': {'plural': 'Branches', 'singular': 'Branch'},
      'platform_operator': {'plural': 'Teams', 'singular': 'Team'},
  }
  ```

### 1.2 Define All Permission Codes
**File:** `backend/apps/organizations/permission_codes.py`

- Organization: `organization.view`, `organization.update`, `organization.suspend`
- Unit: `unit.view`, `unit.create`, `unit.update`, `unit.deactivate`, `unit.assign_user`, `unit.view_members`
- User: `user.view`, `user.invite`, `user.update`, `user.suspend`, `user.reactivate`, `user.remove`
- Invite: `invite.view`, `invite.create`, `invite.resend`, `invite.revoke`
- Role: `role.view`, `role.assign`, `role.create_custom`, `role.update_custom`
- Permission: `permission.view`, `permission.override`
- Module-specific: `employer.manage_branch`, `employer.view_compliance`, `facility.manage_department`, `facility.invite_staff`, `certificate.verify`, `certificate.validate`, `inspection.conduct`, `inspection.assign`, `payment.view`, `settlement.view`, `report.export`
- ~35-40 permissions total

### 1.3 Management Command: Seed Roles + Permissions
**File:** `backend/apps/organizations/management/commands/seed_roles_and_permissions.py`

- Creates all `Permission` rows (idempotent: skip if code already exists)
- Creates all `Role` rows per §14 of PRD (idempotent via unique `code`)
  - Federal Ministry (7 roles): Federal Admin, National Food Safety Programme Officer, National M&E Officer, National Policy Officer, National Finance Officer, Federal Viewer, Executive Viewer
  - State Ministry (9 roles): State Admin, Food Safety Directorate Officer, Certificate Verification Officer, Facility Accreditation Officer, Policy and Finance Officer, Inspectorate Coordinator, Inspector, LGA Office Officer, State Viewer
  - Medical Facility (6 roles): Facility Admin, Doctor, Lab Staff, Medical Records Staff, Finance User, Facility Viewer
  - Employer (5 roles): Employer Admin, Compliance Officer, Branch Manager, Finance User, Employer Viewer
  - Platform Operator (7 roles): Super Admin, Platform Admin, Support Agent, Finance Operator, Compliance Operator, Technical Operator, Auditor
  - **Total: ~34 roles**
- Creates `RolePermission` join rows — assign permission codes to each role
- **Runnable via:** `python manage.py seed_roles_and_permissions`

### 1.4 Run Seed Command in Docker Entrypoint
**File:** `backend/docker-entrypoint.sh` or equivalent

- Add `python manage.py seed_roles_and_permissions` after migrations

**Dependencies:** Chunk 0 (models must exist)
**Estimated files:** ~4 files

---

## Chunk 2: Organization & Unit APIs (Refactor)

**Status:** Implemented and verified.

**Purpose:** Update existing org/unit API layer to expose new fields and add missing endpoints.

### 2.1 Update Organization Serializer
**File:** `backend/apps/organizations/serializers.py`

- Add new fields: `parent`, `contact_person_name`, `website`, `created_by`
- Add read-only fields: `children_count`, `membership_count`, `unit_count`
- Add status transitions validation (e.g., cannot go from ARCHIVED → ACTIVE directly)

### 2.2 Update Organization ViewSet
**File:** `backend/apps/organizations/views.py`

- Add `suspend` action — `POST /organizations/{id}/suspend/`
- Add `reactivate` action — `POST /organizations/{id}/reactivate/`
- Scope list view: Super Admin sees all; org admins see only their org
- Add filtering: `?status=`, `?organization_type=`, `?state=`

### 2.3 Update OrganizationUnit Serializer
**File:** `backend/apps/organizations/serializers.py`

- Add new fields: `manager`, `created_by`, `status` (replacing `is_active`)
- Add `parent_name`, `children` (for tree view)
- Add `member_count` computed field

### 2.4 Update OrganizationUnit ViewSet
**File:** `backend/apps/organizations/views.py`

- Add `members` sub-action — `GET /organizations/{org_id}/units/{id}/members/`
- Add `assign_user` action — `POST /organizations/{org_id}/units/{id}/assign-user/`
- Replace `is_active` toggle with `status` transitions: `deactivate`, `reactivate`, `archive`
- Validate unit-type compatibility per org type (e.g., `LGA_OFFICE` only for `STATE_MINISTRY`)
- Nesting depth validation (max 3 levels)

### 2.5 Write OrganizationUnitService
**File:** `backend/apps/organizations/services.py` (extend existing or new)

- `create_unit()` — validates depth, type compatibility, unique name within parent
- `update_unit()` — validates type changes
- `deactivate_unit()` — soft-deletes, flags member users for reassignment
- `get_unit_tree(org)` — returns nested dict for frontend tree component
- `get_unit_label(org_type, unit_type)` — returns human-readable label

### 2.6 Update OrganizationUnit Permissions
**File:** `backend/apps/organizations/permissions.py`

- `CanManageOrganizationUnit` — check user's membership role has `unit.create`/`unit.update` permission
- Unit-scoped filtering: org admins only see units within their organization

**Dependencies:** Chunks 0 + 1 (models + Role/Permission must exist for permission checks)
**Estimated files:** ~5 files modified

---

## Chunk 3: Membership APIs

**Status:** Implemented and verified.

**Purpose:** Build the full CRUD and lifecycle management for `OrganizationMembership`.

### 3.1 Membership Serializers
**File:** `backend/apps/organizations/serializers.py` (or new `serializers_membership.py`)

- `MembershipListSerializer` — compact (user name, email, role name, unit name, status)
- `MembershipDetailSerializer` — full (includes permissions via role, overrides, audit log)
- `CreateMembershipSerializer` — user, role, unit (optional), unit_restricted
- `UpdateMembershipSerializer` — role, unit, unit_restricted
- `ChangeRoleSerializer` — just role
- `ChangeUnitSerializer` — unit, unit_restricted

### 3.2 Membership ViewSet
**File:** `backend/apps/organizations/views_membership.py` (or add to existing views.py)

```
GET    /api/organizations/{org_id}/memberships/
GET    /api/organizations/{org_id}/memberships/{id}/
PATCH  /api/organizations/{org_id}/memberships/{id}/
PATCH  /api/organizations/{org_id}/memberships/{id}/suspend/
PATCH  /api/organizations/{org_id}/memberships/{id}/reactivate/
PATCH  /api/organizations/{org_id}/memberships/{id}/remove/
PATCH  /api/organizations/{org_id}/memberships/{id}/change-role/
PATCH  /api/organizations/{org_id}/memberships/{id}/change-unit/
PATCH  /api/organizations/{org_id}/memberships/{id}/toggle-unit-restriction/
```

### 3.3 MembershipService
**File:** `backend/apps/organizations/services_membership.py`

- `create_membership()` — creates from invite acceptance or direct assignment
- `suspend_membership()` — sets status to SUSPENDED, logs audit
- `reactivate_membership()` — sets status to ACTIVE
- `remove_membership()` — sets status to REMOVED, preserves audit trail
- `change_role()` — updates role, logs before/after
- `change_unit()` — updates unit + unit_restricted, logs
- `get_user_active_membership(user)` — returns active membership or None

### 3.4 Update User Model Properties
**File:** `backend/apps/accounts/models.py`

- Replace deprecated direct FKs with properties:
  ```python
  @property
  def current_membership(self):
      return self.memberships.filter(status='ACTIVE').first()
  @property
  def current_organization(self):
      return self.current_membership.organization if self.current_membership else None
  @property
  def current_role(self):
      return self.current_membership.role if self.current_membership else None
  ```

### 3.5 Update UserViewSet for Membership-Based Access
**File:** `backend/apps/accounts/views.py`

- `GET /api/users/me/` — return user + current membership + effective permissions
- `PATCH /api/users/me/` — profile fields only (name, phone, etc.)
- **Remove or redirect** direct role/org/unit mutations on User — they should now go through membership endpoints

### 3.6 Audit Logging for Membership Changes
**File:** `backend/apps/audit/` (leverage existing audit app)

- Log events: membership created, role changed, unit changed, unit_restricted toggled, suspended, reactivated, removed
- Include before/after snapshots where applicable

**Dependencies:** Chunks 0, 1, 2
**Estimated files:** ~6 files

---

## Chunk 4: Invite Workflow (Refactor)

**Status:** Implemented and verified.

**Purpose:** Update the invite system to wire through `OrganizationMembership` instead of direct `User` FK assignment, and add missing endpoints.

### 4.1 Update Invite Serializer
**File:** `backend/apps/accounts/serializers.py`

- Add `unit_restricted`, `message` to `InviteUserSerializer`
- Add `org_name`, `org_type`, `invited_by_name` to preview serializer

### 4.2 Update Invite ViewSet
**File:** `backend/apps/accounts/views.py`

Existing endpoints to keep + enhance:
- `GET /api/organizations/{org_id}/invites/` — list, filter by status
- `POST /api/organizations/{org_id}/invites/` — create invite

New endpoints to add:
- `GET /api/organizations/{org_id}/invites/{id}/` — detail
- `POST /api/organizations/{org_id}/invites/{id}/resend/`
- `POST /api/organizations/{org_id}/invites/{id}/revoke/`
- `POST /api/invites/{token}/accept/` — creates OrganizationMembership (not direct User FK)
- `POST /api/invites/{token}/decline/` — marks invite declined
- `GET /api/invites/{token}/preview/` — shows org, role, unit details (public, no auth required)

### 4.3 Update InviteService
**File:** `backend/apps/accounts/services.py`

- `create_invite()` — generates unique token, sets 7-day expiry, links to org + role + optional unit
- `resend_invite()` — regenerates token, resets expiry, increments resend count
- `revoke_invite()` — sets status to REVOKED
- `accept_invite()` — validates token, creates `OrganizationMembership` (status=ACTIVE), marks invite ACCEPTED
- `decline_invite()` — marks invite DECLINED
- `expire_stale_invites()` — finds pending invites past expiry, marks EXPIRED

### 4.4 Invite Acceptance UX (Public Page)
**File:** `frontend/src/app/invite/[token]/page.tsx`

- Shows: organization name, org type, role, unit/branch, invited by, expiry date
- If not logged in: redirect to register → then accept
- If logged in: show "Accept" and "Decline" buttons
- On accept: POST to `/api/invites/{token}/accept/`, redirect to role-specific dashboard

### 4.5 Invite Notifications
**File:** `backend/apps/notifications/`

- Send email/SMS when invite is sent (new user or existing user)
- Send reminder when invite is about to expire (future)
- Notify admin when invite is accepted

**Dependencies:** Chunk 3 (Membership model must exist)
**Estimated files:** ~5 backend files, ~2 frontend files

---

## Chunk 5: EffectiveAccessService

**Status:** Implemented and verified.

**Purpose:** The core permission engine. Every access decision flows through this service.

### 5.1 EffectiveAccessService
**File:** `backend/apps/organizations/services_access.py`

```python
class EffectiveAccessService:
    def check(self, user, permission_code, organization=None, resource=None) -> AccessResult:
        """Returns {allowed: bool, reason: str, scope: str, unit_id: UUID, filters: dict}"""
```

**Logic flow:**
1. Resolve user's active membership for the organization
2. If no active membership → deny (unless super admin)
3. Get role's permissions via `RolePermission`
4. Check for `PermissionOverride` (allow/deny) on membership — overrides take precedence
5. Determine scope:
   - If `unit_restricted=True` → scope = `unit`, filter to that unit
   - If role is org-wide → scope = `organization`
   - If role is state-scoped → scope = `state`, filter to state
   - Super Admin / Platform Admin → scope = `global`
6. Return result with structured filter dict for queryset construction

### 5.2 Unit-Scoped Queryset Mixin
**File:** `backend/apps/organizations/query_filters.py`

```python
class UnitScopedQuerySetMixin:
    """Mixin for DRF ViewSets to apply unit/org/branch scope filtering."""

    def get_scoped_queryset(self, base_queryset, scope_field='unit') -> QuerySet:
        """Filters base_queryset based on user's membership scope."""
        result = EffectiveAccessService().check(...)
        if result.scope == 'unit':
            return base_queryset.filter(**{scope_field: result.unit_id})
        elif result.scope == 'organization':
            return base_queryset.filter(organization=membership.organization)
        # ... etc
```

### 5.3 DRF Permission Class
**File:** `backend/apps/organizations/permissions.py`

```python
class HasStakeholderPermission(BasePermission):
    """Checks EffectiveAccessService for a given permission code."""
    permission_code = None  # Set on view

    def has_permission(self, request, view):
        return EffectiveAccessService().check(request.user, self.permission_code).allowed
```

### 5.4 User Endpoints for Effective Access
**File:** `backend/apps/accounts/views.py`

- `GET /api/me/memberships/` — list all user memberships across orgs
- `GET /api/me/effective-permissions/` — flattened list of all effective permission codes
- `POST /api/permissions/check/` — body `{permission_code, organization_id, resource_id?}`, returns `AccessResult`

### 5.5 Update All Existing Viewsets to Use New Permission Class
**Files:** All `views.py` files across apps

- Replace ad-hoc permission checks with `HasStakeholderPermission` class
- Apply `UnitScopedQuerySetMixin` to views that deal with scoped data
- **Affected apps:** `certificates`, `assessments`, `lab_tests`, `vaccinations`, `inspections`, `food_handlers`, `employers`, `facilities`, `reports`, `payments`, `settlements`

**Dependencies:** Chunks 0–3 (models, roles/permissions, membership APIs)
**Estimated files:** ~8 new backend files, updates to ~12 existing view files

---

## Chunk 6: Role & Permission Management APIs + UI

**Status:** Implemented and verified.

**Purpose:** Provide admin interfaces to view and manage roles and permissions.

### 6.1 Role APIs (Backend)
**File:** `backend/apps/organizations/views_roles.py`

```
GET    /api/roles/
POST   /api/roles/                            # Super admin only: create custom role
GET    /api/roles/{id}/
PATCH  /api/roles/{id}/                       # Update name, description, status
GET    /api/roles/{id}/permissions/           # List permissions for a role
POST   /api/roles/{id}/permissions/           # Add permission to role
DELETE /api/roles/{id}/permissions/{perm_id}/ # Remove permission from role
GET    /api/organization-types/{type}/roles/  # Roles filtered by org type
```

### 6.2 Permission APIs (Backend)
**File:** `backend/apps/organizations/views_permissions.py`

```
GET /api/permissions/                         # List all permissions, filterable by module
GET /api/permissions/{id}/                    # Permission detail
```

### 6.3 Role Serializers
**File:** `backend/apps/organizations/serializers_roles.py`

- `RoleListSerializer` — id, name, code, org_type, permission_count, status
- `RoleDetailSerializer` — full + embedded permission list
- `PermissionSerializer` — id, code, name, module, is_sensitive

### 6.4 Roles Page (Frontend)
**File:** `frontend/src/app/app/stakeholders/organizations/[id]/roles/page.tsx`

- Role list table grouped by organization type
- Click to expand → show permission matrix
- System roles: non-editable name, non-deletable
- Custom role create button (Super Admin only)
- Deprecate role action

### 6.5 Permissions Page (Frontend)
**File:** `frontend/src/app/app/admin/permissions/page.tsx`

- Permissions grouped by module (Organization, Unit, User, Role, ...)
- Sensitive permission indicator
- Search/filter by code, module, description

**Dependencies:** Chunks 0, 1, 3
**Estimated files:** ~5 backend files, ~2 frontend files

---

## Chunk 7: Organization Profile & Unit Tree Frontend

**Purpose:** Build the admin UI for managing organization profiles and unit hierarchies.

### 7.1 Organization Profile Page
**File:** `frontend/src/app/app/stakeholders/organizations/[id]/page.tsx`

- Display + edit form: name, type, contact details, address, state/LGA, status, parent org
- `OrganizationStatusBadge` component — color-coded: Active=green, Suspended=red, etc.
- `OrganizationTypeBadge` component
- Actions: Suspend / Reactivate (confirmation modal)
- Audit log timeline at bottom

### 7.2 Unit Tree Page
**File:** `frontend/src/app/app/stakeholders/organizations/[id]/units/page.tsx`

- Recursive unit tree component (`OrganizationUnitTree`)
  - Expand/collapse nodes
  - Drag-and-drop for restructure (future)
- Click node → slide-out detail panel (`OrganizationUnitDetailPanel`)
- Actions per node: Edit, Deactivate, View Members, Assign Users
- "Create Unit" button → `OrganizationUnitForm` modal
  - Name, Unit Type dropdown (filtered by org type), Parent Unit dropdown (within same org), Description, State/LGA, Address, Phone, Email, Manager/Lead user

### 7.3 Reusable Components
**File:** `frontend/src/components/stakeholders/`

Create these reusable components:
- `OrganizationProfileForm`
- `OrganizationStatusBadge`
- `OrganizationTypeBadge`
- `OrganizationUnitTree` — recursive tree rendering
- `OrganizationUnitForm` — create/edit modal
- `OrganizationUnitDetailPanel` — slide-out info panel
- `UnitStatusBadge`
- `UnitMemberTable` — users assigned to this unit
- `UnitSelector` — dropdown for selecting a unit, filtered by org type labeling
- `OrganizationScopeSwitcher` — for users with multi-org access

### 7.4 Label Adaptation
**File:** `frontend/src/lib/stakeholder-labels.ts`

```typescript
const UNIT_LABEL_MAP = {
  federal_ministry: { plural: 'Departments & Directorates', singular: 'Department' },
  state_ministry: { plural: 'Units & Offices', singular: 'Unit' },
  medical_facility: { plural: 'Departments', singular: 'Department' },
  employer: { plural: 'Branches', singular: 'Branch' },
  platform_operator: { plural: 'Teams', singular: 'Team' },
};
// Usage: getUnitLabel(org.organization_type, { plural: true })
```

**Dependencies:** Chunk 2 (org/unit APIs)
**Estimated files:** ~10 frontend files

---

## Chunk 8: Users & Memberships Frontend

**Purpose:** Build the user management interface (invite, list, manage memberships).

### 8.1 Users / Memberships Page
**File:** `frontend/src/app/app/stakeholders/organizations/[id]/users/page.tsx`

- `UserMembershipTable`
  - Columns: Name, Email, Phone, Role, Unit, Unit Restricted (badge), Status (badge), Last Login, Joined Date, Actions
  - Filters: Role dropdown, Unit dropdown, Status dropdown, free-text Search
  - Paginated
- "Invite User" button → `InviteUserModal`

### 8.2 Invite User Modal
**File:** `frontend/src/components/stakeholders/InviteUserModal.tsx`

- Role selector (dropdown filtered by org type)
- Unit selector (optional, dropdown of org units)
- Unit restriction toggle (shown only when unit selected)
- Email input (single + bulk CSV upload for multiple, future)
- Phone input (optional)
- Custom message textarea
- Submit → POST `/api/organizations/{org_id}/invites/`
- Success state with "Copy Invite Link" button

### 8.3 User Detail Drawer
**File:** `frontend/src/components/stakeholders/UserMembershipDetailDrawer.tsx`

- User profile info (name, email, phone, avatar)
- Current membership: role, unit, unit restricted flag, status
- Actions:
  - Edit Role → `RoleSelector` dropdown
  - Change Unit → `UnitSelector` dropdown + restriction toggle
  - `UnitRestrictionToggle` — on/off switch
  - Suspend / Reactivate (confirmation modal)
  - Remove from organization (confirmation modal)
  - Resend Invite (if status=INVITED)
- Activity timeline (audit events for this user)

### 8.4 Invites Page
**File:** `frontend/src/app/app/stakeholders/organizations/[id]/invites/page.tsx`

- Tabs: Pending | Accepted | Expired | Revoked
- Table columns: Email, Role, Unit, Status, Invited By, Sent Date, Expires
- Actions: Resend, Revoke (for pending), Copy link
- `InviteStatusBadge` component

### 8.5 Public Invite Accept Page
**File:** `frontend/src/app/invite/[token]/page.tsx`

- Load invite preview from `GET /api/invites/{token}/preview/`
- Display: org, role, unit, invited by, expiry
- Accept / Decline buttons
- If unauthenticated → redirect to register/login flow, then back to accept
- On accept → create account/membership → redirect to role dashboard

### 8.6 Reusable Components
**File:** `frontend/src/components/stakeholders/`

- `InviteUserModal` — invite creation form
- `InviteStatusBadge` — Pending=yellow, Accepted=green, Expired=gray, Revoked=red
- `UserMembershipTable` — paginated user table
- `UserMembershipDetailDrawer` — slide-out user detail panel
- `RoleSelector` — dropdown
- `UnitSelector` — dropdown with org-type label
- `UnitRestrictionToggle` — switch
- `UserStatusBadge` — Active/Suspended/Removed
- `MembershipStatusBadge` — Active/Suspended/Invited/Removed

**Dependencies:** Chunks 3 + 4 (membership APIs + invite APIs)
**Estimated files:** ~12 frontend files

---

## Chunk 9: Scope Enforcement (Cross-Module Integration)

**Purpose:** Apply `EffectiveAccessService` and unit scoping to every module's data access layer.

### 9.1 Employer Module
**File:** `backend/apps/employers/views.py`

- Branch-scoped querysets via `UnitScopedQuerySetMixin`
- Branch managers with `unit_restricted=True` see only their branch's food handlers, certificates, inspections
- Employer admins see all branches under their organization

### 9.2 Medical Facility Module
**File:** `backend/apps/facilities/views.py`

- Department-scoped querysets (`unit_type` in `CLINICAL_DEPARTMENT`, `LAB_DEPARTMENT`, etc.)
- Lab staff see only lab department's lab tests
- Doctors see assessments assigned to their clinical department
- Records staff see records department's records
- Facility admins see all departments

### 9.3 Inspector Module
**File:** `backend/apps/inspections/views.py`

- Inspector assigned to LGA office → only sees inspections in that LGA
- Inspectorate coordinator sees all inspections in that state
- State admin sees all inspections in state

### 9.4 Reports Module
**File:** `backend/apps/reports/views.py`

- Apply organization + unit + branch + department filters based on user's membership scope
- `UnitScopedQuerySetMixin` for all report queries
- Filter dropdowns pre-populated to user's accessible units

### 9.5 Certificate & Assessment & LabTest & Vaccination Modules
**File:** `backend/apps/certificates/views.py`, `backend/apps/assessments/views.py`, etc.

- Apply scope filtering to all list/retrieve endpoints
- Certificate verification officer sees certificates in their state
- Facility staff sees only their facility's assessments/lab tests/vaccinations

### 9.6 Scope Enforcement Tests
**Files:** `backend/apps/*/tests/test_scope.py`

- Test: Branch manager (unit_restricted) → can't GET /api/food-handlers/?branch=other-branch
- Test: Lab staff → can't see doctor assessments
- Test: State LGA officer → can't see other state's records
- Test: Employer admin → can't see other employer's data

**Dependencies:** Chunk 5 (EffectiveAccessService)
**Estimated files:** ~12 files modified

---

## Chunk 10: Audit Logging & Notifications

**Purpose:** Full audit trail for all stakeholder actions + notification triggers.

### 10.1 Audit Event Definitions
**File:** `backend/apps/audit/events.py`

Define all audit event types:
- `ORG_CREATED`, `ORG_UPDATED`, `ORG_SUSPENDED`, `ORG_REACTIVATED`
- `UNIT_CREATED`, `UNIT_UPDATED`, `UNIT_DEACTIVATED`, `UNIT_MOVED`
- `USER_INVITED`, `INVITE_RESENT`, `INVITE_REVOKED`, `INVITE_ACCEPTED`
- `USER_ROLE_CHANGED`, `USER_UNIT_CHANGED`, `UNIT_RESTRICTION_CHANGED`
- `USER_SUSPENDED`, `USER_REACTIVATED`, `USER_REMOVED`
- `ROLE_CREATED`, `ROLE_UPDATED`, `ROLE_DEPRECATED`
- `PERMISSION_ADDED_TO_ROLE`, `PERMISSION_REMOVED_FROM_ROLE`
- `PERMISSION_OVERRIDE_GRANTED`, `PERMISSION_OVERRIDE_REVOKED`
- `ACCESS_DENIED` (sensitive action blocked)

### 10.2 Audit Logging in Services
**Files:** All service files

- `OrganizationService` — log org create/update/suspend/reactivate
- `OrganizationUnitService` — log unit create/update/deactivate/move
- `MembershipService` — log role change, unit change, restriction toggle, suspend/reactivate/remove
- `InviteService` — log invite sent/resend/revoke/accept
- `RoleService` — log role create/update/deprecate, permission add/remove

### 10.3 Audit Log APIs
**File:** `backend/apps/organizations/views_audit.py`

```
GET /api/organizations/{org_id}/audit-logs/           # Org-scoped logs
GET /api/stakeholders/audit-logs/                     # Global (Super Admin only)
```
- Filterable by: `?action=`, `?actor=`, `?target_user=`, `?date_from=`, `?date_to=`, `?unit=`
- Response includes: actor, action, org, unit, target user, target role, timestamp, IP, user agent, before/after diff

### 10.4 Audit Logs Page (Frontend)
**File:** `frontend/src/app/app/stakeholders/organizations/[id]/audit/page.tsx`

- `StakeholderAuditTimeline` component
- Filter bar: action type, date range, user, unit
- Timeline view with color-coded action types
- Expand each entry for before/after diff

### 10.5 Notification Triggers
**File:** `backend/apps/notifications/`

**Invite notifications:**
- Invite sent → email to recipient
- Invite resent → email to recipient
- Invite revoked → email to recipient (optional)
- Invite about to expire → reminder email (future)
- Invite accepted → notification to inviter

**Admin notifications:**
- User joined organization → notify org admin
- User role changed → notify affected user + org admin
- User suspended/reactivated → notify affected user + org admin
- Permission override granted → notify affected user + org admin

**User notifications:**
- Role changed, unit changed, access suspended, removed from organization

### 10.6 Background Jobs
**File:** `backend/apps/accounts/tasks.py` (Celery tasks)

1. **Invite expiry job** — runs every hour
   - Finds pending invites past `expires_at`
   - Sets status to `EXPIRED`
   - Notifies inviter
2. **Permission override expiry job** — runs every hour
   - Finds overrides past `expires_at`
   - Deletes or marks expired
   - Notifies affected user + admin

**Dependencies:** Chunks 3, 4 (membership + invite services must exist)
**Estimated files:** ~6 backend files, ~1 frontend file

---

## Chunk 11: Role-Based Navigation & Landing Pages

**Purpose:** Generate navigation menus based on role, permissions, and organization type.

### 11.1 NavigationService (Backend)
**File:** `backend/apps/organizations/services_navigation.py`

```python
class NavigationService:
    def generate_nav(self, user, organization) -> list[NavItem]:
        """Returns role-based navigation tree for frontend sidebar."""
```

**Logic:**
1. Resolve user's membership (role + unit + unit_restricted)
2. Look up role's permissions
3. Build nav tree:
   - Everyone gets: Dashboard (scoped to unit/org)
   - Certificate Verification Officer → Certificate Validation Queue, Certificate Registry, Reports, Notifications
   - Facility Accreditation Officer → Facility Applications, Approved Facilities, Re-accreditation, Reports
   - Branch Manager → Branch Dashboard, Food Handlers, Certificates, Vaccination Compliance, Inspections, Reports
   - Lab Staff → Lab Dashboard, Lab Requests, Result Entry, Submitted Results
   - Doctor → Doctor Dashboard, Assigned Assessments, Declaration Review, Physical Exam, Lab Result Review, Vaccination Review, Fitness Decision
   - etc. (per §19 of PRD)

### 11.2 Navigation API Endpoints
**File:** `backend/apps/accounts/views.py`

- `GET /api/me/navigation/` — returns nav JSON for current user's active membership
- Optional query param: `?organization_id=` — switch org context

### 11.3 Frontend Sidebar Integration
**File:** `frontend/src/components/layout/Sidebar.tsx` (or equivalent)

- Fetch nav from `/api/me/navigation/` on login
- Render sidebar menu dynamically
- Unit-scoped users: use org-type-appropriate labels
- Organization swagger for multi-org users

### 11.4 Role-Specific Landing Pages
**Files:**
- `frontend/src/app/app/dashboard/page.tsx` — generic dashboard; redirects based on role
- `frontend/src/app/app/employer/dashboard/page.tsx` — employer/scoped dashboard
- `frontend/src/app/app/facility/dashboard/page.tsx` — facility staff dashboard
- `frontend/src/app/app/state/dashboard/page.tsx` — state ministry dashboard
- `frontend/src/app/app/federal/dashboard/page.tsx` — federal ministry dashboard
- `frontend/src/app/app/admin/dashboard/page.tsx` — platform admin dashboard

### 11.5 Navigation Preview Component (Future)
**File:** `frontend/src/components/stakeholders/RoleBasedNavigationPreview.tsx`

- For admin use: select a role → see what navigation that role would see
- Useful for role configuration review

**Dependencies:** Chunks 5, 8 (EffectiveAccessService for permission-based nav, Users frontend for landing pages)
**Estimated files:** ~2 backend files, ~8 frontend files

---

## Chunk 12: Testing & Hardening

**Purpose:** Comprehensive test coverage, security review, and performance optimization.

### 12.1 Unit Tests: Organization + Unit
**File:** `backend/apps/organizations/tests/test_organizations.py`

- ✅ Create organization
- ✅ Update organization profile (authorized)
- ❌ Update organization profile (unauthorized)
- ✅ Suspend / reactivate organization
- ❌ Suspended org cannot invite users
- ✅ Create unit
- ✅ Nest units up to 3 levels
- ❌ Reject nesting beyond 3 levels
- ✅ Deactivate unit (soft delete)
- ✅ Assign user to unit
- ❌ Assign LGA_OFFICE to EMPLOYER org type (type mismatch)

### 12.2 Unit Tests: Membership
**File:** `backend/apps/organizations/tests/test_memberships.py`

- ✅ Create membership
- ✅ Two users in same org with different roles
- ✅ Suspend membership → user can't access org resources
- ✅ Reactivate membership → access restored
- ✅ Remove membership → still in audit history
- ✅ Change role → new permissions take effect immediately
- ✅ Change unit → old unit data no longer accessible if unit_restricted
- ✅ Toggle unit restriction → scope changes
- ❌ User cannot assign role higher than their own authority
- ❌ User cannot change membership in another org

### 12.3 Unit Tests: Invites
**File:** `backend/apps/accounts/tests/test_invites.py`

- ✅ Create invite with role + unit
- ✅ Accept invite → membership created
- ✅ Accept invite → invite marked ACCEPTED
- ❌ Accept expired invite → rejected
- ❌ Accept revoked invite → rejected
- ✅ Resend invite → new token, expiry reset
- ✅ Revoke invite → cannot accept
- ✅ User registers then accepts invite → membership assigned

### 12.4 Unit Tests: Permissions
**File:** `backend/apps/organizations/tests/test_permissions.py`

- ✅ Role has correct permission set
- ✅ EffectiveAccessService grants access for assigned permission
- ❌ EffectiveAccessService denies access for unassigned permission
- ✅ Permission override `allow` grants access beyond role
- ✅ Permission override `deny` blocks access despite role
- ✅ Expired permission override → no effect

### 12.5 Integration Tests: Scoped Access
**File:** `backend/apps/*/tests/test_scoping.py`

- ✅ Branch manager (unit_restricted) → only sees own branch food handlers
- ❌ Branch manager (unit_restricted) → cannot access other branch via API
- ✅ Facility lab staff → only sees lab department records
- ❌ Facility lab staff → cannot view clinical assessment records
- ✅ State LGA officer → sees only LGA-scoped certificates
- ❌ State LGA officer → cannot view other LGA
- ✅ Federal national officer → sees national scope
- ✅ Reports module respects unit filtering

### 12.6 Security Tests
**File:** `backend/apps/organizations/tests/test_security.py`

- ❌ Direct API call bypassing unit filter → rejected by backend
- ❌ User modifying their own role via API → rejected
- ❌ User escalating to higher role → rejected
- ❌ Accessing suspended org → rejected
- ❌ Accessing another org's data → rejected
- ✅ Medical privacy: org admin cannot see lab results, doctor notes, NIN
- ✅ Invite token is one-time use
- ✅ Invite token cannot be brute-forced (rate limiting)

### 12.7 Performance Optimization
- Add `select_related` / `prefetch_related` to membership + permission query chains
- Cache `EffectiveAccessService` results per request (thread-local)
- Index `OrganizationMembership.status`, `OrganizationMembership.user_id`, `OrganizationMembership.organization_id`
- Add `db_index=True` to `Permission.code`, `Role.code`

### 12.8 API Documentation
- Ensure all new endpoints are annotated with `@extend_schema` for drf-spectacular
- Verify Swagger UI at `/api/docs/` shows all new endpoints

**Dependencies:** All previous chunks
**Estimated files:** ~15 test files, ~3 files modified

---

## Dependency Graph

```
Chunk 0 (Models + Migration)
  ├──→ Chunk 1 (Seed Roles/Permissions)
  │      └──→ Chunk 2 (Org/Unit APIs)
  │             └──→ Chunk 3 (Membership APIs)
  │                    ├──→ Chunk 4 (Invite Workflow)
  │                    │      └──→ Chunk 8 (Users/Memberships Frontend)
  │                    └──→ Chunk 5 (EffectiveAccessService)
  │                           ├──→ Chunk 6 (Role/Permission APIs + UI)
  │                           ├──→ Chunk 7 (Org/Unit Frontend)
  │                           └──→ Chunk 9 (Cross-Module Scope Enforcement)
  │                                  └──→ Chunk 12 (Testing & Hardening)
  └──→ Chunk 10 (Audit + Notifications) [depends on Chunks 3, 4]
  └──→ Chunk 11 (Navigation) [depends on Chunks 5, 8]
```

**Parallelizable pairs:**
- Chunk 6, 7, 10, 11 can all start in parallel once Chunk 5 is stable
- Chunk 8 can run in parallel with Chunks 6, 7

---

## Summary Table

| Chunk | Name | Effort | Backend Files | Frontend Files | Key Risk |
|---|---|---|---|---|---|
| 0 | Foundation Models | Large | ~8 | 0 | Data migration correctness |
| 1 | Role + Permission Seeds | Medium | ~4 | 0 | Low — idempotent seed command |
| 2 | Org/Unit APIs (Refactor) | Medium | ~5 | 0 | Backward compat with existing consumers |
| 3 | Membership APIs | Large | ~6 | 0 | Race conditions on status changes |
| 4 | Invite Workflow (Refactor) | Medium | ~5 | ~2 | Token security, expiry edge cases |
| 5 | EffectiveAccessService | Large | ~8 | 0 | Performance — every request hits this |
| 6 | Role/Permission APIs + UI | Medium | ~5 | ~2 | Custom role scope creep |
| 7 | Org/Unit Frontend | Medium | 0 | ~10 | Tree rendering at scale |
| 8 | Users/Memberships Frontend | Large | 0 | ~12 | Complex forms (invite, role, unit, restriction) |
| 9 | Cross-Module Scope Enforcement | Large | ~12 | 0 | Missing scoping in an endpoint = data leak |
| 10 | Audit + Notifications | Medium | ~6 | ~1 | Audit log volume, notification spam |
| 11 | Role-Based Navigation | Medium | ~2 | ~8 | Nav JSON shape must be flexible |
| 12 | Testing & Hardening | Large | ~15 | 0 | Gaps in scope enforcement tests |
