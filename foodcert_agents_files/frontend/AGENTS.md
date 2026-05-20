# frontend/AGENTS.md — Next.js Frontend Instructions

## Frontend Scope

This folder contains the Next.js + TypeScript frontend for FoodCert NG.

The frontend must provide role-based portals for:
- Food handlers
- Employers
- Medical facilities
- Doctors
- Lab staff
- Inspectors
- State Ministry users
- Federal Ministry users
- Super Admins
- Public certificate verifiers

## Frontend Stack

Use:
- Next.js
- TypeScript
- Tailwind CSS
- React Hook Form
- Zod
- TanStack Query
- Recharts or ApexCharts
- QR scanner library
- Component-driven structure

## Frontend Structure

Use this structure:

```txt
frontend/src/
  app/
  components/
    ui/
    layout/
    forms/
    tables/
    charts/
    status/
  features/
    auth/
    dashboard/
    food-handlers/
    employers/
    facilities/
    assessments/
    lab-tests/
    vaccinations/
    certificates/
    inspections/
    payments/
    subscriptions/
    reports/
    settings/
  lib/
    api/
    auth/
    permissions/
    formatters/
    validators/
  hooks/
  types/
```

## UX Principles

- Keep workflows step-by-step and clear.
- Use status badges for all workflow states.
- Use dashboards with clear cards, charts, and action lists.
- Keep medical workflows simple for doctors and facility staff.
- Keep employer view focused on compliance and fitness status only.
- Public certificate verification should be fast, simple, and trustworthy.
- Use clear error messages.
- Mobile responsiveness is required, especially for public verification and inspector workflows.

## Role-Based Navigation

Food Handler:
- Profile
- NIN Verification
- Appointments
- Declaration Form
- Assessment Status
- Vaccinations
- Certificates
- Illness Report
- Notifications

Employer:
- Dashboard
- Food Handlers
- Certificates
- Vaccination Compliance
- Illness Reports
- Compliance Reports
- Subscription/Billing
- Inspections

Medical Facility Admin:
- Dashboard
- Accreditation
- Appointments
- Assessments
- Doctors/Lab Staff
- Payments/Settlements
- Reports

Doctor:
- Pending Assessments
- Declaration Review
- Physical Examination
- Lab Results
- Vaccination Review
- Fitness Decision

Lab Staff:
- Lab Requests
- Sample Collection
- Result Entry
- Result Upload

State Ministry:
- Dashboard
- Facilities
- Certificate Validation Queue
- Employers
- Food Handlers
- Inspections
- Fees
- Reports

Federal Ministry:
- National Dashboard
- State Performance
- Certificate Registry
- National Reports
- Policy Settings

Inspector:
- Scan Certificate
- Search Business
- Inspection Checklist
- Notices
- Inspection History

Public:
- Certificate Verification Page

## Privacy UI Rules

Employer screens must not display:
- Lab results
- Doctor notes
- Diagnosis
- Declaration answers
- Full NIN

Public verification must not display:
- Full NIN
- Lab results
- Diagnosis
- Declaration answers
- Doctor notes
- Employer private records

Public verification may display:
- Certificate status
- Certificate number
- Food handler name
- Passport photo
- Issuing State Ministry
- Approved medical facility
- Date issued
- Expiry date
- Fitness status

## Form Rules

- Use React Hook Form with Zod validation.
- Show clear required fields.
- Use multi-step forms for long workflows.
- Save draft where appropriate.
- Prevent submission if required documents are missing.
- Confirm before irreversible actions such as certificate revocation.

## API Rules

- Use a centralized API client.
- Handle auth tokens centrally.
- Handle role-based redirects.
- Use TanStack Query for server state.
- Keep API response types in `types/`.
- Do not duplicate backend business logic in frontend. Frontend may display calculated values returned by backend.

## Do Not Do

- Do not hide backend errors with generic messages when a useful message exists.
- Do not display medical details in employer or public pages.
- Do not calculate final payment, certificate validity, or settlement amounts on the frontend as source of truth.
- Do not make certificate issuance a frontend-only action.
