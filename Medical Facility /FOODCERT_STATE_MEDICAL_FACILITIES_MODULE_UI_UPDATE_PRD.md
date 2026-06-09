# PRD Update: State Ministry Medical Facilities Module Consolidation — FoodCert NG

## 1. Document Purpose

This PRD update defines the revised structure for the **State Ministry Medical Facilities Module** in FoodCert NG.

The purpose is to consolidate facility listing, accreditation, re-accreditation, facility monitoring, and facility reporting into one smooth module, without creating unnecessary tabs for statuses such as Pending Review, More Information Required, Approved, Rejected, Suspended, or Expired.

This update should be used by Codex to correct the Medical Facilities module navigation and UX.

---

# 2. Product Decision

The State Ministry should have one parent module:

```txt
Medical Facilities
```

Inside this module, use only four main tabs:

```txt
Medical Facilities
├── Overview
├── Facilities
├── Accreditation
└── Reports
```

Do not create separate tabs for:

```txt
Pending Review
Under Review
More Information Required
Approved Facilities
Rejected
Suspended
Expired
Re-accreditation
```

These are **statuses, filters, or application types**, not standalone tabs.

---

# 3. Why This Update Is Needed

The earlier structure considered too many tabs:

```txt
Medical Facilities
├── Overview
├── All Facilities
├── Accreditation Applications
├── Approved Facilities
├── Pending Review
├── More Information Required
├── Suspended / Expired
├── Re-accreditation
└── Facility Reports
```

This is too fragmented because most of these items are not separate workflows. They are statuses within either:

1. The facility master list, or
2. The accreditation application workflow.

For example:

- Pending Review is an accreditation application status.
- More Information Required is an accreditation application status.
- Approved is an accreditation decision/status.
- Suspended is a facility accreditation status.
- Expired is a facility accreditation status.
- Re-accreditation is an application type, not a separate module.

The smoother product structure is:

```txt
Medical Facilities
├── Overview
├── Facilities
├── Accreditation
└── Reports
```

---

# 4. Core Product Principle

The Medical Facilities module should manage the full facility lifecycle in one place:

```txt
Facility Registration
→ Facility Profile
→ Accreditation Application
→ Review
→ Approval / Rejection / More Information Required
→ Active Accredited Facility
→ Monitoring
→ Suspension / Expiry
→ Re-accreditation Application
→ Renewal Decision
→ Reports
```

The State Ministry should not have to jump between separate modules called “Facilities” and “Accreditation.” Both belong inside the Medical Facilities module.

---

# 5. Recommended State Ministry Navigation

## 5.1 Sidebar / Main Navigation

Use:

```txt
Dashboard
Stakeholder Management
Medical Facilities
Directory
Certificate Validation
Certificate Registry
Inspections
Reports
Revenue
Settings
```

Do not show this as separate top-level modules:

```txt
Facilities
Accreditation
Pending Applications
Approved Facilities
Re-accreditation
```

## 5.2 Medical Facilities Internal Tabs

Inside the Medical Facilities module:

```txt
Overview
Facilities
Accreditation
Reports
```

---

# 6. Tab Definitions

## 6.1 Overview Tab

### Purpose

The Overview tab gives State Ministry users a quick snapshot of facility registration, accreditation, expiry, suspension, and assessment activity.

### Overview Cards

Show KPI cards such as:

```txt
Total Facilities
Accredited Facilities
Pending Applications
Applications Under Review
More Information Required
Rejected Applications
Suspended Facilities
Expired Accreditation
Re-accreditation Due
Assessments Conducted
Certificates Issued from Facilities
```

### Overview Charts / Tables

Suggested widgets:

- Facilities by accreditation status
- Accreditation applications by status
- Facilities by LGA
- Expiring accreditation timeline
- Top facilities by assessment volume
- Suspended / expired facilities list
- Recent accreditation activity

### Overview Actions

Primary actions:

```txt
View Facilities
Review Applications
Export Facility Report
```

