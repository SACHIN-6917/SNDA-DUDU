import os
import django
from django.db import connection

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'industrial_visit.settings')
django.setup()

def drop_tables():
    with connection.cursor() as cursor:
        # Disable FK checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        
        if not tables:
            print("No tables found to drop.")
        else:
            print(f"Found {len(tables)} tables to drop.")
            for table in tables:
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {table}")
                    print(f"Dropped table {table}")
                except Exception as e:
                    print(f"Error dropping {table}: {e}")
        
        # Re-enable FK checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        print("Database reset complete.")

if __name__ == '__main__':
    drop_tables()
