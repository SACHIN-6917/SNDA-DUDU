import os
import sys
import django
from django.conf import settings

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'industrial_visit.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

def setup_social_app():
    # Ensure current site exists
    current_site = Site.objects.get_current()
    
    # Google Credentials
    client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')
    secret = getattr(settings, 'GOOGLE_CLIENT_SECRET', '')
    
    if not client_id or not secret:
        print("Error: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not found in settings.")
        return

    # Create or update SocialApp
    app, created = SocialApp.objects.update_or_create(
        provider='google',
        defaults={
            'name': 'Google',
            'client_id': client_id,
            'secret': secret,
        }
    )
    
    # Link to current site
    app.sites.add(current_site)
    
    print(f"Successfully {'created' if created else 'updated'} Google SocialApp.")
    print(f"Linked to site: {current_site.domain}")

if __name__ == '__main__':
    setup_social_app()
