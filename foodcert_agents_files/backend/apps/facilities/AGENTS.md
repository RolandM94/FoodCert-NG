# facilities/AGENTS.md — Medical Facility Accreditation Instructions

## Scope

This app manages medical facility registration, accreditation, state approval, monitoring, and yearly re-accreditation.

## Key Product Rules

- Only approved medical facilities can conduct food handler assessments.
- Medical facilities are approved by State Ministries of Health.
- Facilities are mapped to their respective states.
- Re-accreditation is required annually.
- State-approved assessment prices apply to facilities in that state.

## Facility Types

Support:
- hospital
- clinic
- diagnostic_centre
- primary_health_centre
- mobile_health_unit

## Accreditation Checklist

Capture:
- Written reporting and documentation policy
- Computers in medical records unit
- Computer operators
- Standard declaration forms
- Laboratory request forms
- Patient files
- QR-code certificate capability
- Internet access
- Trained medical records staff
- Trained clinical staff
- Trained non-clinical staff

## Accreditation Statuses

Use:
- draft
- submitted
- under_review
- approved
- rejected
- suspended
- expired
- re_accreditation_due

## Workflow

1. Facility registers.
2. Facility submits accreditation application.
3. Facility uploads required documents.
4. State Ministry reviews application.
5. State Ministry approves or rejects.
6. Approved facility is listed for appointment booking.
7. System tracks annual expiry.
8. Facility re-applies before expiry.
9. State can suspend facility for non-compliance.

## Permission Rules

- Facility Admin can create and update own draft application.
- State Ministry Admin can review facilities only in their state.
- Federal Admin can view facilities nationally.
- Super Admin can manage all records.
- Unapproved facilities cannot conduct assessments.

## Do Not Do

- Do not let facility approve itself.
- Do not let facility conduct assessments when suspended or expired.
- Do not allow facilities outside a state to be selected for that state's assessment unless policy allows cross-state access.
