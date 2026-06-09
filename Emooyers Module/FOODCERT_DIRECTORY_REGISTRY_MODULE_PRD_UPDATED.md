# PRD: Directory & Registry Module — FoodCert NG

## 1. Module Name

**Directory & Registry Module**

## 2. Product Context

FoodCert NG needs a central directory layer where authorized users can search, filter, view, and export records for:

- Food handlers
- Employers / food businesses
- Employer branches / outlets / sites
- Certificates and certificate statuses
- Compliance statuses
- Vaccination statuses
- Inspection and enforcement statuses
- Assessment statuses
- State / LGA coverage

This module should not replace the core models for Food Handlers, Employers, Certificates, Assessments, Inspections, Payments, or Stakeholder Management. Instead, it should provide a unified read/search/reporting layer over those modules.

The Directory & Registry Module should be implemented as **one shared module with separate views**, not as two unrelated modules for Food Handlers and Employers.

Recommended structure:

```txt
Directory & Registry Module
├── Overview
├── Food Handlers Directory
├── Employers / Food Businesses Directory
│   ├── Employer Profiles
│   ├── Branches / Outlets / Sites
│   ├── Employer Food Handlers
│   ├── Employer Certificates
│   ├── Employer Inspections
│   └── Employer Compliance
├── Certificate Registry Search
├── Global Search
├── Saved Views
└── Exports
```

**Important product rule:** Branches, outlets, stores, sites, and locations are not standalone business entities. They are sub-units of an Employer/Food Business and should be accessed primarily through the Employers / Food Businesses Directory.

---

# 3. Product Goal

To provide a centralized, role-aware, privacy-safe, and searchable directory for food handlers, employers, branches, certificates, and compliance records on FoodCert NG, enabling regulators, employers, facilities, inspectors, and authorized users to find and act on the right records quickly.

---

# 4. Core Product Decision

## 4.1 One Module, Multiple Views

The Directory should be one shared module with separate views:

1. **Food Handlers Directory**
2. **Employers / Food Businesses Directory**
   - Employer profiles
   - Branches / outlets / sites as employer sub-units
   - Employer food handlers
   - Employer certificates
   - Employer inspections
   - Employer compliance
3. **Certificate Registry Search**
4. **Global Search**
5. **Saved Views and Exports**

Do not create two unrelated modules called “Food Handler Directory” and “Employer Directory.” Also do not treat Branches / Outlets as a separate peer module beside Employers. Branches / Outlets belong under Employers / Food Businesses.

## 4.2 Why One Shared Module

Food handlers and employers are deeply connected:

```txt
Food Handler
→ Employer
→ Branch
→ Certificate
→ Assessment
→ Vaccination
→ Inspection
→ Compliance Status
```

Employers are also connected to food handlers:

```txt
Employer
→ Branches
→ Food Handlers
→ Certificates
→ Inspections
→ Compliance Reports
```

A shared directory avoids duplicated:

- Search logic
- Filter logic
- Export logic
- State/LGA scoping
- Branch scoping
- Permission checks
- Audit logs
- Compliance summary logic
- Report generation logic

## 4.3 Directory UI Consolidation

The frontend should present Directory & Registry as **one parent navigation module**. The following should not appear as scattered top-level modules:

```txt
Food Handlers Directory
Employers Directory
Branches Directory
Certificate Search
Global Search
Saved Views
Exports
```

They should sit under one parent navigation item:

```txt
Directory & Registry
```

Recommended internal tabs/sub-navigation:

```txt
Overview
Food Handlers
Employers / Food Businesses
Certificates
Global Search
Saved Views
Exports
```

The **Employers / Food Businesses** view should contain the branches/outlets experience. Branches, outlets, stores, and sites are implemented as `OrganizationUnit` records linked to an employer. They may be searchable through a shortcut route or filtered view, but conceptually and visually they belong under Employers / Food Businesses.

Recommended Employers / Food Businesses detail tabs:

```txt
Employer Profile
Branches / Outlets / Sites
Food Handlers
Certificates
Inspections
Notices
Compliance Summary
Subscription
Audit Logs
```

A standalone `/directory/branches` route may exist only as a convenience shortcut for users who need to search across employer locations. It should still use the same Employer/OrganizationUnit service layer and must not behave like a separate business module.

---

# 5. Module Objectives

The Directory & Registry Module must allow authorized users to:

1. Search food handlers.
2. Search employers / food businesses.
3. Search employer branches / outlets as employer sub-units.
4. Search certificates by number or status.
5. Filter records by state, LGA, branch, employer, status, and date.
6. View compliance summaries.
7. View role-safe profile details.
8. Export directory results where permitted.
9. Apply state, organization, branch, facility, and unit scoping.
10. Protect sensitive medical information.
11. Provide global search across food handlers, employers, branches, certificates, inspections, and notices.
12. Support dashboards and reports with reusable directory filters.
13. Provide stable APIs for frontend tables and search components.
14. Use privacy-safe serializers by role.
15. Log sensitive searches, sensitive field reveals, and exports.

---

# 6. Key Users and Access Expectations

## 6.1 Federal Ministry Users

Federal users need national oversight.

Can see:

- National food handler directory, based on permission
- National employer directory
- State-level filters
- LGA-level summaries
- Certificate status distribution
- Compliance trends
- National branch coverage
- Aggregate records by default

Should not automatically see:

- Lab results
- Doctor notes
- Diagnosis
- Health declaration answers
- Full NIN
- Detailed medical records

## 6.2 State Ministry Users

State users need state-level regulatory oversight.

Can see:

- Food handlers in their state
- Employers operating in their state
- Branches in their state
- Certificates issued in their state
- Inspection and enforcement status
- Compliance summaries by LGA

Cannot see:

- Records outside their state unless authorized
- Sensitive medical data unless role permits

## 6.3 Employer Admin

Employer admins need to see their own organization’s workers and branches.

