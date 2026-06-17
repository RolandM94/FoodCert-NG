# FoodCert NG — Federal Forms Tool Update Implementation Prompts

## 1. Document Purpose

This document consolidates the Codex implementation prompts for updating the existing **Forms Tool** so it is also available in the **Federal Ministry account**.

The Forms Tool already exists in the State account. The Federal version should reuse the existing Forms Tool engine, components, template builder, assignment engine, response tracking, exports, reports, permissions, and renderer wherever possible.

The Federal version should be focused on:

```txt
National form templates
State reporting templates
Federal M&E data collection
Policy compliance surveys
Guideline implementation monitoring
Cross-state data collection
National response monitoring
Aggregate reports
```

It should **not** become a day-to-day state operational inspection management tool.

---

# 2. Product Decision

The Federal account should have access to the Forms Tool, but with Federal-specific scope, permissions, recipient options, visibility rules, reports, and analytics.

## 2.1 State Forms Tool Purpose

```txt
Operational inspections
Employer data collection
Medical facility reporting
Accreditation checklist workflows
State compliance surveys
State-level form assignments
```

## 2.2 Federal Forms Tool Purpose

```txt
National templates
Federal standard templates
State reporting
Federal M&E data collection
Cross-state monitoring
Policy compliance reporting
Guideline implementation surveys
National response analytics
```

## 2.3 Key Rule

```txt
State account = operational form assignments
Federal account = national templates, reporting, M&E, and oversight
```

---

# 3. Recommended Implementation Order

Use the prompts in this order:

```txt
1. Federal Forms Tool navigation and routes
2. Federal template visibility and scoping
3. State adoption and cloning of Federal templates
4. Federal assignments to States
5. Federal responses and cross-state monitoring
6. Federal reports and exports
7. Permissions, audit, and tests
```

---

# 4. Implementation Chunk 1: Federal Forms Tool Navigation and Routes

## Codex Prompt

```txt
Update the Federal Ministry account to include Forms Tool in the Federal sidebar.

Context:
The Forms Tool already exists in the State account. Reuse the existing Forms Tool components, layouts, template builder, assignment engine, response tracking, exports, reports, and shared form renderer where possible.

Goal:
Enable Forms Tool for the Federal Ministry account, but make it focused on:
- National form templates
- State reporting templates
- Federal M&E data collection
- Policy compliance surveys
- Guideline implementation monitoring
- Cross-state data collection
- National response monitoring
- Aggregate reports

Federal sidebar should include:
- Dashboard
- States Overview
- Directory & Registry
- Forms Tool
- Reports & Analytics
- Account Settings

Federal Forms Tool tabs:
- Overview
- Templates
- Assignments
- Responses
- Reports
- Settings

Do not rebuild the Forms Tool from scratch.
Reuse the State Forms Tool implementation and add federal-specific scoping, permissions, routes, labels, and filters.

Acceptance criteria:
1. Federal account sidebar shows Forms Tool.
2. Federal Forms Tool page loads successfully.
3. Federal Forms Tool uses the same base UI/components as State Forms Tool.
4. Federal Forms Tool has tabs: Overview, Templates, Assignments, Responses, Reports, Settings.
5. Federal Forms Tool is scoped to Federal Ministry users.
6. State Forms Tool continues working unchanged.
7. UI follows the FoodCert NG design system.
```

---

# 5. Implementation Chunk 2: Federal Template Visibility and Scoping

## Codex Prompt