---

## 6.2 Facilities Tab

### Purpose

The Facilities tab is the master list of all medical facilities within the state, regardless of accreditation status.

This tab should include:

- Accredited facilities
- Pending accreditation facilities
- Facilities with applications in progress
- Rejected facilities
- Suspended facilities
- Expired facilities
- Inactive facilities
- Facilities due for re-accreditation

### Facility Table Columns

Recommended columns:

```txt
Facility Name
Facility Type
Ownership Type
LGA
Address
Accreditation Status
Accreditation Expiry Date
Re-accreditation Due
Assessments Conducted
Certificates Issued
Facility Status
Actions
```

### Facility Status Filters

Use filter chips at the top of the Facilities table:

```txt
All
Accredited
Pending Accreditation
Suspended
Expired
Inactive
Re-accreditation Due
```

These filters should not be separate tabs.

### Facility Actions

Actions depend on permissions.

Possible actions:

```txt
View Facility
View Accreditation
View Assessments
View Certificates
Suspend Facility
Reactivate Facility
Request Re-accreditation
Export
```

### Facility Detail View

When a State Ministry user clicks a facility, open a detail page or drawer.

The facility detail view should include sections/tabs:

```txt
Profile
Accreditation History
Documents
Departments / Staff
Assessments Conducted
Certificates Issued
Settlements
Performance
Audit Logs
```

### Facility Detail Rules

- Facility detail should show the current accreditation status.
- Accreditation history should include both new accreditation and re-accreditation applications.
- Documents should be linked to the relevant accreditation application.
- Assessments and certificates should be filtered to that facility.
- Settlements should only be visible to users with finance permissions.
- Audit logs should only be visible to authorized users.

---

## 6.3 Accreditation Tab

### Purpose

The Accreditation tab is where the State Ministry handles all facility accreditation applications.

This includes both:

```txt
New Accreditation
Re-accreditation
```

Re-accreditation should **not** be a separate tab. It should be handled as an application type inside the Accreditation tab.

### Accreditation Table Columns

Recommended columns:

```txt
Application Reference
Facility Name
Facility Type
LGA
Application Type
Application Status
Submitted Date
Assigned Reviewer
Last Updated
Accreditation Expiry Date, if re-accreditation
Actions
```

### Application Type Values

```txt
New Accreditation
Re-accreditation
```

### Accreditation Status Values

```txt
Draft
Submitted
Pending Review
Under Review
More Information Required
Approved
Rejected
Withdrawn
```

### Accreditation Filter Chips

Use filters at the top of the Accreditation table:

```txt
All
New Applications
Re-accreditation
Pending Review
Under Review
More Information Required
Approved
Rejected
```

These filters should not become separate tabs.

### Accreditation Actions

Possible actions:

```txt
View Application
Assign Reviewer
Start Review
Request More Information
Approve
Reject
View Documents
View Checklist
View Facility Profile
```

### Accreditation Review Workflow

```txt
Facility submits application
→ Application appears in Accreditation tab
→ State reviewer opens application
→ Reviewer checks profile, checklist, and documents
→ Reviewer approves, rejects, or requests more information
→ Facility responds if more information is requested
→ Reviewer completes decision
→ Facility accreditation status updates
```

### Re-accreditation Workflow

Re-accreditation follows the same review workflow but with:

```txt
application_type = re_accreditation
```

The UI should distinguish re-accreditation using:

- Application Type column
- Filter chip
- Expiry date
- Renewal due status
- Previous accreditation history

Do not implement re-accreditation as a separate top-level tab.

---

## 6.4 Reports Tab

### Purpose

The Reports tab provides facility-related reporting and exports for State Ministry users.

### Report Types

Recommended reports:

```txt
Facility Master List Report
Accreditation Applications Report
Re-accreditation Report
Accredited Facilities Report
Suspended Facilities Report
Expired Facilities Report
Facility Assessment Volume Report
Facility Certificate Issuance Report
Facility Performance Report
LGA Facility Coverage Report
```

