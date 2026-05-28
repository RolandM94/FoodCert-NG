# FoodCert NG

FoodCert NG is a national web application for automating food handler medical fitness certification in Nigeria.

## Phase 1 Foundation

This scaffold includes:

- Django REST Framework backend
- Next.js + TypeScript + Tailwind frontend
- PostgreSQL and Redis via Docker Compose
- Celery worker configuration
- UUID/timestamp base model mixins
- Custom user with role, organization, and state fields
- Organizations, locations, audit logs, and notifications foundation
- Health check and OpenAPI schema endpoints
- Nigerian states/FCT seed command

## Local Setup

1. Copy backend environment variables:

   ```bash
   cp backend/.env.example backend/.env
   ```

2. Start services:

   ```bash
   docker compose up --build
   ```

3. Run migrations and seed states:

   ```bash
   docker compose exec backend python manage.py migrate
   docker compose exec backend python manage.py seed_states
   ```

## Useful URLs

- Backend health: `http://localhost:8000/api/health/`
- API schema: `http://localhost:8000/api/schema/`
- API docs: `http://localhost:8000/api/docs/`
- Frontend: `http://localhost:3000/`

## Test Accounts

All passwords: **`Demo@2024!`**

| Username | Role | Portal | Notes |
|---|---|---|---|
| `super.admin` | Super Admin | /federal/dashboard | Full system access |
| `federal.admin` | Federal Admin | /federal/dashboard | National oversight |
| `lagos.admin` | State Admin | /state/dashboard | Lagos state admin |
| `lagos.verifier` | State Verifier | /state/dashboard | Certificate verification |
| `lagos.accreditor` | State Accreditor | /state/dashboard | Facility accreditation |
| `lagos.inspector` | Inspector | /inspector/dashboard | Field inspections |
| `excel.admin` | Facility Admin | /facility/dashboard | Excel Medical Centre |
| `prime.admin` | Facility Admin | /facility/dashboard | Prime Diagnostics |
| `excel.doctor` | Doctor | /doctor/dashboard | Assessment workflow |
| `excel.lab` | Lab Staff | /lab/dashboard | Lab tests & results |
| `megachow.hq` | Employer (HQ) | /employer/dashboard | MegaChow head office |
| `megachow.ikeja` | Employer (Branch) | /employer/dashboard | MegaChow Ikeja branch |
| `megachow.surulere` | Employer (Branch) | /employer/dashboard | MegaChow Surulere branch |
| `ada.okafor` | Food Handler | /food-handler/dashboard | Fit — certificate ready |
| `bola.surulere` | Food Handler | /food-handler/dashboard | Fit — Surulere branch |
| `emeka.nnamdi` | Food Handler | /food-handler/dashboard | NIN pending (blocked) |
| `chioma.eze` | Food Handler | /food-handler/dashboard | Temporarily excluded |

## Authentication and Organization APIs

- Register: `POST /api/auth/register/`
- Login: `POST /api/auth/login/`
- Logout: `POST /api/auth/logout/`
- Refresh token: `POST /api/auth/token/refresh/`
- Password reset request: `POST /api/auth/password-reset/`
- Current user: `GET/PATCH /api/users/me/`
- Invite user: `POST /api/users/invite/`
- User status: `PATCH /api/users/{id}/status/`
- Organizations: `GET/POST /api/organizations/`
- Organization detail: `GET/PATCH /api/organizations/{id}/`
- State policy configs: `GET/POST/PATCH /api/state-policy-configs/`

## Identity APIs

- Food handlers: `GET/POST /api/food-handlers/`
- Food handler detail: `GET/PATCH /api/food-handlers/{id}/`
- Verify food handler NIN: `POST /api/food-handlers/{id}/verify-nin/`
- Latest food handler NIN verification: `GET /api/food-handlers/{id}/nin-verification/`
- Employers: `GET/POST /api/employers/`
- Employer detail: `GET/PATCH /api/employers/{id}/`
- Approve NIN override: `PATCH /api/nin-verifications/{id}/approve-override/`
- Reject NIN override: `PATCH /api/nin-verifications/{id}/reject-override/`

## Facility Accreditation APIs

- Medical facilities: `GET/POST /api/medical-facilities/`
- Medical facility detail: `GET/PATCH /api/medical-facilities/{id}/`
- Accreditation applications: `GET/POST /api/facility-accreditation/`
- Submit accreditation: `PATCH /api/facility-accreditation/{id}/submit/`
- Approve accreditation: `PATCH /api/facility-accreditation/{id}/approve/`
- Reject accreditation: `PATCH /api/facility-accreditation/{id}/reject/`
- Suspend accreditation: `PATCH /api/facility-accreditation/{id}/suspend/`
- Reactivate accreditation: `PATCH /api/facility-accreditation/{id}/reactivate/`