```txt
Update the Forms Tool template scoping model to support Federal templates.

Context:
The Forms Tool already exists in the State account and has now been enabled for the Federal account. Do not rebuild the Forms Tool. Extend the existing template model and UI to support Federal-specific visibility and ownership.

Goal:
Federal users should be able to create national templates and control whether they are private, shared with selected states, or published as Federal Standard Templates.

Add template visibility/scoping values:
- federal_private: visible only to Federal users
- federal_shared: visible to selected states
- federal_standard: official national standard template available to all states
- state_owned: existing state-owned templates

Federal form purposes:
Add/support these Federal-specific form purposes:
- National Policy Template
- State Reporting Form
- Federal M&E Data Collection
- Federal Compliance Review
- National Incident Reporting
- Programme Monitoring Form
- Guideline Implementation Survey
- Cross-State Survey
- National Facility Reporting Template
- Inspection Performance Reporting Template

Federal Forms Tool → Templates UI:
Add filters:
- All
- Federal Private
- Shared with States
- Federal Standard
- Adopted by States

Add columns:
- Template Name
- Purpose
- Visibility
- Shared With
- Adoption Count
- Version
- Status
- Last Updated
- Actions

Template behaviour:
- Federal users can create Federal templates.
- Federal users can publish templates.
- Federal users can mark published templates as Federal Standard Templates.
- Federal users can share templates with all states or selected states.
- Federal users cannot edit state-owned templates.
- State users cannot edit Federal templates directly.

Required permissions:
- forms.template.view_federal
- forms.template.create_federal
- forms.template.publish_federal
- forms.template.share_to_states
- forms.template.mark_as_standard

Acceptance criteria:
1. Federal templates support visibility values: federal_private, federal_shared, federal_standard.
2. State-owned templates remain unchanged.
3. Federal Templates table shows visibility, shared states, adoption count, version, and status.
4. Federal users can mark a template as Federal Standard only with permission.
5. Federal users can share a template with selected states only with permission.
6. Federal users cannot edit state-owned templates.
7. State users cannot directly edit Federal templates.
8. Existing State Forms Tool still works unchanged.
9. All template visibility changes are audit logged.
```

---

# 6. Implementation Chunk 3: State Adoption and Cloning of Federal Templates

## Codex Prompt

```txt
Implement State adoption and cloning of Federal templates.

Context:
Federal Forms Tool now supports Federal Private, Federal Shared, and Federal Standard templates. State accounts should be able to view Federal templates shared with them and either adopt or clone them.

Goal:
Allow State users to use Federal Standard Templates or Federal Shared Templates in their own State workflows without directly editing the Federal-owned template.

State adoption flow:
1. Federal creates and publishes a Federal Standard Template or shares a template with selected states.
2. State user opens Forms Tool or Account Settings.
3. State user sees Federal templates available to their state.
4. State user can:
   - Preview template
   - Adopt template as-is
   - Clone template into a state-owned version
5. Adopted or cloned templates can be selected in State settings, such as:
   - Inspection Settings
   - Medical Facility Settings
   - Forms assignments

Definitions:
- Adopt Federal Template:
  State uses the Federal-owned template version as-is. State cannot edit it.
- Clone Federal Template:
  State creates a state-owned copy of the Federal template. State can edit the cloned version.

State Forms Tool UI:
Add a section or filter under Templates:
- Federal Templates
- Federal Standard Templates
- Shared With My State
- Adopted Templates
- Cloned Templates

State template actions:
- Preview
- Adopt
- Clone
- View Federal Source
- Use in Assignment
- Use in Settings, where applicable

Required APIs:
- GET /api/state/forms/federal-templates
- POST /api/state/forms/federal-templates/:id/adopt
- POST /api/state/forms/federal-templates/:id/clone

Required permissions:
- forms.template.view_federal_shared
- forms.template.adopt_federal
- forms.template.clone_federal
- forms.template.create_state

Rules:
- State users cannot edit Federal-owned templates.
- Adopted Federal templates should remain linked to the Federal source template and version.
- Cloned templates become state_owned.
- Cloned templates should preserve original template metadata in a source reference.
- If Federal updates a standard template, adopted states should be able to see that a newer version exists.
- State should decide whether to continue using the adopted version or adopt the newer version.
- Cloned templates should not auto-update when Federal templates change.

Acceptance criteria:
1. State users can view Federal templates shared with their state.
2. State users can view Federal Standard Templates.
3. State users can preview Federal templates.
4. State users can adopt Federal templates as read-only templates.
5. State users can clone Federal templates into state-owned editable templates.
6. Adopted templates can be selected in State settings and assignments.
7. Cloned templates behave like normal State templates.
8. Federal templates cannot be edited directly by State users.
9. Adoption and cloning actions are audit logged.
10. Existing State-created templates remain unchanged.
```

---

# 7. Implementation Chunk 4: Federal Assignments to States

## Codex Prompt

