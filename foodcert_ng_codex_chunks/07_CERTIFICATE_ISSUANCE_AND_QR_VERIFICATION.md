# Chunk 07 — Certificate Issuance and Public QR Verification

## Goal

Implement State Ministry certificate validation, certificate generation, QR code creation, PDF generation, central registry, and public verification.

## Certificate Authority

Certificates are issued by the State Ministry of Health.

## Certificate Validity

Default validity:
- 6 months

Rules:
- Configurable by authorized admin.
- National default remains 6 months.
- Expired certificates automatically become invalid for work.
- Renewal reminders should be sent 30 days and 7 days before expiry.

## Certificate Eligibility

Certificate can be generated only if:

1. NIN is verified or override approved.
2. Payment is successful.
3. Facility is approved and active.
4. Doctor is authorized under facility.
5. Declaration is validated.
6. Physical examination is complete.
7. Required lab tests are reviewed.
8. Vaccination records are valid or doctor-cleared.
9. Doctor decision is `fit`.
10. State Ministry validation is completed, if policy requires.

## State Validation Queue

State Ministry Admin should see pending certificate requests from facilities in their state.

Actions:
- Approve certificate issuance
- Reject issuance
- Request correction
- Suspend assessment
- Flag facility

## Certificate Fields

- Certificate number
- Food handler full name
- Date of birth
- Gender
- Passport photograph
- Masked NIN or internal NIN reference
- Food handler ID
- Employer name
- Medical facility
- Doctor name
- Doctor registration number
- Date of assessment
- Date issued
- Expiry date
- Fitness status
- State of issuance
- Issuing State Ministry of Health
- QR code
- Verification URL
- Digital signature hash

## Certificate Statuses

```txt
active
expired
revoked
suspended
replaced
pending_validation
rejected
```

## Public Verification

Anyone can scan QR code without login.

Public page should show:
- Certificate valid/invalid status
- Certificate number
- Food handler name
- Passport photo
- Issuing State Ministry
- Approved medical facility
- Date issued
- Expiry date
- Fitness status
- Last verified timestamp

Public page must not show:
- Full NIN
- Lab results
- Medical notes
- Diagnosis
- Declaration answers
- Employer private compliance records

## Anti-Fraud Controls

- QR code contains signed token or certificate verification slug.
- Certificate PDF contains digital hash.
- Verification checks database, not just PDF data.
- Revoked and suspended certificates show invalid.
- Expired certificates show expired.
- Verification attempts are logged.

## Models

```python
class Certificate(models.Model):
    id = UUIDField(primary_key=True)
    certificate_number = CharField(unique=True)
    food_handler = ForeignKey(FoodHandlerProfile)
    assessment = OneToOneField(MedicalAssessment)
    employer = ForeignKey(Employer, null=True, blank=True)
    facility = ForeignKey(MedicalFacility)
    doctor = ForeignKey(User)
    issuing_state = ForeignKey(State)
    issued_by_state_user = ForeignKey(User, null=True, blank=True, related_name="issued_certificates")
    issue_date = DateField()
    expiry_date = DateField()
    status = CharField()
    qr_code_url = URLField(blank=True)
    verification_url = URLField()
    pdf_url = URLField(blank=True)
    digital_signature_hash = CharField()
    revoked_by = ForeignKey(User, null=True, blank=True, related_name="revoked_certificates")
    revoked_at = DateTimeField(null=True, blank=True)
    revocation_reason = TextField(blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

```python
class CertificateVerificationLog(models.Model):
    id = UUIDField(primary_key=True)
    certificate = ForeignKey(Certificate, null=True, blank=True)
    certificate_number_submitted = CharField()
    result = CharField()
    ip_address = CharField(blank=True)
    user_agent = TextField(blank=True)
    verified_at = DateTimeField(auto_now_add=True)
```

## API Endpoints

```txt
GET   /api/certificate-requests
POST  /api/assessments/:id/request-certificate
PATCH /api/certificate-requests/:id/approve
PATCH /api/certificate-requests/:id/reject

POST  /api/certificates/generate
GET   /api/certificates
GET   /api/certificates/:id
GET   /api/certificates/:id/download
PATCH /api/certificates/:id/revoke
PATCH /api/certificates/:id/suspend

GET   /verify/:certificateNumber
GET   /api/public/certificates/verify/:certificateNumber
```

## Acceptance Criteria

- Certificate is issued under State Ministry authority.
- Certificate validity defaults to 6 months.
- Certificate has QR code.
- QR opens public verification page.
- Certificate cannot be edited after issuance.
- Revoked, suspended, expired, or invalid certificate is clearly shown in verification.
- Public verification hides sensitive medical data.
