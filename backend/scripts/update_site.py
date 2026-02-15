import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'industrial_visit.settings')
django.setup()

from django.contrib.sites.models import Site

def update_site_domain():
    site = Site.objects.get_current()
    site.domain = '127.0.0.1:8000'
    site.name = 'DUDU IV Hub'
    site.save()
    print(f"Updated site to: {site.domain} ({site.name})")

if __name__ == '__main__':
    update_site_domain()