```txt
Implement Federal Forms Tool assignment workflow for assigning forms to State Ministries and Federal users.

Context:
The Federal Forms Tool is for national templates, state reporting, federal M&E data collection, policy compliance surveys, and cross-state monitoring. Federal should generally assign forms to States, State Ministry roles/users, Federal departments, Federal officers, or national programme teams.

Goal:
Allow Federal users to create assignments for Federal templates and assign them to all states or selected states.

Federal assignment recipients:
- All States
- Selected States
- State Ministry Role
- State Ministry User
- Federal Department
- Federal User
- National Programme Team

Federal should not normally assign forms directly to:
- Employers
- Medical Facilities
- Food Handlers
- State Inspectors

Exception:
Allow direct assignment to operational users/entities only if the user has:
- forms.assignment.assign_national_operational

Federal Forms Tool → Assignments UI:
Update the assignment wizard for Federal account:
Step 1: Select Template
Step 2: Select Assignment Purpose
Step 3: Select Recipient Scope
Step 4: Select States / Roles / Users
Step 5: Configure Due Date, Reminders, Review Rules
Step 6: Review and Publish Assignment

Federal assignment purposes:
- State Reporting
- Federal M&E Data Collection
- Policy Compliance Review
- Guideline Implementation Survey
- National Incident Reporting
- Programme Monitoring
- Cross-State Survey

Federal assignment behaviour:
- If assigned to All States, create recipients for every active state account.
- If assigned to Selected States, create recipients only for selected states.
- If assigned to State Ministry Role, route to users with that role in selected states.
- If assigned to Federal Department/User, keep within Federal account.
- Federal assignments should appear in the recipient State account as assigned Federal forms.
- State users should be able to submit responses to Federal assignments based on their role/permission.

Required APIs:
- GET /api/federal/forms/assignments
- POST /api/federal/forms/assignments
- GET /api/federal/forms/assignments/:id
- GET /api/federal/forms/assignments/:id/recipients
- GET /api/state/forms/federal-assignments
- GET /api/state/forms/federal-assignments/:id
- POST /api/state/forms/federal-assignments/:id/response

Required permissions:
Federal:
- forms.assignment.assign_to_states
- forms.assignment.view_federal
- forms.assignment.create_federal
- forms.assignment.assign_national_operational, only for exceptional operational assignment

State:
- forms.assignment.view_federal_assigned
- forms.response.submit_federal_assigned

Acceptance criteria:
1. Federal users can assign forms to all states.
2. Federal users can assign forms to selected states.
3. Federal users can assign forms to State Ministry roles/users.
4. Federal direct assignment to employers, facilities, food handlers, or inspectors is hidden unless special permission exists.
5. Federal assignments appear in State Forms Tool as assigned Federal forms.
6. State users can respond to Federal assignments if permitted.
7. Federal can track recipient states and response status.
8. Assignment creation and recipient resolution are audit logged.
9. Existing State assignment workflow remains unchanged.
```

---

# 8. Implementation Chunk 5: Federal Responses and Cross-State Monitoring

## Codex Prompt

```txt
Implement Federal response tracking and cross-state monitoring for Federal Forms Tool.

Context:
Federal users need to monitor responses from State Ministries and Federal users for national templates, state reporting forms, Federal M&E data collection, policy compliance surveys, and guideline implementation forms.

Goal:
Federal Forms Tool → Responses should show cross-state response monitoring, response rate, overdue submissions, pending states, submitted responses, and aggregate analytics.

Federal Forms Tool → Responses UI:
Add filters:
- State
- Zone, if available
- LGA, if response data supports it
- Respondent Type
- Organization Type
- Assignment Status
- Submission Status
- Date Range
- Form Purpose
- Template
- Template Version

Federal response summary cards:
- Total Assigned States
- Submitted States
- Pending States
- Overdue States
- Response Rate %
- Returned Responses

Federal Responses table columns:
- Assignment
- Template
- Purpose
- State
- Respondent
- Organization
- Status
- Submitted Date
- Reviewed By
- Actions

State-level response monitoring:
Show a state response matrix:
- State
- Assigned Forms
- Submitted
- Pending
- Overdue
- Response Rate
- Last Submission
- Action

Privacy rules:
- Federal users can view responses to forms Federal assigned.
- Federal users can view aggregate cross-state response analytics.
- Federal users should not see private medical details unless explicitly permitted.
- Medical/private fields should be masked, omitted, or aggregated unless permission allows detail access.
- Federal reports should default to state-level or aggregate summaries.

Required APIs:
- GET /api/federal/forms/responses
- GET /api/federal/forms/responses/:id
- GET /api/federal/forms/assignments/:id/response-summary
- GET /api/federal/forms/assignments/:id/state-response-matrix

Required permissions:
- forms.response.view_federal
- forms.response.view_cross_state_aggregate
- forms.response.view_sensitive_detail, only where allowed
- forms.response.review_federal
- forms.export.federal

Acceptance criteria:
1. Federal users can view responses to Federal assignments.
2. Federal users can filter responses by state, status, date range, purpose, and template.
3. Federal users can see response rate by state.
4. Federal users can see pending and overdue states.
5. Federal users can view state response matrix.
6. Federal users cannot view unauthorized private medical fields.
7. Aggregate analytics are available without exposing sensitive details.
8. Response detail access is permission-controlled.
9. Response viewing and exports are audit logged.
```

