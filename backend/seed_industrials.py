import os
import django
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'industrial_visit.settings')
django.setup()

from dudu.models import Industrial

def seed_industrials():
    industrials_data = [
        {
            "title": "Bengaluru Industrial Tech Tour",
            "description": "Explore the Silicon Valley of India with visits to top IT hubs and tech parks.",
            "location": "Bengaluru",
            "price": Decimal("2500.00"),
            "duration": "1 Day",
            "image": "images/Bengaluru.png"
        },
        {
            "title": "Chennai Manufacturing Hub",
            "description": "Visit major automobile and manufacturing plants in the 'Detroit of Asia'.",
            "location": "Chennai",
            "price": Decimal("2200.00"),
            "duration": "1 Day",
            "image": "images/Chennai.jpg"
        },
        {
            "title": "Coimbatore Textile & Pump Industry",
            "description": "Discover the textile capital and the pump manufacturing heart of South India.",
            "location": "Coimbatore",
            "price": Decimal("1800.00"),
            "duration": "1 Day",
            "image": "images/Coimbatore.webp"
        },
        {
            "title": "Kodaikanal Agricultural Tour",
            "description": "Learn about hill station agriculture, spice plantations, and sustainable farming.",
            "location": "Kodaikanal",
            "price": Decimal("3500.00"),
            "duration": "2 Days 1 Night",
            "image": "images/Kodaikanal.avif"
        },
        {
            "title": "Madurai Heritage & MSME Tour",
            "description": "Explore vibrant MSME clusters and the rich cultural heritage of the temple city.",
            "location": "Madurai",
            "price": Decimal("1500.00"),
            "duration": "1 Day",
            "image": "images/Madurai.jpg"
        },
        {
            "title": "Ooty Tea Estates Experience",
            "description": "A deep dive into tea processing, chocolate making, and hill-station industries.",
            "location": "Ooty",
            "price": Decimal("4000.00"),
            "duration": "2 Days 1 Night",
            "image": "images/Ooty.jpg"
        },
        {
            "title": "Pondicherry French Colony & Food Industry",
            "description": "Experience the unique blend of French influence and modern food processing units.",
            "location": "Pondicherry",
            "price": Decimal("3000.00"),
            "duration": "1 Day",
            "image": "images/Pondicherry.webp"
        },
        {
            "title": "Salem Steel & Power Insights",
            "description": "Visit the major steel plants and power distribution networks in Salem.",
            "location": "Salem",
            "price": Decimal("2000.00"),
            "duration": "1 Day",
            "image": "images/Salem.jpg"
        },
        {
            "title": "Tirunelveli Wind Energy & Food Tech",
            "description": "Explore the massive wind farms and the local food processing industries.",
            "location": "Tirunelveli",
            "price": Decimal("1700.00"),
            "duration": "1 Day",
            "image": "images/Tirunelveli.jpg"
        },
        {
            "title": "Trichy Heavy Engineering Tour",
            "description": "Visit world-class heavy engineering and boiler manufacturing plants.",
            "location": "Trichy",
            "price": Decimal("2300.00"),
            "duration": "1 Day",
            "image": "images/Trichy.jpg"
        },
        {
            "title": "Kochi Port & Logistics Tour",
            "description": "Understand international shipping, port operations, and marine logistics in Kochi.",
            "location": "Kochi",
            "price": Decimal("2800.00"),
            "duration": "1 Day",
            "image": "images/kochi.jpg"
        }
    ]

    for data in industrials_data:
        Industrial.objects.get_or_create(
            title=data["title"],
            defaults={
                "description": data["description"],
                "location": data["location"],
                "price": data["price"],
                "duration": data["duration"],
                "image": data["image"],
                "status": "active"
            }
        )
    print(f"Successfully seeded {len(industrials_data)} industrials.")

if __name__ == "__main__":
    seed_industrials()
