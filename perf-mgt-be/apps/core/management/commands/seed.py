from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run all seeders"

    def handle(self, *args, **options):
        call_command("seed_users")
        call_command("seed_core")
        call_command("seed_pme")

        self.stdout.write(self.style.SUCCESS("All seeders completed."))
