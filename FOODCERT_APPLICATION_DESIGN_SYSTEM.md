# FoodCert NG — Application-Wide Design System & AI Coding Rules

## 1. Purpose

This document is the **single source of truth for the entire FoodCert NG application**.

It applies to every screen, module, workflow, and user type across the platform, including:

- Public pages
- Authentication
- Food Handler portal
- Employer portal
- Medical Facility portal
- State Ministry portal
- Federal Ministry portal
- Inspector portal
- Platform Admin portal
- Stakeholder Management
- Directory & Registry
- Medical Assessment workflows
- Certificates and QR verification
- Payments, subscriptions, and settlements
- Reports, dashboards, and M&E
- Notifications and messaging
- Policy and settings

FoodCert NG is a:

```txt
Next.js + React + TypeScript + Tailwind CSS
```

application. All implementation must follow this stack.

This file replaces any old design-system guidance that assumed:

```txt
Vanilla JavaScript
Vanilla CSS only
BudgetIQ-specific app.js routing
GSAP-only animation system
Chart.js-only dashboard system
```

Those rules are not valid for FoodCert NG.

---

# 2. Global Product Design Principles

FoodCert NG must feel:

```txt
Government-grade
Trustworthy
Clean
Accessible
Modern
Operational
Data-driven
Privacy-safe
National-scale
```

The application serves different user groups, but the design language must remain consistent across all portals.

The UI should feel like one national platform, not multiple disconnected products.

---

# 3. Application-Wide Stack Rules

## 3.1 Required Stack

Use:

```txt
Next.js
React
TypeScript
Tailwind CSS
```

## 3.2 Preferred Project Structure

```txt
app/
  (auth)/
  public/
  food-handler/
  employer/
  facility/
  state/
  federal/
  inspector/
  admin/

components/
  ui/
  layout/
  navigation/
  data-table/
  forms/
  status/
  modals/
  charts/
  feedback/

features/
  stakeholders/
  directory/
  food-handlers/
  employers/
  facilities/
  assessments/
  certificates/
  payments/
  inspections/
  reports/
  notifications/
  policy/

lib/
  api.ts
  auth.ts
  permissions.ts
  formatters.ts
  constants.ts
  navigation.ts
  validators.ts

hooks/
  use-permissions.ts
  use-current-organization.ts
  use-active-workspace.ts

types/
  common.ts
  api.ts
  auth.ts
```

## 3.3 React and TypeScript Rules

- Use React components for UI.
- Use TypeScript everywhere.
- Avoid `any`.
- Define prop types.
- Define API response types.
- Define status enums/unions.
- Use reusable hooks for API state and permissions.
- Do not manipulate the DOM manually.
- Do not use old vanilla JS page module patterns.
- Do not use `document.createElement` for normal UI.
- Do not implement custom routers outside Next.js.

## 3.4 Tailwind Rules

- Use Tailwind utility classes.
- Use the configured theme tokens.
- Avoid hardcoded random colors.
- Avoid one-off inline styles.
- Use shared UI components instead of rebuilding buttons/cards/tables repeatedly.
- Use `cn()` utility for conditional classes if available.

Example:

```tsx
className={cn(
  "rounded-lg px-4 py-2 text-sm font-medium",
  active ? "bg-brand-600 text-white" : "bg-white text-neutral-700"
)}
```

---

# 4. Color System

## 4.1 Tailwind Theme Tokens

Configure the following in `tailwind.config.ts`.

```ts
const colors = {
  brand: {
    50: "#F0FDF4",
    100: "#DCFCE7",
    200: "#BBF7D0",
    300: "#86EFAC",
    400: "#4ADE80",
    500: "#22C55E",
    600: "#16A34A",
    700: "#15803D",
    800: "#166534",
    900: "#14532D",
  },
  neutral: {
    50: "#F9FAFB",
    100: "#F3F4F6",
    200: "#E5E7EB",
    300: "#D1D5DB",
    400: "#9CA3AF",
    500: "#6B7280",
    600: "#4B5563",
    700: "#374151",
    800: "#1F2937",
    900: "#111827",
  },
  warning: {
    50: "#FFFBEB",
    100: "#FEF3C7",
    500: "#F59E0B",
    700: "#B45309",
  },
  danger: {
    50: "#FEF2F2",
    100: "#FEE2E2",
    500: "#EF4444",
    700: "#B91C1C",
  },
  info: {
    50: "#EFF6FF",
    100: "#DBEAFE",
    500: "#3B82F6",
    700: "#1D4ED8",
  },
};
```

