import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'industrial_visit.settings')
django.setup()

from dudu.models import Industrial

for p in Industrial.objects.all():
    print(f"{p.id} | {p.title} | {p.location}")
