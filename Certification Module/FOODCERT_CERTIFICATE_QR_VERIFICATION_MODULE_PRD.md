# PRD: Certificate & QR Verification Module — FoodCert NG

## 1. Module Name

**Certificate & QR Verification Module**

## 2. Product Context

The Certificate & QR Verification Module is the official certification and public verification layer of **FoodCert NG**. It converts a completed and State-validated medical assessment into a secure, state-issued, digitally verifiable food handler fitness certificate.

This module sits after the Medical Assessment Workflow Module and depends on:

- Food handler profile completion
- NIN verification or approved override
- Assessment payment confirmation
- Approved medical facility participation
- Doctor fitness decision
- Laboratory and vaccination review
- State Ministry validation
- Policy configuration for certificate validity
- Public verification privacy rules

The module must support a national rollout while preserving State Ministry issuing authority. The Federal Ministry has national oversight of the certificate registry but does not replace the State Ministry as the certificate issuer.

---

# 3. Product Goal

To provide a secure, tamper-resistant, publicly verifiable certificate system that allows State Ministries of Health to issue food handler fitness certificates and allows employers, inspectors, food handlers, regulators, and the public to verify certificate authenticity without exposing sensitive medical information.

---

# 4. Core Objectives

The Certificate & QR Verification Module must:

1. Generate food handler fitness certificates only after State Ministry approval.
2. Ensure each certificate is linked to a complete and valid assessment.
3. Show State Ministry of Health as the certificate issuing authority.
4. Generate unique certificate numbers.
5. Generate QR codes for public verification.
6. Generate downloadable PDF certificates.
7. Provide public certificate verification without login.
8. Protect sensitive medical data from public and employer views.
9. Support certificate expiry, renewal, suspension, revocation, and replacement.
10. Maintain a central certificate registry.
11. Support state-level certificate registry management.
12. Support federal-level national registry oversight.
13. Provide inspector-friendly QR verification.
14. Provide employer-safe certificate visibility.
15. Create audit logs for all certificate actions.

---

# 5. Key Actors

## 5.1 Food Handler

Can:

- View own certificates.
- Download active certificate PDF.
- View certificate status.
- Share public verification link.
- Renew certificate when expiring or expired.
- View revocation/suspension notice where applicable.

Cannot:

- Edit certificate.
- Generate certificate manually.
- Override expiry, revocation, or suspension.
- Access certificate audit internals unless permitted.

## 5.2 Employer

Can:

- View certificate status for linked food handlers.
- Download certificate copy where permitted.
- Verify certificate using QR or certificate number.
- Receive expiry alerts.
- View operational certificate categories.

Cannot:

- View medical assessment details.
- View lab results.
- View doctor notes.
- View diagnosis.
- View full NIN.
- Edit or revoke certificate.

## 5.3 Medical Facility

Can:

- View certificates resulting from assessments conducted by the facility.
- View certificate issuance status.
- Respond to State Ministry clarification requests before issuance.
- View certificate rejection reasons related to submitted assessments.
- Download facility-level certificate issuance reports.

Cannot:

- Issue certificate directly.
- Edit issued certificate.
- Revoke or suspend certificate.
- Override State Ministry decision.

## 5.4 Doctor

Can:

- View certificate status for assessments they completed.
- View certificate issued after their fit decision and State validation.
- View rejection or clarification related to their assessment.
- Provide clarification when State Ministry requests it.

Cannot:

- Issue certificate directly.
- Edit certificate after issuance.
- Revoke certificate.

## 5.5 State Ministry Certificate Verification Officer

Can:

- Review certificate validation queue.
- Approve or reject certificate issuance.
- Request clarification.
- Generate certificate after approval.
- View state certificate registry.
- Suspend certificates.
- Revoke certificates.
- Replace certificates.
- Export state certificate reports.

## 5.6 State Ministry Admin

Can:

- Manage certificate templates for the state where policy allows.
- Approve certificate issuance.
- Manage state registry.
- Configure state certificate policies if permitted.
- Suspend/revoke certificates.
- Monitor certificate performance.

## 5.7 Federal Ministry User

Can:

- View national certificate registry oversight dashboard.
- Compare certificate issuance by state.
- View aggregate certificate metrics.
- Flag suspicious certificates for review.
- Monitor revoked/suspended certificates nationally.
- Configure national certificate policy defaults where authorized.

Cannot by default:

- Replace State Ministry issuing authority.
- Edit state-issued certificates unless explicit federal override policy exists.
- View sensitive medical details without authorization.

## 5.8 Inspector / Environmental Health Officer

Can:

- Scan QR code.
- Verify certificate authenticity.
- View public/inspector-safe certificate details.
- Save verification result into inspection record.
- Flag invalid or suspicious certificates.
- Verify certificates by number where scanning fails.

Cannot:

- View lab results.
- View diagnosis.
- View doctor notes.
- Edit certificate.

## 5.9 Public Verifier

Can:

- Scan QR code.
- Enter certificate number.
- See public verification result.

Cannot:

- View medical details.
- View full NIN.
- View employer private compliance records.
- View assessment details.

---

# 6. Module Scope

## 6.1 In Scope

The module includes:

- Certificate eligibility validation
- State Ministry approval workflow
- Certificate number generation
- Certificate PDF generation
- QR code generation
- Public verification page
- Manual certificate number verification
- Certificate registry
- Certificate expiry
- Certificate renewal trigger
- Certificate suspension
- Certificate revocation
- Certificate replacement
- Digital signature/hash
- Certificate audit trail
- Employer certificate visibility
- Inspector QR verification
- Federal registry oversight
- Certificate reports and exports

## 6.2 Out of Scope for MVP

The following may be deferred:

- Blockchain certificate anchoring
- Offline QR verification cache
- Biometric certificate verification
- Complex appeal workflow
- Third-party API marketplace
- Cross-border verification
- Bulk certificate printing service
- Physical card issuance

---

# 7. Certificate Issuance Governance

## 7.1 Issuing Authority

Certificates are issued by the **State Ministry of Health**.

The certificate must clearly display:

- Issuing State Ministry of Health
- State of issuance
- Approved medical facility
- Doctor name and registration number
- Certificate number
- Certificate issue date
- Certificate expiry date
- QR code
- Public verification URL
- Digital signature or certificate hash

## 7.2 Federal Oversight

The Federal Ministry has national oversight of the central certificate registry.

Federal Ministry can:

- Monitor certificate issuance nationally.
- Compare issuance patterns by state.
- View suspended/revoked certificates.
- Review state performance.
- Configure national defaults where authorized.
- Flag suspicious certificates.

Federal Ministry does not automatically replace State Ministry issuing authority.

---

# 8. Certificate Eligibility Requirements

Before a certificate can be generated, the backend must validate:

1. Food handler profile is complete.
2. Food handler NIN is verified or override approved.
3. Assessment payment is confirmed.
4. Assessment was conducted by an approved and active medical facility.
5. Facility accreditation was valid at assessment time.
6. Doctor was authorized for that facility.
7. Health declaration was submitted and validated.
8. Physical examination was completed.
9. Required lab tests were completed and reviewed.
10. Vaccination review was completed.
11. Doctor final decision is `Fit to Work`.
12. Assessment was digitally signed by doctor.
13. Assessment was submitted to State Ministry.
14. State Ministry approved certificate issuance.
15. No unresolved illness/exclusion block exists.
16. No conflicting active certificate exists unless replacement/renewal policy permits it.
17. Certificate validity policy is available.
18. Certificate template is available.

## 8.1 Blocking Rules

Certificate generation must be blocked if:

- Doctor decision is not `Fit to Work`.
- State Ministry has not approved issuance.
- NIN is not verified or overridden.
- Payment is not confirmed.
- Facility is not approved.
- Facility accreditation is suspended or expired.
- Lab results are pending review.
- Vaccination review is pending.
- There is an unresolved illness exclusion.
- Certificate was already issued for the same assessment.
- Certificate policy is missing or invalid.

---

# 9. Certificate Issuance Workflow

## 9.1 High-Level Flow

```txt
Doctor marks food handler Fit
→ Facility submits completed assessment to State Ministry
→ State Verification Desk reviews eligibility checklist
→ State approves certificate issuance
→ System generates certificate number
→ System calculates issue and expiry dates
→ System generates certificate PDF
→ System generates QR code
→ Certificate is stored in central registry
→ Food handler, employer, facility, and State Ministry are notified
→ Public verification becomes active
```

## 9.2 State Approval Actions

State Ministry can:

- Approve issuance
- Reject issuance
- Request clarification
- Escalate for supervisor review

## 9.3 Certificate Generation Trigger

Certificate generation should be triggered only after State approval.

Recommended design:

- `CertificateIssuanceService.approve_and_generate(assessment_id, approved_by)`
- Service validates all requirements.
- Service creates immutable certificate record.
- Service creates certificate PDF.
- Service creates QR code.
- Service logs audit event.
- Service sends notifications.

---

# 10. Certificate Numbering

## 10.1 Requirements

Certificate numbers must be:

- Globally unique.
- Human-readable.
- Traceable to issuing state and year.
- Difficult to guess where possible.
- Never reused.
- Preserved even after revocation or replacement.

## 10.2 Suggested Format