Can see:

- Their own food handlers
- Their own branches
- Certificate status
- Vaccination compliance status
- Fitness status
- Return-to-work status
- Inspection status
- Branch compliance summaries

Cannot see:

- Other employers’ records
- Lab results
- Doctor notes
- Diagnosis
- Declaration answers
- Full NIN

## 6.4 Branch Manager

Branch managers need branch-scoped access.

If `unit_restricted = true`, they can see:

- Food handlers in their assigned branch
- Certificates for assigned branch food handlers
- Vaccination status for assigned branch food handlers
- Branch inspections
- Branch compliance summaries

Cannot see:

- Other branches
- Employer-wide reports unless permission allows
- Sensitive medical data

## 6.5 Medical Facility Users

Medical facilities need to see assessment-related food handlers, not all national records.

Can see:

- Food handlers assessed by their facility
- Food handlers with appointments at their facility
- Assessment status for facility-linked records
- Certificate issuance status for facility assessments
- Facility performance directory views

Cannot see:

- Food handlers not linked to their facility
- Employer-wide directories unless tied to facility workflows
- Other facilities’ records

## 6.6 Inspector / Environmental Health Officer

Inspectors need field verification and compliance context.

Can see:

- Assigned employers/branches
- Food handler operational status
- Certificate status
- Vaccination due status
- Return-to-work status
- Public/inspector-safe certificate details

Cannot see:

- Lab results
- Diagnosis
- Doctor notes
- Declaration answers
- Full NIN

## 6.7 Super Admin / Platform Operator

Can manage and view records globally according to platform administration permissions, but sensitive medical data should still require explicit permission and audit logging.

---

# 7. Directory Views

## 7.1 Food Handlers Directory

### Purpose

The Food Handlers Directory allows authorized users to search and monitor food handlers, their certification status, employer linkage, branch assignment, and operational compliance status.

### Primary Use Cases

- State officer searches for food handlers in a state/LGA.
- Employer views all food handlers under their business.
- Branch manager views food handlers in a branch.
- Inspector checks expected food handlers during inspection.
- Facility sees food handlers assessed by facility.
- Federal user views aggregate national food handler registry.

### Food Handler Directory Columns

Recommended columns:

- Passport photo
- Food handler name
- Food handler ID
- Masked NIN
- Phone, permission-based
- Gender
- Date of birth, permission-based
- Employer
- Branch
- Job role / food handler category
- State
- LGA
- Certificate status
- Certificate number
- Certificate expiry date
- Fitness status
- Vaccination status
- Assessment status
- Return-to-work status
- Last assessment date
- Medical facility, permission-based
- Date registered
- Actions

### Food Handler Filters

Required filters:

- State
- LGA
- Employer
- Branch
- Food handler category
- Certificate status
- Fitness status
- Vaccination status
- Assessment status
- Return-to-work status
- Certificate expiry window
- Medical facility
- Date registered
- Last assessment date
- Gender, permission-based
- Age range, permission-based

### Food Handler Actions

Actions depend on role and permission.

Possible actions:

- View profile
- View certificate
- Verify certificate
- Send renewal reminder
- View assessment status
- View vaccination status
- View employer linkage
- Assign/reassign branch, employer users only where permitted
- Export selected records
- Open inspection context, inspector only
- View audit trail, regulatory users only

### Food Handler Privacy Rules

Food Handlers Directory must not show by default:

- Lab results
- Diagnosis
- Doctor notes
- Health declaration answers
- Treatment notes
- Full NIN
- Internal medical report

Full NIN may only be visible to explicitly authorized users and must be audit logged.

---

## 7.2 Employers / Food Businesses Directory

### Purpose

The Employers Directory allows authorized users to search and monitor food businesses, branches, linked food handlers, compliance scores, inspections, and subscription status.

### Primary Use Cases

- State Ministry monitors food businesses in a state.
- Federal Ministry compares employer compliance nationally.
- Inspector searches for a business before inspection.
- Employer admin views own business profile.
- Compliance officer filters non-compliant businesses.

### Employer Directory Columns

Recommended columns:

- Employer / business name
- Employer ID
- Establishment category
- Business type
- Registration/profile status
- State
- LGA
- Address
- Contact person, permission-based
- Phone, permission-based
- Number of branches
- Number of food handlers
- Certified food handlers
- Expired certificate count
- Temporarily not fit count
- Vaccination due count
- Overall compliance percentage
- Inspection status
- Open notices
- Last inspection date
- Subscription status, permission-based
- Date registered
- Actions

### Employer Filters

Required filters:

- State
- LGA
- Establishment category
- Business type
- Registration/profile status
- Compliance status
- Certificate compliance range
- Inspection status
- Notice status
- Subscription status
- Branch count range
- Food handler count range
- Date registered
- Last inspection date

### Employer Actions

Possible actions:

- View employer profile
- View branches
- View food handlers
- View compliance summary
- View inspections
- View notices
- Assign inspection, authorized State users
- Export employer list
- View subscription status, authorized users only
- View audit trail, authorized users only

### Employer Privacy Rules

Employer Directory should not expose:

- Payment transaction details to inspectors by default
- Medical records of workers
- Full NINs of workers
- Lab or diagnosis information
- Internal employer private records outside user scope

---

## 7.3 Employer Branches / Outlets View

### Purpose

Branches, outlets, sites, stores, and locations are sub-units of an Employer/Food Business. They are managed through the shared `OrganizationUnit` model and should be accessed primarily from the Employers / Food Businesses Directory.

The Branches / Outlets view allows authorized users to monitor employer locations, but it should not be treated as a separate peer module to Employers.

### Branch Directory Columns

- Branch name
- Employer
- Unit type
- State
- LGA
- Address
- Branch manager
- Food handler count
- Active certificate count
- Expired certificate count
- Vaccination due count
- Temporarily not fit count
- Inspection status
- Open notices
- Compliance percentage
- Last inspection date
- Status
- Actions

