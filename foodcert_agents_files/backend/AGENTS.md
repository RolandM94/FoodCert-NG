# backend/AGENTS.md — Django Backend Instructions

## Backend Scope

This folder contains the Django + Django REST Framework backend for FoodCert NG.

The backend is responsible for:
- Authentication and authorization
- Organization and tenant management
- Food handler profiles
- Employer management
- Medical facility accreditation
- NIN verification
- Assessment payments
- Employer subscriptions
- Facility settlements
- Medical assessments
- Lab tests
- Vaccinations
- Fitness decisions
- Certificate generation and QR verification
- Inspections
- Dashboards, reports, and audit logs

## Backend Stack

Use:
- Django
- Django REST Framework
- PostgreSQL
- Celery
- Redis
- SimpleJWT or equivalent JWT auth
- django-filter for filtering
- drf-spectacular or equivalent for API docs
- pytest or Django TestCase for tests

## Backend App Structure

Use this app structure:

```txt
backend/
  apps/
    accounts/
    organizations/
    geography/
    food_handlers/
    employers/
    facilities/
    nin_verification/
    payments/
    subscriptions/
    settlements/
    appointments/
    assessments/
    lab_tests/
    vaccinations/
    certificates/
    inspections/
    reports/
    notifications/
    audit/
    policy/
```

## Model Rules

- Use UUID primary keys for core records.
- Add `created_at` and `updated_at` timestamps.
- Use explicit status fields with enums/TextChoices.
- Avoid deleting critical records. Prefer soft status changes for certificates, payments, settlements, assessments, and medical records.
- Add model constraints where needed:
  - Certificate number must be unique.
  - Payment internal reference must be unique.
  - NIN verification should be uniquely tied to a food handler unless manual override requires history.
  - Approved facility must belong to a state.
- Use indexes for frequently queried fields:
  - certificate_number
  - status
  - state_id
  - employer_id
  - facility_id
  - food_handler_id
  - created_at

## API Rules

- Use ViewSets where appropriate.
- Use custom actions for workflow transitions:
  - submit
  - approve
  - reject
  - validate
  - revoke
  - suspend
  - verify
  - settle
- Put permission logic in custom permission classes.
- Put workflow logic in service classes, not directly in views.
- Serialize public and private views differently.
- Public certificate verification must use a dedicated public serializer.

## Permission Rules

Always enforce:
- Super Admin can manage global settings.
- Federal Admin can view national data and aggregate reports.
- State Admin can manage only their state-level records.
- Medical Facility Admin can manage only their facility records.
- Doctor can act only within assigned/authorized facility.
- Lab Staff can manage only lab requests assigned to their facility.
- Employer can view only linked food handlers and operational status.
- Food Handler can view only their own profile, assessment status, certificates, and vaccination records.
- Public verifier can only access public certificate verification.

## Service Layer Requirements

Create service classes for:
- NIN verification
- Payment initialization and confirmation
- Subscription activation
- Settlement calculation and payout
- Facility accreditation approval
- Assessment workflow validation
- Fitness decision validation
- Certificate generation
- Certificate QR creation
- Certificate public verification
- Certificate revocation/suspension
- Notification dispatch
- Report generation
- Audit logging

## Audit Rules

Create audit logs for:
- User role changes
- Facility accreditation approval/rejection/suspension
- Payment confirmation
- Settlement creation and payout
- Declaration validation
- Lab result submission
- Fitness decision
- Certificate issuance
- Certificate revocation/suspension
- Public certificate verification attempt
- Employer subscription changes
- Medical record access

## Testing Rules

Add backend tests for:
- Permissions
- Serializers
- Model constraints
- Workflow state transitions
- Certificate generation
- Public verification privacy
- Payment and settlement transitions
- NIN verification statuses
- Facility accreditation
- Employer visibility restrictions

## Do Not Do

- Do not expose doctor notes, lab results, diagnosis, or declaration answers in employer/public serializers.
- Do not perform certificate generation inside a serializer.
- Do not trust frontend calculations for payment amounts, validity dates, fees, or settlements.
- Do not allow a certificate to be issued from an unapproved facility.
- Do not allow assessment completion if payment has not been confirmed.