## 4.2 Semantic Usage

| Use | Token |
|---|---|
| Primary CTA | `brand-600` |
| CTA hover | `brand-700` |
| Active nav background | `brand-50` |
| Active nav text | `brand-700` |
| Success / compliant | `brand-100 text-brand-700` |
| Warning / expiring / pending action | `warning-100 text-warning-700` |
| Error / revoked / failed | `danger-100 text-danger-700` |
| Info / submitted / in review | `info-100 text-info-700` |
| Page background | `neutral-50` |
| Card background | `white` |
| Border | `neutral-200` |
| Primary text | `neutral-900` |
| Secondary text | `neutral-500` |
| Disabled text | `neutral-400` |

## 4.3 Color Rules

Do not:

- Use random hex colors inside components.
- Introduce new color families without approval.
- Use color alone to communicate status.
- Use green text on green backgrounds without enough contrast.

Use:

- Text labels with badges.
- Icons plus text for warnings.
- Consistent semantic tones.

---

# 5. Typography

## 5.1 Font

Use the application’s configured font.

Recommended default:

```txt
Inter
```

If the project already has another approved font, keep it consistent application-wide.

## 5.2 Type Scale

| UI Element | Tailwind |
|---|---|
| Page title | `text-2xl font-semibold tracking-tight text-neutral-900` |
| Module title | `text-xl font-semibold text-neutral-900` |
| Section title | `text-lg font-semibold text-neutral-900` |
| Card title | `text-sm font-medium text-neutral-700` |
| KPI value | `text-2xl font-semibold text-neutral-900` |
| Body text | `text-sm text-neutral-700` |
| Metadata | `text-xs text-neutral-500` |
| Table header | `text-xs font-medium uppercase tracking-wide text-neutral-500` |
| Table cell | `text-sm text-neutral-700` |
| Button | `text-sm font-medium` |
| Badge | `text-xs font-medium` |

## 5.3 Text Rules

- Use clear, plain language.
- Use sentence case.
- Keep labels short.
- Avoid unexplained acronyms except where familiar to the user group.
- Use consistent naming across modules.

---

# 6. Layout System

## 6.1 Global App Shell

All authenticated portals should use a consistent shell.

```tsx
<div className="min-h-screen bg-neutral-50">
  <AppSidebar />
  <div className="lg:pl-64">
    <AppTopbar />
    <main className="p-4 lg:p-6">
      <div className="mx-auto w-full max-w-[1600px]">
        {children}
      </div>
    </main>
  </div>
</div>
```

## 6.2 Public Shell

Public routes such as certificate verification should use a simpler shell:

```tsx
<div className="min-h-screen bg-neutral-50">
  <PublicHeader />
  <main className="mx-auto w-full max-w-5xl p-4 lg:p-8">
    {children}
  </main>
</div>
```

## 6.3 Page Spacing

| Use | Class |
|---|---|
| Page wrapper | `space-y-6` |
| Card grid | `grid gap-4` |
| Section | `space-y-4` |
| Form | `space-y-6` |
| Form field group | `space-y-2` |
| Inline controls | `flex items-center gap-2` |
| Table toolbar | `flex flex-col gap-3 md:flex-row md:items-center md:justify-between` |

## 6.4 Responsive Rules

- Use Tailwind default breakpoints.
- Mobile first.
- Sidebar becomes drawer on mobile.
- Tables scroll horizontally on mobile.
- Filter bars stack vertically on mobile.
- Cards stack into one column on small screens.
- Detail drawers become full-screen on mobile.

---

# 7. Core UI Components

These components should be shared across the whole application.

## 7.1 PageHeader

Use on all module pages.

