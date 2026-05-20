# Chunk 00b — Models Registry and Policy Clarifications

## Goal

Define all models referenced but not fully specified in other chunks, resolve ambiguous
policy rules, and standardize API conventions across the build pack.

---

## 1 — Missing Models

### Appointment

Referenced in Chunk 06 (`ForeignKey(Appointment)`) but never defined.

```python
class Appointment(models.Model):
    id = UUIDField(primary_key=True)
    food_handler = ForeignKey(FoodHandlerProfile)
    facility = ForeignKey(MedicalFacility)
    assessment = ForeignKey(MedicalAssessment, null=True, blank=True)
    appointment_date = DateTimeField()
    notes = TextField(blank=True)
    status = CharField(
        choices=[
            "pending",
            "confirmed",
            "rescheduled",
            "cancelled",
            "completed",
            "no_show",
        ],
        default="pending",
    )
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### Employer

Referenced across Chunks 03, 05, 08, and 09 (`ForeignKey(Employer)`) but only
described as a field list in Chunk 03. This model is distinct from `Organization`
— the `Organization` represents the platform account, while `Employer` holds the
food-business-specific profile data.

```python
class Employer(models.Model):
    id = UUIDField(primary_key=True)
    organization = OneToOneField(Organization)
    business_name = CharField()
    business_registration_number = CharField(blank=True)
    establishment_category = CharField()
    contact_person_name = CharField()
    contact_person_phone = CharField()
    contact_person_email = EmailField()
    address = TextField()
    state = ForeignKey(State)
    lga = ForeignKey(LGA)
    ward = CharField(blank=True)
    number_of_food_handlers = IntegerField(default=0)
    compliance_status = CharField(
        choices=["compliant", "non_compliant", "under_review"],
        default="under_review",
    )
    subscription_status = CharField(
        choices=["active", "expired", "cancelled", "never_subscribed"],
        default="never_subscribed",
    )
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### LabTest

Referenced in Chunk 06 with statuses and endpoints but no model.

```python
class LabTest(models.Model):
    id = UUIDField(primary_key=True)
    assessment = ForeignKey(MedicalAssessment)
    test_type = CharField(
        choices=[
            "stool_microscopy",
            "stool_culture_sensitivity",
            "hepatitis_a_antigen",
            "typhoid",
            "cholera",
            "other",
        ],
    )
    requested_by = ForeignKey(User, related_name="requested_lab_tests")
    requested_at = DateTimeField(auto_now_add=True)
    sample_collected_at = DateTimeField(null=True, blank=True)
    result = TextField(blank=True)
    result_details = JSONField(default=dict)
    status = CharField(
        choices=[
            "requested",
            "sample_collected",
            "in_progress",
            "positive",
            "negative",
            "inconclusive",
            "repeat_required",
            "reviewed",
        ],
        default="requested",
    )
    submitted_by = ForeignKey(User, null=True, blank=True, related_name="submitted_lab_tests")
    submitted_at = DateTimeField(null=True, blank=True)
    reviewed_by = ForeignKey(User, null=True, blank=True, related_name="reviewed_lab_tests")
    reviewed_at = DateTimeField(null=True, blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### Vaccination

Referenced in Chunk 06 with rules and endpoints but no model.

```python
class Vaccination(models.Model):
    id = UUIDField(primary_key=True)
    food_handler = ForeignKey(FoodHandlerProfile, related_name="vaccinations")
    assessment = ForeignKey(MedicalAssessment, null=True, blank=True)
    facility = ForeignKey(MedicalFacility, null=True, blank=True)
    vaccine_type = CharField(
        choices=[
            "typhoid",
            "hepatitis_a_dose_1",
            "hepatitis_a_dose_2",
            "other",
        ],
    )
    administered_date = DateField()
    expiry_date = DateField(null=True, blank=True)
    batch_number = CharField(blank=True)
    administered_by = ForeignKey(User, null=True, blank=True)
    administering_facility_name = CharField(blank=True)
    notes = TextField(blank=True)
    status = CharField(
        choices=["valid", "expired", "pending_reminder"],
        default="valid",
    )
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### Notification

Referenced across multiple chunks (certificate expiry reminders, Hepatitis A
second-dose reminders, re-accreditation reminders) but never modeled.

