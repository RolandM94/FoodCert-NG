# Codex Prompt: Role Permissions Modal for Stakeholder Management

## Objective

Update the **Stakeholder Management → Roles & Permissions** UI so that permission selection and editing happens inside a centered popup modal, similar to the reference screenshot.

FoodCert NG is a **Next.js + React + TypeScript + Tailwind CSS** application. This implementation must follow the application-wide FoodCert NG design system.

---

## Context

Stakeholder Management is a parent module with tabs for:

```txt
Overview
Stakeholders
Roles & Permissions
Units / Offices / Branches / Departments
Invites
Audit Logs
```

The **Roles & Permissions** tab should allow authorized organization admins to create and edit roles. Permission selection should not happen on a separate page. It should happen inside a modal.

---

## Expected User Flow

1. User opens **Stakeholder Management**.
2. User clicks the **Roles & Permissions** tab.
3. User sees a roles table.
4. User clicks **Create Role** or selects **Edit Role** from a role row action menu.
5. A centered modal opens over a dimmed backdrop.
6. User enters or edits the role name and optional description.
7. User selects permissions grouped by module/category.
8. User clicks **Save**.
9. Role is created or updated.
10. Modal closes after successful save.
11. Roles table refreshes.

---

## Roles Table Requirements

The Roles & Permissions tab should display a roles table with columns:

```txt
No.
Role Name
Description
Users Assigned
Permissions
Status
Actions
```

The **Permissions** column should show count format:

```txt
11 / 34
```

Where:

- `11` = selected permissions for that role
- `34` = total available permissions for that organization type

Actions menu should include:

```txt
Edit Role
View Permissions
Duplicate Role, optional/future
Deactivate Role, if permitted
```

---

## Modal Requirements

### Modal Trigger

Open the modal when the user clicks:

```txt
Create Role
Edit Role
```

### Modal Title

Use:

```txt
Create Role
```

for new roles.

Use:

```txt
Edit Role
```

for existing roles.

### Modal Fields

The modal should contain:

1. Role name input
2. Optional role description textarea
3. Permission groups by module/category
4. Selected permissions count
5. Save button
6. Cancel button
7. Close X button

---

## Modal Layout

The modal should be:

- Centered on screen
- Displayed over a dimmed backdrop
- White card
- Rounded corners
- Scroll-safe
- Responsive
- Keyboard accessible

Recommended Tailwind classes:

### Backdrop

```tsx
fixed inset-0 z-40 bg-black/40
```

### Modal Container

```tsx
fixed inset-0 z-50 flex items-center justify-center p-4
```

### Modal Card

```tsx
w-full max-w-2xl overflow-hidden rounded-2xl bg-white shadow-md
```

### Modal Header

```tsx
flex items-center justify-between border-b border-neutral-200 px-6 py-4
```

### Modal Body

```tsx
max-h-[65vh] overflow-y-auto px-6 py-4
```

### Modal Footer

```tsx
flex items-center justify-end gap-2 border-t border-neutral-200 px-6 py-4
```

---

## Permission Selection Design

Permissions should be grouped by module/category.

Example permission groups:

```txt
Stakeholder Management
Users
Invites
Units & Offices / Branches / Departments
Roles & Permissions
Employers
Food Handlers
Medical Facilities
Assessments
Certificates
Inspections
Payments
Reports
Settings
Audit Logs
```

Each group should show:

- Group title
- List of permission items
- Permission checkboxes/chips
- Optional description or tooltip for sensitive permissions

Each permission item should show:

```txt
Permission label
Optional info icon for sensitive permissions
Checkbox
Selected state
```

Selected permissions should use a green accent.

Recommended selected style:

```tsx
border-brand-200 bg-brand-50 text-brand-700
```

Unselected style:

```tsx
border-neutral-200 bg-white text-neutral-700 hover:bg-neutral-50
```

---

## Example Permission Labels

### Stakeholder Management

```txt
View stakeholder management
View users
Invite users
Update users
Suspend users
View roles
Assign roles
View units
Create units
Update units
View invites
Resend invites
Revoke invites
View audit logs
```

### Certificates

```txt
View certificate registry
Verify certificate
Validate certificate issuance
Suspend certificate
Revoke certificate
```

### Inspections