```tsx
type PageHeaderProps = {
  title: string;
  description?: string;
  badge?: React.ReactNode;
  actions?: React.ReactNode;
};

export function PageHeader({ title, description, badge, actions }: PageHeaderProps) {
  return (
    <div className="flex flex-col gap-4 border-b border-neutral-200 pb-4 md:flex-row md:items-center md:justify-between">
      <div>
        <div className="flex flex-wrap items-center gap-2">
          <h1 className="text-2xl font-semibold tracking-tight text-neutral-900">{title}</h1>
          {badge}
        </div>
        {description ? <p className="mt-1 text-sm text-neutral-500">{description}</p> : null}
      </div>
      {actions ? <div className="flex flex-wrap items-center gap-2">{actions}</div> : null}
    </div>
  );
}
```

## 7.2 Card

```tsx
<div className="rounded-xl border border-neutral-200 bg-white p-4 shadow-sm">
  {children}
</div>
```

## 7.3 StatCard

```tsx
type StatCardProps = {
  title: string;
  value: string | number;
  description?: string;
  icon?: React.ReactNode;
};

export function StatCard({ title, value, description, icon }: StatCardProps) {
  return (
    <div className="rounded-xl border border-neutral-200 bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-neutral-600">{title}</p>
        {icon}
      </div>
      <p className="mt-3 text-2xl font-semibold text-neutral-900">{value}</p>
      {description ? <p className="mt-1 text-xs text-neutral-500">{description}</p> : null}
    </div>
  );
}
```

## 7.4 StatusBadge

Use this for all statuses.

```tsx
type StatusTone = "success" | "warning" | "danger" | "info" | "neutral";

const statusToneClass: Record<StatusTone, string> = {
  success: "bg-brand-100 text-brand-700",
  warning: "bg-warning-100 text-warning-700",
  danger: "bg-danger-100 text-danger-700",
  info: "bg-info-100 text-info-700",
  neutral: "bg-neutral-100 text-neutral-600",
};

export function StatusBadge({ label, tone }: { label: string; tone: StatusTone }) {
  return (
    <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ${statusToneClass[tone]}`}>
      {label}
    </span>
  );
}
```

## 7.5 DataTable

All data-heavy modules should use a consistent table pattern.

```tsx
<div className="overflow-hidden rounded-xl border border-neutral-200 bg-white">
  <table className="w-full text-left text-sm">
    <thead className="bg-neutral-50 text-xs uppercase tracking-wide text-neutral-500">
      <tr>
        <th className="px-4 py-3 font-medium">Name</th>
        <th className="px-4 py-3 font-medium">Status</th>
        <th className="px-4 py-3 font-medium">Actions</th>
      </tr>
    </thead>
    <tbody className="divide-y divide-neutral-200">
      {rows}
    </tbody>
  </table>
</div>
```

## 7.6 FilterBar

```tsx
<div className="flex flex-col gap-3 rounded-xl border border-neutral-200 bg-white p-4 md:flex-row md:items-center md:justify-between">
  <div className="flex flex-1 items-center gap-2">
    <Input placeholder="Search..." />
  </div>
  <div className="flex flex-wrap items-center gap-2">
    <Button variant="outline">Filters</Button>
    <Button variant="outline">Export</Button>
  </div>
</div>
```

## 7.7 Tabs

Use tabs for sub-sections inside modules.

```tsx
<button
  className={
    active
      ? "border-b-2 border-brand-600 px-3 py-3 text-sm font-medium text-brand-700"
      : "border-b-2 border-transparent px-3 py-3 text-sm font-medium text-neutral-500 hover:text-neutral-800"
  }
>
  {label}
</button>
```

## 7.8 EmptyState

```tsx
<div className="rounded-xl border border-dashed border-neutral-300 bg-white p-8 text-center">
  <h3 className="text-sm font-medium text-neutral-900">No records found</h3>
  <p className="mt-1 text-sm text-neutral-500">Try adjusting your filters or search term.</p>
</div>
```

## 7.9 LoadingState

Use skeleton loaders for tables, cards, and detail pages.

```tsx
<div className="animate-pulse rounded-xl border border-neutral-200 bg-white p-4">
  <div className="h-4 w-1/3 rounded bg-neutral-200" />
  <div className="mt-4 h-8 w-1/2 rounded bg-neutral-200" />