---

# 9. Implementation Chunk 6: Federal Reports and Exports

## Codex Prompt

```txt
Implement Federal Forms Tool reports and exports.

Context:
Federal Forms Tool is used for national templates, state reporting, Federal M&E data collection, policy compliance, guideline implementation surveys, and cross-state monitoring.

Goal:
Add Federal Forms Tool reports that help Federal Ministry users monitor state submissions, compare states, and export responses where permitted.

Federal Forms Tool → Reports:
Add these reports:
- State Reporting Response Rate
- Cross-State Form Submission Summary
- Guideline Implementation Survey Report
- Federal M&E Data Collection Report
- National Policy Compliance Report
- State-by-State Response Comparison
- Overdue State Submissions Report
- Template Adoption by State Report
- Federal Standard Template Usage Report

Report filters:
- Template
- Template Version
- Purpose
- State
- Zone, if available
- Date Range
- Submission Status
- Assignment
- Respondent Type
- Organization Type

Report outputs:
- Summary cards
- Tables
- Charts
- CSV export
- Excel export
- PDF summary export, optional

Export rules:
- Exports must respect permissions and field sensitivity.
- Sensitive/private medical fields should be excluded or masked unless permission allows.
- Export action must be audit logged.
- Large exports should be queued if necessary.

Required APIs:
- GET /api/federal/forms/reports
- GET /api/federal/forms/reports/:reportKey
- POST /api/federal/forms/exports
- GET /api/federal/forms/exports/:id/download

Required permissions:
- forms.report.view_federal
- forms.report.view_cross_state
- forms.export.federal
- forms.export.sensitive_detail, only where allowed

Acceptance criteria:
1. Federal Reports tab shows Federal-specific form reports.
2. Reports can be filtered by state, template, purpose, date, and status.
3. Federal users can compare state submissions.
4. Federal users can see overdue state submissions.
5. Federal users can see template adoption by state.
6. Exports work for authorized users.
7. Sensitive fields are masked/omitted unless permission allows.
8. Export actions are audit logged.
9. Existing State reports remain unchanged.
```

---

# 10. Implementation Chunk 7: Federal Forms Tool Permissions, Audit, and Tests

## Codex Prompt

