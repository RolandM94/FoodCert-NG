# Employers Module — Implementation Plan

## Audit Summary

| Component | Status |
|-----------|--------|
| Employer model + CRUD | Done |
| `employers/services.py` service layer | Done |
| `employers/permissions.py` role/scoping helpers | Done |
| Employer-scoped API endpoints | Done |
| Employer staff roles: admin, branch manager, compliance, finance | Done |
| Branch management and branch detail | Done |
| Business profile and employer registration | Done |
| Food handler list, filters, privacy-safe fields, and row actions | Done — final QA polish added |
| Food handler invite, bulk upload, existing-handler link, branch reassignment | Done |
| Certificate and vaccination monitoring | Done |
| Illness reporting and return-to-work monitoring | Done |
| Subscription, plan change, invoices, and payments | Done |
| Inspection history, detail, and employer responses | Done |
| Compliance reports and privacy-safe exports | Done |
| Employer user management and invite management | Done |
| Dashboard, charts, branch scope, settings, and notifications | Done |
| Backend employer tests and privacy/workflow coverage | Done — consolidated in `backend/apps/employers/tests.py` |

### Final QA Status

Final product-polish pass completed:

- Removed stale placeholder/sample-data surfaces from employer pages and shared portal wrappers.
- Added food handler list filters for branch, category, fitness status, certificate status, and expiry window.
- Added food handler row actions for certificate verification, illness reporting, and branch reassignment.
- Added backend support and regression coverage for employer food handler operational filters.
- Scoped frontend lint to `src` to avoid generated build artifacts.
- Current verification target: `apps.employers` backend tests, frontend typecheck/lint/build.

---

## Build Order

```
Chunk E1 → Chunk E2 → Chunk E3 → Chunk E4 → Chunk E5
  │           │           │           │           │
  ▼           ▼           ▼           ▼           ▼
Profile    Food        Onboard    Cert/Vax   Illness
+Reg      Handlers    (invite,    Monitor    +Return
          List        bulk,link)            to Work

Chunk E6 → Chunk E7 → Chunk E8 → Chunk E9 → Chunk E10
  │           │           │           │           │
  ▼           ▼           ▼           ▼           ▼
Subscrip   Inspect    Reports    User       Dashboard
+Billing   History    +Export    Mgmt       Enhance
```

Each chunk produces a working, testable increment. You can stop after any chunk.

---

## Chunk E1: Employer Registration & Profile

### Goal
Employer can register a business account, create a business profile, and edit profile details.

### Backend
- Create `backend/apps/employers/services.py` — `EmployerService` with:
  - `register_business(actor, **data)` — creates employer profile linked to user + organization
  - `update_profile(employer, **data)` — validates and updates profile fields
  - `get_profile_for_user(user)` — returns employer profile for current user
- Create `backend/apps/employers/permissions.py`:
  - `IsEmployerOwner` — only the employer owner/admin
  - `IsBranchManager` — employer user with unit_restricted
  - `IsComplianceOfficer` — employer user with compliance officer scope
- Add `business_type` field to Employer model (migration)
- Add `GET /api/employers/me` endpoint on EmployerViewSet
- Add `is_active` field to Employer model (migration)
- Refactor `perform_create` and `perform_update` to use service layer

### Frontend
- Replace `frontend/src/app/employer/business-profile/page.tsx` — real form with:
  - Business name, registration number
  - Establishment category dropdown (20+ categories)
  - Contact person name, phone, email
  - Address, state, LGA, ward
  - Estimated number of food handlers
  - Save button with loading/error states
- Update `frontend/src/app/register/page.tsx` — add "Register as Employer" tab/option:
  - Account creation (name, email, phone, password)
  - Business profile creation (inline after account)
  - Subscription plan selection (redirect to billing)
- Build `EmployerProfileForm` component with react-hook-form + zod validation
- Add employer-specific fields to registration API call

### Files
| Backend | Frontend |
|---------|----------|
| `employers/services.py` (new) | `employer/business-profile/page.tsx` (replace) |
| `employers/permissions.py` (new) | `register/page.tsx` (update) |
| `employers/views.py` (update) | `features/employer/profile-form.tsx` (new) |
| `employers/models.py` (update — business_type, is_active) | |
| `employers/serializers.py` (update) | |
| Migration (auto-generated) | |

