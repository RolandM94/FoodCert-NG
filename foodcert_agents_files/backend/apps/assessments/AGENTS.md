# assessments/AGENTS.md — Medical Assessment Workflow Instructions

## Scope

This app manages the food handler medical assessment lifecycle:
- Assessment creation
- Health declaration
- Doctor validation
- Physical examination
- Lab request linkage
- Vaccination review linkage
- Fitness decision
- Submission to State Ministry for certificate validation

## Key Rules

- An assessment must be linked to:
  - Food handler
  - Employer, where applicable
  - Approved medical facility
  - Doctor
  - Payment transaction
  - State
- Do not allow assessment activation before payment confirmation unless policy explicitly allows it.
- Do not allow assessment completion if the facility is not approved.
- Do not allow certificate eligibility if NIN is not verified or manually overridden.
- Do not allow final fitness decision if required declaration, exam, lab, and vaccination review steps are incomplete.
- All workflow transitions must be auditable.

## Assessment Status Flow

Recommended statuses:
- draft
- payment_pending
- payment_confirmed
- appointment_booked
- declaration_submitted
- declaration_validated
- physical_exam_completed
- lab_tests_pending
- lab_results_reviewed
- vaccination_reviewed
- doctor_decision_pending
- fit
- temporarily_not_fit
- not_fit
- submitted_for_state_validation
- certificate_issued
- closed

## Health Declaration

The food handler must answer the guideline declaration questions:
- Diarrhoea/vomiting in last 7 days
- Fever
- Skin trouble
- Boils, styes, or sepsis
- Discharge from eye, ear, nose, gums, or mouth
- Recurring skin or ear infection
- Recurring bowel disorder
- Cholera contact
- Diarrhoea/vomiting contact
- Typhoid/paratyphoid/jaundice contact
- Typhoid/paratyphoid carrier history
- Current or previous typhoid fever

If any high-risk answer is yes:
- Set `risk_flag = true`
- Require doctor review
- Do not block automatically unless policy says so

## Physical Examination

Doctor records:
- Fever
- Jaundice
- Skin infection
- Boils/styes/sepsis
- Discharge
- Diarrhoea
- Vomiting
- Sore throat with fever
- Cough or flu
- Doctor notes

## Fitness Decision

Possible decisions:
- fit
- temporarily_not_fit
- not_fit
- requires_vaccination
- requires_lab_test
- requires_recheck
- requires_public_health_clearance

The decision service must validate:
- Payment confirmed
- NIN verified or override approved
- Facility approved
- Declaration validated
- Physical exam completed
- Required lab tests reviewed
- Vaccination status reviewed
- Doctor authorized

## Do Not Do

- Do not issue certificate directly from this app.
- Do not expose doctor notes to employers or public verifiers.
- Do not allow frontend to override backend workflow state.
- Do not allow a doctor outside the facility to complete an assessment unless explicitly authorized.