### Report Filters

Reports should support:

```txt
Date range
Facility type
Ownership type
LGA
Accreditation status
Application type
Application status
Assessment volume
Certificate issuance count
```

### Export Formats

Support:

```txt
CSV
Excel
PDF
```

### Report Privacy

Reports should respect permissions.

- Finance/settlement details require finance permissions.
- Facility staff details require stakeholder/facility permissions.
- Assessment summaries must not expose private medical records.
- Exports must be audit logged.

---

# 7. Data Model Clarification

This UI update does not require separate new models for each tab.

Use existing or planned models:

```txt
MedicalFacility
FacilityAccreditationApplication
FacilityDocument
FacilityStaffProfile
Organization
OrganizationUnit
MedicalAssessment
Certificate
AuditLog
```

## 7.1 Facility Accreditation Application

The accreditation application should include:

```txt
application_type
status
facility
submitted_at
reviewer
reviewed_at
review_comment
```

Recommended application types:

```txt
new_accreditation
re_accreditation
```

Recommended statuses:

```txt
draft
submitted
pending_review
under_review
more_information_required
approved
rejected
withdrawn
```

## 7.2 Medical Facility Accreditation Status

Facility accreditation status should be separate from application status.

Recommended facility accreditation statuses:

```txt
not_accredited
pending_accreditation
accredited
suspended
expired
re_accreditation_due
inactive
```

## 7.3 Important Rule

Do not confuse:

```txt
Facility Accreditation Status
```

with:

```txt
Application Status
```

Example:

A facility can be:

```txt
facility.accreditation_status = accredited
```

while also having:

```txt
application.application_type = re_accreditation
application.status = pending_review
```

This means the facility is currently accredited but has submitted a renewal application.

---

# 8. Frontend Routes

## 8.1 State Ministry Routes

Use one Medical Facilities parent route.

```txt
/state/medical-facilities
/state/medical-facilities?tab=overview
/state/medical-facilities?tab=facilities
/state/medical-facilities?tab=accreditation
/state/medical-facilities?tab=reports
```

## 8.2 Facility Detail Route

```txt
/state/medical-facilities/[facilityId]
```

Optional section query:

```txt
/state/medical-facilities/[facilityId]?section=profile
/state/medical-facilities/[facilityId]?section=accreditation-history
/state/medical-facilities/[facilityId]?section=documents
/state/medical-facilities/[facilityId]?section=assessments
/state/medical-facilities/[facilityId]?section=certificates
/state/medical-facilities/[facilityId]?section=performance
/state/medical-facilities/[facilityId]?section=audit
```

## 8.3 Accreditation Application Detail Route

```txt
/state/medical-facilities/accreditation/[applicationId]
```

or:

```txt
/state/medical-facilities?tab=accreditation&applicationId={applicationId}
```

Use whichever route pattern is already consistent with the project.

---

# 9. Frontend Components

Create or update these components:

```txt
MedicalFacilitiesPage
MedicalFacilitiesTabs
MedicalFacilitiesOverview
FacilitiesTable
FacilitiesFilterChips
FacilityDetailPage
FacilityDetailTabs
AccreditationApplicationsTable
AccreditationFilterChips
AccreditationReviewPanel
AccreditationDecisionModal
FacilityDocumentsPanel
FacilityReportsPage
FacilityStatusBadge
AccreditationStatusBadge
ApplicationTypeBadge
```

---

# 10. Permissions

Recommended permissions:

```txt
medical_facility.view
medical_facility.view_detail
medical_facility.export
medical_facility.suspend
medical_facility.reactivate

facility_accreditation.view
facility_accreditation.review
facility_accreditation.assign_reviewer
facility_accreditation.request_more_info
facility_accreditation.approve
facility_accreditation.reject
facility_accreditation.view_documents

facility_reports.view
facility_reports.export
```

## 10.1 Permission Rules

