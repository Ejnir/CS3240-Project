from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp

class Command(BaseCommand):
    help = 'Cleanup duplicate Google OAuth apps'

    def handle(self, *args, **options):
        google_apps = SocialApp.objects.filter(provider='google')

        if google_apps.count() > 1:
            first_app = google_apps.first()
            duplicates = google_apps.exclude(id=first_app.id)
            count = duplicates.count()

            duplicates.delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted {count} duplicate Google OAuth apps."))
        else:
            self.stdout.write(self.style.SUCCESS("No duplicates found."))