</div>
```

---

# 8. Application Navigation

## 8.1 Navigation Principles

Navigation must be:

- Role-aware
- Organization-aware
- Permission-aware
- Consistent across portals
- Not duplicated per user manually

## 8.2 Workspace-Specific Navigation

### Food Handler Portal

```txt
Dashboard
My Assessment
Appointments
My Certificate
Vaccinations
Payments
Notifications
Profile
```

### Employer Portal

```txt
Dashboard
Stakeholder Management
Food Handlers
Directory
Certificates
Vaccination Compliance
Illness Reports
Inspections
Billing
Reports
Settings
```

### Medical Facility Portal

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

### State Ministry Portal

```txt
Dashboard
Stakeholder Management
Facilities
Directory
Accreditation
Certificate Validation
Certificate Registry
Inspections
Reports
Revenue
Settings
```

### Federal Ministry Portal

```txt
Dashboard
Stakeholder Management
States
Directory
National Registry
Policy
M&E
Reports
Data Quality
Settings
```

### Inspector Portal

```txt
Dashboard
Assigned Inspections
Certificate Verification
Directory
Notices
Reports
Profile
```

### Platform Admin Portal

```txt
Dashboard
Organizations
Stakeholder Management
Directory
Users
Roles & Permissions
System Settings
Audit Logs
Reports
```

## 8.3 Permission-Based Navigation

Navigation items should be generated from config.

```ts
export const stateMinistryNav = [
  { label: "Dashboard", href: "/state/dashboard", permission: "dashboard.view" },
  { label: "Stakeholder Management", href: "/state/stakeholder-management", permission: "stakeholder.view" },
  { label: "Facilities", href: "/state/facilities", permission: "facility.view" },
  { label: "Directory", href: "/state/directory", permission: "directory.view" },
  { label: "Certificate Validation", href: "/state/certificate-validation", permission: "certificate.validate" },
];
```

UI can hide unauthorized links, but the backend must still enforce permissions.

---

# 9. Stakeholder Management Design Pattern

## 9.1 One Parent Module

Stakeholder-related administration must be grouped under:

```txt
Stakeholder Management
```

Do not show these as separate top-level modules:

```txt
Users
Invites
Units & Offices
Branches
Departments
Staff
```

They must be tabs inside Stakeholder Management.

## 9.2 Stakeholder Management Tabs

Base tabs:

```txt
Overview
Stakeholders
Roles & Permissions
Units / Offices / Departments / Branches
Invites
Audit Logs
```

## 9.3 Organization-Specific Labels

| Organization Type | Stakeholder Label | Unit Label | Invite Button |
|---|---|---|---|
| Federal Ministry | Federal Users | Departments / Directorates | Invite Federal User |
| State Ministry | Officers | Units & Offices | Invite Officer |
| Medical Facility | Staff | Departments | Invite Staff |
| Employer | Team Members | Branches / Outlets | Invite Team Member |
| Platform Operator | Platform Users | Teams / Units | Invite Platform User |

## 9.4 Stakeholder Layout

```tsx
export function StakeholderManagementPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Stakeholder Management"
        description="Manage users, roles, units, offices, branches, departments and invitations for this organization."
        badge={<OrganizationContextBadge />}
        actions={<Button>Invite Officer</Button>}
      />

      <StakeholderTabs />

      <section className="space-y-4">
        {/* active tab content */}
      </section>
    </div>
  );
}
```

## 9.5 Overview Tab

Cards:

- Total users
- Active users
- Pending invites
- Suspended users
- Total units/offices/departments/branches
- Roles in use
- Users without unit assignment
- Recent activity

## 9.6 Stakeholders Tab

Columns:

- Name
- Email
- Phone
- Role
- Unit / Department / Branch / Office
- Unit restricted
- Status
- Last login
- Actions

## 9.7 Units Tab

Columns:

- Name
- Type
- Parent
- State
- LGA
- Manager
- Members
- Status
- Actions

## 9.8 Invites Tab

Columns:

- Recipient
- Role
- Unit / Department / Branch / Office
- Unit restricted
- Invited by
- Status
- Expires at
- Actions

## 9.9 Roles & Permissions Tab

Columns:

- Role name
- Description
- Organization type
- Users assigned
- Permissions count
- Status
- Actions

## 9.10 Audit Logs Tab

Columns:

- Date
- Actor
- Action
- Target
- Details
- IP address
- Actions

---

# 10. Directory & Registry Design Pattern

## 10.1 One Parent Module

Directory should be one shared module with separate views.

```txt
Directory & Registry
├── Food Handlers
├── Employers / Food Businesses
├── Branches / Outlets
├── Certificates
└── Global Search
```

## 10.2 Directory Pages

Every directory page should include:

- PageHeader
- FilterBar
- DataTable
- StatusBadge
- Pagination
- Export button, permission-based
- Saved views, future

## 10.3 Directory Privacy

Directory tables must not expose:

- Lab results
- Diagnosis
- Doctor notes
- Health declaration answers
- Full NIN
- Treatment notes

Sensitive identifiers should be masked by default.

---

# 11. Module-Specific UI Standards

## 11.1 Food Handler Portal

Must be simple and guided.

Use:

- Stepper for assessment progress
- Clear next action cards
- Certificate status card
- Appointment card
- Payment status card

Avoid:

- Complex administrative tables
- Regulatory jargon

## 11.2 Employer Portal

Must focus on compliance management.

Use:

- Branch filters
- Food handler compliance table
- Certificate expiry cards
- Vaccination due cards
- Inspection notices
- Billing status cards

## 11.3 Medical Facility Portal

Must focus on operational queues.

Use:

- Appointment queue
- Assessment queue
- Lab request queue
- Doctor task queue
- Settlement summary
- Accreditation status card

## 11.4 State Ministry Portal

Must focus on regulatory operations.

Use:

- State dashboard
- Certificate validation queue
- Facility accreditation queue
- Inspection dashboard
- Directory and registry tables
- Revenue and settlement summaries

## 11.5 Federal Ministry Portal

Must focus on national oversight.

Use:

- National dashboard
- State comparison tables
- National registry summaries
- M&E indicators
- Data quality alerts
- Policy configuration panels

## 11.6 Inspector Portal

Must be mobile-friendly.

Use:

- Large scan button
- Assigned inspection cards
- Checklist forms
- Certificate verification result cards
- Evidence upload
- Notice generation flow

---

# 12. Forms

## 12.1 Form Layout

```tsx
<form className="space-y-6">
  <div className="grid gap-4 md:grid-cols-2">
    {/* fields */}
  </div>
