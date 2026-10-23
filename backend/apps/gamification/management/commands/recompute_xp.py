from django.core.management.base import BaseCommand

from apps.gamification.services.xp import recompute_user_cache
from apps.users.models import User


class Command(BaseCommand):
    help = "Recalcule Profile.total_xp et Profile.level a partir du ledger XPTransaction."

    def handle(self, *args, **options):
        count = 0
        for user in User.objects.iterator():
            recompute_user_cache(user)
            count += 1
        self.stdout.write(f"{count} profil(s) recalcule(s).")
