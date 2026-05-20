# Landing Page Redesign Plan — FoodCert NG

## Current State

The current `frontend/src/app/page.tsx` is a developer-facing MVP checklist. It shows build progress, backend/API URLs, and implementation status. This is useful internally, but it is not appropriate as the public home page for FoodCert NG.

## Target State

Replace the developer dashboard with a public-facing landing page that presents FoodCert NG as trustworthy national food handler certification infrastructure.

The page should explain what the platform does, guide food handlers toward registration, provide clear sign-in entry points for invited stakeholders, and make public certificate verification immediately accessible.

The tone should be institutional, precise, and public-health oriented, not generic SaaS marketing.

---

## Messaging Principles

- Use `FoodCert NG` as the hero headline.
- Describe the platform as a unified certification and compliance platform.
- Avoid overclaiming official deployment or endorsement unless confirmed.
- Avoid saying facilities issue certificates. Facilities conduct assessments; State Ministries validate and issue certificates.
- Avoid saying NIN verification is definitely via NIMC in production. Use "configured identity provider integration."
- Public verification copy must make clear that sensitive medical and identity data is not exposed.

Recommended positioning:

```txt
FoodCert NG

A unified platform for food handler medical fitness certification,
facility accreditation, inspections, and public certificate verification.
```

Supporting copy:

```txt
Built around State Ministry certificate validation workflows and aligned
with the National Guidelines for Food Handlers' Medical Test 2024.
```

---

## Page Structure

```txt
1. Header
2. Hero with certificate verification input
3. Trust strip
4. How it works
5. Role entry points
6. Platform capabilities
7. Public verification section
8. Footer
```

---

## 1. Header

### Content

- Logo / brand: `FoodCert NG`
- Navigation actions:
  - `Verify Certificate`
  - `Get Certified`
  - `Sign In`

### Links

| Label | Target |
|---|---|
| Verify Certificate | scroll to verification section or focus hero verification input |
| Get Certified | `/register` |
| Sign In | `/login` |

### Style

- White background
- Bottom border using emerald/slate border color
- Compact institutional layout
- Sticky header is optional but recommended

---

## 2. Hero

### Goal

Immediately communicate that FoodCert NG is the national-style platform for food handler certification and public verification.

### Content

Hero headline:

```txt
FoodCert NG
```

Hero supporting text:

```txt
A unified platform for food handler medical fitness certification,
facility accreditation, inspections, and public certificate verification.
```

Secondary support:

```txt
Designed for food handlers, employers, medical facilities, inspectors,
and State and Federal health authorities.
```

### CTAs

| CTA | Target |
|---|---|
| Get Certified | `/register` |
| Sign In | `/login` |

### Certificate Verification Input

Include a prominent certificate verification form in the hero.

Behavior:

- Input placeholder: `Enter certificate number`
- Button label: `Verify Certificate`
- If empty, do not navigate; show small inline validation text.
- If filled, redirect to `/verify/[certificateNumber]`.
- Certificate number should be trimmed and URL encoded.

### Hero Visual

Use a real or generated bitmap-style visual, not an abstract SVG-only shield graphic.

Recommended visual direction:

- Food safety inspection
- QR certificate verification
- Clinic assessment workflow
- Nigerian public health certification context

Avoid:

- Gradient orb backgrounds
- Abstract decorative blobs
- Generic SaaS illustrations
- Dark, blurred, or stock-like visuals that do not show the subject clearly

---

## 3. Trust Strip

Show four compact trust signals.

Recommended items:

| Label | Detail |
|---|---|
| 36 States + FCT | National rollout ready |
| QR Verification | Public certificate checks |
| State Validation | Certificate review workflow |
| 2024 Guidelines | Aligned with national guidance |

Use restrained stat cards or inline tiles.

Do not claim official government endorsement unless confirmed.

---

## 4. How It Works

Use a 5-step process.

```txt
1. Register
   Food handler creates a profile.

2. Verify Identity
   Identity is checked through configured provider integration.

3. Complete Medical Assessment
   Approved facility handles declaration, examination, lab tests, and vaccination review.

4. State Review
   State Ministry workflow validates eligible certificate requests.

5. Receive Certificate
   Food handler receives a QR-coded certificate for public verification.
```

Mobile:

- Stack vertically.

Desktop:

- Horizontal or responsive grid.

---

## 5. Role Entry Points

Represent all major user groups.

| Role | Description | CTA |
|---|---|---|
| Food Handlers | Register, verify identity, complete assessment, and access certificate status. | Get Certified -> `/register` |
| Employers | Manage branches, food handlers, subscriptions, compliance, illness reports, and inspections. | Sign In -> `/login` |
| Medical Facilities | Submit accreditation, conduct approved assessments, manage appointments and records. | Sign In -> `/login` |
| Doctors | Review declarations, perform exams, request lab tests, and make fitness decisions. | Sign In -> `/login` |
| Lab Staff | Manage lab requests, enter results, and support assessment workflows. | Sign In -> `/login` |
| Inspectors | Conduct workplace inspections and verify certificates in the field. | Sign In -> `/login` |
| State MOH | Manage facilities, fees, certificate validation, inspections, and state reports. | Sign In -> `/login` |
| Federal MOH | View national dashboards, trends, reports, and oversight data. | Sign In -> `/login` |