- Users without `medical_facility.view` cannot access the module.
- Users without `facility_accreditation.view` should not see the Accreditation tab.
- Users without `facility_accreditation.review` should not see review actions.
- Users without `facility_accreditation.approve` should not see approval action.
- Users without `facility_accreditation.reject` should not see rejection action.
- Users without `facility_reports.view` should not see Reports tab.
- Backend remains the source of truth for permissions.

---

# 11. UI Requirements

## 11.1 Page Header

The Medical Facilities page should show:

```txt
Medical Facilities
Manage facility registration, accreditation, re-accreditation, monitoring, and reporting for your state.
```

Actions:

```txt
Export
Review Applications
```

depending on permissions.

## 11.2 Tab Layout

Tabs:

```txt
Overview
Facilities
Accreditation
Reports
```

Use permission-based tab visibility.

## 11.3 Filter Chips

Use filter chips inside tables instead of creating separate tabs for statuses.

Example:

```txt
All | New Applications | Re-accreditation | Pending Review | Under Review | More Info Required | Approved | Rejected
```

## 11.4 Empty States

### Facilities Empty State

```txt
No medical facilities found.
Try adjusting your filters or search criteria.
```

### Accreditation Empty State

```txt
No accreditation applications found.
Applications submitted by medical facilities will appear here.
```

### Reports Empty State

```txt
No facility reports available for the selected filters.
```

## 11.5 Status Badges

Use status badges consistently.

### Facility Accreditation Status

| Status | Tone |
|---|---|
| Accredited | success |
| Pending Accreditation | info |
| Re-accreditation Due | warning |
| Suspended | danger |
| Expired | warning |
| Inactive | neutral |
| Not Accredited | neutral |

### Application Status

| Status | Tone |
|---|---|
| Draft | neutral |
| Submitted | info |
| Pending Review | info |
| Under Review | info |
| More Information Required | warning |
| Approved | success |
| Rejected | danger |
| Withdrawn | neutral |

### Application Type

| Type | Tone |
|---|---|
| New Accreditation | info |
| Re-accreditation | warning |

---

# 12. UX Rules

## 12.1 Do Not Create Status Tabs

Do not create main tabs for:

```txt
Pending Review
Under Review
More Information Required
Approved
Rejected
Suspended
Expired
Re-accreditation
```

Use filters, badges, table columns, and dashboard cards instead.

## 12.2 Facility List Is Master List

The Facilities tab is the source for all facility records in the state.

## 12.3 Accreditation Tab Is Application Queue

The Accreditation tab is the workflow queue for new accreditation and re-accreditation applications.

## 12.4 Facility Detail Holds Deep Information

When users need more information, they should click a facility and view:

```txt
Profile
Accreditation History
Documents
Departments / Staff
Assessments
Certificates
Performance
Audit Logs
```

## 12.5 Re-accreditation Is an Application Type

Re-accreditation should be handled as:

```txt
application_type = re_accreditation
```

not as a separate tab.

---

# 13. Implementation Chunks for Codex

## Chunk 1: Navigation Consolidation

### Goal

Replace separate Facilities and Accreditation navigation with one Medical Facilities parent module.

### Tasks

- Remove separate top-level Accreditation menu item if present.
- Add or update Medical Facilities nav item.
- Route all facility-related state ministry screens under `/state/medical-facilities`.
- Ensure permission `medical_facility.view` controls visibility.

### Acceptance Criteria

- State Ministry sidebar shows Medical Facilities as one parent module.
- Accreditation no longer appears as a separate top-level module.
- Medical Facilities page loads with tabs.
- Existing old routes redirect to the appropriate Medical Facilities tab.

Suggested redirects:

```txt
/state/facilities → /state/medical-facilities?tab=facilities
/state/accreditation → /state/medical-facilities?tab=accreditation
/state/accreditation/pending → /state/medical-facilities?tab=accreditation&status=pending_review
```

---

## Chunk 2: Medical Facilities Page Shell

