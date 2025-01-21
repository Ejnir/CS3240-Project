import os
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

class Command(BaseCommand):
    help = 'Creates Google OAuth application'

    def handle(self, *args, **options):
        site = Site.objects.get_current()

        client_id = os.environ.get('GOOGLE_CLIENT_ID')
        client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')

        if not client_id or not client_secret:
            self.stdout.write(self.style.ERROR('Google client ID or secret key missing in environment variables.'))
            return
        
        try:
            social_app = SocialApp.objects.get(provider='google')
            social_app.client_id = client_id
            social_app.secret = client_secret
            social_app.save()
            self.stdout.write(self.style.SUCCESS('Updated Google OAuth configuration.'))
        except SocialApp.DoesNotExist:
            social_app = SocialApp.objects.create(
                provider='google',
                name='google',
                client_id=client_id,
                secret=client_secret,
            )
            social_app.sites.add(site)
            self.stdout.write(self.style.SUCCESS('Added new Google OAuth configuration.'))