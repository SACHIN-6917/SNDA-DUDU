import os
import django
import random
from datetime import timedelta
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'industrial_visit.settings')
django.setup()

from dudu.models import Feedback, User

def seed_feedbacks():
    # Example avatars from local images or generic ones
    # The user image showed Rajesh, Praveen, Kajal
    
    feedbacks_data = [
        {
            "name": "Rajesh",
            "rating": 5,
            "comment": "Our Chennai industrial visit with DUDU IV Hub was very well organized. The travel arrangements were safe and punctual, the accommodation was clean and comfortable, and the food provided was of good quality. The industrial visit activities were properly scheduled and highly informative for students. Overall, it was a smooth and stress-free experience."
        },
        {
            "name": "Praveen",
            "rating": 4,
            "comment": "The Kochi industrial visit was excellently managed by DUDU IV Hub. Travel, hotel stay, and food arrangements were handled professionally. All company visits and activities were conducted on time and as planned. The team's coordination made the entire trip comfortable and hassle-free. Highly recommended for college industrial visits."
        },
        {
            "name": "Kajal",
            "rating": 5,
            "comment": "The Varkala friends trip with DUDU IV Hub was very enjoyable. Travel arrangements were safe, the stay was comfortable with good privacy, and the food was hygienic. Activities and sightseeing were well planned. As a female traveler, I felt safe and well supported throughout the trip, with clear attention to women's safety and privacy."
        },
        {
            "name": "Ananya",
            "rating": 5,
            "comment": "Incredible experience with the Bangalore IT tour. The DUDU team managed to get us into top-tier tech parks which was highly educational. The luxury bus transit was super comfortable. Definitely using them for our next batch too!"
        },
        {
            "name": "Suresh Kumar",
            "rating": 4,
            "comment": "Great coordination for our Coimbatore pump industry visit. The food was specifically tailored to our student preferences which was a plus. The on-site coordinator was very helpful and knowledgeable about the industries."
        },
        {
            "name": "Meera",
            "rating": 5,
            "comment": "DUDU IV Hub made our Ooty tea estate visit a breeze. From permissions to stay, everything was seamless. The fun activities in the evening were the highlight and helped in team bonding among students. Excellent service!"
        }
    ]

    for data in feedbacks_data:
        # Create or update based on name and message to avoid exact duplicates
        Feedback.objects.get_or_create(
            name=data["name"],
            message=data["comment"],
            defaults={
                "rating": data["rating"],
                "is_approved": True,
                # Randomize date slightly within last 3 months
                "created_at": timezone.now() - timedelta(days=random.randint(0, 90))
            }
        )
    print(f"Successfully seeded {len(feedbacks_data)} feedbacks.")

if __name__ == "__main__":
    seed_feedbacks()
