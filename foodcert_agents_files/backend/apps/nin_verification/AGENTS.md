# nin_verification/AGENTS.md — NIN Verification Instructions

## Scope

This app manages automatic NIN verification for food handlers.

## Key Product Rules

- NIN must be verified automatically before certificate issuance.
- Certificate issuance requires NIN status `verified` or `override_approved`.
- The app must support provider abstraction.
- Full NIN must not be exposed publicly.
- NIN verification attempts must be logged and auditable.

## Verification Workflow

1. Food handler submits NIN.
2. Backend sends request to configured NIN provider.
3. Provider returns identity data.
4. Backend compares returned identity with food handler profile.
5. If the match is acceptable, status becomes `verified`.
6. If data conflicts, status becomes `mismatch` or `manual_review_required`.
7. Authorized State/Federal user may approve override.
8. Certificate issuance service checks NIN status before issuance.

## Statuses

Use:
- not_submitted
- pending
- verified
- failed
- mismatch
- manual_review_required
- override_approved

## Data to Compare

Compare:
- Full name
- Date of birth
- Gender
- Photograph, if available

## Privacy Rules

- Store full NIN securely.
- Mask NIN in normal API responses.
- Never return full NIN to public certificate verification.
- Restrict full NIN access to authorized compliance/regulatory users only.
- Log all access to full NIN.

## Provider Abstraction

Create provider interface methods:
- verify_nin(nin)
- normalize_response(response)
- calculate_match_score(profile, verified_data)

Do not place provider-specific logic directly in views.

## Do Not Do

- Do not issue certificates if NIN is unverified unless override is approved.
- Do not expose full NIN publicly.
- Do not allow employers to see full NIN.
- Do not hardcode one NIN provider.
