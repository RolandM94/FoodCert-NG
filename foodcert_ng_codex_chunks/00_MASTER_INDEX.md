# FoodCert NG — Codex Build Pack

## Purpose

This folder breaks the FoodCert NG application into implementation-ready chunks for Codex.

FoodCert NG is a national platform for automating food handlers’ medical assessment, vaccination tracking, fitness certification, QR-code verification, employer compliance monitoring, medical facility accreditation, payments, settlements, and regulatory reporting in line with the National Guidelines for Food Handlers’ Medical Test 2024.

## Final Product Decisions

1. The app is for national rollout across all 36 States and the FCT.
2. Certificates are issued by the State Ministry of Health.
3. Food handlers pay assessment fees through the platform.
4. Employers pay subscription fees.
5. Medical facilities receive payments/settlements through the app.
6. NIN verification is automatic before certificate issuance, with manual override only by authorized regulators.
7. Certificate validity defaults to 6 months, but validity should be configurable by authorized administrators.
8. Employers see operational fitness status categories only, not sensitive medical records.
9. QR-code certificate verification is public.

## Recommended Stack

- Backend: Django + Django REST Framework
- Database: PostgreSQL
- Background jobs: Celery + Redis
- Frontend: Next.js + TypeScript + Tailwind CSS
- Storage: S3-compatible file storage abstraction
- Payments: provider abstraction for Paystack, Flutterwave, Remita, or another approved provider
- Identity: NIN verification provider abstraction

## Pre-Build Reference

Read `00b_MODELS_REGISTRY_AND_POLICY_CLARIFICATIONS.md` before starting —
it defines API conventions, missing models, and policy resolutions that apply
across all build chunks.

Read `00c_STAKEHOLDER_MANAGEMENT_SUPPLEMENT.md` before starting —
it adds OrganizationUnit, branch/department structures, multi-actor invite
workflows, and scoping rules needed for a national multi-tenant platform.

## Suggested Build Order

1. `01_FOUNDATION_AND_ARCHITECTURE.md`
2. `02_USERS_ROLES_ORGANIZATIONS.md`
3. `03_IDENTITY_FOOD_HANDLERS_EMPLOYERS.md`
4. `04_MEDICAL_FACILITY_ACCREDITATION.md`
5. `05_PAYMENTS_SUBSCRIPTIONS_SETTLEMENTS.md`
6. `06_MEDICAL_ASSESSMENT_WORKFLOW.md`
7. `07_CERTIFICATE_ISSUANCE_AND_QR_VERIFICATION.md`
8. `08_ILLNESS_RETURN_TO_WORK_INSPECTIONS.md`
9. `09_DASHBOARDS_REPORTING_ANALYTICS.md`
10. `10_FRONTEND_PAGES_AND_UX.md`
11. `11_SECURITY_PRIVACY_AUDIT.md`
12. `12_API_ENDPOINTS_AND_ACCEPTANCE_CRITERIA.md`
13. `13_CODEX_MASTER_PROMPT.md`

## MVP Priority

The MVP should focus on:
- Registration and RBAC
- Food handler profile
- NIN verification workflow
- Employer registration and subscription
- Facility registration and accreditation
- Assessment fee payment
- Medical assessment workflow
- Vaccination tracking
- Certificate issuance by State Ministry
- Public QR verification
- Employer, State, and Federal dashboards
