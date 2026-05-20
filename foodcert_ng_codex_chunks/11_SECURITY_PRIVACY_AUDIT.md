# Chunk 11 — Security, Privacy, and Audit

## Goal

Implement security and privacy controls suitable for sensitive health, identity, payment, and regulatory data.

## Security Requirements

- HTTPS only in production.
- Strong password hashing.
- Role-based access control.
- Object-level permissions.
- Optional MFA for high-privilege users.
- Secure file uploads.
- Virus scanning hook for uploaded files, if available.
- Rate limiting for public verification and login.
- Secure cookies and tokens.
- Audit logs for critical actions.
- Environment-based secrets.
- No secrets in code.

## Sensitive Data

Sensitive data includes:
- NIN
- Passport photo
- Medical declaration
- Doctor notes
- Lab results
- Vaccination documents
- Certificate records
- Payment references
- Facility accreditation documents

## Privacy Rules

Employers should see only:
- Name
- Passport photo
- Certificate status
- Operational fitness category
- Certificate expiry date
- Vaccination compliance status
- Return-to-work status/date where applicable

Employers should not see:
- Lab results
- Doctor notes
- Diagnosis
- Full declaration answers
- Full NIN

Public verification should show:
- Validity status
- Certificate number
- Food handler name
- Passport photo
- Issuing State Ministry
- Approved facility
- Date issued
- Expiry date
- Fitness status

Public verification should not show:
- Full NIN
- Lab results
- Medical notes
- Diagnosis
- Declaration answers

## Audit Log Events

Audit every:
- Login failure for high-privilege accounts
- User role change
- Facility accreditation approval/rejection/suspension
- Assessment payment confirmation
- Lab result creation/update
- Doctor fitness decision
- Certificate request
- Certificate approval
- Certificate generation
- Certificate revocation/suspension
- NIN override approval
- Illness clearance
- Inspection submission
- Settlement processing
- Policy configuration update

## AuditLog Model

```python
class AuditLog(models.Model):
    id = UUIDField(primary_key=True)
    actor_user = ForeignKey(User, null=True, blank=True)
    action = CharField()
    entity_type = CharField()
    entity_id = UUIDField(null=True, blank=True)
    old_value = JSONField(null=True, blank=True)
    new_value = JSONField(null=True, blank=True)
    ip_address = CharField(blank=True)
    user_agent = TextField(blank=True)
    created_at = DateTimeField(auto_now_add=True)
```

## Certificate Security

- Certificate number must be unique and hard to guess.
- QR code must reference server verification, not static local data.
- Certificate PDF should contain digital hash.
- Verification endpoint must check current database status.
- Revoked/suspended certificates must fail verification.

## Payment Security

- Verify all payment callbacks server-side.
- Do not trust frontend payment success alone.
- Store provider reference and internal reference.
- Use idempotency for payment webhook processing.
- Reconcile payments daily.

## NIN Security

- Do not log full NIN in application logs.
- Mask NIN in UI except for authorized identity verification users.
- Encrypt NIN at rest if feasible.
- Track every manual override.

## Acceptance Criteria

- Users cannot access records outside their role/scope.
- Public verification leaks no sensitive medical data.
- Critical actions create audit logs.
- Certificate verification is tamper-resistant.
- Payment webhooks are idempotent and verified.
