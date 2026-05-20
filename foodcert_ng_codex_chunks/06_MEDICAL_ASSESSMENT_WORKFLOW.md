# Chunk 06 — Medical Assessment Workflow

## Goal

Implement the medical workflow: appointment, declaration, doctor examination, lab tests, vaccination records, and fitness decision.

## Appointment Workflow

Statuses:
```txt
pending
confirmed
rescheduled
cancelled
completed
no_show
```

Rules:
- Only approved facilities can receive bookings.
- Payment must be successful before assessment is activated.
- Food handler must complete declaration before doctor validation.

## Health Declaration Questions

Food handler answers Yes/No:

1. Suffered from diarrhoea/vomiting in the last seven days?
2. Suffered from fever since more than one week ago?
3. Skin trouble affecting hands, arms, or face?
4. Boils, styes, or sepsis on fingers or hands?
5. Discharge from eye, ear, nose, gums, or mouth?
6. Recurring skin or ear infection?
7. Recurring bowel disorder?
8. Contact with anyone with cholera in last five days?
9. Contact with anyone with diarrhoea/vomiting in last seven days?
10. Contact with anyone with typhoid, paratyphoid, or jaundice in last 21 days?
11. Ever known carrier of typhoid or paratyphoid?
12. Ever had or currently known to have typhoid fever?

Risk logic:
- Any “Yes” to high-risk question should set `risk_flag=True`.
- Doctor must review risk flag before proceeding.

## Physical Examination Checklist

Doctor records:

- Fever
- Jaundice
- Skin infection on hands, arms, or face
- Boils, styes, or sepsis on finger
- Discharge from eye, ear, nose, gums, or mouth
- Diarrhoea
- Vomiting
- Sore throat with fever
- Cough or flu
- Known typhoid carrier history
- Other notes

## Lab Tests

Required/standard:
- Stool microscopy
- Stool culture and sensitivity
- Hepatitis A antigen

Optional:
- Typhoid
- Cholera
- Other clinically indicated tests

Statuses:
```txt
requested
sample_collected
in_progress
positive
negative
inconclusive
repeat_required
reviewed
```

## Vaccination Records

Track:
- Typhoid
- Hepatitis A
- Other vaccines if configured

Rules:
- Typhoid validity: 3 years by default.
- Hepatitis A: dose 1 at month 0 and dose 2 after 6 months.
- Missing/expired vaccination should trigger doctor review and/or prescription.
- Reminder should be created for Hepatitis A second dose.

## Fitness Decision Outcomes

```txt
pending
fit
temporarily_not_fit
not_fit
requires_vaccination
requires_lab_test
requires_recheck
requires_treatment
requires_public_health_clearance
return_to_work_on_date
```

## Fit-to-Work Rule

A certificate can be requested only if:
- NIN is verified or regulator override is approved.
- Assessment payment is successful.
- Declaration is submitted and doctor-validated.
- Physical exam is completed.
- Required lab tests are completed/reviewed.
- Vaccination requirements are valid or doctor-cleared.
- Doctor sets final decision to `fit`.

## Models

```python
class MedicalAssessment(models.Model):
    id = UUIDField(primary_key=True)
    food_handler = ForeignKey(FoodHandlerProfile)
    employer = ForeignKey(Employer, null=True, blank=True)
    facility = ForeignKey(MedicalFacility)
    doctor = ForeignKey(User, null=True, blank=True)
    appointment = ForeignKey(Appointment, null=True, blank=True)
    assessment_date = DateTimeField(null=True)
    payment_transaction = ForeignKey(PaymentTransaction, null=True)
    declaration_status = CharField()
    physical_exam_status = CharField()
    lab_status = CharField()
    vaccination_status = CharField()
    final_decision = CharField(default="pending")
    return_to_work_date = DateField(null=True, blank=True)
    doctor_notes = TextField(blank=True)
    signed_at = DateTimeField(null=True, blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

```python
class HealthDeclaration(models.Model):
    id = UUIDField(primary_key=True)
    assessment = OneToOneField(MedicalAssessment)
    diarrhoea_vomiting_last_7_days = BooleanField()
    fever_more_than_one_week = BooleanField()
    skin_trouble = BooleanField()
    boils_styes_sepsis = BooleanField()
    discharge_eye_ear_nose_mouth = BooleanField()
    recurring_skin_or_ear_infection = BooleanField()
    recurring_bowel_disorder = BooleanField()
    cholera_contact_last_5_days = BooleanField()
    diarrhoea_vomiting_contact_last_7_days = BooleanField()
    typhoid_paratyphoid_jaundice_contact_last_21_days = BooleanField()
    typhoid_or_paratyphoid_carrier = BooleanField()
    previous_or_current_typhoid = BooleanField()
    certified_true = BooleanField(default=False)
    risk_flag = BooleanField(default=False)
    submitted_at = DateTimeField(null=True)
    validated_by_doctor = ForeignKey(User, null=True, blank=True)
    validated_at = DateTimeField(null=True)
```

## API Endpoints

```txt
POST  /api/appointments
GET   /api/appointments
PATCH /api/appointments/:id

POST  /api/assessments
GET   /api/assessments
GET   /api/assessments/:id

POST  /api/assessments/:id/declaration
PATCH /api/declarations/:id/validate

POST  /api/assessments/:id/physical-examination

POST  /api/assessments/:id/lab-tests
PATCH /api/lab-tests/:id/result
PATCH /api/lab-tests/:id/review

POST  /api/assessments/:id/vaccinations
GET   /api/food-handlers/:id/vaccinations

PATCH /api/assessments/:id/fitness-decision
```

## Acceptance Criteria

- Food handler can book an appointment only with approved facility.
- Assessment is not active until payment succeeds.
- Declaration risk answers are flagged.
- Doctor can validate declaration and complete exam.
- Lab staff can submit results.
- Doctor can issue final decision.
- Certificate workflow can begin only when decision is `fit`.