```txt
View inspections
Assign inspections
Conduct inspections
Submit inspection report
Issue notice
Review corrective action
```

### Payments

```txt
View payments
View subscriptions
View settlements
Export finance reports
```

---

## Required Behavior

### Create Role

When creating a role:

- Role name should be empty.
- Description should be empty.
- No permissions selected by default unless the product already defines default templates.
- Save should create role and selected permissions.

### Edit Role

When editing a role:

- Role name should be prefilled.
- Description should be prefilled if available.
- Existing permissions should be preselected.
- Save should update role and selected permissions.

### Permission Count

Show live selected permission count in the modal.

Example:

```txt
11 permissions selected
```

or:

```txt
11 / 34 permissions selected
```

The count should update immediately when permissions are selected or deselected.

---

## Validation Rules

- Role name is required.
- Role name should be trimmed before submit.
- Save button should be disabled if role name is empty.
- Save button should be disabled while submitting.
- Show validation message under role name if empty.
- Do not close modal if save fails.
- Show error message if API call fails.
- Show loading state while permissions are loading.
- Show empty state if no permissions are available.

---

## API Expectations

Use existing Stakeholder Management APIs where present. Do not create a separate roles module.

Suggested API flow:

```txt
GET    /api/roles?organization_type={organizationType}
GET    /api/permissions
GET    /api/roles/:id/permissions
POST   /api/roles
PATCH  /api/roles/:id
POST   /api/roles/:id/permissions
PATCH  /api/roles/:id/permissions
```

If the actual backend endpoints differ, create service functions that can be easily mapped to existing endpoints.

Create or update service file:

```txt
features/stakeholders/services/role-service.ts
```

Suggested service functions:

```ts
getRoles(organizationType: OrganizationType)
getPermissions(organizationType: OrganizationType)
getRolePermissions(roleId: string)
createRole(payload: CreateRolePayload)
updateRole(roleId: string, payload: UpdateRolePayload)
saveRolePermissions(roleId: string, permissionIds: string[])
```

---

## Required Components

Create or update the following components.

### 1. RolesPermissionsTab

Responsibilities:

- Display roles table
- Fetch roles
- Show Create Role button
- Open RolePermissionModal in create mode
- Open RolePermissionModal in edit mode
- Refresh roles after save

Suggested path:

```txt
features/stakeholders/components/roles-permissions-tab.tsx
```

### 2. RolePermissionModal

Responsibilities:

- Render centered modal
- Load available permissions
- Load role permissions for edit mode
- Manage selected permissions
- Submit role create/update
- Save permissions

Suggested path:

```txt
features/stakeholders/components/role-permission-modal.tsx
```

Props:

```ts
type RolePermissionModalProps = {
  open: boolean;
  mode: "create" | "edit";
  role?: Role;
  organizationType: OrganizationType;
  onClose: () => void;
  onSaved: () => void;
};
```

### 3. PermissionGroup

Responsibilities:

- Render permission group heading
- Render permission items
- Support selected state
- Support toggling permissions

Suggested path:

```txt
features/stakeholders/components/permission-group.tsx
```

### 4. PermissionCheckbox

Responsibilities:

- Render individual permission chip/checkbox
- Show selected state
- Show sensitive info icon/tooltip if needed

Suggested path:

```txt
features/stakeholders/components/permission-checkbox.tsx
```

### 5. PermissionCountBadge

Responsibilities:

- Show selected permission count

Suggested path:

```txt
features/stakeholders/components/permission-count-badge.tsx
```

---

## TypeScript Types

Create or update:

```txt
features/stakeholders/types.ts
```

Types:

```ts
export type OrganizationType =
  | "federal_ministry"
  | "state_ministry"
  | "medical_facility"
  | "employer"
  | "platform_operator";

export type Permission = {
  id: string;
  code: string;
  name: string;
  module: string;
  description?: string;
  isSensitive?: boolean;
};

export type Role = {
  id: string;
  name: string;
  code?: string;
  description?: string;
  organizationType: OrganizationType;
  permissionsCount: number;
  totalPermissions?: number;
  status: "active" | "inactive" | "deprecated";
};

export type PermissionGroup = {
  module: string;
  label: string;
  permissions: Permission[];
};

export type CreateRolePayload = {
  name: string;
  description?: string;
  organizationType: OrganizationType;
  permissionIds: string[];
};

export type UpdateRolePayload = {
  name: string;
  description?: string;
  permissionIds: string[];
};
```