### Branch Filters

- Employer
- State
- LGA
- Branch status
- Compliance status
- Inspection status
- Notice status
- Certificate status
- Food handler count range
- Last inspection date

### Branch Actions

- View branch profile
- View branch food handlers
- View branch certificates
- View branch inspections
- View branch notices
- Export branch compliance report
- Assign inspection, authorized users
- Edit branch, employer/stakeholder permissions only

### Branch Navigation Rule

Primary path:

```txt
Directory & Registry → Employers / Food Businesses → Employer Detail → Branches / Outlets / Sites
```

Optional shortcut path:

```txt
Directory & Registry → Employers / Food Businesses → Branches View
```

or:

```txt
/app/directory/branches
```

The optional shortcut must still be powered by Employer + OrganizationUnit data and should be described in the UI as a location-level view of employers, not as a separate module.

---

## 7.4 Certificate Registry Search

### Purpose

The Directory Module should expose certificate search for users with permission, while the Certificate Module remains the source of truth.

### Search Inputs

- Certificate number
- Verification token, authorized/internal
- Food handler name
- Employer
- Branch
- State
- LGA
- Facility
- Certificate status
- Issue date
- Expiry date

### Certificate Search Result Columns

- Certificate number
- Food handler name
- Passport photo
- Employer
- Branch
- Issuing state
- Medical facility
- Issue date
- Expiry date
- Certificate status
- Fitness status
- Actions

### Privacy Rule

Certificate Registry Search must use certificate-safe serializers and must not expose medical records.

---

## 7.5 Global Search

### Purpose

Global Search allows authorized users to search across key entities.

### Searchable Entities

- Food handlers
- Employers
- Branches
- Certificates
- Inspections
- Notices
- Medical facilities, optional
- State/LGA records, optional

### Global Search Input

One search box:

```txt
Search by name, certificate number, employer, branch, phone, or ID
```

### Result Grouping

Results should be grouped by type:

```txt
Food Handlers
Employers
Branches
Certificates
Inspections
Notices
```

### Global Search Rules

- Results must respect role and scope.
- Sensitive fields must not appear in search result snippets.
- Full NIN search should require explicit permission.
- Searches using sensitive identifiers should be audit logged.

---

# 8. Directory Access Scoping

## 8.1 Scope Types

Directory access must support:

- Global scope
- National scope
- State scope
- LGA scope
- Organization scope
- Branch / unit scope
- Facility scope
- Own-record scope

## 8.2 Scope Examples

| User | Directory Scope |
|---|---|
| Super Admin | Global |
| Federal Admin | National |
| State Admin | Own state |
| State LGA Officer | Assigned LGA |
| Employer Admin | Own employer organization |
| Branch Manager | Assigned branch only |
| Facility Admin | Facility-linked assessments/food handlers |
| Doctor | Assigned assessments only |
| Inspector | Assigned inspections / state-LGA scope |
| Food Handler | Own record only |

## 8.3 Scope Enforcement Rules

- Directory APIs must enforce scope in the backend.
- Frontend filters are not sufficient.
- Branch managers with `unit_restricted = true` must only see assigned branch records.
- State users must only see their state unless explicitly authorized.
- Facility users must only see facility-linked records.
- Federal users should see aggregate data by default and record-level data only if permitted.
- Exports must respect the same scope as table views.

---

# 9. Compliance Status Integration

## 9.1 Purpose

The Directory should display operational compliance fields from other modules without duplicating business logic.

The Directory Module should consume a shared `ComplianceStatusService`.

## 9.2 Food Handler Operational Status

For each food handler, directory should show:

- Certificate status
- Fitness status
- Vaccination status
- Assessment status
- Return-to-work status
- Employer linkage status
- Branch assignment status

## 9.3 Employer Compliance Summary

For each employer, directory should show:

- Total food handlers
- Certified food handlers
- Expired certificates
- Expiring certificates
- Uncertified food handlers
- Temporarily not fit
- Return-to-work pending
- Vaccination due
- Open inspection notices
- Compliance percentage

## 9.4 Branch Compliance Summary

For each branch, directory should show:

- Total food handlers
- Active certificates
- Expired certificates
- Suspended/revoked certificates
- Uncertified food handlers
- Temporarily not fit
- Vaccination due
- Open notices
- Inspection status
- Compliance percentage

## 9.5 Compliance Status Values

Recommended values:

- Compliant
- Partially Compliant
- Non-Compliant
- High Risk
- Unknown
- Not Applicable

---

# 10. Directory Privacy Requirements

## 10.1 Sensitive Fields

The following fields are sensitive:

- Full NIN
- Date of birth
- Phone number
- Email
- Home address
- Lab results
- Doctor notes
- Diagnosis
- Declaration answers
- Medical report
- Treatment notes
- Payment transaction references
- Settlement details

## 10.2 Role-Safe Serializers

The module must use separate serializers:

- Public-safe serializer
- Employer-safe serializer
- Inspector-safe serializer
- Facility-safe serializer
- State-regulatory serializer
- Federal-aggregate serializer
- Admin/internal serializer

## 10.3 Field Visibility Examples

### Employer View

Can see:

- Worker name
- Passport photo
- Certificate status
- Fitness status
- Vaccination status
- Expiry date
- Branch

Cannot see:

- Lab results
- Diagnosis
- Doctor notes
- Declaration answers
- Full NIN

### Inspector View

Can see:

- Worker name
- Passport photo
- Certificate status
- Fitness status
- Return-to-work status

Cannot see:

- Lab results
- Doctor notes
- Diagnosis
- Declaration answers
- Full NIN

### State View

Can see:

- Regulatory compliance data
- Certificate status
- Employer/branch linkage
- Assessment status summary

Sensitive medical details require additional medical/regulatory permission.

### Federal View

