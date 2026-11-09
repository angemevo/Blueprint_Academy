from django.core.management.base import BaseCommand

from apps.learning.services.seed import seed_blueprint


class Command(BaseCommand):
    help = "Cree la structure (non publiee) du parcours Blueprint Fundamentals."

    def handle(self, *args, **options):
        created = seed_blueprint()
        self.stdout.write(self.style.SUCCESS(f"Seed termine, crees : {created}"))