---

## Access Control

The UI should respect permissions.

Required permission checks:

```txt
stakeholder.role.view
stakeholder.role.create
stakeholder.role.update
stakeholder.permission.assign
```

Rules:

- Only users with `stakeholder.role.view` can see the Roles & Permissions tab.
- Only users with `stakeholder.role.create` can see Create Role.
- Only users with `stakeholder.role.update` can edit roles.
- Only users with `stakeholder.permission.assign` can change permissions.
- Unauthorized actions must be hidden in the UI.
- Backend permissions remain the source of truth.

---

## UI Details

### Modal Header

Header should include:

- Icon, optional
- Title
- Close X button

Example:

```txt
Edit Role
```

### Modal Body

Body should include:

```txt
Role name input
Description textarea
Selected permissions count
Permission groups
```

### Modal Footer

Footer should include:

```txt
Cancel
Save
```

Save button should show loading state:

```txt
Saving...
```

---

## Accessibility Requirements

- Modal should trap focus.
- Escape key should close modal unless submitting.
- Close X button must have `aria-label="Close modal"`.
- Permission checkboxes must be keyboard accessible.
- Role name input must have a label.
- Validation errors must be visible and linked to the input.
- Status should not be communicated by color alone.

If the project already uses a dialog component from shadcn/ui or another UI library, use it.

---

## Responsive Requirements

- Modal should fit mobile screens.
- Body should scroll internally.
- Footer should remain visible.
- Permission chips should wrap.
- On small screens, permission groups should stack cleanly.

---

## Do Not Do

Do not:

- Create a separate page for permission selection.
- Create separate role editors for State, Employer, Facility, and Federal users.
- Create a separate backend module for roles.
- Hardcode permissions only in the UI.
- Expose permissions that are not allowed for the active organization type.
- Use `any`.
- Use random hex colors outside the Tailwind design system.
- Bypass backend permission checks.
- Close modal when save fails.
- Scatter permission editing across multiple screens.

---

## Acceptance Criteria

1. Roles & Permissions tab displays roles table.
2. Roles table shows permission count as `selected / total`.
3. Create Role opens a centered modal.
4. Edit Role opens the same modal with prefilled role name, description, and permissions.
5. Permissions are grouped by module/category.
6. Admin can select and deselect permissions.
7. Selected permission count updates live.
8. Role name validation works.
9. Save creates or updates role and assigned permissions.
10. Save button shows loading state while submitting.
11. Modal closes only after successful save.
12. Roles table refreshes after save.
13. Unauthorized users do not see create/edit controls.
14. Modal is responsive.
15. Permission list scrolls internally.
16. UI follows the FoodCert NG Tailwind design system.
17. No medical or unrelated sensitive data is exposed.
18. Implementation uses TypeScript types and avoids `any`.
19. Backend service functions are reusable.
20. Existing Stakeholder Management module structure is preserved.

---

## Suggested Implementation Order

### Step 1: Types and Services

- Add Role, Permission, PermissionGroup types.
- Add role service functions.
- Add permission service functions.

### Step 2: Roles Table

- Update RolesPermissionsTab.
- Add Create Role button.
- Add Edit Role action.
- Show permission count.

### Step 3: Modal Shell

- Create RolePermissionModal.
- Add header, body, footer.
- Add open/close logic.

### Step 4: Permission Groups

- Fetch permissions.
- Group permissions by module.
- Render PermissionGroup and PermissionCheckbox.
- Add selected state.

### Step 5: Create and Edit Behavior

- Implement create role.
- Implement edit role.
- Prefill edit mode.
- Save permissions.

### Step 6: Validation and Error States

- Add required role name validation.
- Add loading, empty, and error states.
- Prevent modal closing on save failure.

### Step 7: Access Control

- Hide unauthorized actions.
- Confirm permission checks.
- Confirm backend enforcement remains intact.

### Step 8: QA

Run:

```bash
npm run lint
npm run typecheck
npm run build
```

Also verify:

- Modal opens and closes correctly.
- Edit mode preloads current permissions.
- Permission count updates.
- Save works.
- Table refreshes.
- Mobile layout works.