### Goal

Create parent module page with header and four tabs.

### Tasks

- Create or update `MedicalFacilitiesPage`.
- Add `MedicalFacilitiesTabs`.
- Tabs:
  - Overview
  - Facilities
  - Accreditation
  - Reports
- Add permission-based tab visibility.
- Add page header and description.

### Acceptance Criteria

- Page renders with four tabs.
- Active tab state works.
- URL query param can control tab.
- Unauthorized tabs are hidden.
- Layout follows FoodCert NG design system.

---

## Chunk 3: Overview Tab

### Goal

Create the facility overview dashboard.

### Tasks

- Fetch facility summary statistics.
- Render KPI cards.
- Render recent accreditation activity.
- Render expiring/suspended facilities summary.
- Add quick links to Facilities and Accreditation tabs.

### Acceptance Criteria

- Overview shows total facilities, accredited facilities, pending applications, suspended, expired, and re-accreditation due counts.
- Cards are clickable where appropriate.
- Clicking a card can filter the Facilities or Accreditation tab.
- Empty/loading/error states work.

---

## Chunk 4: Facilities Tab

### Goal

Create master list of all medical facilities in the state.

### Tasks

- Implement `FacilitiesTable`.
- Add search and filters.
- Add filter chips:
  - All
  - Accredited
  - Pending Accreditation
  - Suspended
  - Expired
  - Inactive
  - Re-accreditation Due
- Add facility status badges.
- Add row actions.
- Link rows to facility detail page/drawer.

### Acceptance Criteria

- Facilities tab shows all facility records in the state.
- Status filters work.
- Re-accreditation Due is a filter, not a tab.
- Suspended/Expired are filters, not tabs.
- Clicking a facility opens detail view.
- State scoping is enforced.

---

## Chunk 5: Facility Detail View

### Goal

Create detailed facility view.

### Tasks

- Create `FacilityDetailPage` or drawer.
- Add internal sections:
  - Profile
  - Accreditation History
  - Documents
  - Departments / Staff
  - Assessments Conducted
  - Certificates Issued
  - Settlements, permission-based
  - Performance
  - Audit Logs
- Fetch selected facility details.
- Filter related records by facility ID.

### Acceptance Criteria

- Facility detail opens from Facilities table.
- Departments/staff data appears only inside facility detail.
- Accreditation history shows new and re-accreditation applications.
- Assessments and certificates are filtered to the facility.
- Sensitive medical data is not exposed.

---

## Chunk 6: Accreditation Tab

### Goal

Create one accreditation application queue for both new accreditation and re-accreditation.

### Tasks

- Implement `AccreditationApplicationsTable`.
- Add application type column.
- Add application status column.
- Add filters:
  - All
  - New Applications
  - Re-accreditation
  - Pending Review
  - Under Review
  - More Information Required
  - Approved
  - Rejected
- Add row actions:
  - View Application
  - Assign Reviewer
  - Start Review
  - Request More Information
  - Approve
  - Reject
  - View Documents
- Add badges for application type and status.

### Acceptance Criteria

- Accreditation tab shows all accreditation applications.
- Re-accreditation appears as application type/filter, not as a separate tab.
- Pending Review appears as status/filter, not as a separate tab.
- More Information Required appears as status/filter, not as a separate tab.
- Review actions are permission-based.
- Application table is state-scoped.

---

## Chunk 7: Accreditation Review Flow

### Goal

Implement review workflow actions.

### Tasks

- Create application detail or review panel.
- Show facility profile summary.
- Show checklist.
- Show uploaded documents.
- Show reviewer notes.
- Add decision actions:
  - Request More Information
  - Approve
  - Reject
- Add confirmation modals for decision actions.
- Update application and facility statuses after decision.

### Acceptance Criteria

- State reviewer can review application.
- Reviewer can request more information.
- Reviewer can approve or reject.
- Approving new accreditation sets facility to Accredited.
- Approving re-accreditation renews accreditation expiry date.
- Rejection stores reason.
- Actions are audit logged.