Aggregate by default. Record-level sensitive data requires explicit permission.

---

# 11. Directory Exports

## 11.1 Export Formats

The module should support:

- CSV
- Excel
- PDF summary report

## 11.2 Export Types

- Food handler directory export
- Employer directory export
- Branch directory export
- Certificate status export
- Compliance summary export
- Inspection status export

## 11.3 Export Rules

- Exports must respect filters.
- Exports must respect user scope.
- Exports must respect privacy serializer.
- Sensitive exports require explicit permission.
- Export action must be audit logged.
- Large exports should be background jobs.

## 11.4 Export Columns

Export columns should match the user’s allowed visible fields.

Do not export hidden/sensitive fields just because they exist in the database.

---

# 12. Directory Audit Logging

Audit logs should be created for:

- Sensitive search performed
- Full NIN search performed
- Food handler profile viewed by regulator
- Employer profile viewed by regulator
- Directory export generated
- Large export requested
- Sensitive field viewed
- Search results downloaded
- Cross-state search attempted
- Unauthorized directory access denied

Audit metadata:

- Actor
- Organization
- Role
- Search query
- Filters used
- Result count
- Export type
- Target entity type
- Timestamp
- IP address
- User agent

---

# 13. Data Model Approach

## 13.1 Do Not Create a Single Directory Table

Do not create one table called `Directory`.

Keep core models separate:

```txt
FoodHandlerProfile
Employer
OrganizationUnit
Certificate
MedicalAssessment
VaccinationReview / VaccinationRecord
Inspection
EnforcementNotice
EmployerSubscription
```

The Directory Module should expose a searchable API/service layer over those models.

## 13.2 Optional Denormalized Directory Index

For performance, a denormalized index may be used later.

Possible model:

```txt
DirectoryIndex
```

Used only for search optimization, not as the source of truth.

MVP can start with optimized queryset-based directory APIs.

---

# 14. Data Model Requirements

## 14.1 DirectorySavedView

Allows users to save commonly used filters.

```python
class DirectorySavedView(models.Model):
    id = models.UUIDField(primary_key=True)
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    organization = models.ForeignKey("organizations.Organization", null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255)
    directory_type = models.CharField(max_length=50)  # food_handlers, employers, branches, certificates
    filters = models.JSONField(default=dict)
    columns = models.JSONField(default=list)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 14.2 DirectoryExportJob

Handles large exports.

```python
class DirectoryExportJob(models.Model):
    id = models.UUIDField(primary_key=True)
    requested_by = models.ForeignKey("accounts.User", null=True, on_delete=models.SET_NULL)
    organization = models.ForeignKey("organizations.Organization", null=True, blank=True, on_delete=models.SET_NULL)
    directory_type = models.CharField(max_length=50)
    filters = models.JSONField(default=dict)
    columns = models.JSONField(default=list)
    status = models.CharField(max_length=50)
    file_url = models.URLField(blank=True)
    record_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
```

## 14.3 DirectorySearchLog

Logs sensitive or auditable searches.

```python
class DirectorySearchLog(models.Model):
    id = models.UUIDField(primary_key=True)
    user = models.ForeignKey("accounts.User", null=True, blank=True, on_delete=models.SET_NULL)
    organization = models.ForeignKey("organizations.Organization", null=True, blank=True, on_delete=models.SET_NULL)
    directory_type = models.CharField(max_length=50)
    query = models.CharField(max_length=255, blank=True)
    filters = models.JSONField(default=dict)
    result_count = models.PositiveIntegerField(default=0)
    contained_sensitive_identifier = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

# 15. API Requirements

## 15.1 Food Handlers Directory APIs

```txt
GET /api/directory/food-handlers
GET /api/directory/food-handlers/:id
GET /api/directory/food-handlers/:id/compliance-summary
GET /api/directory/food-handlers/:id/certificates
GET /api/directory/food-handlers/:id/assessments
GET /api/directory/food-handlers/:id/inspections
```

## 15.2 Employers Directory APIs

```txt
GET /api/directory/employers
GET /api/directory/employers/:id
GET /api/directory/employers/:id/compliance-summary
GET /api/directory/employers/:id/branches
GET /api/directory/employers/:id/food-handlers
GET /api/directory/employers/:id/inspections
GET /api/directory/employers/:id/notices
```

## 15.3 Branches Directory APIs

```txt
GET /api/directory/branches
GET /api/directory/branches/:id
GET /api/directory/branches/:id/compliance-summary
GET /api/directory/branches/:id/food-handlers
GET /api/directory/branches/:id/certificates
GET /api/directory/branches/:id/inspections
```

## 15.4 Certificate Directory APIs

```txt
GET /api/directory/certificates
GET /api/directory/certificates/:id
```

## 15.5 Global Search API

```txt
GET /api/directory/global-search
```

Query parameters:

```txt
?q=
&type=
&state=
&lga=
&organization=
&employer=
&branch=
&status=
```

## 15.6 Saved Views APIs

```txt
GET    /api/directory/saved-views
POST   /api/directory/saved-views
GET    /api/directory/saved-views/:id
PATCH  /api/directory/saved-views/:id
DELETE /api/directory/saved-views/:id
POST   /api/directory/saved-views/:id/set-default
```

## 15.7 Export APIs

```txt
POST /api/directory/exports
GET  /api/directory/exports
GET  /api/directory/exports/:id
GET  /api/directory/exports/:id/download
```

---

# 16. API Filter Requirements

## 16.1 Common Filters

All directory list APIs should support:

```txt
?q=
?state=
?lga=
?date_from=
?date_to=
?status=
?page=
?page_size=
?sort=
```

## 16.2 Food Handler Filters

```txt
?employer=
?branch=
?certificate_status=
?fitness_status=
?vaccination_status=
?assessment_status=
?return_to_work_status=
?food_handler_category=
?expiry_window=
?facility=
```

