import os
import django
from django.db import connection
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'industrial_visit.settings')
django.setup()

def list_tables():
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("Existing tables:")
        for table in tables:
            print(table[0])

if __name__ == '__main__':
    list_tables()