## Payment, Subscription, and Settlement APIs

- Assessment fees: `GET/POST /api/assessment-fees/`
- Assessment fee detail: `GET/PATCH /api/assessment-fees/{id}/`
- Initiate assessment payment: `POST /api/payments/assessment/initiate/`
- Initiate subscription payment: `POST /api/payments/subscription/initiate/`
- Verify payment: `GET /api/payments/verify/{reference}/`
- Payment webhook: `POST /api/payments/webhook/`
- Payment transactions: `GET /api/payments/`
- Subscription plans: `GET/POST /api/subscription-plans/`
- Employer subscribe: `POST /api/employers/{id}/subscribe/`
- Employer current subscription: `GET /api/employers/{id}/subscription/`
- Settlements: `GET /api/settlements/`
- Create settlement from payment: `POST /api/settlements/create-from-payment/`
- Process settlement: `POST /api/settlements/{id}/process/`
- Facility settlements: `GET /api/facilities/{id}/settlements/`

## Medical Assessment APIs

- Appointments: `GET/POST /api/appointments/`
- Appointment detail: `GET/PATCH /api/appointments/{id}/`
- Assessments: `GET/POST /api/assessments/`
- Assessment detail: `GET /api/assessments/{id}/`
- Submit declaration: `POST /api/assessments/{id}/declaration/`
- Validate declaration: `PATCH /api/declarations/{id}/validate/`
- Submit physical examination: `POST /api/assessments/{id}/physical-examination/`
- Request lab tests: `POST /api/assessments/{id}/lab-tests/`
- Record lab result: `PATCH /api/lab-tests/{id}/result/`
- Review lab result: `PATCH /api/lab-tests/{id}/review/`
- Record vaccination review: `POST /api/assessments/{id}/vaccinations/`
- Food handler vaccinations: `GET /api/food-handlers/{id}/vaccinations/`
- Set fitness decision: `PATCH /api/assessments/{id}/fitness-decision/`

## Certificate APIs

- Certificate requests: `GET /api/certificate-requests/`
- Request certificate: `POST /api/assessments/{id}/request-certificate/`
- Approve certificate request: `PATCH /api/certificate-requests/{id}/approve/`
- Reject certificate request: `PATCH /api/certificate-requests/{id}/reject/`
- Generate certificate: `POST /api/certificates/generate/`
- Certificates: `GET /api/certificates/`
- Certificate detail: `GET /api/certificates/{id}/`
- Certificate PDF: `GET /api/certificates/{id}/download/`
- Revoke certificate: `PATCH /api/certificates/{id}/revoke/`
- Suspend certificate: `PATCH /api/certificates/{id}/suspend/`
- Public certificate verification: `GET /api/public/certificates/verify/{certificateNumber}/`
- Public verification page: `GET /verify/{certificateNumber}`

## Illness and Inspection APIs

- Illness reports: `GET/POST /api/illness-reports/`
- Illness report detail: `GET /api/illness-reports/{id}/`
- Review illness report: `PATCH /api/illness-reports/{id}/review/`
- Return-to-work clearance: `PATCH /api/illness-reports/{id}/clearance/`
- Inspections: `GET/POST /api/inspections/`
- Inspection detail: `GET/PATCH /api/inspections/{id}/`
- Submit inspection: `PATCH /api/inspections/{id}/submit/`
- Add inspection evidence: `POST /api/inspections/{id}/evidence/`
- Scan certificate during inspection: `POST /api/inspections/{id}/scan-certificate/`

## Dashboard and Report APIs

- Employer dashboard: `GET /api/dashboard/employer/`
- Facility dashboard: `GET /api/dashboard/facility/`
- State dashboard: `GET /api/dashboard/state/`
- Federal dashboard: `GET /api/dashboard/federal/`
- Employer compliance report: `GET /api/reports/employer-compliance/`
- Facility performance report: `GET /api/reports/facility-performance/`
- State monthly report: `GET /api/reports/state-monthly/`
- National report: `GET /api/reports/national/`
- Vaccination coverage report: `GET /api/reports/vaccination-coverage/`
- Illness trends report: `GET /api/reports/illness-trends/`
- Inspection outcomes report: `GET /api/reports/inspection-outcomes/`
- Schedule report: `POST /api/reports/schedule/`
- Generated reports: `GET /api/reports/generated/`
- Download generated report: `GET /api/reports/generated/{id}/download/`

## API Response Envelope

Successful JSON API responses use:

```json
{
  "success": true,
  "data": {},
  "message": ""
}
```

Errors use:

```json
{
  "success": false,
  "error": "Validation failed.",
  "code": "VALIDATION_ERROR",
  "details": {}
}
```

List endpoints support `page`, `page_size`, and `ordering`; paginated responses include `meta`.