</form>
```

## 12.2 Input Classes

```txt
h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm text-neutral-900 placeholder:text-neutral-400 focus:border-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-100
```

## 12.3 Required Fields

```tsx
<span className="text-danger-500">*</span>
```

## 12.4 Help Text

```tsx
<p className="mt-1 text-xs text-neutral-500">This information will be used for certificate verification.</p>
```

## 12.5 Error Text

```tsx
<p className="mt-1 text-xs text-danger-700">This field is required.</p>
```

## 12.6 Long Forms

For long workflows use:

- Sections
- Stepper
- Save draft
- Review page
- Confirmation modal
- Progress indicator

Applicable to:

- Medical assessment
- Facility accreditation
- Dynamic assessment forms
- Inspection checklist
- Employer registration
- State policy configuration

---

# 13. Modal, Drawer, and Detail Views

## 13.1 Modal

Use modals for:

- Invite user
- Create branch
- Create department
- Confirm destructive action
- Submit clarification
- Confirm payment action

Classes:

```txt
rounded-2xl bg-white p-6 shadow-md
```

## 13.2 Drawer

Use drawers for:

- User details
- Employer details
- Food handler details
- Certificate details
- Inspection details
- Payment details
- Audit details

Drawers should be right-aligned on desktop and full-screen on mobile.

## 13.3 Detail Pages

Use detail pages for complex records:

- Food handler profile
- Employer profile
- Facility profile
- Assessment record
- Certificate record
- Inspection case
- State report

---

# 14. Status System

Use the shared `StatusBadge`.

## 14.1 Certificate Status

| Status | Tone |
|---|---|
| Active | success |
| Expiring Soon | warning |
| Expired | warning |
| Suspended | danger |
| Revoked | danger |
| Replaced | neutral |
| Pending Validation | info |

## 14.2 Assessment Status

| Status | Tone |
|---|---|
| Draft | neutral |
| Awaiting Payment | warning |
| Payment Confirmed | success |
| Declaration Pending | warning |
| Lab Pending | warning |
| Doctor Decision Pending | info |
| Fit | success |
| Temporarily Not Fit | warning |
| Not Fit | danger |
| Submitted to State | info |
| Certificate Issued | success |

## 14.3 Facility Accreditation Status

| Status | Tone |
|---|---|
| Draft | neutral |
| Submitted | info |
| Under Review | info |
| More Information Required | warning |
| Approved | success |
| Rejected | danger |
| Suspended | danger |
| Expired | warning |
| Re-accreditation Due | warning |

## 14.4 Payment Status

| Status | Tone |
|---|---|
| Pending | warning |
| Successful | success |
| Failed | danger |
| Refunded | neutral |
| Reversed | neutral |

## 14.5 Subscription Status

| Status | Tone |
|---|---|
| Active | success |
| Trial | info |
| Past Due | warning |
| Expired | warning |
| Suspended | danger |
| Cancelled | neutral |

## 14.6 Inspection Status

| Status | Tone |
|---|---|
| Assigned | info |
| In Progress | info |
| Submitted | info |
| Notice Issued | warning |
| Corrective Action Pending | warning |
| Escalated | danger |
| Closed | success |

---

# 15. Privacy and Sensitive Data UI Rules

FoodCert NG handles sensitive identity, health, and payment data.

## 15.1 Sensitive Medical Data

Never expose to unauthorized users:

- Lab results
- Diagnosis
- Doctor notes
- Health declaration answers
- Treatment notes
- Medical reports
- Full NIN

## 15.2 Employer and Inspector Views

Employer and inspector views must show only:

- Operational fitness status
- Certificate status
- Vaccination compliance status
- Return-to-work status
- Expiry date
- Public/inspector-safe certificate details

## 15.3 Sensitive Field Masking

Mask sensitive identifiers by default.

Example:

```txt
NIN: 1234******89
```

If reveal is allowed:

- Require permission.
- Require reason.
- Log the action.
- Show temporary reveal.

## 15.4 Privacy Notices

Add small privacy notices on sensitive screens.

Example:

```txt
Medical details are restricted. This view only shows operational compliance information.
```

---

# 16. Icons

Use the project’s icon library.

Recommended:

```txt
lucide-react
```

Rules:

- Icons should usually be `h-4 w-4` or `h-5 w-5`.
- Use `text-neutral-500` by default.
- Use `text-brand-600` for positive/active states.
- Use `text-danger-500` for destructive states.
- Icons must have accessible labels where necessary.

---

# 17. Charts and Dashboards

Use the project’s approved chart library.

Recommended:

```txt
recharts
```

If another charting library already exists, use the existing one.

Dashboard rules:

- KPI cards at top.
- Filters near the page header.
- Charts in cards.
- Tables below charts.
- Use simple chart types.
- Do not overuse colors.
- Use green as primary series, amber as warning, red as negative.

---

# 18. Motion

Use minimal motion.

Recommended Tailwind transitions:

```txt
transition-colors
transition-shadow
transition-transform
duration-150
duration-200
```

Allowed:

- Button hover color transitions.
- Card hover shadow for clickable cards.
- Drawer/modal enter transitions if provided by component library.
- Loading skeleton pulse.

Avoid:

- Heavy GSAP animations.
- Infinite decorative animations.
- Complex page transitions.
- Motion that distracts from workflows.

Respect reduced motion.

---

# 19. Accessibility

Required:

- All buttons must be real buttons.
- Links must be real links.
- Inputs must have labels.
- Dialogs must trap focus.
- Dropdowns must support keyboard navigation.
- Tables must have headers.
- Status badges must include text.
- Forms must show validation messages.
- Do not remove focus rings without replacement.
- Maintain color contrast.
- Use `aria-label` for icon-only buttons.
- Use `aria-describedby` for help/error text where appropriate.

Focus style:

```txt
focus:outline-none focus:ring-2 focus:ring-brand-100 focus:border-brand-600
```

---

# 20. API and Data Fetching Rules

## 20.1 API Client

Use a shared API client.

```txt
lib/api.ts
```

Do not call raw `fetch` inside deeply nested UI components.

## 20.2 Feature Services

Keep API calls in feature service files.

Example:

```txt
features/stakeholders/services/stakeholder-service.ts
features/directory/services/directory-service.ts
features/certificates/services/certificate-service.ts
```

## 20.3 Loading and Error States

Every API-driven page must handle:

- Loading
- Empty
- Error
- Success
- Permission denied

## 20.4 Types

Every response should have a TypeScript type.

---

# 21. Permissions and Scoping

## 21.1 Backend Is Source of Truth

The frontend may hide actions, but backend must enforce all permissions.

## 21.2 UI Permission Rules

- Hide buttons the user cannot use.
- Hide tabs the user cannot view.
- Hide exports unless permitted.
- Do not render sensitive fields without permission.
- Do not rely on frontend-only permission checks.

## 21.3 Scope Rules

Always respect:

- Organization scope
- Unit scope
- Branch scope
- State scope
- LGA scope
- Facility scope
- Own-record scope

---

# 22. Naming Conventions

## 22.1 Component Names

Use PascalCase:

```txt
StakeholderManagementPage
StakeholderTabs
StakeholderTable
InviteUserModal
UnitStructureTable
StatusBadge
DataTable
PageHeader
```

## 22.2 Hook Names

Use camelCase and start with `use`:

```txt
useStakeholderContext
useOrganizationMembers
useDirectoryFilters
usePermissions
useCurrentOrganization
```

## 22.3 Type Names

Use PascalCase:

```txt
OrganizationType
StakeholderContextResponse
DirectoryFilterState
CertificateStatus
```

---

# 23. Forbidden Patterns

Do not:

- Use vanilla JS DOM-building patterns.
- Use old BudgetIQ `app.js` page modules.
- Use old GSAP animation rules from BudgetIQ.
- Use old Chart.js defaults from BudgetIQ.
- Use `var(--green-core)` from old CSS unless mapped into Tailwind tokens.
- Create separate top-level modules for Users, Invites, Units, Branches, Departments, and Staff.
- Expose medical details in employer, inspector, public, or unauthorized views.
- Hardcode role labels without organization-type mapping.
- Bypass backend permissions.
- Use `any` unnecessarily.
- Add packages without checking existing project setup.
- Leave `console.log` in committed code.
- Create one-off components when shared components exist.

---

# 24. Verification Before Marking Done

Before reporting completion, verify:

```bash
npm run lint
npm run typecheck
npm run build
```

Use the project’s actual scripts if different.

Also verify:

- App renders without console errors.
- Navigation is role-aware.
- Stakeholder Management is one parent module.
- Directory & Registry is one parent module.
- Tables are responsive.
- Forms show validation.
- Sensitive fields are hidden.
- Permission-restricted buttons/tabs are hidden.
- Backend still enforces permissions.
- Mobile layouts work.
- Empty, loading, error, and permission-denied states work.

---

# 25. Codex Implementation Notes

When implementing FoodCert NG:

1. Confirm the project’s actual folder structure first.
2. Check installed packages before adding any dependency.
3. Reuse existing UI components.
4. Use Tailwind-compatible patterns.
5. Keep design consistent across all portals.
6. Keep Stakeholder Management consolidated.
7. Keep Directory & Registry consolidated.
8. Use role-safe views.
9. Preserve medical privacy.
10. Use TypeScript types for API responses and props.
11. Run lint, typecheck, and build before marking done.

---

# 26. Application-Wide Codex Prompt

```txt
Use this file as the application-wide design system and coding rules for FoodCert NG.

FoodCert NG is a Next.js + React + TypeScript + Tailwind CSS application. Ignore any old BudgetIQ-specific vanilla JS, vanilla CSS, Chart.js, GSAP, or app.js page-module instructions.

Apply this design system across the whole application: public pages, authentication, food handler portal, employer portal, medical facility portal, state ministry portal, federal ministry portal, inspector portal, admin portal, stakeholder management, directory, assessments, certificates, payments, inspections, reports, notifications, and settings.

Use reusable React components, Tailwind theme tokens, TypeScript types, permission-aware navigation, responsive layouts, accessible forms, privacy-safe serializers/views, and consistent status badges.

Stakeholder Management must be one parent module with tabs for Overview, Stakeholders, Roles & Permissions, Units/Offices/Branches/Departments, Invites, and Audit Logs.

Directory & Registry must be one parent module with views for Food Handlers, Employers/Food Businesses, Branches/Outlets, Certificates, and Global Search.

Do not expose medical data in employer, inspector, public, or unauthorized views. Backend permissions remain the source of truth.
```
