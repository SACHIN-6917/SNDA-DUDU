from django.conf import settings
from django.core.management.base import BaseCommand
from dudu.models import ProjectStat
import csv
import os

class Command(BaseCommand):
    help = 'Import Project Statistics'
    
    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, 'data', 'stats.csv')
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return
            
        ProjectStat.objects.all().delete()
        
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ProjectStat.objects.create(
                    title=row['title'],
                    count=int(row['count']),
                    suffix=row['suffix'],
                    icon=row['icon']
                )
                self.stdout.write(self.style.SUCCESS(f'Imported: {row["title"]}'))
