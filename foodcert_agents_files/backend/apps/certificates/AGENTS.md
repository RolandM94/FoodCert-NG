# certificates/AGENTS.md — Certificate Issuance and QR Verification Instructions

## Scope

This app manages:
- State Ministry certificate validation
- Certificate generation
- Certificate PDF generation
- QR code generation
- Public verification
- Certificate expiry
- Revocation
- Suspension
- Replacement

## Key Product Rules

- Certificates are issued by the State Ministry of Health.
- Certificate validity defaults to 6 months.
- Certificate validity must be configurable through policy settings.
- Certificates must be publicly verifiable through QR code.
- Certificate records are immutable after issuance.
- Only revocation, suspension, expiry, and replacement status transitions are allowed after issuance.
- Certificates must be stored in a central registry.

## Certificate Issuance Requirements

Before issuing a certificate, validate:
- Food handler profile is complete.
- NIN verification is successful or override approved.
- Assessment payment is confirmed.
- Assessment was conducted by an approved facility.
- Doctor is authorized.
- Required medical workflow is complete.
- Doctor decision is `fit`.
- State Ministry validation is complete.
- Certificate fee/payment requirements are satisfied, if any.
- There is no active conflicting certificate unless replacement is intended.

## Certificate Fields

Certificate should include:
- Certificate number
- Food handler name
- Date of birth
- Gender
- Passport photo
- Masked NIN or policy-approved identifier
- Food handler ID
- Employer name, where applicable
- Medical facility
- Doctor name and registration number
- Issuing State Ministry
- State of issuance
- Date of assessment
- Date issued
- Expiry date
- Fitness status
- QR code
- Verification URL
- Digital signature/hash

## Public Verification

Public verification may show:
- Certificate status
- Certificate number
- Food handler name
- Passport photo
- Issuing State Ministry
- Approved medical facility
- Date issued
- Expiry date
- Fitness status

Public verification must not show:
- Full NIN
- Lab results
- Diagnosis
- Doctor notes
- Health declaration answers
- Employer private compliance records

## Certificate Statuses

Use:
- active
- expired
- revoked
- suspended
- replaced
- invalid

## QR Code Rules

- QR code should contain a verification URL or opaque verification token.
- Do not encode sensitive medical data directly inside QR code.
- Verification endpoint must check database status, expiry, revocation, and digital signature/hash.
- Log all verification attempts.

## Do Not Do

- Do not generate certificates for non-fit assessments.
- Do not allow certificates from unapproved facilities.
- Do not expose private medical data.
- Do not allow direct editing of certificate fields after issuance.