---

## Chunk 8: Reports Tab

### Goal

Create facility reporting tab.

### Tasks

- Add report cards or report table.
- Add filters:
  - Date range
  - LGA
  - Facility type
  - Ownership type
  - Accreditation status
  - Application type
  - Application status
- Add export actions.
- Ensure permissions.

### Acceptance Criteria

- Reports tab shows facility-related reports.
- Exports respect permissions.
- Reports are state-scoped.
- Reports do not expose restricted medical data.
- Export actions are audit logged.

---

## Chunk 9: Permission and Scope Tests

### Goal

Ensure module is secure and state-scoped.

### Tests

- User without `medical_facility.view` cannot access module.
- User without `facility_accreditation.view` cannot see Accreditation tab.
- User without review permission cannot see review actions.
- State user sees only facilities in their state.
- Suspended/expired/re-accreditation due filters work.
- Re-accreditation is not rendered as a separate tab.
- Pending Review is not rendered as a separate tab.
- Old route redirects work.

### Acceptance Criteria

- All permission tests pass.
- All scoping tests pass.
- UI does not expose unauthorized actions.

---

## Chunk 10: Final UI QA

### Goal

Confirm the UX is clean and not over-tabbed.

### QA Checklist

- Medical Facilities sidebar item exists.
- Separate Accreditation sidebar item is removed or redirected.
- Medical Facilities has only:
  - Overview
  - Facilities
  - Accreditation
  - Reports
- Facilities tab uses status filters.
- Accreditation tab uses application type/status filters.
- Re-accreditation is not a standalone tab.
- Pending Review is not a standalone tab.
- More Information Required is not a standalone tab.
- Facility detail contains deeper sections.
- UI is responsive.
- Empty states work.
- Loading states work.

---

# 14. Codex Implementation Prompt

Use this prompt for Codex:

```txt
Update the State Ministry Medical Facilities module in FoodCert NG.

The goal is to consolidate all facility listing, accreditation, re-accreditation, suspension, expiry, and reporting workflows into one parent module called Medical Facilities.

Do not create separate top-level modules or tabs for Facilities, Accreditation, Pending Review, Approved Facilities, More Information Required, Suspended/Expired, or Re-accreditation.

Use this clean tab structure:
- Overview
- Facilities
- Accreditation
- Reports

Facilities tab:
- Shows the master list of all facilities in the state.
- Use filters/status chips for Accredited, Pending Accreditation, Suspended, Expired, Inactive, and Re-accreditation Due.
- Clicking a facility opens facility detail view.

Accreditation tab:
- Shows all accreditation applications.
- Handles both New Accreditation and Re-accreditation.
- Use application_type to distinguish New Accreditation vs Re-accreditation.
- Use status filters for Pending Review, Under Review, More Information Required, Approved, and Rejected.
- Re-accreditation must not be a separate tab.
- Pending Review must not be a separate tab.

Facility detail:
- Include Profile, Accreditation History, Documents, Departments/Staff, Assessments, Certificates, Performance, and Audit Logs.
- Related records must be filtered by selected facility.

Navigation:
- State Ministry sidebar should show Medical Facilities as one parent module.
- If separate Facilities or Accreditation routes exist, redirect them to the correct Medical Facilities tab.

Permissions:
- Enforce medical_facility.view, facility_accreditation.view, facility_accreditation.review, facility_accreditation.approve, facility_accreditation.reject, facility_reports.view, and facility_reports.export.
- Backend remains source of truth.

Use Next.js + React + TypeScript + Tailwind CSS and follow the FoodCert NG application-wide design system.
```

---

# 15. MVP Build Order

1. Navigation consolidation
2. Medical Facilities page shell
3. Overview tab
4. Facilities tab
5. Facility detail view
6. Accreditation tab
7. Accreditation review flow
8. Reports tab
9. Permission and scope tests
10. Final UI QA
