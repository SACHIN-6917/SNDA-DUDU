import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'industrial_visit.settings')
django.setup()

from dudu.models import Industrial

def check_industrials():
    count = Industrial.objects.count()
    print(f"Total Industrials: {count}")
    
    active_count = Industrial.objects.filter(status='active').count()
    print(f"Active Industrials: {active_count}")
    
    for ind in Industrial.objects.all():
        print(f" - {ind.name} (Status: {ind.status}, Image: {ind.image})")

if __name__ == '__main__':
    check_industrials()
