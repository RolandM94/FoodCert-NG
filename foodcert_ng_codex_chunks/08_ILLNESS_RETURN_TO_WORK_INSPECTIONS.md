# Chunk 08 — Illness Reporting, Return-to-Work, and Inspections

## Goal

Implement post-certification illness reporting, exclusion from food handling, return-to-work clearance, and inspection/enforcement workflow.

## Illness Reporting

Who can report:
- Food handler
- Employer
- Doctor
- Inspector
- State Ministry Admin

Symptoms:
- Jaundice
- Diarrhoea
- Vomiting
- Fever
- Sore throat with fever
- Infected skin lesions
- Discharge from ear, eye, or nose
- Cough or flu
- Other symptoms

## Illness Workflow

1. Illness is reported.
2. Food handler status becomes `temporarily_excluded`.
3. Employer is notified not to assign food handling duties.
4. Doctor reviews case.
5. System applies return-to-work rules.
6. Lab tests/clearance may be requested.
7. Doctor clears or rejects return.
8. Return-to-work certificate is generated if cleared.
9. Food handler status returns to fit, where appropriate.

## Return-to-Work Rules

| Condition | Rule |
|---|---|
| General diarrhoea/vomiting | Exclude until 48 hours after symptoms stop |
| Cholera | Require medical clearance and two negative stool samples at least 24 hours apart |
| Shigella | Require medical clearance and two negative stool samples at least 48 hours apart |
| Hepatitis A | Exclude for seven days after onset of jaundice or symptoms |
| Infected skin lesion | Allow only if completely covered; otherwise exclude |
| Amoebic dysentery | Require one negative stool sample at least one week after treatment |
| Taenia solium | Require two negative stool tests at 1 and 2 weeks post-treatment |
| Lassa fever | Require documentation, medical clearance, and health authority approval |

## IllnessReport Model

```python
class IllnessReport(models.Model):
    id = UUIDField(primary_key=True)
    food_handler = ForeignKey(FoodHandlerProfile)
    employer = ForeignKey(Employer, null=True, blank=True)
    reported_by = ForeignKey(User)
    symptoms = JSONField(default=dict)
    suspected_condition = CharField(blank=True)
    symptom_start_date = DateField(null=True)
    symptom_end_date = DateField(null=True)
    exclusion_start_date = DateField()
    earliest_return_date = DateField(null=True, blank=True)
    clearance_required = BooleanField(default=True)
    clearance_status = CharField(default="pending")
    reviewed_by_doctor = ForeignKey(User, null=True, blank=True)
    notes = TextField(blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

## Inspection Module

Inspectors should be able to:
- Search food business
- Scan certificates
- Start inspection
- Complete checklist
- Upload evidence/photos
- Record GPS location
- Issue notices
- Submit inspection report
- Track remediation

## Inspection Checklist

- Are all food handlers registered?
- Are certificates valid?
- Are certificates genuine?
- Are vaccination records current?
- Are sick handlers excluded?
- Are handwashing facilities available?
- Are PPEs available?
- Are hygiene practices enforced?
- Are employer records up to date?
- Are expired certificates being used?

## Enforcement Actions

```txt
none
advisory
warning
compliance_notice
follow_up_required
sanction_recommended
escalated_to_state
```

## Inspection Model

```python
class Inspection(models.Model):
    id = UUIDField(primary_key=True)
    inspector = ForeignKey(User)
    employer = ForeignKey(Employer)
    inspection_date = DateTimeField()
    gps_latitude = DecimalField(null=True)
    gps_longitude = DecimalField(null=True)
    checklist_responses = JSONField(default=dict)
    compliance_score = DecimalField(null=True)
    enforcement_action = CharField()
    findings = TextField(blank=True)
    evidence_files = JSONField(default=list)
    status = CharField(default="draft")
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

## API Endpoints

```txt
POST  /api/illness-reports
GET   /api/illness-reports
GET   /api/illness-reports/:id
PATCH /api/illness-reports/:id/review
PATCH /api/illness-reports/:id/clearance

POST  /api/inspections
GET   /api/inspections
GET   /api/inspections/:id
PATCH /api/inspections/:id
PATCH /api/inspections/:id/submit
POST  /api/inspections/:id/evidence
```

## Acceptance Criteria

- Illness report automatically excludes food handler from food handling.
- Employer sees operational status only.
- Return-to-work date is calculated where possible.
- Doctor can clear food handler.
- Inspector can scan certificate during inspection.
- Inspection report is visible to State Ministry.
