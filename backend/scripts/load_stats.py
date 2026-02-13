import os
import sys
import django
import csv
from django.conf import settings

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'industrial_visit.settings')
django.setup()

from dudu.models import ProjectStat

def run():
    print("Loading Statistics...")
    
    file_path = os.path.join(settings.BASE_DIR, 'data', 'stats.csv')
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    # clear existing
    ProjectStat.objects.all().delete()
    
    # Read CSV
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                title = row['title']
                count = int(row['count'])
                suffix = row['suffix']
                icon = row['icon'].strip()
                
                ProjectStat.objects.create(
                    title=title,
                    count=count,
                    suffix=suffix,
                    icon=icon
                )
                print(f"Created: {title}")
            except Exception as e:
                print(f"Error: {e}")

    print("Done!")

if __name__ == "__main__":
    run()