---

## Chunk E2: Food Handler List Page

### Goal
Employer sees all their food handlers with fitness status, certificate status, vaccination status, and can filter by branch/category/status.

### Backend
- Add `GET /api/employers/{id}/food-handlers` endpoint:
  - Returns scoped list based on user's role (head office sees all, branch manager sees branch only)
  - Supports query params: `branch`, `category`, `fitness_status`, `certificate_status`, `expiry_window`
  - Returns employer-visible fields only (no lab results, doctor notes, NIN)
- Extend `EmployerFoodHandlerSerializer` with computed fitness status mapping:
  - Maps internal `FoodHandlerStatus` + `CertificateStatus` to employer-visible categories (PRD Section 12.1)
  - Adds `certificate_number`, `certificate_expiry_date`, `vaccination_summary` as read-only computed fields

### Frontend
- Replace `frontend/src/app/employer/food-handlers/page.tsx` — real data table:
  - Columns: name, photo, branch, category, fitness status badge, certificate status, vaccination status, last assessment, actions
  - Row actions dropdown: view operational status, view certificate, report illness, reassign branch, remove
- Build `FitnessStatusBadge` component:
  - Fit to Handle Food (green)
  - Certification Pending (amber)
  - Certificate Expired (red)
  - Temporarily Not Fit (orange)
  - Excluded from Food Handling (red)
  - Return-to-Work Pending (amber)
  - Cleared to Return (green)
  - Vaccination Due (blue)
- Build filter bar: branch selector, category dropdown, status dropdown, expiry window radio
- Branch manager sees only their branch — branch filter locked

### Files
| Backend | Frontend |
|---------|----------|
| `employers/views.py` (update — add food_handler list action) | `employer/food-handlers/page.tsx` (replace) |
| `employers/serializers.py` (update — extended food handler serializer) | `components/ui/fitness-status-badge.tsx` (new) |
| `employers/services.py` (update — food handler query service) | |

---

## Chunk E3: Food Handler Onboarding

### Goal
Employer can invite food handlers, bulk upload via CSV, and link existing certified handlers.

### Backend
- Add `POST /api/employers/{id}/food-handlers/invite`:
  - Accepts: email, phone, food_handler_category, branch (pre-selected)
  - Creates UserInvite with role=food_handler, unit=branch
  - Sends email/SMS notification
- Add `POST /api/employers/{id}/food-handlers/bulk-upload`:
  - Accepts CSV file upload
  - Validates: required columns present, duplicates, invalid branches, invalid categories
  - Returns preview with error rows flagged
  - On confirm, creates UserInvite for each valid row
- Add `POST /api/employers/{id}/food-handlers/link`:
  - Search by phone, certificate number, or food handler ID
  - Send link request to food handler
  - Food handler approves — employer sees operational status
- Add `PATCH /api/employers/{id}/food-handlers/{fh_id}/branch`:
  - Reassign food handler to a different branch
  - Head office only (branch manager cannot move handlers between branches)

### Frontend
- Replace `frontend/src/app/employer/food-handlers/invite/page.tsx`:
  - `InviteFoodHandlerModal` — email, phone, role pre-set, food handler category dropdown, branch selector (pre-filled for branch managers), message
- Create `frontend/src/app/employer/food-handlers/import/page.tsx`:
  - File upload area (drag-and-drop CSV)
  - Preview table with validation status per row
  - Error flags: missing name, duplicate phone, invalid branch
  - Fix errors inline or remove rows
  - Confirm import button
- Create `frontend/src/app/employer/food-handlers/link/page.tsx`:
  - Search bar (phone / certificate number / ID)
  - Search results with food handler name, current status
  - "Request Link" button per result
  - Pending link requests table
- Build `BulkUploadFoodHandlers` component with file parsing and preview

### Files
| Backend | Frontend |
|---------|----------|
| `employers/views.py` (update — invite, bulk, link actions) | `employer/food-handlers/invite/page.tsx` (replace) |
| `employers/serializers.py` (update — invite, bulk serializers) | `employer/food-handlers/import/page.tsx` (new) |
| `employers/services.py` (update — bulk upload service) | `employer/food-handlers/link/page.tsx` (new) |
| `employers/urls.py` (update) | `components/ui/bulk-upload-food-handlers.tsx` (new) |

