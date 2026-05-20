# Chunk 01 — Foundation and Architecture

## Goal

Set up the full-stack project foundation for FoodCert NG.

## Build Objective

Create a maintainable, modular, production-ready web application with:
- Django REST backend
- PostgreSQL database
- Celery + Redis for async jobs
- Next.js frontend
- Docker-based local development
- Environment-based configuration
- Role-based access design from the beginning

## Project Structure

```txt
foodcert-ng/
  backend/
    manage.py
    requirements.txt
    Dockerfile
    config/
      __init__.py
      settings.py
      urls.py
      celery.py
    apps/
      accounts/
      organizations/
      locations/
      food_handlers/
      employers/
      facilities/
      payments/
      subscriptions/
      settlements/
      assessments/
      lab_tests/
      vaccinations/
      certificates/
      illness/
      inspections/
      reports/
      notifications/
      audit/
    media/
    static/
  frontend/
    package.json
    next.config.js
    tsconfig.json
    src/
      app/
      components/
      features/
      lib/
      hooks/
      types/
  docker-compose.yml
  README.md
```

## Backend Requirements

Use Django + Django REST Framework.

Install and configure:
- Django
- djangorestframework
- django-cors-headers
- psycopg2-binary
- celery
- redis
- python-decouple or django-environ
- Pillow
- qrcode
- WeasyPrint or ReportLab for PDFs
- django-filter
- drf-spectacular for API documentation

## Frontend Requirements

Use:
- Next.js
- TypeScript
- Tailwind CSS
- React Hook Form
- Zod
- TanStack Query
- Axios or Fetch wrapper
- Recharts or ApexCharts
- QR scanner package
- Component structure suitable for role-based dashboards

## Environment Variables

Backend `.env` should support:

```env
DEBUG=True
SECRET_KEY=
DATABASE_URL=
REDIS_URL=
ALLOWED_HOSTS=
CORS_ALLOWED_ORIGINS=

DEFAULT_CERTIFICATE_VALIDITY_MONTHS=6
DEFAULT_TYPHOID_VALIDITY_YEARS=3
DEFAULT_HEPATITIS_A_SECOND_DOSE_MONTHS=6

PAYMENT_PROVIDER=mock
PAYSTACK_SECRET_KEY=
FLUTTERWAVE_SECRET_KEY=
REMITA_SECRET_KEY=

NIN_PROVIDER=mock
NIN_API_BASE_URL=
NIN_API_KEY=

STORAGE_BACKEND=local
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=

EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=

SMS_PROVIDER=mock
SMS_API_KEY=
```

## Foundational Apps

### accounts
Authentication, users, roles, permissions.

### organizations
Organization-level ownership and multi-tenant structure.

### locations
States, LGAs, wards.

### audit
Critical action logging.

### notifications
Email/SMS/in-app notification.

## Technical Standards

- Use UUID primary keys.
- Use created_at and updated_at on all major models.
- Use soft status fields instead of hard delete for regulatory objects.
- Use permissions at API level and object level.
- Ensure every financial, medical, certificate, and regulatory action is auditable.
- Use service classes for business logic.
- Use serializers for validation.
- Use background jobs for notifications, report generation, and settlements.

## Initial Deliverables

1. Docker Compose with backend, frontend, postgres, redis.
2. Django project with all apps scaffolded.
3. Next.js app scaffolded.
4. Health-check endpoint.
5. API schema endpoint.
6. Seed script for Nigerian states and FCT.
7. Base model mixins:
   - UUIDModel
   - TimestampedModel
   - StatusModel
8. Basic audit log model and utility.
