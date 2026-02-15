import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'industrial_visit.settings')
django.setup()

from django.contrib.auth import get_user_model
from dudu.models import UserProfile

User = get_user_model()

def create_admin():
    email = 'admin@dudu.com'
    password = 'admin123'
    username = 'admin'

    if not User.objects.filter(username=username).exists() and not User.objects.filter(email=email).exists():
        print(f"Creating admin user: {email}")
        user = User.objects.create_superuser(username=username, email=email, password=password)
        
        # Ensure profile exists and has role 'admin'
        if not hasattr(user, 'profile'):
            UserProfile.objects.create(user=user, role='admin')
        else:
            user.profile.role = 'admin'
            user.profile.save()
            
        print("Admin user created successfully.")
        print(f"Email: {email}")
        print(f"Password: {password}")
    else:
        print("Admin user already exists.")
        # Ensure role is admin
        user = User.objects.filter(email=email).first() or User.objects.filter(username=username).first()
        if user:
            user.set_password(password)
            user.save()
            print("Password reset to admin123.")
            if not hasattr(user, 'profile'):
                UserProfile.objects.create(user=user, role='admin')
            else:
                user.profile.role = 'admin'
                user.profile.save()
            print("Admin role verified.")

if __name__ == '__main__':
    create_admin()
