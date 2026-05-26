from django.core.management.base import BaseCommand

from apps.inspections.models import ChecklistCategory, ChecklistSeverity, InspectionChecklistItem

DEFAULT_CHECKLIST_ITEMS = [
    # A. Food Handler Certification
    ("A1", ChecklistCategory.FOOD_HANDLER_CERT, "Are all food handlers registered on FoodCert NG?", ChecklistSeverity.CRITICAL, 1),
    ("A2", ChecklistCategory.FOOD_HANDLER_CERT, "Do all active food handlers have valid certificates?", ChecklistSeverity.CRITICAL, 2),
    ("A3", ChecklistCategory.FOOD_HANDLER_CERT, "Are expired certificates being used?", ChecklistSeverity.CRITICAL, 3),
    ("A4", ChecklistCategory.FOOD_HANDLER_CERT, "Are suspended or revoked certificates being used?", ChecklistSeverity.CRITICAL, 4),
    ("A5", ChecklistCategory.FOOD_HANDLER_CERT, "Are certificates available for verification on-site?", ChecklistSeverity.MAJOR, 5),
    ("A6", ChecklistCategory.FOOD_HANDLER_CERT, "Are uncertified persons handling food?", ChecklistSeverity.CRITICAL, 6),

    # B. Fitness and Exclusion Compliance
    ("B1", ChecklistCategory.FITNESS_EXCLUSION, "Are temporarily not-fit handlers excluded from food handling?", ChecklistSeverity.CRITICAL, 7),
    ("B2", ChecklistCategory.FITNESS_EXCLUSION, "Are sick handlers present in food handling areas?", ChecklistSeverity.CRITICAL, 8),
    ("B3", ChecklistCategory.FITNESS_EXCLUSION, "Are return-to-work clearances respected?", ChecklistSeverity.MAJOR, 9),
    ("B4", ChecklistCategory.FITNESS_EXCLUSION, "Has employer reported illness where required?", ChecklistSeverity.MAJOR, 10),

    # C. Vaccination Compliance
    ("C1", ChecklistCategory.VACCINATION, "Are required vaccination statuses up to date?", ChecklistSeverity.MAJOR, 11),
    ("C2", ChecklistCategory.VACCINATION, "Are food handlers with vaccination due flagged for renewal?", ChecklistSeverity.MINOR, 12),
    ("C3", ChecklistCategory.VACCINATION, "Are vaccination compliance records maintained?", ChecklistSeverity.MINOR, 13),

    # D. Employer Records
    ("D1", ChecklistCategory.EMPLOYER_RECORDS, "Does employer maintain food handler records?", ChecklistSeverity.MAJOR, 14),
    ("D2", ChecklistCategory.EMPLOYER_RECORDS, "Are branch records up to date?", ChecklistSeverity.MAJOR, 15),
    ("D3", ChecklistCategory.EMPLOYER_RECORDS, "Are linked food handlers correctly assigned to branch?", ChecklistSeverity.MAJOR, 16),
    ("D4", ChecklistCategory.EMPLOYER_RECORDS, "Are compliance records available for inspection?", ChecklistSeverity.MAJOR, 17),

    # E. Hygiene and Food Safety Practices
    ("E1", ChecklistCategory.HYGIENE, "Handwashing facilities available", ChecklistSeverity.MAJOR, 18),
    ("E2", ChecklistCategory.HYGIENE, "Soap/sanitizer available at handwashing stations", ChecklistSeverity.MAJOR, 19),
    ("E3", ChecklistCategory.HYGIENE, "PPE available for food handlers", ChecklistSeverity.MINOR, 20),
    ("E4", ChecklistCategory.HYGIENE, "Clean food handling area", ChecklistSeverity.MAJOR, 21),
    ("E5", ChecklistCategory.HYGIENE, "Waste disposal adequate", ChecklistSeverity.MINOR, 22),
    ("E6", ChecklistCategory.HYGIENE, "Food handlers observe hygiene rules", ChecklistSeverity.MAJOR, 23),
    ("E7", ChecklistCategory.HYGIENE, "No visible unsafe food handling practice", ChecklistSeverity.CRITICAL, 24),

    # F. Certificate Authenticity
    ("F1", ChecklistCategory.CERT_AUTHENTICITY, "QR codes verified successfully", ChecklistSeverity.CRITICAL, 25),
    ("F2", ChecklistCategory.CERT_AUTHENTICITY, "No fake certificates identified", ChecklistSeverity.CRITICAL, 26),
    ("F3", ChecklistCategory.CERT_AUTHENTICITY, "No certificate-person mismatch detected", ChecklistSeverity.CRITICAL, 27),
    ("F4", ChecklistCategory.CERT_AUTHENTICITY, "No repeated suspicious certificate use", ChecklistSeverity.CRITICAL, 28),

    # G. Corrective Action Compliance
    ("G1", ChecklistCategory.CORRECTIVE_ACTION, "Previous notices addressed", ChecklistSeverity.CRITICAL, 29),
    ("G2", ChecklistCategory.CORRECTIVE_ACTION, "Evidence of correction available", ChecklistSeverity.MAJOR, 30),
    ("G3", ChecklistCategory.CORRECTIVE_ACTION, "Outstanding corrective actions remain", ChecklistSeverity.MAJOR, 31),
]

class Command(BaseCommand):
    help = "Seed default inspection checklist items."

    def handle(self, *args, **options):
        created_count = 0
        for ref, category, question, severity, order in DEFAULT_CHECKLIST_ITEMS:
            _, created = InspectionChecklistItem.objects.update_or_create(
                category=category,
                question=question,
                defaults={
                    "severity_if_failed": severity,
                    "sort_order": order,
                    "is_active": True,
                },
            )
            created_count += int(created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(DEFAULT_CHECKLIST_ITEMS)} checklist items ({created_count} created)."
            )
        )