## 16.3 Employer Filters

```txt
?establishment_category=
?business_type=
?compliance_status=
?inspection_status=
?notice_status=
?subscription_status=
?branch_count_min=
?branch_count_max=
?food_handler_count_min=
?food_handler_count_max=
```

## 16.4 Branch Filters

```txt
?employer=
?branch_status=
?compliance_status=
?inspection_status=
?notice_status=
?certificate_status=
```

## 16.5 Certificate Filters

```txt
?certificate_number=
?certificate_status=
?issue_date_from=
?issue_date_to=
?expiry_date_from=
?expiry_date_to=
?issuing_state=
?facility=
```

---

# 17. Frontend Routes

## 17.1 Directory Routes

```txt
/app/directory
/app/directory/food-handlers
/app/directory/food-handlers/[id]
/app/directory/employers
/app/directory/employers/[id]
/app/directory/employers/[id]/branches
/app/directory/employers/[id]/branches/[branch_id]
/app/directory/branches              # optional shortcut / filtered view
/app/directory/branches/[id]          # optional shortcut / filtered view
/app/directory/certificates
/app/directory/global-search
/app/directory/saved-views
/app/directory/exports
```

## 17.2 Role-Specific Aliases

The same module can be exposed through role-specific navigation.

### State Ministry

```txt
/app/state/directory/food-handlers
/app/state/directory/employers
/app/state/directory/branches
```

### Federal Ministry

```txt
/app/federal/directory/food-handlers
/app/federal/directory/employers
/app/federal/directory/branches
```

### Employer

```txt
/app/employer/directory/food-handlers
/app/employer/directory/branches  # employer-owned branches/outlets
```

### Inspector

```txt
/app/inspector/directory/employers
/app/inspector/directory/branches # assigned/searchable employer locations
```

### Medical Facility

```txt
/app/facility/directory/food-handlers
```

---

# 18. Frontend Components

Build reusable components:

- DirectoryLayout
- DirectorySearchBar
- DirectoryFilterPanel
- DirectoryTable
- DirectoryColumnSelector
- DirectorySavedViewSelector
- DirectoryExportButton
- FoodHandlerDirectoryTable
- FoodHandlerDirectoryDetail
- EmployerDirectoryTable
- EmployerDirectoryDetail
- BranchDirectoryTable
- BranchDirectoryDetail
- CertificateDirectoryTable
- GlobalSearchResults
- ComplianceStatusBadge
- CertificateStatusBadge
- FitnessStatusBadge
- VaccinationStatusBadge
- InspectionStatusBadge
- SubscriptionStatusBadge
- DirectoryPrivacyNotice
- SensitiveFieldRevealButton
- DirectoryAuditNotice
- ExportJobStatusCard

---

# 19. UX Requirements

## 19.1 Directory Landing Page

The landing page should show cards:

- Food Handlers Directory
- Employers Directory
- Employer Branches / Outlets View
- Certificate Search
- Global Search
- Saved Views
- Recent Exports

## 19.2 Table UX

Directory tables should support:

- Search
- Filters
- Sort
- Pagination
- Column selection
- Saved views
- Export
- Row detail drawer
- Bulk selection, where permitted

## 19.3 Detail Pages

Each detail page should show:

- Summary card
- Status badges
- Related records
- Timeline/history
- Available actions
- Privacy notice

## 19.4 Empty States

Examples:

```txt
No food handlers found for the selected filters.
No employers match this search.
No branches have been created yet.
No certificates found.
```

## 19.5 Sensitive Field Reveal

For authorized users only:

- Show masked sensitive field by default.
- Allow reveal with reason.
- Log reveal action.

Example:

```txt
Masked NIN: 1234******89
[Reveal full NIN]
Reason required before reveal.
```

---

# 20. Permissions

## 20.1 Directory Permissions

Recommended permission codes:

```txt
directory.view
directory.food_handler.view
directory.food_handler.export
directory.food_handler.view_sensitive
directory.employer.view
directory.employer.export
directory.branch.view
directory.branch.export
directory.certificate.view
directory.global_search
directory.saved_view.create
directory.export.create
directory.export.download
directory.sensitive_search
```

## 20.2 Permission Rules

- Users can only see directory views allowed by their role.
- Users can only export records they can view.
- Sensitive fields require explicit permission.
- Sensitive searches require audit logging.
- Global search requires permission.
- Directory views must apply organization/unit/state scope.

---

# 21. Backend Services

## 21.1 Required Services

Implement:

- DirectoryScopeService
- FoodHandlerDirectoryService
- EmployerDirectoryService
- BranchDirectoryService
- CertificateDirectoryService
- GlobalSearchService
- DirectoryExportService
- DirectorySavedViewService
- DirectoryAuditService
- DirectorySerializerSelector

## 21.2 DirectoryScopeService

Responsibilities:

- Determine user scope.
- Apply state/LGA filters.
- Apply organization filters.
- Apply branch/unit filters.
- Prevent cross-scope access.
- Return filtered querysets.

## 21.3 DirectorySerializerSelector

Responsibilities:

- Select serializer based on user role and view.
- Hide sensitive fields.
- Mask NIN.
- Hide medical fields.
- Apply employer-safe, inspector-safe, state-safe, or federal-safe formats.

## 21.4 GlobalSearchService

Responsibilities:

- Search across allowed entity types.
- Apply scope per entity.
- Group results by type.
- Return safe snippets only.
- Log sensitive searches.

---

# 22. Performance Requirements

## 22.1 Pagination

All directory endpoints must be paginated.

Default:

```txt
page_size = 25
```

Maximum:

```txt
page_size = 100
```

## 22.2 Indexing

Add database indexes for commonly filtered fields:

- state_id
- lga_id
- employer_id
- branch_id
- certificate_status
- fitness_status
- vaccination_status
- assessment_status
- inspection_status
- created_at
- updated_at

