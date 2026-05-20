# Chunk 02 — Users, Roles, Permissions, and Organizations

## Goal

Implement authentication, role-based access control, and organization structure.

## User Roles

The system must support:

1. Super Admin
2. Federal Ministry Admin
3. State Ministry Admin
4. Inspector / Environmental Health Officer
5. Medical Facility Admin
6. Doctor
7. Laboratory Staff
8. Employer / Food Business Owner
9. Food Handler
10. Public Verifier

## Organization Types

```txt
platform_operator
federal_ministry
state_ministry
medical_facility
employer
```

## User Model

```python
class User(AbstractUser):
    id = UUIDField(primary_key=True)
    email = EmailField(unique=True)
    phone = CharField()
    role = CharField(choices=RoleChoices)
    organization = ForeignKey(Organization, null=True, blank=True)
    status = CharField(choices=["active", "inactive", "suspended"])
    email_verified = BooleanField(default=False)
    phone_verified = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

## Organization Model

```python
class Organization(models.Model):
    id = UUIDField(primary_key=True)
    name = CharField()
    type = CharField(choices=OrganizationTypeChoices)
    state = ForeignKey(State, null=True, blank=True)
    lga = ForeignKey(LGA, null=True, blank=True)
    address = TextField(blank=True)
    phone = CharField(blank=True)
    email = EmailField(blank=True)
    status = CharField(choices=["active", "inactive", "suspended"])
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

## Permission Rules

### Super Admin
Can manage all records and system configuration.

### Federal Ministry Admin
Can view national dashboards, aggregate analytics, all state reports, certificate registry, and national policy configurations.

### State Ministry Admin
Can manage facilities, certificates, inspections, fees, and reports for their state.

### Inspector
Can verify certificates, conduct inspections, and submit findings.

### Medical Facility Admin
Can manage facility staff, appointments, assessments, and facility reports.

### Doctor
Can validate declarations, conduct exams, request/review lab tests, validate vaccinations, and submit fitness decisions.

### Lab Staff
Can manage lab requests and submit results.

### Employer
Can manage business profile, food handlers, subscriptions, illness reports, and compliance reports.

### Food Handler
Can manage own profile, declaration, appointments, certificates, vaccinations, and illness reports.

### Public Verifier
No login required. Can verify QR certificate via public verification endpoint.

## Authentication Requirements

- Register
- Login
- Logout
- Refresh token
- Password reset
- Invite user to organization
- Activate/deactivate user
- Suspend user
- Optional MFA for high-privilege users

## API Endpoints

```txt
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
POST /api/auth/token/refresh
POST /api/auth/password-reset
GET  /api/users/me
PATCH /api/users/me
GET  /api/users
POST /api/users/invite
PATCH /api/users/:id/status
GET  /api/organizations
POST /api/organizations
GET  /api/organizations/:id
PATCH /api/organizations/:id
```

## Acceptance Criteria

- User can register and login.
- Every user has one role.
- Organization users can only access records belonging to their organization unless they have regulatory permissions.
- State Ministry users can only manage records in their state.
- Federal Ministry users can view national data but cannot casually edit state records unless authorized.
- Public certificate verification does not require login.
