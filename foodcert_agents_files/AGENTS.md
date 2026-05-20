# AGENTS.md — FoodCert NG

## Project Overview

FoodCert NG is a national web application for automating food handler medical fitness certification in Nigeria, based on the National Guidelines for Food Handlers’ Medical Test 2024.

The platform supports:
- Food handler registration
- Automatic NIN verification
- Employer registration and subscriptions
- Medical facility accreditation
- Food handler assessment payments
- Doctor-led medical assessment workflow
- Laboratory test management
- Vaccination tracking
- State Ministry certificate validation and issuance
- QR-code public certificate verification
- Medical facility settlements
- Employer compliance monitoring
- State and Federal dashboards
- Inspection, enforcement, reporting, and audit logs

## Core Product Decisions

- This is a national rollout platform covering all 36 Nigerian states and the FCT.
- Certificates are issued by the State Ministry of Health.
- Food handlers pay assessment fees through the platform.
- Employers pay subscription fees.
- Medical facilities receive settlements through the platform.
- NIN must be verified automatically before certificate issuance.
- Certificate validity defaults to 6 months but must be configurable by authorized administrators.
- Employers only see operational fitness categories, not detailed medical records.
- Certificate QR verification is public.
- The Federal Ministry has national oversight.
- State Ministries manage state facilities, certificates, prices, inspections, and state reporting.

## Preferred Tech Stack

Backend:
- Django
- Django REST Framework
- PostgreSQL
- Celery
- Redis

Frontend:
- Next.js
- TypeScript
- Tailwind CSS
- React Hook Form
- Zod
- TanStack Query

Infrastructure:
- Docker
- Object storage abstraction
- Payment provider abstraction
- NIN verification provider abstraction
- QR code generation
- PDF certificate generation

## Development Order

Build in this order:

1. Foundation, authentication, roles, permissions, organizations, states, LGAs
2. Food handler, employer, and medical facility profiles
3. NIN verification workflow
4. Payment, employer subscription, and settlement infrastructure
5. Medical facility accreditation
6. Appointment booking
7. Health declaration
8. Doctor physical examination
9. Laboratory test workflow
10. Vaccination records
11. Fitness decision workflow
12. State Ministry certificate validation and issuance
13. QR-code certificate generation
14. Public certificate verification page
15. Employer, facility, state, and federal dashboards
16. Audit logs and reports

## Global Development Rules

- Implement backend models, serializers, permissions, APIs, and tests before frontend screens.
- Use UUID primary keys for core models.
- Use role-based and organization-based access control.
- Do not expose medical details to employers or public verifiers.
- Public certificate verification must show only limited certificate validity information.
- Keep business rules configurable where possible, especially certificate validity, fees, renewal rules, and provider settings.
- All sensitive actions must create audit logs.
- Certificate records must be immutable after issuance except for revocation, suspension, or replacement workflows.
- Use service-layer functions for payments, NIN verification, certificate generation, settlements, notifications, and reporting.
- Do not hardcode one payment provider. Create a provider abstraction.
- Do not hardcode one NIN provider. Create a provider abstraction.
- Do not allow unapproved medical facilities to conduct assessments.
- Do not issue certificates before payment, NIN verification, medical workflow completion, and State validation are complete.
- Do not allow employers to edit medical records.
- Do not allow certificates to be edited after issuance.

## Privacy and Security Rules

- Mask NIN except where authorized users require full access.
- Never expose lab results, doctor notes, diagnosis, or declaration answers publicly.
- Employers may only see operational status categories:
  - Fit to Handle Food
  - Certificate Expired
  - Certification Pending
  - Temporarily Not Fit
  - Excluded from Food Handling
  - Return-to-Work Clearance Pending
  - Cleared to Return to Work
  - Vaccination Due
  - Medical Review Required
- Public QR verification may show:
  - Certificate status
  - Certificate number
  - Food handler name
  - Passport photo
  - Issuing State Ministry
  - Approved medical facility
  - Date issued
  - Expiry date
  - Fitness status
- Public QR verification must not show:
  - Full NIN
  - Lab results
  - Diagnosis
  - Doctor notes
  - Declaration answers
  - Employer private compliance records

## Testing Requirements

Add tests for:
- Role and organization permissions
- Certificate generation rules
- Public verification privacy
- Payment status transitions
- NIN verification statuses
- Employer visibility restrictions
- Facility accreditation approval
- Assessment-to-certificate workflow
- Certificate expiry, revocation, and suspension
- Settlement eligibility and payout calculation

## Coding Standards

- Keep code modular.
- Prefer services for complex business logic.
- Avoid putting business logic directly in views.
- Use DRF serializers for validation.
- Use database constraints where appropriate.
- Use type-safe frontend components.
- Keep frontend pages role-aware.
- Add meaningful error messages.
- Write migrations for every model change.
- Keep enums/constants centralized.
- Add docstrings to service classes and complex workflows.

## Do Not Do

- Do not expose sensitive medical data in public verification.
- Do not allow unapproved facilities to conduct assessments.
- Do not issue certificates before payment, NIN verification, medical completion, and State validation.
- Do not allow employers to edit medical records.
- Do not allow certificates to be edited after issuance.
- Do not hardcode certificate validity without policy configuration.
- Do not put payment provider-specific logic directly inside views.
- Do not put NIN provider-specific logic directly inside views.