```txt
FCNG-{STATE_CODE}-{YEAR}-{SEQUENCE}-{CHECK}
```

Example:

```txt
FCNG-LA-2026-000123-A7
```

Where:

- `FCNG` = FoodCert NG
- `LA` = state code
- `2026` = year of issuance
- `000123` = state-year sequence
- `A7` = checksum/random check segment

## 10.3 Numbering Rules

- Sequence should be unique per state per year.
- Certificate number should not reveal sensitive data.
- Replacement certificates should get new certificate numbers.
- Old certificate should be marked `Replaced`.
- Renewals should get new certificate numbers.
- Duplicate generation must be prevented with database constraints.

---

# 11. Certificate Validity and Expiry

## 11.1 Default Validity

Default certificate validity is **6 months**.

## 11.2 Configurable Validity

Certificate validity must be configurable through policy settings:

- National default validity
- State override, if permitted
- Renewal reminder days
- Grace period, if any
- Expired certificate behavior
- Renewal window

## 11.3 Issue and Expiry Date Rules

- `issue_date` = date State approves and certificate is generated.
- `expiry_date` = issue date + configured validity period.
- Expired certificate becomes invalid automatically.
- Expiry status should be calculated or updated by scheduled job.
- Public verification must show expired certificates as invalid/expired.

## 11.4 Renewal

Renewal requires a new assessment unless policy explicitly allows administrative renewal.

Recommended rule:

- Certificate renewal requires fresh medical assessment.

---

# 12. Certificate PDF Generation

## 12.1 Certificate PDF Requirements

The certificate PDF should include:

- Platform name/logo
- Issuing State Ministry of Health
- Certificate title
- Certificate number
- Food handler full name
- Passport photo
- Gender
- Date of birth
- Masked NIN or approved identifier
- Food handler ID
- Employer name, where applicable
- Business branch, where applicable
- Medical facility name
- Doctor name
- Doctor registration number
- Date of assessment
- Issue date
- Expiry date
- Fitness status
- QR code
- Public verification URL
- Digital signature/hash
- Disclaimer/privacy notice
- State Ministry authorized signatory, where applicable

## 12.2 PDF Rules

- PDF must be regenerated only through controlled replacement/correction workflow.
- PDF should not include lab results.
- PDF should not include diagnosis.
- PDF should not include doctor notes.
- PDF should not include full NIN.
- PDF should be stored securely.
- Public verification should not expose the PDF unless policy permits.
- Food handler and employer may download certificate PDF where allowed.

## 12.3 PDF Template

Template should support:

- National default template
- State-specific branding
- State signatory block
- Dynamic QR code
- Dynamic certificate metadata
- Watermark for revoked/expired where downloaded later

---

# 13. QR Code Generation

## 13.1 QR Code Purpose

QR code enables certificate authenticity verification.

## 13.2 QR Content

QR code should contain:

- Public verification URL with opaque token

Example:

```txt
https://verify.foodcert.ng/cert/{verification_token}
```

## 13.3 QR Code Rules

- Do not encode sensitive medical data directly inside QR code.
- Do not encode full NIN.
- Use opaque token or certificate public ID.
- Token should be unique.
- Token should remain valid for verification even after expiry/revocation, so page can show expired/revoked status.
- Verification attempt should be logged.

## 13.4 QR Security

Verification should validate:

- Token exists.
- Certificate number exists.
- Certificate has not been tampered with.
- Certificate status.
- Certificate expiry.
- Digital signature/hash.
- Issuing state.
- Facility approval status at issuance.

---

# 14. Public Certificate Verification

## 14.1 Purpose

Public verification allows anyone to confirm whether a certificate is genuine and valid.

## 14.2 Entry Points

Public users can verify by:

1. Scanning QR code.
2. Entering certificate number.
3. Entering verification token, where applicable.

## 14.3 Public Verification Display

If certificate is valid, show:

- Green `Valid` badge
- Certificate number
- Food handler name
- Passport photo
- Issuing State Ministry
- Approved medical facility
- Date issued
- Expiry date
- Fitness status
- Last verified timestamp

If certificate is expired, show:

- Amber `Expired` badge
- Certificate number
- Food handler name
- Issuing State Ministry
- Expiry date
- Message: “This certificate has expired and is no longer valid.”

If certificate is revoked, show:

- Red `Revoked` badge
- Certificate number
- Issuing State Ministry
- Message: “This certificate has been revoked and is not valid.”

If certificate is suspended, show:

- Red/amber `Suspended` badge
- Message: “This certificate is currently suspended.”

If certificate is not found:

- Show `Invalid / Not Found`
- Message: “Certificate not found or QR code is invalid.”