## 22.3 Search

For MVP:

- Use database search with indexed fields.
- Add trigram/full-text search where available.

Future:

- Elasticsearch/OpenSearch if dataset becomes very large.

## 22.4 Large Exports

Large exports should be processed asynchronously.

Export job statuses:

- Pending
- Processing
- Completed
- Failed
- Expired

---

# 23. Background Jobs

## 23.1 Export Processing Job

Tasks:

- Process large export.
- Apply filters and scope.
- Generate file.
- Store file.
- Notify user.
- Log export.

## 23.2 Export Cleanup Job

Tasks:

- Delete expired export files.
- Mark export job expired.
- Retain audit log.

## 23.3 Directory Index Refresh Job

Optional/future.

Tasks:

- Refresh denormalized search index.
- Recalculate compliance summary fields.
- Update stale directory cache.

---

# 24. Cross-Module Dependencies

## 24.1 Stakeholder Management Module

Required for:

- Organization scope
- Unit/branch scope
- Membership permissions
- User roles
- Branch manager restrictions

## 24.2 Employer Module

Required for:

- Employer profile
- Employer category
- Employer branches
- Employer users
- Employer subscription status

## 24.3 Food Handler / Identity Module

Required for:

- Food handler profile
- Identity fields
- Employer linkage
- Branch assignment

## 24.4 Certificate Module

Required for:

- Certificate status
- Certificate number
- Issue/expiry dates
- QR verification status

## 24.5 Medical Assessment Module

Required for:

- Assessment status
- Last assessment date
- Facility linkage
- Doctor decision status, privacy-safe

## 24.6 Medical Facility Module

Required for:

- Facility-linked food handlers
- Facility assessments
- Facility performance directory views

## 24.7 Inspector & Enforcement Module

Required for:

- Inspection status
- Notice status
- Enforcement history

## 24.8 Payments Module

Required for:

- Employer subscription status, read-only
- Assessment payment status, limited/read-only
- No transaction detail exposure by default

## 24.9 Reports & M&E Module

Consumes directory filters for:

- State reports
- Federal reports
- Employer compliance reports
- Facility reports
- Inspection reports

---

# 25. Implementation Chunks for Codex

## Chunk 0: Directory UI Consolidation

### Goal

Ensure Directory & Registry appears as one parent module with organized internal views, not scattered standalone modules.

### Frontend Tasks

- Add one parent navigation item: `Directory & Registry`.
- Add internal tabs/sub-navigation:
  - Overview
  - Food Handlers
  - Employers / Food Businesses
  - Certificates
  - Global Search
  - Saved Views
  - Exports
- Place Branches / Outlets / Sites under Employers / Food Businesses.
- Add employer detail tabs:
  - Employer Profile
  - Branches / Outlets / Sites
  - Food Handlers
  - Certificates
  - Inspections
  - Notices
  - Compliance Summary
  - Subscription
  - Audit Logs
- If a `/directory/branches` page already exists, convert it into a shortcut/filtered view for employer locations, not a separate peer module.
- Update breadcrumbs so branch pages read as employer location views.

### Backend Tasks

- No new core backend module is required for UI consolidation.
- Ensure branch/outlet APIs use Employer + OrganizationUnit service logic.
- Ensure branch/outlet scope is enforced through employer organization and unit scope.

### Acceptance Criteria

- Directory & Registry appears as a single parent module.
- Food Handlers, Employers, Certificates, Global Search, Saved Views, and Exports appear as organized views/tabs.
- Branches / Outlets / Sites appear under Employers / Food Businesses.
- Any branch shortcut route is clearly treated as a filtered employer-location view.
- No duplicate Branches module is created.

## Chunk 1: Directory Module Foundation

### Goal

Create the base directory module structure and shared services.

### Backend Tasks

- Create `directory` backend app/module.
- Add directory route namespace.
- Create base service classes:
  - `DirectoryScopeService`
  - `DirectorySerializerSelector`
  - `DirectoryAuditService`
- Add base permissions:
  - `directory.view`
  - `directory.global_search`
  - `directory.export.create`
- Add shared filter utilities.
- Add pagination defaults.

### Frontend Tasks

- Create `/app/directory` route.
- Create `DirectoryLayout`.
- Create directory landing page.
- Create shared components:
  - `DirectorySearchBar`
  - `DirectoryFilterPanel`
  - `DirectoryTable`
  - `DirectoryPrivacyNotice`

### Acceptance Criteria

- Directory module exists.
- Authenticated users with permission can access directory landing page.
- Users without permission are denied.
- Base layout and routing are implemented.
- Scope service can identify user organization and unit scope.

---

## Chunk 2: Food Handlers Directory API and UI

### Goal

Implement searchable and filterable Food Handlers Directory.

### Backend Tasks

- Implement `FoodHandlerDirectoryService`.
- Add endpoints:

```txt
GET /api/directory/food-handlers
GET /api/directory/food-handlers/:id
```

- Add filters:
  - state
  - lga
  - employer
  - branch
  - certificate_status
  - fitness_status
  - vaccination_status
  - assessment_status
  - return_to_work_status
  - food_handler_category
  - facility
- Add role-safe serializers:
  - employer-safe
  - inspector-safe
  - state-safe
  - federal-safe
- Mask NIN.
- Hide medical fields.
- Add audit logging for sensitive views.

### Frontend Tasks

- Create `/app/directory/food-handlers`.
- Create `FoodHandlerDirectoryTable`.
- Create `FoodHandlerDirectoryDetail`.
- Add filter panel.
- Add status badges.
- Add empty/loading/error states.

### Acceptance Criteria

- Authorized users can list food handlers.
- Results are scoped correctly.
- Employer sees only own food handlers.
- Branch manager sees only assigned branch.
- Medical fields are hidden.
- Filters work.
- Detail page is privacy-safe.

---

## Chunk 3: Employers Directory API and UI

