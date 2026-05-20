# Chunk 13 — Codex Master Prompt

Copy and paste this into Codex to begin implementation.

```txt
Build a full-stack national web application called FoodCert NG.

The application should automate food handler medical fitness certification based on the National Guidelines for Food Handlers’ Medical Test 2024.

This is a national rollout platform covering all 36 Nigerian States and the FCT.

Final product decisions:
1. Certificates are issued by the State Ministry of Health.
2. Food handlers pay assessment fees through the platform.
3. Employers pay subscription fees.
4. Medical facilities receive settlement payments through the platform.
5. NIN must be verified automatically before certificate issuance.
6. Certificate validity defaults to 6 months, but should be configurable by authorized administrators.
7. Employers should only see operational fitness status categories, not detailed medical records.
8. Certificate verification should be public through QR code.

Use:
- Backend: Django + Django REST Framework
- Database: PostgreSQL
- Background jobs: Celery + Redis
- Frontend: Next.js + TypeScript + Tailwind CSS
- File storage abstraction for passport photos, lab results, certificates, and accreditation documents.
- Payment integration abstraction supporting a mock provider first, then Paystack, Flutterwave, Remita, or other providers.
- NIN verification integration abstraction supporting a mock provider first, then a real authorized NIN provider.

Implement the MVP in phases.

Phase 1 — Foundation:
- Scaffold backend and frontend.
- Configure Docker Compose with backend, frontend, Postgres, Redis.
- Implement base models with UUID and timestamps.
- Implement authentication, users, roles, permissions, organizations, states, LGAs, audit logs.

Phase 2 — Identity:
- Implement food handler profiles.
- Implement employer profiles.
- Implement NIN verification workflow.
- Block certificate issuance unless NIN is verified or override is approved.

Phase 3 — Facilities:
- Implement medical facility profiles.
- Implement facility accreditation workflow.
- Allow State Ministry users to approve, reject, suspend, and renew facilities.
- Only approved facilities can accept appointments and conduct assessments.

Phase 4 — Payments:
- Implement assessment fee configuration per state.
- Implement food handler assessment payment.
- Implement employer subscription plans and subscriptions.
- Implement facility settlement ledger.
- Ensure all payment verification is server-side and auditable.

Phase 5 — Medical Assessment:
- Implement appointment booking.
- Implement health declaration form.
- Implement doctor physical examination.
- Implement lab test request/result workflow.
- Implement vaccination records.
- Implement fitness decision workflow.

Phase 6 — Certificates:
- Implement State Ministry certificate validation queue.
- Generate certificate only after successful eligibility checks.
- Generate QR code and PDF certificate.
- Implement public certificate verification page.
- Implement certificate revocation and suspension.

Phase 7 — Compliance:
- Implement employer compliance dashboard.
- Implement illness reporting and return-to-work workflow.
- Implement inspector certificate scanning and inspection checklist.
- Implement State and Federal dashboards.
- Implement reports and exports.

Important privacy rules:
- Employers must not see lab results, doctor notes, diagnoses, or declaration answers.
- Public QR verification must not show full NIN, lab results, doctor notes, diagnoses, or declaration answers.
- All medical, payment, certificate, and regulatory actions must be auditable.

Start by creating the project structure and backend models. Then implement APIs and permissions. After that, build frontend pages.
```

## Chunk-by-Chunk Prompting Strategy

Use one markdown file at a time. Start with `01_FOUNDATION_AND_ARCHITECTURE.md`. Do not ask Codex to build everything at once.

Recommended prompt format:

```txt
Use the attached PRD chunk as the source of truth.
Implement only this chunk.
Do not implement future chunks yet.
Create clean, documented, production-ready code.
After implementation, summarize what files you created or changed and what remains.
```