## 14.4 Public Verification Must Not Show

- Full NIN
- Lab results
- Diagnosis
- Doctor notes
- Declaration answers
- Treatment details
- Internal assessment notes
- Employer private compliance records
- Payment records
- Settlement records

## 14.5 Public Verification Actions

Public verifier can:

- Verify another certificate.
- Print verification result.
- Report suspicious certificate.

---

# 15. Inspector Verification

## 15.1 Purpose

Inspectors need a mobile-friendly verification interface during field inspections.

## 15.2 Inspector Verification Features

Inspector can:

- Scan QR code.
- Enter certificate number manually.
- View public/inspector-safe certificate status.
- Confirm passport photo matches handler.
- Save verification result to inspection record.
- Flag suspicious certificate.
- Continue inspection checklist.

## 15.3 Inspector Verification Result

Show:

- Certificate status
- Food handler name
- Passport photo
- Certificate number
- Issuing state
- Facility
- Issue date
- Expiry date
- Fitness status
- Verification timestamp

Do not show:

- Lab details
- Diagnosis
- Doctor notes
- Full NIN

---

# 16. Employer Certificate Visibility

## 16.1 Employer Certificate View

Employers can view certificate information for linked food handlers.

Employer can see:

- Food handler name
- Passport photo
- Certificate number
- Certificate status
- Issue date
- Expiry date
- Issuing State Ministry
- Facility
- Fitness status
- Renewal status
- Download certificate, if permitted

Employer cannot see:

- Lab results
- Diagnosis
- Doctor notes
- Declaration answers
- Full NIN

## 16.2 Employer Certificate Actions

Employer can:

- View certificate
- Download certificate copy
- Verify certificate
- Send renewal reminder
- Export certificate list
- Filter expiring/expired certificates

---

# 17. Certificate Statuses

## 17.1 Status List

Use the following statuses:

- Pending State Validation
- Active
- Expiring Soon
- Expired
- Suspended
- Revoked
- Replaced
- Invalid
- Draft Generation Failed
- Correction Pending

## 17.2 Status Definitions

| Status | Meaning |
|---|---|
| Pending State Validation | Assessment is awaiting State approval |
| Active | Certificate is valid and within expiry |
| Expiring Soon | Certificate is active but nearing expiry |
| Expired | Certificate validity date has passed |
| Suspended | Certificate temporarily invalidated |
| Revoked | Certificate permanently invalidated |
| Replaced | Certificate replaced by corrected/new certificate |
| Invalid | Certificate failed verification or is not recognized |
| Draft Generation Failed | Certificate generation process failed |
| Correction Pending | Correction/replacement workflow is underway |

---

# 18. Certificate Suspension

## 18.1 Purpose

Suspension temporarily invalidates a certificate.

## 18.2 Who Can Suspend

- Authorized State Ministry users
- Federal users only if explicit federal override policy exists
- Super Admin only for technical/security emergency, with audit trail

## 18.3 Suspension Reasons

Examples:

- Suspected fraud
- Pending investigation
- Incorrect certificate information
- Facility issue
- Medical risk discovered after issuance
- Regulatory hold

## 18.4 Suspension Requirements

User must provide:

- Reason
- Supporting note
- Effective date
- Expected review date, optional
- Approval, where policy requires

## 18.5 Suspension Effect

- Public verification shows `Suspended`.
- Employer sees certificate not currently valid.
- Food handler receives notification.
- State registry shows suspended status.
- Certificate may later be reinstated or revoked.

---

# 19. Certificate Revocation

## 19.1 Purpose

Revocation permanently invalidates a certificate.

## 19.2 Who Can Revoke

- Authorized State Ministry users
- Federal users only if explicit policy allows
- Super Admin only for technical/security emergency, with audit trail

## 19.3 Revocation Reasons

Examples:

- Fraudulent information
- Invalid assessment
- Doctor/facility misconduct
- Certificate issued in error
- Serious public health risk
- Duplicate certificate
- Regulatory decision

## 19.4 Revocation Requirements

User must provide:

- Reason
- Detailed note
- Evidence/reference, optional
- Confirmation
- Approval chain, where required

## 19.5 Revocation Effect

- Public verification shows `Revoked`.
- Certificate cannot be reactivated.
- Food handler/employer/facility are notified.
- New certificate requires new assessment or replacement workflow.
- Audit log is permanent.

---

# 20. Certificate Replacement and Correction

## 20.1 Purpose

Replacement handles certificate corrections or reissuance without editing the original certificate.

## 20.2 Replacement Reasons

- Name typo
- Passport photo issue
- Employer/branch correction
- Facility metadata correction
- PDF generation error
- Template correction
- Administrative correction

## 20.3 Replacement Rules

