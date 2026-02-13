import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'industrial_visit.settings')
django.setup()

from dudu.models import Industrial

packages = Industrial.objects.all()
print(f"ID | Title | Location | Current Image")
print("-" * 60)
for p in packages:
    print(f"{p.id} | {p.title} | {p.location} | {p.image}")