```txt
Add permissions, audit logs, and tests for the Federal Forms Tool update.

Context:
The Federal Forms Tool has been added using the existing Forms Tool engine. It now supports Federal templates, sharing with states, Federal Standard Templates, state adoption/cloning, Federal assignments to states, cross-state responses, reports, and exports.

Goal:
Secure the Federal Forms Tool with proper permissions, state/federal scoping, privacy rules, and audit logging.

Federal permissions:
- forms.template.view_federal
- forms.template.create_federal
- forms.template.publish_federal
- forms.template.share_to_states
- forms.template.mark_as_standard
- forms.assignment.view_federal
- forms.assignment.create_federal
- forms.assignment.assign_to_states
- forms.assignment.assign_national_operational
- forms.response.view_federal
- forms.response.view_cross_state_aggregate
- forms.response.view_sensitive_detail
- forms.response.review_federal
- forms.report.view_federal
- forms.report.view_cross_state
- forms.export.federal
- forms.export.sensitive_detail

State permissions:
- forms.template.view_federal_shared
- forms.template.adopt_federal
- forms.template.clone_federal
- forms.assignment.view_federal_assigned
- forms.response.submit_federal_assigned
- forms.template.create_state
- forms.assignment.create_state
- forms.response.view_state

Audit log these actions:
- Federal template created
- Federal template published
- Federal template shared with states
- Federal template marked as standard
- Federal template unshared
- State adopted Federal template
- State cloned Federal template
- Federal assignment created
- Federal assignment sent to states
- State response submitted to Federal assignment
- Federal response viewed
- Federal report exported
- Sensitive response viewed
- Direct national operational assignment created

Tests:
1. Federal user with permission can create Federal template.
2. Federal user without permission cannot create Federal template.
3. Federal user can share template with selected states.
4. State user can see only Federal templates shared with their state or standard templates.
5. State user cannot edit Federal template directly.
6. State user can adopt Federal template with permission.
7. State user can clone Federal template with permission.
8. Federal user cannot edit state-owned template.
9. Federal assignment to all states creates recipients for all active states.
10. Federal assignment to selected states creates recipients only for selected states.
11. Federal direct assignment to employers/facilities/food handlers is blocked unless special permission exists.
12. Federal user can view cross-state aggregate responses.
13. Federal user cannot view sensitive/private fields without permission.
14. State user can submit response to Federal assignment if permitted.
15. Export respects permissions and field sensitivity.
16. All major actions are audit logged.
17. Existing State Forms Tool functionality remains unchanged.

Acceptance criteria:
1. All Federal Forms Tool permissions are enforced.
2. State and Federal scoping works correctly.
3. Sensitive data is protected.
4. Audit logs are created for all major actions.
5. Tests pass.
6. Existing State Forms Tool workflows are not broken.
```

---

# 11. Consolidated Codex Master Prompt

Use this only if Codex can handle a larger instruction. Otherwise use the smaller chunks above.