- Original certificate must not be edited.
- Original certificate status becomes `Replaced`.
- Replacement certificate gets new certificate number.
- Replacement links to original certificate.
- Public verification of old certificate should show `Replaced` and optionally point to new certificate status, without exposing sensitive data.
- Replacement must be audit logged.

---

# 21. Certificate Renewal

## 21.1 Purpose

Renewal allows food handlers to obtain a new certificate when their current certificate is expiring or expired.

## 21.2 Renewal Trigger

Renewal may be initiated by:

- Food handler
- Employer reminder
- Automatic system reminder
- Facility follow-up
- State campaign

## 21.3 Renewal Rules

- Default renewal requires a new assessment.
- Renewal certificate gets a new certificate number.
- Previous certificate remains active until expiry unless replaced/revoked.
- Employer sees renewal status.
- Renewal reminders should start 30 days before expiry by default.

## 21.4 Renewal Statuses

- Renewal Not Started
- Renewal Started
- Assessment Pending
- Awaiting State Validation
- New Certificate Issued
- Renewal Overdue

---

# 22. Certificate Registry

## 22.1 State Certificate Registry

State users can:

- Search certificates issued by their state.
- View certificate details.
- Filter by status.
- Suspend certificates.
- Revoke certificates.
- Replace certificates.
- Export state certificate reports.
- View certificate audit trail.

## 22.2 Federal Certificate Registry

Federal users can:

- View national registry.
- Filter by state.
- Monitor issuance trends.
- Monitor revoked/suspended certificates.
- Flag suspicious patterns.
- Export national registry summaries.
- View aggregate certificate metrics.

## 22.3 Registry Search Filters

- Certificate number
- Verification token/public ID
- Food handler name
- State
- LGA
- Employer
- Branch
- Facility
- Doctor
- Status
- Issue date
- Expiry date
- Assessment ID

## 22.4 Registry Privacy

Registry must use role-based serializers:

- Public serializer
- Employer-safe serializer
- Inspector-safe serializer
- State regulatory serializer
- Federal aggregate serializer
- Medical/internal serializer

---

# 23. Digital Signature and Certificate Hash

## 23.1 Purpose

Digital signature/hash helps detect tampering and verify authenticity.

## 23.2 Certificate Hash Inputs

Generate hash from immutable certificate fields such as:

- Certificate number
- Food handler ID
- Assessment ID
- Facility ID
- Issuing state ID
- Doctor ID
- Issue date
- Expiry date
- Status at issuance
- Verification token
- Secret signing key or private key, depending on implementation

## 23.3 Hash Rules

- Store hash on certificate record.
- Recalculate hash during verification.
- If hash mismatch, show invalid/tampered warning.
- Hash should not expose sensitive data.
- Secret keys must not be committed to code.

## 23.4 Digital Signature Options

MVP can use:

- HMAC-based signature/hash

Future can support:

- Public/private key digital signing
- Hardware security module
- Government PKI integration

---

# 24. Certificate Notifications

## 24.1 Food Handler Notifications

Notify when:

- Certificate issued
- Certificate expiring in 30 days
- Certificate expiring in 7 days
- Certificate expired
- Certificate suspended
- Certificate revoked
- Replacement certificate issued
- Renewal started

## 24.2 Employer Notifications

Notify when:

- Linked food handler certificate issued
- Certificate expiring soon
- Certificate expired
- Certificate suspended/revoked
- Renewal completed

## 24.3 Facility Notifications

Notify when:

- Assessment certificate issued
- Certificate issuance rejected
- Clarification requested
- Certificate replaced due to facility metadata issue

## 24.4 State Ministry Notifications

Notify when:

- Certificate validation pending
- Certificate generation failed
- Suspicious verification activity detected
- Revocation/suspension requires approval

## 24.5 Federal Ministry Notifications

Notify when:

- State issuance volume exceeds threshold
- High revocation rate detected
- Suspicious certificate patterns detected
- State registry data quality issue found

---

# 25. Data Model Requirements

## 25.1 Certificate