### Goal

Implement searchable and filterable Employers Directory.

### Backend Tasks

- Implement `EmployerDirectoryService`.
- Add endpoints:

```txt
GET /api/directory/employers
GET /api/directory/employers/:id
```

- Add filters:
  - state
  - lga
  - establishment_category
  - compliance_status
  - inspection_status
  - notice_status
  - subscription_status
  - date_registered
- Add employer compliance summary integration.
- Add role-safe serializers.

### Frontend Tasks

- Create `/app/directory/employers`.
- Create `EmployerDirectoryTable`.
- Create `EmployerDirectoryDetail`.
- Add employer compliance cards.
- Add filter panel.
- Add status badges.

### Acceptance Criteria

- Authorized users can search employers.
- State users see only state employers.
- Federal users can see national employer summaries.
- Employer users cannot see other employers.
- Subscription status is read-only and permission-based.
- Compliance summaries display correctly.

---

## Chunk 4: Employer Branches / Outlets View

### Goal

Implement branch/outlet/location search as a sub-view of Employers / Food Businesses using `OrganizationUnit`. This should support employer detail tabs and an optional shortcut route for cross-location search.

### Backend Tasks

- Implement `BranchDirectoryService`.
- Add endpoints:

```txt
GET /api/directory/branches
GET /api/directory/branches/:id
```

- Filter OrganizationUnit by:
  - `unit_type = branch/outlet/site/store/regional_office`
- Add branch compliance summary.
- Apply employer and branch scope rules.

### Frontend Tasks

- Create `/app/directory/employers/[id]/branches`.
- Create `/app/directory/employers/[id]/branches/[branch_id]`.
- Optionally keep `/app/directory/branches` as a shortcut/filtered view.
- Create `EmployerBranchesTable`.
- Create `BranchDirectoryDetail`.
- Add branch compliance summary.
- Add branch food handler tab.
- Add branch inspection tab.

### Acceptance Criteria

- Employer admin can view all own branches.
- Branch manager can view only assigned branch.
- State user can view branches in state.
- Branch compliance summary displays correctly.
- Branch/outlet view uses OrganizationUnit, not a duplicate branch model.
- Branches/outlets are shown as employer sub-units, not as a separate peer module.

---

## Chunk 5: Certificate Directory Search

### Goal

Expose certificate search through the Directory Module while keeping Certificate Module as source of truth.

### Backend Tasks

- Implement `CertificateDirectoryService`.
- Add endpoints:

```txt
GET /api/directory/certificates
GET /api/directory/certificates/:id
```

- Add filters:
  - certificate_number
  - certificate_status
  - issuing_state
  - facility
  - issue_date
  - expiry_date
- Use certificate-safe serializer.
- Hide medical data.

### Frontend Tasks

- Create `/app/directory/certificates`.
- Create `CertificateDirectoryTable`.
- Add certificate status filters.
- Add link to certificate verification/detail page.

### Acceptance Criteria

- Certificate search works.
- Public/private fields are separated.
- State users see certificates in their state.
- Federal users see registry according to permission.
- Employers see linked worker certificates only.

---

## Chunk 6: Global Search

### Goal

Implement unified global search across directory entities.

### Backend Tasks

- Implement `GlobalSearchService`.
- Add endpoint:

```txt
GET /api/directory/global-search
```

- Search allowed entities:
  - food handlers
  - employers
  - branches
  - certificates
  - inspections
  - notices
- Apply role scope per entity type.
- Return grouped results.
- Log sensitive searches.

### Frontend Tasks

- Create `/app/directory/global-search`.
- Create `GlobalSearchResults`.
- Group results by entity type.
- Add safe snippets only.
- Add no-results state.

### Acceptance Criteria

- Search results respect user scope.
- Sensitive fields are not shown in snippets.
- Global search works across multiple entity types.
- Unauthorized entities are excluded.
- Sensitive searches are audit logged.

---

## Chunk 7: Saved Views

### Goal

Allow users to save common directory filters and column preferences.

### Backend Tasks

- Add `DirectorySavedView` model.
- Add endpoints:
  - create
  - list
  - update
  - delete
  - set default
- Validate directory type.
- Store filters and columns.

### Frontend Tasks

- Create `DirectorySavedViewSelector`.
- Allow save current filters.
- Allow apply saved view.
- Allow set default view.

### Acceptance Criteria

- User can save a directory view.
- User can apply saved filters.
- User can set default view.
- Saved views are user-scoped.
- Invalid filters are rejected.

---

## Chunk 8: Directory Exports

### Goal

Implement role-safe export system.

### Backend Tasks

- Add `DirectoryExportJob` model.
- Add export endpoints:
  - create export
  - list exports
  - download export
- Build `DirectoryExportService`.
- Export CSV for MVP.
- Apply filters, scope, and serializer.
- Audit export.
- Add background job support for large exports.

### Frontend Tasks

- Create `DirectoryExportButton`.
- Create `/app/directory/exports`.
- Create `ExportJobStatusCard`.
- Show export progress/status.
- Provide download link when complete.

### Acceptance Criteria

- Users can export allowed directory records.
- Export respects filters.
- Export respects scope.
- Export excludes hidden sensitive fields.
- Large export runs in background.
- Export action is audit logged.

---

## Chunk 9: Sensitive Search and Field Reveal

### Goal

Implement safe handling of sensitive identifiers like full NIN.

### Backend Tasks

- Add sensitive search detection.
- Require `directory.sensitive_search` permission for full NIN search.
- Add sensitive field reveal endpoint where needed.
- Require reason for reveal.
- Audit reveal.

### Frontend Tasks

- Add `SensitiveFieldRevealButton`.
- Show masked fields by default.
- Require reason modal before reveal.
- Show audit notice.

### Acceptance Criteria

