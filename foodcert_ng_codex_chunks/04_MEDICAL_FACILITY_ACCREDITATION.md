# Chunk 04 — Medical Facility Registration and Accreditation

## Goal

Build the workflow for State Ministries of Health to approve, monitor, suspend, and re-accredit medical facilities.

## Facility Types

- Hospital
- Clinic
- Diagnostic centre
- Primary health centre
- Mobile health unit

## Facility Fields

```txt
facility_name
facility_type
ownership_type
license_number
registration_number
address
state
LGA
contact_person
phone
email
accreditation_status
accreditation_start_date
accreditation_expiry_date
approved_by
standard_assessment_price
```

## Accreditation Checklist

Facility must indicate/prove that it has:

- Written reporting and documentation policy
- Computers in medical records unit
- Computer operators
- Standard health declaration forms
- Laboratory request forms
- Patient files
- QR-code certificate capability
- Internet access
- Trained medical records staff
- Trained clinical staff
- Trained non-clinical staff

## Accreditation Statuses

```txt
draft
submitted
under_review
approved
rejected
suspended
expired
reaccreditation_due
```

## Workflow

1. Facility admin creates facility profile.
2. Facility completes accreditation application.
3. Facility uploads required documents.
4. Facility submits application.
5. State Ministry Admin reviews.
6. State Ministry Admin approves or rejects.
7. Approved facility can accept appointments and conduct assessments.
8. Annual re-accreditation countdown begins.
9. Facility receives reminders before expiry.
10. State Ministry can suspend facility.
11. Suspended/expired facilities cannot conduct new assessments.

## Models

```python
class MedicalFacility(models.Model):
    id = UUIDField(primary_key=True)
    organization = OneToOneField(Organization)
    facility_name = CharField()
    facility_type = CharField()
    ownership_type = CharField()
    license_number = CharField()
    address = TextField()
    state = ForeignKey(State)
    lga = ForeignKey(LGA)
    accreditation_status = CharField()
    accreditation_start_date = DateField(null=True)
    accreditation_expiry_date = DateField(null=True)
    approved_by = ForeignKey(User, null=True, blank=True)
    standard_assessment_price = DecimalField()
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

```python
class FacilityAccreditationApplication(models.Model):
    id = UUIDField(primary_key=True)
    facility = ForeignKey(MedicalFacility)
    application_status = CharField()
    has_reporting_policy = BooleanField(default=False)
    has_medical_records_computers = BooleanField(default=False)
    has_computer_operators = BooleanField(default=False)
    has_standard_forms = BooleanField(default=False)
    has_patient_files = BooleanField(default=False)
    has_qr_certificate_capability = BooleanField(default=False)
    has_internet_access = BooleanField(default=False)
    has_trained_records_staff = BooleanField(default=False)
    has_trained_clinical_staff = BooleanField(default=False)
    has_trained_non_clinical_staff = BooleanField(default=False)
    reviewer = ForeignKey(User, null=True, blank=True)
    review_comment = TextField(blank=True)
    submitted_at = DateTimeField(null=True)
    reviewed_at = DateTimeField(null=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

## API Endpoints

```txt
POST /api/medical-facilities
GET  /api/medical-facilities
GET  /api/medical-facilities/:id
PATCH /api/medical-facilities/:id

POST  /api/facility-accreditation
PATCH /api/facility-accreditation/:id/submit
PATCH /api/facility-accreditation/:id/approve
PATCH /api/facility-accreditation/:id/reject
PATCH /api/facility-accreditation/:id/suspend
PATCH /api/facility-accreditation/:id/reactivate
```

## Acceptance Criteria

- Facility can register and apply for accreditation.
- State Ministry can approve/reject only facilities in its state.
- Only approved facilities can receive appointments and assessments.
- Expired or suspended facilities cannot issue assessment records.
- Facility accreditation is valid for one year by default.