```python
class Notification(models.Model):
    id = UUIDField(primary_key=True)
    recipient = ForeignKey(User, related_name="notifications")
    notification_type = CharField(
        choices=[
            "certificate_expiry_reminder",
            "certificate_renewal",
            "vaccination_due",
            "accreditation_expiry",
            "illness_reported",
            "return_to_work_cleared",
            "subscription_expiry",
            "settlement_processed",
            "inspection_assigned",
            "compliance_notice",
            "system_announcement",
            "other",
        ],
    )
    channel = CharField(choices=["email", "sms", "in_app"], default="in_app")
    subject = CharField(blank=True)
    body = TextField()
    template_name = CharField(blank=True)
    context_data = JSONField(default=dict)
    status = CharField(
        choices=["pending", "sent", "delivered", "failed", "read"],
        default="pending",
    )
    sent_at = DateTimeField(null=True, blank=True)
    read_at = DateTimeField(null=True, blank=True)
    failure_reason = TextField(blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

---

## 2 — State Ministry Certificate Validation Policy

Chunk 06 states a certificate can be requested when the doctor decision is `fit`.
Chunk 07 adds: *"State Ministry validation is completed, if policy requires."*
This section resolves that ambiguity.

### Policy Configuration

Add a per-state configuration flag to a `StatePolicyConfig` model:

```python
class StatePolicyConfig(models.Model):
    id = UUIDField(primary_key=True)
    state = OneToOneField(State)
    requires_state_certificate_validation = BooleanField(default=True)
    certificate_validity_months = IntegerField(default=6)
    typhoid_validity_years = IntegerField(default=3)
    hepatitis_a_second_dose_months = IntegerField(default=6)
    auto_renewal_reminder_days = JSONField(default=[30, 7])
    updated_by = ForeignKey(User, null=True, blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### Field-level defaults in `.env` remain the fallback:

```
DEFAULT_CERTIFICATE_VALIDITY_MONTHS=6
DEFAULT_TYPHOID_VALIDITY_YEARS=3
DEFAULT_HEPATITIS_A_SECOND_DOSE_MONTHS=6
```

### Resolution Rule

1. If `state_policy.requires_state_certificate_validation` is `true` (default):
   - Certificate request goes into the State Review Queue.
   - Certificate is **not** generated until a State Ministry Admin approves.
2. If `state_policy.requires_state_certificate_validation` is `false`:
   - Certificate is generated automatically once all eligibility checks pass
     (NIN verified, payment success, doctor decision `fit`, all steps complete).
3. Only Federal Ministry Admins can toggle this flag per state.

---

## 3 — API Conventions

### Response Envelope

**Success:**
```json
{
  "success": true,
  "data": { ... },
  "message": "...",
  "meta": {
    "page": 1,
    "page_size": 25,
    "total": 156,
    "total_pages": 7
  }
}
```

Single-resource responses omit `meta`.

**Error:**
```json
{
  "success": false,
  "error": "Validation failed.",
  "code": "VALIDATION_ERROR",
  "details": {
    "email": ["This field is required."],
    "nin": ["NIN must be 11 digits."]
  }
}
```

### Error Codes

| Code | Meaning |
|------|---------|
| `VALIDATION_ERROR` | Input validation failure |
| `AUTHENTICATION_REQUIRED` | No valid auth token |
| `PERMISSION_DENIED` | Insufficient role/scope |
| `NOT_FOUND` | Resource does not exist |
| `CONFLICT` | Duplicate or state conflict |
| `PAYMENT_REQUIRED` | Payment must be completed first |
| `NIN_NOT_VERIFIED` | NIN verification pending/failed |
| `FACILITY_NOT_ACCREDITED` | Facility not approved |
| `SUBSCRIPTION_EXPIRED` | Employer subscription inactive |
| `CERTIFICATE_INVALID` | Certificate revoked/suspended/expired |
| `INTERNAL_ERROR` | Unexpected server error |

### Pagination

Query parameters on all `GET /api/...` list endpoints:

- `?page=1` (default 1)
- `?page_size=25` (default 25, max 100)
- `?ordering=created_at` (prefix `-` for descending, e.g. `-created_at`)

### Filtering

Each list endpoint supports relevant query filters. Standard patterns:

- `?status=active`
- `?state=uuid`
- `?lga=uuid`
- `?date_from=2026-01-01&date_to=2026-12-31`

---

## 4 — Certificate Number Format

```
FH-{STATE_CODE}-{YYYY}-{8-HEX-RANDOM}
```

| Part | Description |
|------|-------------|
| `FH` | Fixed prefix: Food Handler |
| `STATE_CODE` | 2-letter state code (e.g. `LA` for Lagos, `AB` for Abia, `FC` for FCT) |
| `YYYY` | Year of issuance |
| `8-HEX-RANDOM` | 8-character uppercase hex string |

**Example:** `FH-LA-2026-A3F7B1C2`

Generated server-side at certificate creation time. Collision check against existing
certificate numbers before finalization.

### State Code Reference

See `locations` app state seed data. The state code is the official 2-letter
abbreviation stored on each `State` record.

---

## 5 — Model Relationship Diagram

```
User ────────────┐
  │              │ (organization)
  ▼              ▼
FoodHandler    Organization
  │ (FK)         │ (OneToOne)
  ├─► Employer ──┘
  │     │ (FK)
  │     ├─► EmployerSubscription ───► EmployerSubscriptionPlan
  │     └─► Inspection
  │
  ├─► NINVerification
  ├─► Vaccination
  ├─► IllnessReport
  │
  ▼
MedicalAssessment
  ├─► Appointment
  ├─► HealthDeclaration
  ├─► LabTest
  ├─► PaymentTransaction
  └─► Certificate ──► CertificateVerificationLog



MedicalFacility (FK→ State)
  ├─► FacilityAccreditationApplication
  ├─► Appointment
  ├─► MedicalAssessment (FK)
  └─► Settlement ──► PaymentTransaction



State ──► LGA
State ──► StatePolicyConfig
State ──► AssessmentFee



AuditLog ──► User (actor)
Notification ──► User (recipient)
```

- `FoodHandlerProfile` links to `User` via OneToOne.
- `Employer` links to `Organization` via OneToOne.
- `MedicalFacility` links to `Organization` via OneToOne.
- `MedicalAssessment` is the central hub connecting payment, declaration,
  lab tests, vaccinations, and the final certificate.
- `Certificate` is OneToOne with `MedicalAssessment`.
