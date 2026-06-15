from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.core.models import Profile


class Command(BaseCommand):
    help = "Seed default users"

    def handle(self, *args, **options):
        User = get_user_model()

        admin, created = User.objects.get_or_create(
            email="admin@example.com",
            defaults={
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )

        if created:
            admin.set_password("Admin12345")
            admin.save(update_fields=["password"])

        Profile.objects.get_or_create(
            user=admin,
            defaults={
                "first_name": "System",
                "middle_name": "",
                "last_name": "Administrator",
                "suffix": "",
            },
        )

        self.stdout.write(self.style.SUCCESS("Users seeded successfully."))
