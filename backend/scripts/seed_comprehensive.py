import os
import sys
import django
import random
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'industrial_visit.settings')
django.setup()

from django.contrib.auth.models import User
from dudu.models import Industrial, Booking, Enquiry, UserProfile, NewsEvent, Feedback

def seed_data():
    print("Starting comprehensive seeding...")

    # 1. Seed Users
    print("Seeding Users...")
    first_names = ["Rahul", "Priya", "Amit", "Sneha", "Sanjay", "Anjali", "Vikram", "Deepa", "Arjun", "Kavita"]
    last_names = ["Sharma", "Verma", "Gupta", "Patel", "Reddy", "Nair", "Iyer", "Singh", "Joshi", "Das"]
    cities = ["Mumbai", "Delhi", "Bengaluru", "Chennai", "Hyderabad", "Pune", "Kolkata", "Ahmedabad"]

    for i in range(25):
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        username = f"{fname.lower()}.{lname.lower()}{i}"
        email = f"{username}@example.com"
        
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                first_name=fname,
                last_name=lname
            )
            profile = user.profile
            profile.phone = f"98765{random.randint(10000, 99999)}"
            profile.city = random.choice(cities)
            profile.role = 'customer'
            profile.save()

    # 2. Seed Industrials (If not enough)
    print("Seeding Industrials...")
    locations = [
        ('Chennai', 'Automobile Manufacturing Hub'),
        ('Pune', 'IT & Automotive Tech Park'),
        ('Mumbai', 'Financial District & Port Authority'),
        ('Hyderabad', 'Pharmaceutical & Biotech Hub'),
        ('Kochi', 'Shipyard & Maritime Industry'),
        ('Delhi', 'Manufacturing & Logistics Center')
    ]

    for loc, desc in locations:
        Industrial.objects.get_or_create(
            name=f"{loc} {desc.split()[0]} Tour",
            defaults={
                'location': loc,
                'description': f"A comprehensive visit to {desc}. Explore industry standards and operations.",
                'price': random.randint(1500, 5000),
                'duration': '1 Day',
                'status': 'active',
                'visit_count': random.randint(10, 50)
            }
        )

    # 3. Seed Enquiries
    print("Seeding Enquiries...")
    options = ["Industrial Info", "Custom Visit", "Pricing Query"]
    for i in range(40):
        Enquiry.objects.create(
            name=f"Lead {i}",
            city=random.choice(cities),
            phone=f"99000{random.randint(10000, 99999)}",
            option=random.choice(options),
            travel_date=datetime.now().date() + timedelta(days=random.randint(10, 60)),
            no_of_people=random.randint(20, 100),
            status=random.choice(['pending', 'contacted', 'closed'])
        )

    # 4. Seed Bookings
    print("Seeding Bookings...")
    all_users = list(User.objects.filter(is_staff=False))
    all_industrials = list(Industrial.objects.all())
    
    for i in range(60):
        user = random.choice(all_users)
        industrial = random.choice(all_industrials)
        status = random.choice(['pending', 'completed', 'cancelled'])
        
        booking = Booking.objects.create(
            user=user,
            industrial=industrial,
            name=f"{user.first_name} {user.last_name}",
            email=user.email,
            phone=user.profile.phone,
            plan=random.choice(['full', 'advance']),
            amount=industrial.price,
            status=status,
            payment_status='completed' if status == 'completed' else 'pending'
        )
        # Shift created_at back randomly for historical data
        booking.created_at = datetime.now() - timedelta(days=random.randint(1, 90))
        booking.save()

    # 5. Seed News
    print("Seeding News & Events...")
    news_titles = [
        "New Partnership with Tech Hub Chennai",
        "Upcoming Industrial Seminar at IIT Bombay",
        "DUDU IV Hub crosses 10,000 students milestone",
        "Safety Protocol updates for 2026 visits",
        "Excellence Award in Student Travel"
    ]
    for title in news_titles:
        NewsEvent.objects.get_or_create(
            title=title,
            defaults={
                'content': "We are proud to announce our latest updates. Join us in celebrating our milestones and progress toward better education travel.",
                'date': datetime.now().date() - timedelta(days=random.randint(0, 30)),
                'is_active': True
            }
        )

    print("✅ Comprehensive seeding complete!")

if __name__ == '__main__':
    seed_data()