```python
class Certificate(models.Model):
    id = models.UUIDField(primary_key=True)
    certificate_number = models.CharField(max_length=100, unique=True)
    public_id = models.UUIDField(unique=True)
    verification_token = models.CharField(max_length=255, unique=True)

    food_handler = models.ForeignKey("food_handlers.FoodHandlerProfile", on_delete=models.PROTECT)
    assessment = models.OneToOneField("assessments.MedicalAssessment", on_delete=models.PROTECT)
    employer = models.ForeignKey("employers.Employer", null=True, blank=True, on_delete=models.SET_NULL)
    business_branch = models.ForeignKey("organizations.OrganizationUnit", null=True, blank=True, on_delete=models.SET_NULL)
    facility = models.ForeignKey("facilities.MedicalFacility", on_delete=models.PROTECT)
    doctor = models.ForeignKey("accounts.User", related_name="certificates_as_doctor", on_delete=models.PROTECT)
    issuing_state = models.ForeignKey("geography.State", on_delete=models.PROTECT)
    issued_by = models.ForeignKey("accounts.User", related_name="certificates_issued", null=True, on_delete=models.SET_NULL)

    issue_date = models.DateField()
    expiry_date = models.DateField()
    status = models.CharField(max_length=50)

    qr_code_url = models.URLField(blank=True)
    verification_url = models.URLField(blank=True)
    pdf_url = models.URLField(blank=True)
    digital_signature_hash = models.CharField(max_length=255)

    replaced_by = models.ForeignKey("self", null=True, blank=True, related_name="replaces", on_delete=models.SET_NULL)
    replacement_reason = models.TextField(blank=True)

    suspended_by = models.ForeignKey("accounts.User", null=True, blank=True, related_name="certificates_suspended", on_delete=models.SET_NULL)
    suspended_at = models.DateTimeField(null=True, blank=True)
    suspension_reason = models.TextField(blank=True)

    revoked_by = models.ForeignKey("accounts.User", null=True, blank=True, related_name="certificates_revoked", on_delete=models.SET_NULL)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revocation_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 25.2 CertificateVerificationLog

```python
class CertificateVerificationLog(models.Model):
    id = models.UUIDField(primary_key=True)
    certificate = models.ForeignKey("certificates.Certificate", null=True, blank=True, on_delete=models.SET_NULL)
    certificate_number_attempted = models.CharField(max_length=100, blank=True)
    verification_token_attempted = models.CharField(max_length=255, blank=True)
    verification_result = models.CharField(max_length=50)
    verifier_type = models.CharField(max_length=50)  # public, inspector, employer, state, federal
    verifier_user = models.ForeignKey("accounts.User", null=True, blank=True, on_delete=models.SET_NULL)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    location_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    location_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 25.3 CertificateAction