```txt
Update the Federal Ministry account to include a Federal version of the Forms Tool.

Important context:
The Forms Tool already exists in the State account. Do not rebuild it from scratch. Reuse the existing Forms Tool components, data models, renderer, template builder, assignment engine, response tracking, exports, and reports where possible.

Goal:
Enable the Forms Tool for the Federal Ministry account, but adjust its purpose and permissions so it is focused on national templates, state reporting, federal M&E data collection, and cross-state monitoring — not day-to-day state operational inspection management.

Federal Forms Tool should support:
- National form templates
- Federal M&E data collection
- State reporting templates
- Policy compliance surveys
- Guideline implementation monitoring
- Cross-state data collection
- National response monitoring
- Aggregate reports

Federal account navigation:
Add Forms Tool to the Federal Ministry sidebar:

Federal Ministry
- Dashboard
- States Overview
- Directory & Registry
- Forms Tool
- Reports & Analytics
- Account Settings

Federal Forms Tool tabs:
- Overview
- Templates
- Assignments
- Responses
- Reports
- Settings

Federal form purposes:
Add/support these Federal-specific form purposes:
- National Policy Template
- State Reporting Form
- Federal M&E Data Collection
- Federal Compliance Review
- National Incident Reporting
- Programme Monitoring Form
- Guideline Implementation Survey
- Cross-State Survey
- National Facility Reporting Template
- Inspection Performance Reporting Template

Federal template behaviour:
- Federal users can create national form templates.
- Federal users can publish templates as Federal Standard Templates.
- Federal templates can be shared with all states or selected states.
- State accounts can view, adopt, or clone Federal templates.
- State accounts should be able to use adopted/cloned Federal templates in their own operational settings, such as Inspection Settings or Medical Facility Settings.
- Federal should not directly control a State’s active operational template unless explicitly permitted by policy.

Add template visibility/scoping:
- federal_private: visible only to Federal users
- federal_shared: visible to selected states
- federal_standard: official national standard template available to all states
- state_owned: existing state-owned templates

Federal assignment behaviour:
Federal can assign forms to:
- State Ministries
- State Ministry roles/users
- Federal departments
- Federal officers
- National programme teams

Federal should not normally assign forms directly to:
- State inspectors
- Employers
- Medical facilities
- Food handlers

Exception:
Allow direct assignment to employers, facilities, inspectors, or food handlers only if a permission like `forms.assignment.assign_national_operational` is granted.

Federal response visibility:
- Federal can view responses to forms it assigned.
- Federal can view aggregate cross-state response analytics.
- Federal can filter responses by state, LGA, organization type, respondent type, status, date range, and form purpose.
- Federal should not see private medical response details unless explicitly permitted.
- Federal reports should default to aggregate or state-level summaries.

State adoption flow:
Implement this workflow:
1. Federal creates and publishes a Federal Standard Template.
2. State user opens Forms Tool or Account Settings.
3. State user sees Federal Standard Templates available for adoption.
4. State user can:
   - Adopt template as-is
   - Clone template into state-owned version
   - Preview template
5. Adopted template can be selected in State settings, such as:
   - Inspection Settings
   - Medical Facility Settings
   - Forms assignments

Required permissions:
Federal:
- forms.template.view_federal
- forms.template.create_federal
- forms.template.publish_federal
- forms.template.share_to_states
- forms.template.mark_as_standard
- forms.assignment.assign_to_states
- forms.response.view_federal
- forms.response.view_cross_state_aggregate
- forms.report.view_federal
- forms.report.view_cross_state
- forms.export.federal

State:
- forms.template.view_federal_shared
- forms.template.adopt_federal
- forms.template.clone_federal
- forms.template.create_state
- forms.assignment.create_state
- forms.response.view_state

Restrictions:
- Federal users should not edit state-owned templates.
- State users should not edit Federal templates directly.
- State users can clone Federal templates into state-owned templates.
- Federal assignments to States should appear in the State account as assigned Federal forms.
- State responses to Federal forms should be visible to Federal users based on permissions.
- Federal users should not see unauthorized medical/private fields.

UI updates:
Federal Forms Tool → Templates:
- Add filters:
  - All
  - Federal Private
  - Shared with States
  - Federal Standard
  - Adopted by States
- Add columns:
  - Template Name
  - Purpose
  - Visibility
  - Shared With
  - Adoption Count
  - Version
  - Status
  - Last Updated
  - Actions

Federal Forms Tool → Assignments:
- Add recipient options:
  - All States
  - Selected States
  - State Ministry Role
  - Federal Department
  - Federal User
  - National Programme Team
- Disable or hide Employer / Facility / Food Handler direct assignment unless `forms.assignment.assign_national_operational` is granted.

Federal Forms Tool → Responses:
- Add cross-state filters:
  - State
  - LGA
  - Respondent Type
  - Organization Type
  - Assignment Status
  - Submission Status
  - Date Range
  - Form Purpose
- Show response rate by state.
- Show pending states.
- Show overdue state submissions.
- Show submitted responses.
- Allow export where permitted.

Federal Forms Tool → Reports:
Add reports:
- State Reporting Response Rate
- Cross-State Form Submission Summary
- Guideline Implementation Survey Report
- Federal M&E Data Collection Report
- National Policy Compliance Report
- State-by-State Response Comparison
- Overdue State Submissions Report

APIs:
Reuse existing Forms Tool APIs where possible, but add Federal scoping/filters:
- GET /api/federal/forms/templates
- POST /api/federal/forms/templates
- POST /api/federal/forms/templates/:id/publish
- POST /api/federal/forms/templates/:id/share-to-states
- POST /api/federal/forms/templates/:id/mark-standard
- GET /api/federal/forms/assignments
- POST /api/federal/forms/assignments
- GET /api/federal/forms/responses
- GET /api/federal/forms/reports
- GET /api/state/forms/federal-templates
- POST /api/state/forms/federal-templates/:id/adopt
- POST /api/state/forms/federal-templates/:id/clone

Acceptance criteria:
1. Federal account has Forms Tool in the sidebar.
2. Federal Forms Tool reuses the existing Forms Tool engine.
3. Federal users can create, publish, and share national templates.
4. Federal users can mark templates as Federal Standard Templates.
5. Federal users can assign forms to all states or selected states.
6. Federal users can monitor state responses.
7. Federal users can view cross-state response analytics.
8. States can view Federal shared/standard templates.
9. States can adopt or clone Federal templates.
10. Federal users cannot edit state-owned templates.
11. State users cannot edit Federal templates directly.
12. Federal direct assignment to employers/facilities/food handlers is hidden unless special permission is granted.
13. Medical/private response fields remain protected.
14. All actions are audit logged.
15. UI follows the FoodCert NG application-wide design system using Next.js + React + TypeScript + Tailwind CSS.
```