- Full NIN is masked by default.
- Unauthorized users cannot search full NIN.
- Authorized reveal requires reason.
- Reveal is audit logged.
- Sensitive data is not exported unless explicitly permitted.

---

## Chunk 10: Role-Specific Directory Navigation

### Goal

Expose directory pages through relevant portals.

### Backend Tasks

- Update navigation service permissions.
- Add route permissions.
- Add role-to-directory mapping.

### Frontend Tasks

- Add State directory links.
- Add Federal directory links.
- Add Employer directory links.
- Add Facility directory links.
- Add Inspector directory links.
- Ensure labels match role context.

### Acceptance Criteria

- State users see state directory pages.
- Federal users see national directory pages.
- Employers see own food handler/branch directory.
- Facilities see facility-linked food handler directory.
- Inspectors see assigned employer/branch directory.
- Navigation respects permissions.

---

## Chunk 11: Compliance Summary Integration

### Goal

Connect directory rows to shared compliance summary service.

### Backend Tasks

- Implement or integrate:
  - `ComplianceStatusService.get_food_handler_operational_status`
  - `ComplianceStatusService.get_employer_compliance_summary`
  - `ComplianceStatusService.get_branch_compliance_summary`
- Add summary fields to directory rows.
- Cache where necessary.

### Frontend Tasks

- Add compliance cards to detail pages.
- Add compliance badges to tables.
- Add compliance filters.

### Acceptance Criteria

- Food handler rows show correct operational status.
- Employer rows show compliance percentage.
- Branch rows show compliance percentage.
- Filters work on compliance status.
- Directory does not duplicate compliance logic.

---

## Chunk 12: Tests and Hardening

### Goal

Complete test coverage and security hardening.

### Backend Tests

Add tests for:

- Food handler directory scope
- Employer directory scope
- Branch manager branch restriction
- State user state restriction
- Facility user facility-linked restriction
- Inspector assigned inspection scope
- Federal aggregate permissions
- Sensitive field masking
- Sensitive search permission
- Export privacy
- Saved views
- Global search scope
- Audit logs

### Frontend Tests

Add tests for:

- Directory table rendering
- Filter behavior
- Empty states
- Permission denied states
- Sensitive field reveal UI
- Export button visibility
- Saved view flow
- Role-specific navigation

### Acceptance Criteria

- All directory endpoints enforce backend permissions.
- Privacy tests pass.
- Scope tests pass.
- Export tests pass.
- Unauthorized access returns appropriate error.
- No sensitive fields leak in unauthorized serializers.

---

# 26. Acceptance Criteria

## 26.1 Food Handlers Directory

- Authorized users can search food handlers.
- Filters work.
- Results are scoped by role.
- Employer sees only own food handlers.
- Branch manager sees only assigned branch.
- Sensitive medical data is hidden.
- NIN is masked.

## 26.2 Employers Directory

- Authorized users can search employers.
- State users see employers in their state.
- Federal users see national employer records according to permission.
- Employer users cannot see other employers.
- Compliance summaries display.
- Subscription status is read-only and permission-based.

## 26.3 Branches Directory

- Branches use OrganizationUnit.
- Employer admin sees own branches.
- Branch manager sees only assigned branch.
- State users see branches in state.
- Branch compliance summary works.

## 26.4 Global Search

- Global search returns grouped results.
- Results respect scope.
- Sensitive fields do not appear in snippets.
- Sensitive searches are audit logged.

## 26.5 Export

- Export respects filters and scope.
- Export excludes hidden sensitive fields.
- Export jobs can be downloaded when complete.
- Export actions are audit logged.

## 26.6 Privacy

- Employers cannot see medical details.
- Inspectors cannot see medical details.
- Public users cannot access directory data.
- Full NIN is hidden unless explicitly authorized.
- Sensitive field reveal is audit logged.

---

# 27. Codex Implementation Prompt

Use this prompt for Codex:

```txt
Implement the Directory & Registry Module for FoodCert NG.

The module must provide one shared directory engine with separate views for Food Handlers, Employers/Food Businesses, Certificates, and Global Search. Branches/Outlets/Sites must be handled as sub-views under Employers/Food Businesses, with an optional shortcut/filtered branch view.

Important rules:
- Do not create one database table as the source of truth for directory records.
- Use existing models: FoodHandlerProfile, Employer, OrganizationUnit, Certificate, MedicalAssessment, Inspection, EnforcementNotice, and EmployerSubscription.
- Directory APIs must be read/search/reporting APIs over existing modules.
- Directory access must be scoped by Role + Organization + Unit + State/LGA + Permission.
- Backend must enforce scope; frontend filters are not enough.
- Use separate serializers for employer-safe, inspector-safe, state-safe, federal-safe, and admin/internal views.
- Employers must not see lab results, diagnosis, doctor notes, declaration answers, or full NIN.
- Inspectors must not see lab results, diagnosis, doctor notes, declaration answers, or full NIN.
- Federal views should be aggregate or permission-controlled.
- Food Handlers Directory, Employers Directory, Employer Branches/Outlets sub-view, Certificate Directory, Saved Views, Exports, and Global Search must be implemented.
- Exports must respect filters, permissions, scope, and privacy rules.
- Sensitive searches and sensitive field reveals must be audit logged.
- Compliance summary fields should come from a shared ComplianceStatusService, not duplicated inside the directory module.

Build backend services, serializers, permissions, endpoints, frontend pages, reusable components, saved views, export jobs, audit logs, tests, and role-specific navigation for the module.
```

---

# 28. MVP Build Order Summary

0. Directory UI consolidation
1. Directory module foundation
2. Food Handlers Directory
3. Employers Directory
4. Employer Branches / Outlets sub-view
5. Certificate Directory Search
6. Global Search
7. Saved Views
8. Directory Exports
9. Sensitive Search and Field Reveal
10. Role-Specific Directory Navigation
11. Compliance Summary Integration
12. Tests and Security Hardening
