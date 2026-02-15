import os
import sys
import django
from django.urls import reverse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'industrial_visit.settings')
django.setup()

try:
    url = reverse('payment_list')
    print(f"Success! URL is: {url}")
except Exception as e:
    print(f"Error: {e}")

try:
    url = reverse('index')
    print(f"Index URL is: {url}")
except Exception as e:
    print(f"Error reversing index: {e}")
