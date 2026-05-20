# Chunk 10 — Frontend Pages and UX

## Goal

Build the Next.js frontend for all MVP workflows.

## General UX Requirements

- Responsive design.
- Mobile-friendly for inspectors and food handlers.
- Role-based navigation.
- Clear status badges.
- Step-by-step workflows.
- Form validation with helpful error messages.
- Dashboard cards and charts.
- Accessible colors and readable typography.
- Loading, empty, and error states for every page.

## Public Pages

```txt
/
/login
/register
/verify/[certificateNumber]
/facilities/approved
```

## Food Handler Pages

```txt
/food-handler/dashboard
/food-handler/profile
/food-handler/nin-verification
/food-handler/appointments
/food-handler/declaration
/food-handler/assessments
/food-handler/vaccinations
/food-handler/certificate
/food-handler/illness-report
/food-handler/notifications
```

## Employer Pages

```txt
/employer/dashboard
/employer/business-profile
/employer/food-handlers
/employer/food-handlers/invite
/employer/compliance
/employer/vaccinations
/employer/illness-reports
/employer/subscription
/employer/reports
/employer/inspections
```

## Medical Facility Pages

```txt
/facility/dashboard
/facility/profile
/facility/accreditation
/facility/appointments
/facility/assessments
/facility/lab-tests
/facility/certificates
/facility/settlements
/facility/reports
/facility/staff
```

## Doctor Pages

```txt
/doctor/dashboard
/doctor/assessments
/doctor/assessments/[id]/declaration-review
/doctor/assessments/[id]/physical-exam
/doctor/assessments/[id]/lab-results
/doctor/assessments/[id]/vaccinations
/doctor/assessments/[id]/fitness-decision
```

## Lab Staff Pages

```txt
/lab/dashboard
/lab/test-requests
/lab/test-requests/[id]
/lab/results
```

## State Ministry Pages

```txt
/state/dashboard
/state/facilities
/state/facilities/accreditation
/state/certificate-requests
/state/certificates
/state/employers
/state/food-handlers
/state/inspections
/state/fees
/state/reports
/state/users
```

## Federal Ministry Pages

```txt
/federal/dashboard
/federal/states
/federal/certificates
/federal/facilities
/federal/analytics
/federal/reports
/federal/policy-config
```

## Inspector Pages

```txt
/inspector/dashboard
/inspector/scan
/inspector/businesses
/inspector/inspections
/inspector/inspections/new
/inspector/inspections/[id]
```

## Key Components

- StatusBadge
- RoleGuard
- DashboardCard
- DataTable
- FilterBar
- CertificateCard
- QRScanner
- PaymentButton
- SubscriptionPlanCard
- Stepper
- FileUpload
- FormSection
- ConfirmDialog
- AuditTimeline

## Important UX Workflows

### Food Handler Certification Stepper

Steps:
1. Profile
2. NIN verification
3. Select facility
4. Payment
5. Appointment
6. Declaration
7. Medical assessment
8. Lab tests
9. Vaccination validation
10. Certificate

### Doctor Assessment Stepper

Steps:
1. Review declaration
2. Physical examination
3. Request/review lab tests
4. Validate vaccinations
5. Fitness decision
6. Submit to State

### State Certificate Queue

Columns:
- Food handler
- Facility
- Doctor
- Assessment date
- Payment status
- NIN status
- Lab status
- Doctor decision
- Action

## Acceptance Criteria

- Users only see pages relevant to their role.
- Public verification works without login.
- Food handler can complete certification journey.
- Employer can monitor compliance.
- Doctor can complete assessment.
- State can approve certificate issuance.
- Dashboards are understandable and filterable.
