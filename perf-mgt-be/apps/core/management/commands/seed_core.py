from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.core.models import Unit, UnitOfMeasure, UserUnit


class Command(BaseCommand):
    help = "Seed core reference data"

    def handle(self, *args, **options):
        User = get_user_model()

        up_cebu, _ = Unit.objects.get_or_create(
            short_code="UP-Cebu",
            defaults={
                "name": "University of the Philippines Cebu",
                "description": "Main campus unit",
            },
        )

        child_units = [
            ("CAS", "College of Arts and Sciences"),
            ("SOM", "School of Management"),
            ("CCAD", "College of Communication, Art, and Design"),
        ]

        for short_code, name in child_units:
            Unit.objects.get_or_create(
                short_code=short_code,
                defaults={
                    "name": name,
                    "description": name,
                    "parent": up_cebu,
                },
            )

        units_of_measure = [
            ("%", "Percentage", "Percentage value"),
            ("count", "Count", "Numeric count"),
            ("peso", "Peso", "Philippine peso amount"),
        ]

        for short_code, name, description in units_of_measure:
            UnitOfMeasure.objects.get_or_create(
                short_code=short_code,
                defaults={
                    "name": name,
                    "description": description,
                },
            )

        admin = User.objects.filter(email="admin@example.com").first()

        if admin:
            UserUnit.objects.get_or_create(
                user=admin,
                unit=up_cebu,
                defaults={
                    "is_primary": True,
                    "is_active": True,
                },
            )

        self.stdout.write(self.style.SUCCESS("Core data seeded successfully."))
