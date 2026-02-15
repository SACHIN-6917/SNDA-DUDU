import os
import sys
import django
from decimal import Decimal

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'industrial_visit.settings')
django.setup()

from dudu.models import Industrial, ProjectStat

def seed_industrials():
    industrials = [
        {
            'name': 'Bengaluru Industrial Tech Tour',
            'location': 'Bengaluru',
            'description': 'Explore the Silicon Valley of India with visits to top IT hubs and tech parks.',
            'price': 2500.00,
            'duration': '1 Day',
            'image': 'images/Bengaluru.png',
            'status': 'active'
        },
        {
            'name': 'Chennai Manufacturing Hub',
            'location': 'Chennai',
            'description': "Visit major automobile and manufacturing plants in the 'Detroit of Asia'.",
            'price': 2200.00,
            'duration': '1 Day',
            'image': 'images/Chennai.jpg',
            'status': 'active'
        },
        {
            'name': 'Coimbatore Textile & Pump Industry',
            'location': 'Coimbatore',
            'description': 'Discover the textile capital and the pump manufacturing heart of South India.',
            'price': 1800.00,
            'duration': '1 Day',
            'image': 'images/Coimbatore.webp',
            'status': 'active'
        },
        {
            'name': 'Kodaikanal Agricultural Tour',
            'location': 'Kodaikanal',
            'description': 'Learn about hill station agriculture, spice plantations, and sustainable farming.',
            'price': 3500.00,
            'duration': '1 Day',
            'image': 'images/Kodaikanal Solar Observatory.jpg',
            'status': 'active'
        },
        {
            'name': 'Madurai Heritage & MSME Tour',
            'location': 'Madurai',
            'description': 'Explore vibrant MSME clusters and the rich cultural heritage of the temple city.',
            'price': 1500.00,
            'duration': '1 Day',
            'image': 'images/Madurai.jpg',
            'status': 'active'
        },
        {
            'name': 'Ooty Tea Estates Experience',
            'location': 'Ooty',
            'description': 'A deep dive into tea processing, chocolate making, and hill-station industries.',
            'price': 4000.00,
            'duration': '1 Day',
            'image': 'images/Ooty.jpg',
            'status': 'active'
        },
    ]

    print("Seeding Industrials...")
    for data in industrials:
        # Update if exists, else create
        obj, created = Industrial.objects.update_or_create(
            name=data['name'],
            defaults=data
        )
        if created:
            print(f"Created: {data['name']}")
        else:
            print(f"Updated: {data['name']}")

def seed_stats():
    stats = [
        {'title': 'Colleges', 'count': 120, 'suffix': '+', 'icon': 'fas fa-university'},
        {'title': 'Companies', 'count': 50, 'suffix': '', 'icon': 'fas fa-building'},
    ]

    print("\nSeeding Stats...")
    for data in stats:
        obj, created = ProjectStat.objects.update_or_create(
            title=data['title'],
            defaults=data
        )
        if created:
            print(f"Created Stat: {data['title']}")
        else:
            print(f"Updated Stat: {data['title']}")

if __name__ == '__main__':
    seed_industrials()
    seed_stats()
    print("\nSeeding Complete!")
