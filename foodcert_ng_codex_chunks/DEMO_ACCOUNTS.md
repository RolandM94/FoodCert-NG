# FoodCert NG — Demo Accounts

All passwords: **`Demo@2024!`**

---

## Regulatory & Admin

| Username | Role | Org | Unit | Portal |
|----------|------|-----|------|--------|
| `super.admin` | Super Admin | — | — | `/federal/dashboard` |
| `federal.admin` | Federal Admin | Federal MOH | — | `/federal/dashboard` |
| `lagos.admin` | State MOH Admin | Lagos MOH | — | `/state/dashboard` |
| `lagos.verifier` | State Admin | Lagos MOH | Verification Desk | `/state/dashboard` |
| `lagos.accreditor` | State Admin | Lagos MOH | Accreditation Unit | `/state/dashboard` |
| `lagos.inspector` | Inspector | — | Ikeja LGA Office | `/inspector/dashboard` |

---

## Medical Facilities

| Username | Role | Org | Unit | Portal |
|----------|------|-----|------|--------|
| `excel.admin` | Facility Admin | Excel Diagnostics (approved) | — | `/facility/dashboard` |
| `excel.doctor` | Doctor | Excel Diagnostics | Clinical Dept | `/doctor/dashboard` |
| `excel.lab` | Lab Staff | Excel Diagnostics | Lab Dept | `/lab/dashboard` |
| `prime.admin` | Facility Admin | Prime Health (pending accreditation) | — | `/facility/dashboard` |

---

## Employer

| Username | Role | Org | Unit | Portal |
|----------|------|-----|------|--------|
| `megachow.hq` | Employer | MegaChow Ltd | Headquarters | `/employer/dashboard` |
| `megachow.ikeja` | Employer | MegaChow Ltd | Branch — Ikeja | `/employer/dashboard` |
| `megachow.surulere` | Employer | MegaChow Ltd | Branch — Surulere | `/employer/dashboard` |

---

## Food Handlers

| Username | Role | Branch | Status | Portal |
|----------|------|--------|--------|--------|
| `ada.okafor` | Food Handler | Ikeja | **Fit to Handle Food** — full journey, certificate with QR code | `/food-handler/dashboard` |
| `bola.surulere` | Food Handler | Surulere | **Fit to Handle Food** — demonstrates branch isolation | `/food-handler/dashboard` |
| `emeka.nnamdi` | Food Handler | Ikeja | **NIN Pending** — certificate blocked | `/food-handler/dashboard` |
| `chioma.eze` | Food Handler | Ikeja | **Temporarily Excluded** — illness reported, return-to-work pending | `/food-handler/dashboard` |

---

## Branch Scoping Demo

| Log in as | Can see food handlers |
|-----------|----------------------|
| `megachow.hq` | Ada, Bola, Emeka, Chioma (all 4) |
| `megachow.ikeja` | Ada, Emeka, Chioma (Ikeja branch only) |
| `megachow.surulere` | Bola (Surulere branch only) |

---

## Re-seed

```bash
cd backend && source .venv/bin/activate && python manage.py seed_demo --clear
```