Important:

- Food handlers self-register.
- Other roles are expected to enter through invitation and sign in.

---

## 6. Platform Capabilities

Show six key capabilities.

| Capability | Description |
|---|---|
| Identity Verification | Food handler identity checks through configured provider integration. |
| Medical Assessment Workflow | Declarations, physical examinations, lab tests, vaccinations, and doctor decisions. |
| Facility Accreditation | State-reviewed facility approval and reaccreditation workflows. |
| Employer Compliance | Branches, food handler status, subscriptions, illness reporting, and compliance views. |
| Inspections | Inspector workflows for workplace checks, evidence, and enforcement actions. |
| Dashboards and Reports | Employer, facility, state, and federal analytics with exportable reports. |

Keep copy short and operational.

---

## 7. Public Verification Section

### Purpose

Give the public a second clear place to verify a certificate.

### Content

Heading:

```txt
Verify a FoodCert NG Certificate
```

Supporting copy:

```txt
Enter a certificate number or scan a QR code to confirm certificate validity.
Public verification shows only limited certificate information.
```

Privacy note:

```txt
No full NIN, lab results, diagnosis, doctor notes, or declaration answers are shown.
```

### Form Behavior

Same as hero verification input:

- Trim input.
- Empty input does not navigate.
- Valid input redirects to `/verify/[certificateNumber]`.

---

## 8. Footer

### Content

```txt
FoodCert NG
Food handler medical fitness certification and public verification platform.
Aligned with the National Guidelines for Food Handlers' Medical Test 2024.
```

### Links

| Label | Target |
|---|---|
| Register | `/register` |
| Sign In | `/login` |
| Verify Certificate | verification section or `/verify` flow |
| API Docs | `/api/docs/` if exposed in environment |

---

## Technical Details

### File Affected

| File | Action |
|---|---|
| `frontend/src/app/page.tsx` | Replace developer dashboard with public landing page |

No new dependencies are required.

### Recommended Implementation Style

- Keep all data arrays inside `page.tsx`.
- Use arrays for:
  - trust stats
  - process steps
  - role cards
  - capability cards
- Use existing Tailwind classes and brand tokens.
- Use `lucide-react` icons already available in the project.
- Keep cards at `rounded-lg` or smaller.
- Avoid nested cards.
- Avoid gradient orb or blob backgrounds.
- Use responsive constraints so text does not overflow on mobile.

### Suggested Icons

From `lucide-react`:

```txt
ShieldCheck
QrCode
IdCard
Building2
Stethoscope
FlaskConical
ClipboardCheck
Landmark
UsersRound
MapPin
BadgeCheck
ArrowRight
SearchCheck
```

Use icons sparingly and consistently.

---

## Style Guidance

Use the existing FoodCert NG frontend style:

- Background: `bg-[#f7faf8]`
- Primary CTA: `bg-brand-green text-white`
- Strong brand text: `text-brand-deep`
- Headings: `text-slate-950`
- Body copy: `text-slate-600`
- Cards: `rounded-lg border border-slate-200 bg-white shadow-sm`
- Section labels: `text-xs font-bold uppercase tracking-wide text-brand-deep`

The page should feel calm, official, and operational.

---

## Acceptance Criteria

- Hero clearly identifies `FoodCert NG`.
- Page explains certification, accreditation, inspection, and public verification workflows.
- Food handlers have a clear `Get Certified` path to `/register`.
- Invited users have a clear `Sign In` path to `/login`.
- Public certificate verification input works without login.
- Empty verification input does not navigate.
- Valid verification input redirects to `/verify/[certificateNumber]`.
- All major user groups are represented.
- Facilities are described as conducting assessments, not issuing certificates.
- Identity verification wording does not overclaim a specific production provider.
- Page references guideline alignment without implying unconfirmed official endorsement.
- No developer checklist, MVP status, backend health URL, or API build-progress content remains.
- No public copy exposes or implies access to full NIN, lab results, diagnoses, doctor notes, or declaration answers.
- Page is responsive across mobile, tablet, and desktop.
- Text does not overflow buttons, cards, or hero areas.
- Landing page uses existing design tokens and does not introduce new dependencies.

---

## Verification Checklist

After implementation, run:

```bash
npm run lint
npm run typecheck
npm run build
```

Manual checks:

- `/` loads correctly.
- `/register` CTA works.
- `/login` CTA works.
- Verification form redirects correctly.
- Empty verification input shows inline validation.
- Mobile layout is readable.
- No old developer dashboard content remains.

---

## Assumptions

- Food handlers can self-register.
- Employers, facilities, doctors, lab staff, inspectors, State MOH, and Federal MOH users are invited and then sign in.
- Production NIMC integration is not claimed unless confirmed.
- Official MOH endorsement is not claimed unless confirmed.
- Public verification remains privacy-limited.