---

## Chunk E4: Certificate & Vaccination Monitoring

### Goal
Employer has dedicated pages for certificate compliance and vaccination tracking with metrics, filters, and export.

### Backend
- Add `GET /api/employers/{id}/certificates`:
  - Returns certificate list filtered by branch, status, expiry window
  - Metrics: total, active, expired, expiring 30d, expiring 7d, pending, revoked
  - Employer-visible serializer (certificate number, handler, branch, facility, dates, status — no medical data)
- Add `GET /api/employers/{id}/vaccinations`:
  - Returns per-handler vaccination status (typhoid + hepatitis A)
  - Metrics: typhoid valid, typhoid expired, hepA dose1, hepA dose2 pending, hepA complete
  - Employer-visible serializer (handler, branch, vaccine type, status, dates — no clinical notes)
- Add `POST /api/employers/{id}/food-handlers/{fh_id}/send-renewal-reminder`:
  - Sends notification to food handler about expiring certificate or vaccination

### Frontend
- Create `frontend/src/app/employer/certificates/page.tsx`:
  - Metrics cards row: total, active, expired, expiring 30d, expiring 7d, pending
  - Data table: handler, branch, certificate number, issuing state, facility, issue date, expiry date, status badge, actions
  - Actions: view, download, verify, send renewal reminder
  - Export button (CSV/PDF)
- Replace `frontend/src/app/employer/vaccinations/page.tsx`:
  - Metrics cards: typhoid valid, typhoid expired, hepA dose1, hepA dose2 pending, hepA complete, missing
  - Data table: handler, branch, typhoid status + date, hepA dose1 + date, hepA dose2 + date, next due, actions
  - Actions: send vaccination reminder, export report
- Build `CertificateStatusBadge` component (active/expired/revoked/suspended/pending colors)
- Build `VaccinationStatusBadge` component (valid/expired/due/missing colors)

### Files
| Backend | Frontend |
|---------|----------|
| `employers/views.py` (update — certificates, vaccinations actions) | `employer/certificates/page.tsx` (new) |
| `employers/serializers.py` (update) | `employer/vaccinations/page.tsx` (replace) |
| `employers/urls.py` (update) | `components/ui/certificate-status-badge.tsx` (new) |
| | `components/ui/vaccination-status-badge.tsx` (new) |

---

## Chunk E5: Illness Reporting & Return-to-Work

### Goal
Employer can report illness for a food handler, see exclusion status, and monitor return-to-work clearance.

### Backend
- Add `POST /api/employers/{id}/illness-reports`:
  - Accepts: food_handler, branch, symptoms (checkboxes), symptom_start_date, notes, exclusion_confirmed
  - Sets food_handler status to TEMPORARILY_EXCLUDED
  - Creates IllnessReport record
  - Sends notification to food handler and doctor
- Add `GET /api/employers/{id}/illness-reports`:
  - Filtered by branch, status, date range
  - Returns employer-visible fields: handler, branch, symptoms summary, date, exclusion status, return-to-work status
- Add `GET /api/employers/{id}/illness-reports/{report_id}`:
  - Full detail with return-to-work status timeline
- Add `GET /api/employers/{id}/return-to-work`:
  - List of handlers currently excluded or awaiting clearance
  - Return-to-work dates where calculated

### Frontend
- Replace `frontend/src/app/employer/illness-reports/page.tsx`:
  - Illness report list: handler, branch, symptoms, date reported, status, return-to-work status
  - "Report Illness" button opens modal/form