```python
class CertificateAction(models.Model):
    id = models.UUIDField(primary_key=True)
    certificate = models.ForeignKey("certificates.Certificate", on_delete=models.CASCADE)
    action_type = models.CharField(max_length=50)
    actor = models.ForeignKey("accounts.User", null=True, on_delete=models.SET_NULL)
    reason = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 25.4 CertificateTemplate

```python
class CertificateTemplate(models.Model):
    id = models.UUIDField(primary_key=True)
    scope = models.CharField(max_length=20)  # national or state
    state = models.ForeignKey("geography.State", null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255)
    template_file_url = models.URLField(blank=True)
    logo_url = models.URLField(blank=True)
    signatory_name = models.CharField(max_length=255, blank=True)
    signatory_title = models.CharField(max_length=255, blank=True)
    signature_image_url = models.URLField(blank=True)
    is_default = models.BooleanField(default=False)
    status = models.CharField(max_length=50)
    created_by = models.ForeignKey("accounts.User", null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

---

# 26. API Requirements

## 26.1 Certificate Generation and Issuance

```txt
POST   /api/certificates/generate
POST   /api/state/certificate-validation/:assessment_id/approve-and-generate
GET    /api/certificates/:id
GET    /api/certificates/:id/pdf
```

## 26.2 Public Verification

```txt
GET    /api/public/certificates/verify/:verification_token
POST   /api/public/certificates/verify-by-number
POST   /api/public/certificates/report-suspicious
```

## 26.3 Inspector Verification

```txt
GET    /api/inspector/certificates/verify/:verification_token
POST   /api/inspector/certificates/verify-by-number
POST   /api/inspector/certificates/:id/save-to-inspection
POST   /api/inspector/certificates/:id/flag
```

## 26.4 Employer Certificate APIs

```txt
GET    /api/employers/:id/certificates
GET    /api/employers/:id/certificates/:certificate_id
GET    /api/employers/:id/certificates/:certificate_id/download
POST   /api/employers/:id/certificates/:certificate_id/send-renewal-reminder
```

## 26.5 State Certificate Registry

```txt
GET    /api/state/certificates
GET    /api/state/certificates/:id
PATCH  /api/state/certificates/:id/suspend
PATCH  /api/state/certificates/:id/reinstate
PATCH  /api/state/certificates/:id/revoke
POST   /api/state/certificates/:id/replace
GET    /api/state/certificates/:id/audit
GET    /api/state/certificates/export
```

## 26.6 Federal Certificate Registry

```txt
GET    /api/federal/certificates
GET    /api/federal/certificates/:id
POST   /api/federal/certificates/:id/flag
GET    /api/federal/certificates/analytics
GET    /api/federal/certificates/export-summary
```

## 26.7 Certificate Templates

```txt
GET    /api/certificate-templates
POST   /api/certificate-templates
GET    /api/certificate-templates/:id
PATCH  /api/certificate-templates/:id
DELETE /api/certificate-templates/:id
POST   /api/certificate-templates/:id/set-default
```

---

# 27. Frontend Routes

## 27.1 Public Routes

```txt
/verify
/verify/[verificationToken]
/verify/certificate-number
/report-suspicious-certificate
```

## 27.2 Food Handler Routes

```txt
/app/food-handler/certificates
/app/food-handler/certificates/[id]
/app/food-handler/certificates/[id]/download
/app/food-handler/certificates/[id]/renew
```

## 27.3 Employer Routes

```txt
/app/employer/certificates
/app/employer/certificates/[id]
```

## 27.4 Inspector Routes

```txt
/app/inspector/scan
/app/inspector/certificates/verify
/app/inspector/certificates/[id]
```

## 27.5 State Routes

```txt
/app/state/certificate-validation
/app/state/certificate-validation/[assessment_id]
/app/state/certificates
/app/state/certificates/[id]
/app/state/certificates/[id]/audit
/app/state/certificate-templates
```

## 27.6 Federal Routes

```txt
/app/federal/certificates
/app/federal/certificates/[id]
/app/federal/certificates/analytics
/app/federal/certificate-registry
```

## 27.7 Admin Routes

```txt
/app/admin/certificate-templates
/app/admin/certificate-policy
```

---

# 28. Core Frontend Components

- CertificateStatusBadge
- CertificatePreview
- CertificatePDFViewer
- QRCodeDisplay
- QRScanner
- PublicVerificationResult
- CertificateNumberVerificationForm
- CertificateRegistryTable
- CertificateValidationChecklist
- CertificateIssuancePanel
- CertificateAuditTimeline
- CertificateSuspensionModal
- CertificateRevocationModal
- CertificateReplacementModal
- CertificateRenewalCard
- CertificateTemplateEditor
- CertificateAnalyticsCards
- SuspiciousCertificateReportForm
- InspectorVerificationPanel
- EmployerCertificateTable

---

# 29. Permissions and Access Control

## 29.1 Public

Can access only public verification endpoint and public-safe serializer.

## 29.2 Food Handler

Can access own certificates only.

## 29.3 Employer

Can access certificates for linked food handlers only and only employer-safe fields.

## 29.4 Inspector

Can verify certificate and save result to inspection record.

## 29.5 State Ministry

Can manage certificates issued by their state.

## 29.6 Federal Ministry

Can view national registry and analytics; individual data access depends on permission.

## 29.7 Super Admin

Can manage system templates, technical settings, and emergency administrative functions.

---

# 30. Privacy Requirements

## 30.1 Public Privacy

Public verification must never expose:

- Full NIN
- Lab results
- Doctor notes
- Diagnosis
- Declaration answers
- Treatment details
- Payment records
- Employer private compliance information

## 30.2 Employer Privacy

Employer certificate view must never expose:

- Lab results
- Doctor notes
- Diagnosis
- Declaration answers
- Full NIN

## 30.3 Federal Privacy

Federal dashboards should be aggregate by default.

Individual record access must be permission-controlled and audit logged.

---

# 31. Audit Logs

Create audit logs for:

- State certificate approval
- Certificate generation
- PDF generation
- QR generation
- Public verification attempt
- Inspector verification attempt
- Employer certificate download
- Food handler certificate download
- Certificate suspension
- Certificate reinstatement
- Certificate revocation
- Certificate replacement
- Certificate renewal started
- Certificate template update
- Certificate policy update
- Suspicious certificate report
- Failed certificate generation
- Hash mismatch/tamper warning

---

# 32. Background Jobs

Required scheduled/background jobs:

## 32.1 Certificate Expiry Job

Runs daily.

Tasks:

- Find certificates past expiry date.
- Mark active certificates as expired.
- Send expiry notifications.
- Update registry status.

## 32.2 Expiring Soon Notification Job

Runs daily.

Tasks:

- Find certificates expiring in 30 days.
- Find certificates expiring in 7 days.
- Notify food handler.
- Notify employer where linked.

## 32.3 Certificate Generation Retry Job

Handles failed PDF/QR generation where safe.

## 32.4 Suspicious Verification Monitoring

Detects:

- Repeated invalid verification attempts.
- High verification attempts for one certificate.
- Verification from unusual locations.
- Certificates repeatedly flagged by inspectors.

---

# 33. Error Handling

## 33.1 Certificate Generation Errors

Possible errors:

- Missing template
- Missing passport photo
- Missing State approval
- Invalid certificate policy
- PDF generation failed
- QR generation failed
- Duplicate certificate number
- Hash/signature generation failed

Error handling:

- Mark status `Draft Generation Failed`.
- Show internal error to authorized user.
- Do not expose technical error publicly.
- Allow retry by authorized user.
- Audit log failure.

## 33.2 Verification Errors

Public messages should be simple:

- Certificate not found.
- Certificate expired.
- Certificate revoked.
- Certificate suspended.
- Verification temporarily unavailable.

Do not expose internal exception details.

---

# 34. Acceptance Criteria

## 34.1 Certificate Issuance

- Certificate is generated only after State Ministry approval.
- Certificate is linked to one completed assessment.
- Certificate shows State Ministry as issuing authority.
- Certificate has unique certificate number.
- Certificate has issue date and expiry date.
- Certificate validity defaults to 6 months unless policy overrides.
- Certificate includes QR code.
- Certificate is stored in central registry.
- Certificate generation is audit logged.

## 34.2 QR Verification

- QR code opens public verification page.
- Public verification works without login.
- Public verification shows valid/expired/revoked/suspended/not found status.
- Public verification does not expose medical data.
- Verification attempts are logged.

## 34.3 Certificate PDF

- Food handler can download certificate PDF.
- Employer can download linked food handler certificate where permitted.
- PDF includes certificate number, QR code, issue/expiry date, state, facility, doctor, and food handler identity.
- PDF excludes lab results, diagnosis, doctor notes, declaration answers, and full NIN.

## 34.4 Certificate Registry

- State users can view certificates issued by their state.
- Federal users can view national registry overview.
- Registry can filter by state, status, facility, employer, and date.
- Registry exports respect privacy rules.

## 34.5 Suspension and Revocation

- Authorized state user can suspend certificate.
- Suspended certificate shows suspended in public verification.
- Authorized state user can revoke certificate.
- Revoked certificate shows revoked in public verification.
- Revocation cannot be reversed.
- Suspension/revocation requires reason and audit log.

## 34.6 Replacement

- Certificate can be replaced without editing original.
- Original certificate is marked replaced.
- New certificate gets new certificate number.
- Replacement links to original certificate.
- Replacement is audit logged.

## 34.7 Renewal

- Expiring certificates trigger reminders.
- Renewal requires new assessment by default.
- New certificate gets new certificate number.
- Employer sees renewal status.

## 34.8 Privacy

- Public users cannot view medical records.
- Employers cannot view medical records.
- Full NIN is not exposed publicly.
- Sensitive actions and access are audit logged.

---

# 35. Codex Implementation Instructions

Use this prompt for Codex:

```txt
Implement the Certificate & QR Verification Module for FoodCert NG.

The module must support State Ministry certificate issuance, certificate eligibility validation, unique certificate number generation, PDF certificate generation, QR code generation, public certificate verification, inspector verification, employer-safe certificate views, food handler certificate downloads, certificate registry, certificate expiry, renewal triggers, suspension, revocation, replacement, certificate templates, digital signature/hash validation, audit logging, and background jobs.

Important rules:
- Certificates are issued by the State Ministry of Health.
- Federal Ministry has national oversight but does not replace State issuing authority.
- Certificate generation requires State approval and a complete Fit assessment.
- Certificate validity defaults to 6 months but must use policy configuration.
- Public QR verification must not expose medical data.
- Employers must not see medical details.
- QR code must not contain sensitive data directly.
- Certificate records are immutable after issuance except status transitions and replacement workflow.
- Revoked certificates cannot be reinstated.
- Suspended certificates can be reinstated by authorized users.
- Replacement creates a new certificate and marks the old one replaced.
- All certificate actions and verification attempts must be audit logged.

Build backend models, services, serializers, permissions, API endpoints, background jobs, tests, and frontend pages for the module.
```

---

# 36. MVP Build Order

1. Certificate model
2. Certificate number generation service
3. Certificate eligibility validation service
4. State approve-and-generate certificate endpoint
5. Certificate hash/signature service
6. QR code generation
7. PDF certificate generation
8. Public verification endpoint
9. Public verification page
10. Food handler certificate page
11. Employer certificate table
12. State certificate registry
13. Inspector QR verification
14. Expiry background job
15. Expiring soon notification job
16. Suspension workflow
17. Revocation workflow
18. Replacement workflow
19. Federal certificate registry overview
20. Certificate template management
21. Privacy-safe serializers
22. Certificate audit logs
23. Permission tests
24. Public verification privacy tests
25. Certificate generation tests
