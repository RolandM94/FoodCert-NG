from django.core.management.base import BaseCommand

from apps.locations.models import State


NIGERIAN_STATES = [
    ("Abia", "AB"),
    ("Adamawa", "AD"),
    ("Akwa Ibom", "AK"),
    ("Anambra", "AN"),
    ("Bauchi", "BA"),
    ("Bayelsa", "BY"),
    ("Benue", "BE"),
    ("Borno", "BO"),
    ("Cross River", "CR"),
    ("Delta", "DE"),
    ("Ebonyi", "EB"),
    ("Edo", "ED"),
    ("Ekiti", "EK"),
    ("Enugu", "EN"),
    ("Federal Capital Territory", "FCT"),
    ("Gombe", "GO"),
    ("Imo", "IM"),
    ("Jigawa", "JI"),
    ("Kaduna", "KD"),
    ("Kano", "KN"),
    ("Katsina", "KT"),
    ("Kebbi", "KE"),
    ("Kogi", "KO"),
    ("Kwara", "KW"),
    ("Lagos", "LA"),
    ("Nasarawa", "NA"),
    ("Niger", "NI"),
    ("Ogun", "OG"),
    ("Ondo", "ON"),
    ("Osun", "OS"),
    ("Oyo", "OY"),
    ("Plateau", "PL"),
    ("Rivers", "RI"),
    ("Sokoto", "SO"),
    ("Taraba", "TA"),
    ("Yobe", "YO"),
    ("Zamfara", "ZA"),
]


class Command(BaseCommand):
    help = "Seed all 36 Nigerian states and the FCT."

    def handle(self, *args, **options):
        created_count = 0
        for name, code in NIGERIAN_STATES:
            _, created = State.objects.update_or_create(
                code=code,
                defaults={"name": name, "is_fct": code == "FCT"},
            )
            created_count += int(created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(NIGERIAN_STATES)} states/FCT ({created_count} created)."
            )
        )
