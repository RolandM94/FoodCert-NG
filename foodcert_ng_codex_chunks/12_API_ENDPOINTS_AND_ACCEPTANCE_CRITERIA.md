# Chunk 12 — API Endpoints and Acceptance Criteria

## API Endpoint Map

### Auth and Users

```txt
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/logout
POST   /api/auth/token/refresh
POST   /api/auth/password-reset
GET    /api/users/me
PATCH  /api/users/me
GET    /api/users
POST   /api/users/invite
PATCH  /api/users/:id/status
```

### Organizations and Locations

```txt
GET    /api/states
GET    /api/states/:id/lgas
GET    /api/organizations
POST   /api/organizations
GET    /api/organizations/:id
PATCH  /api/organizations/:id
```

### Food Handlers and Employers

```txt
POST   /api/food-handlers
GET    /api/food-handlers
GET    /api/food-handlers/:id
PATCH  /api/food-handlers/:id
POST   /api/food-handlers/:id/verify-nin
GET    /api/food-handlers/:id/nin-verification

POST   /api/employers
GET    /api/employers
GET    /api/employers/:id
PATCH  /api/employers/:id
POST   /api/employers/:id/invite-food-handler
```

### Facilities and Accreditation

```txt
POST   /api/medical-facilities
GET    /api/medical-facilities
GET    /api/medical-facilities/:id
PATCH  /api/medical-facilities/:id

POST   /api/facility-accreditation
PATCH  /api/facility-accreditation/:id/submit
PATCH  /api/facility-accreditation/:id/approve
PATCH  /api/facility-accreditation/:id/reject
PATCH  /api/facility-accreditation/:id/suspend
```

### Payments and Subscriptions

```txt
POST   /api/payments/assessment/initiate
POST   /api/payments/subscription/initiate
GET    /api/payments/verify/:reference
POST   /api/payments/webhook

GET    /api/assessment-fees
POST   /api/assessment-fees
PATCH  /api/assessment-fees/:id

GET    /api/subscription-plans
POST   /api/subscription-plans
POST   /api/employers/:id/subscribe
GET    /api/employers/:id/subscription

GET    /api/settlements
POST   /api/settlements/:id/process
GET    /api/facilities/:id/settlements
```

### Assessments

```txt
POST   /api/appointments
GET    /api/appointments
PATCH  /api/appointments/:id

POST   /api/assessments
GET    /api/assessments
GET    /api/assessments/:id

POST   /api/assessments/:id/declaration
PATCH  /api/declarations/:id/validate

POST   /api/assessments/:id/physical-examination

POST   /api/assessments/:id/lab-tests
PATCH  /api/lab-tests/:id/result
PATCH  /api/lab-tests/:id/review

POST   /api/assessments/:id/vaccinations
GET    /api/food-handlers/:id/vaccinations

PATCH  /api/assessments/:id/fitness-decision
```

### Certificates

```txt
GET    /api/certificate-requests
POST   /api/assessments/:id/request-certificate
PATCH  /api/certificate-requests/:id/approve
PATCH  /api/certificate-requests/:id/reject

POST   /api/certificates/generate
GET    /api/certificates
GET    /api/certificates/:id
GET    /api/certificates/:id/download
PATCH  /api/certificates/:id/revoke
PATCH  /api/certificates/:id/suspend

GET    /api/public/certificates/verify/:certificateNumber
```

### Illness and Inspections

```txt
POST   /api/illness-reports
GET    /api/illness-reports
GET    /api/illness-reports/:id
PATCH  /api/illness-reports/:id/review
PATCH  /api/illness-reports/:id/clearance

POST   /api/inspections
GET    /api/inspections
GET    /api/inspections/:id
PATCH  /api/inspections/:id
PATCH  /api/inspections/:id/submit
POST   /api/inspections/:id/evidence
```

### Dashboards and Reports

```txt
GET    /api/dashboard/employer
GET    /api/dashboard/facility
GET    /api/dashboard/state
GET    /api/dashboard/federal

GET    /api/reports/employer-compliance
GET    /api/reports/facility-performance
GET    /api/reports/state-monthly
GET    /api/reports/national
GET    /api/reports/vaccination-coverage
GET    /api/reports/illness-trends
GET    /api/reports/inspection-outcomes
```

## Global Acceptance Criteria

### National Rollout

- System supports all 36 States and FCT.
- State users only manage their state.
- Federal users can view national aggregates.

### NIN Verification

- Food handler cannot receive certificate without verified NIN or approved override.
- Mismatch triggers manual review.
- Full NIN is not public.

### Payments

- Food handler pays before assessment is activated.
- Payment is verified server-side.
- Receipt is generated.
- Settlement is created after valid completed assessment.

### Employer Subscription

- Employer can subscribe to plan.
- Expired subscription restricts premium functions.
- Regulatory visibility is not blocked.

### Medical Assessment

- Food handler declaration is digitized.
- Doctor validates declaration.
- Doctor completes exam.
- Lab tests are managed.
- Vaccination records are tracked.
- Doctor submits fitness decision.

### Certificate

- Certificate is issued by State Ministry.
- Default validity is 6 months.
- Certificate has QR code.
- Public verification works.
- Certificate cannot be edited after issuance.
- Revoked/suspended/expired certificates show invalid or expired.

### Employer Visibility

- Employer sees operational fitness status only.
- Employer cannot see detailed medical data.

### Public Verification

- Anyone can verify certificate.
- Sensitive medical data is hidden.

### Audit

- Critical actions are logged.
