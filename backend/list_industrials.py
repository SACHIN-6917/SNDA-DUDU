
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'industrial_visit.settings')
django.setup()

from dudu.models import Industrial

for i in Industrial.objects.all():
    print(f"ID: {i.id} | Name: {i.name} | Image: {i.image}")