- Build `IllnessReportForm` component:
  - Food handler selector (filtered by employer's handlers)
  - Branch auto-filled
  - Symptom checkboxes: jaundice, diarrhoea, vomiting, fever, sore throat, skin lesions, discharge, cough/flu, other
  - Symptom start date
  - Notes
  - "Yes, exclude from food handling" confirmation checkbox
- Build return-to-work status display on illness list rows:
  - Excluded (red) / Awaiting Review (amber) / Awaiting Clearance (amber) / Cleared (green)
- Replace `frontend/src/app/employer/compliance/page.tsx`:
  - Return-to-work tracking table
  - Excluded handlers list
  - Clearance status monitoring

### Files
| Backend | Frontend |
|---------|----------|
| `employers/views.py` (update — illness report actions) | `employer/illness-reports/page.tsx` (replace) |
| `employers/serializers.py` (update) | `employer/compliance/page.tsx` (replace) |
| `employers/urls.py` (update) | `components/ui/illness-report-form.tsx` (new) |
| | `components/ui/return-to-work-status.tsx` (new) |

---

## Chunk E6: Subscription & Billing

### Goal
Employer can view plans, subscribe, change plans, view invoices, and see payment history.

### Backend
- Add `POST /api/employers/{id}/subscription/checkout`:
  - Accepts plan_id, billing_cycle
  - Creates PaymentTransaction via provider abstraction
  - On success, activates EmployerSubscription
- Add `PATCH /api/employers/{id}/subscription/change-plan`:
  - Accepts new plan_id, billing_cycle
  - Calculates proration if needed
  - Updates subscription record
- Add `GET /api/employers/{id}/invoices`:
  - List of invoice records (date, amount, status, download link)
- Add `GET /api/employers/{id}/payments`:
  - Payment history (date, amount, provider, status, receipt)
- Add `GET /api/employers/{id}/subscription`:
  - Current plan, usage (handlers used / max), next billing date, status, renewal date

### Frontend
- Replace `frontend/src/app/employer/subscription/page.tsx`:
  - Current plan card: plan name, features list, usage bar (handlers used / max allowed), billing cycle, next billing date, status badge
  - Upgrade/downgrade section: plan comparison cards (Basic/Standard/Enterprise with feature checkmarks), "Change Plan" button
  - Billing history table: invoice #, date, amount, status, receipt download link
  - Payment history table: date, amount, provider reference, status
- Build `SubscriptionPlanCard` component (already partially exists — enhance)
- Add subscription expiry warning banner to dashboard (when ≤7 days to expiry)
- Grace period UX: expired subscriptions show what's restricted vs still accessible

### Files
| Backend | Frontend |
|---------|----------|
| `employers/views.py` (update — subscription/billing actions) | `employer/subscription/page.tsx` (replace) |
| `employers/serializers.py` (update) | `components/ui/subscription-plan-card.tsx` (update) |
| `employers/urls.py` (update) | |
| `subscriptions/views.py` (update — checkout endpoint) | |
| `subscriptions/services.py` (update — change plan logic) | |

---

## Chunk E7: Inspection History & Response

### Goal
Employer can view inspection history, see findings, respond with corrective actions, and upload evidence.

### Backend
- Add `GET /api/employers/{id}/inspections`:
  - Filtered by branch, status, date range
  - Returns employer-visible fields: date, inspector, branch, score, findings summary, enforcement action, status, follow-up date
- Add `GET /api/employers/{id}/inspections/{inspection_id}`:
  - Full detail: checklist responses, findings, evidence files, enforcement notice, response history
- Add `POST /api/employers/{id}/inspections/{inspection_id}/responses`:
  - Accepts: response_type (acknowledge/corrective_action/evidence/comment), content, file upload
  - Creates InspectionResponse record
  - Updates inspection status to "Employer Response Submitted"
- Add `InspectionResponse` model (or extend existing Inspection model with response fields)

### Frontend
- Replace `frontend/src/app/employer/inspections/page.tsx`:
  - Inspection list: date, inspector, branch, compliance score (colored), findings (truncated), enforcement action badge, status, follow-up date, actions
- Create `frontend/src/app/employer/inspections/[id]/page.tsx`:
  - Inspection metadata header (date, inspector, branch, score)
  - Checklist responses section (question + Yes/No/NA with evidence indicator)
  - Findings section
  - Evidence files section (thumbnails or links)
  - Enforcement notice section
  - Response history timeline
  - Response form: acknowledge button, corrective action text area, file upload, comment
- Build `InspectionResponseForm` component
- Add inspection notice badge to dashboard when open inspections exist

### Files
| Backend | Frontend |
|---------|----------|
| `employers/views.py` (update — inspection actions) | `employer/inspections/page.tsx` (replace) |
| `employers/serializers.py` (update) | `employer/inspections/[id]/page.tsx` (new) |
| `employers/urls.py` (update) | `components/ui/inspection-response-form.tsx` (new) |
| `inspections/models.py` (update — add response fields) | |
| Migration (auto-generated) | |

---

## Chunk E8: Compliance Reports

### Goal
Employer can generate and export compliance reports with filters and multiple export formats.

### Backend
- Add `GET /api/employers/{id}/reports/compliance`:
  - Employer-wide or branch-filtered compliance report
  - Includes: handler count, certified count, expired count, compliance %, vaccination coverage
  - Supports `?format=csv|pdf|excel`
- Add `GET /api/employers/{id}/reports/certificates`:
  - Certificate expiry report filtered by date range and branch
- Add `GET /api/employers/{id}/reports/vaccinations`:
  - Vaccination compliance report filtered by vaccine type and branch
- Ensure all reports honor privacy rules — no lab results, doctor notes, diagnosis, declaration answers, full NIN

### Frontend
- Replace `frontend/src/app/employer/reports/page.tsx`:
  - Report type selector: compliance overview, certificate expiry, vaccination compliance, illness/exclusion, return-to-work, handler roster
  - Filters panel: date range, branch, state, LGA, category, certificate status, fitness status
  - Export format selector: PDF, Excel, CSV
  - "Generate Report" button with loading state
  - Generated reports list: type, date generated, format, download link
- Build `ComplianceReportBuilder` component
- Link "View Compliance Report" from branch detail page and food handler list

### Files
| Backend | Frontend |
|---------|----------|
| `employers/views.py` (update — report actions) | `employer/reports/page.tsx` (replace) |
| `employers/urls.py` (update) | `components/ui/compliance-report-builder.tsx` (new) |
| `reports/services.py` (update — employer-specific report generators) | |

---

## Chunk E9: Employer User Management

### Goal
Employer admin can invite and manage internal users (compliance officers, branch managers, finance users).

### Backend
- Add `GET /api/employers/{id}/users`:
  - List employer users with role, unit/branch, status
- Add `POST /api/employers/{id}/invites`:
  - Invite compliance officer, branch manager, or finance user
  - Specify role, unit/branch, email, phone, message
  - Creates UserInvite scoped to employer organization
- Add `GET /api/employers/{id}/invites`:
  - List all invites with status (pending/accepted/expired/revoked)
- Add `DELETE /api/employers/{id}/invites/{invite_id}`:
  - Revoke a pending invite
- Add `PATCH /api/employers/{id}/users/{user_id}`:
  - Change user role, unit assignment, or deactivate
- Ensure invite lifecycle: only owner/admin can invite head office users, head office can invite branch managers, branch manager can only invite food handlers to own branch

### Frontend
- Create `frontend/src/app/employer/users/page.tsx`:
  - User list: name, email, role badge, unit/branch, status, actions (edit, deactivate)
- Create `frontend/src/app/employer/invites/page.tsx`:
  - Invite list: email, role, unit, invited by, status badge (pending/accepted/expired/revoked), expires at, actions (resend, revoke)
  - "Invite User" button opens `InviteEmployerUserModal`
- Build `InviteEmployerUserModal` component:
  - Email, phone, role dropdown (compliance officer, branch manager, finance user), unit/branch selector, message
- Link from branch detail page: "Assign Branch Manager" → opens invite modal with branch pre-selected

### Files
| Backend | Frontend |
|---------|----------|
| `employers/views.py` (update — user/invite management actions) | `employer/users/page.tsx` (new) |
| `employers/serializers.py` (update) | `employer/invites/page.tsx` (new) |
| `employers/urls.py` (update) | `components/ui/invite-employer-user-modal.tsx` (new) |

---

## Chunk E10: Dashboard Enhancements & Settings

### Goal
Real employer dashboard with all PRD metrics, charts, branch scope integration, notifications, and settings.

### Backend
- Add `GET /api/employers/{id}/dashboard`:
  - Returns all PRD Section 20.1 metrics: total handlers, fit, pending, expired, expiring soon, temporarily not fit, excluded, vaccination due, active branches, open inspections, subscription status, compliance %
  - Supports `?branch=` filter for branch-scoped view
  - Branch manager gets only their branch's metrics
- Add `GET /api/employers/{id}/compliance-summary`:
  - Compliance by branch breakdown
  - Certificate status distribution
  - Vaccination coverage summary
- Add `GET /api/employers/{id}/notifications`:
  - In-app notifications for employer (invite accepted, certificate expiring, illness reported, inspection notice, subscription expiring)
- Add `PATCH /api/employers/{id}/settings`:
  - Notification preferences, business settings

### Frontend
- Replace `frontend/src/app/employer/dashboard/page.tsx`:
  - 12+ DashboardCards in a responsive grid
  - Charts section: compliance by branch (bar chart), certificate status distribution (pie/donut), expiring certificates timeline (line chart), illness reports trend
  - OrganizationScopeSwitcher at top (branch filter, locked for branch managers)
  - Recent activity feed
  - Open inspection notices banner
- Create `frontend/src/app/employer/settings/page.tsx`:
  - Notification preferences (email, SMS, in-app toggles per notification type)
  - Business profile link
  - Subscription summary
- Add notification bell/counter to PortalShell header for employer users
- Branch manager dashboard: pre-filtered to assigned branch, branch switcher locked

### Files
| Backend | Frontend |
|---------|----------|
| `employers/views.py` (update — dashboard, notifications, settings actions) | `employer/dashboard/page.tsx` (replace) |
| `employers/serializers.py` (update) | `employer/settings/page.tsx` (new) |
| `employers/urls.py` (update) | `components/layout/portal-shell.tsx` (update — notification bell) |
| `employers/services.py` (update — dashboard aggregation service) | |

---

## Chunk E11: Tests & Privacy Verification

### Goal
Comprehensive test coverage for employer workflows, permissions, and privacy rules.

### Backend Tests
- `employers/tests/test_permissions.py`:
  - Branch manager can only see assigned branch food handlers
  - Branch manager cannot see other branches
  - Compliance officer cannot access billing
  - Finance user cannot view medical data
  - Head office can view all branches
- `employers/tests/test_privacy.py`:
  - Employer serializer excludes lab results
  - Employer serializer excludes doctor notes
  - Employer serializer excludes diagnosis
  - Employer serializer excludes declaration answers
  - Employer serializer excludes full NIN
  - Food handler list endpoint does not leak medical data
  - Certificate endpoint does not leak medical data
  - Vaccination endpoint does not leak clinical notes
- `employers/tests/test_workflows.py`:
  - Employer registration creates profile + organization
  - Invite food handler creates UserInvite with correct scope
  - Accept invite assigns food handler to branch
  - Bulk upload validates and creates invites
  - Illness report auto-excludes food handler
  - Return-to-work status updates correctly
  - Subscription expiry restricts premium features
  - Subscription expiry does not block regulatory notices
  - Inspection response workflow
  - Dashboard returns correct metrics for branch manager

### Frontend Tests (if test framework exists)
- Dashboard renders correct metrics from API
- Food handler list filters by branch
- Illness report form submits with correct data
- Privacy — employer pages never render medical data in DOM
- Branch manager sees locked branch filter
- Head office sees branch switcher

### Files
| Backend | Frontend |
|---------|----------|
| `employers/tests/test_permissions.py` (new) | `__tests__/employer/` (new — if framework exists) |
| `employers/tests/test_privacy.py` (new) | |
| `employers/tests/test_workflows.py` (new) | |

---

## Total Files per Chunk

| Chunk | Name | Backend | Frontend |
|:-----:|------|:---:|:---:|
| E1 | Registration & Profile | 6 | 3 |
| E2 | Food Handler List | 3 | 3 |
| E3 | Onboarding (invite, bulk, link) | 4 | 4 |
| E4 | Certificate & Vax Monitor | 3 | 4 |
| E5 | Illness & Return-to-Work | 3 | 4 |
| E6 | Subscription & Billing | 5 | 2 |
| E7 | Inspection History & Response | 4 | 3 |
| E8 | Compliance Reports | 3 | 2 |
| E9 | Employer User Management | 3 | 3 |
| E10 | Dashboard Enhance + Settings | 4 | 3 |
| E11 | Tests & Privacy | 3 | 1 |
| **Total** | | **41** | **32** |

**Grand total: ~73 files across 11 chunks.**
