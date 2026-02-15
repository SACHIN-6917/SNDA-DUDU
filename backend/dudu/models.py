from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=20, blank=True)
    dob = models.DateField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)  # Store actual images
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Industrial(models.Model):
    name = models.CharField(max_length=200)  # Renamed from title
    description = models.TextField()
    location = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=50)
    image = models.CharField(max_length=255, blank=True)
    visit_count = models.IntegerField(default=0)  # Added
    status = models.CharField(max_length=20, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    industrial = models.ForeignKey(Industrial, on_delete=models.SET_NULL, null=True, blank=True)  # Added
    message = models.TextField()  # Renamed from comment
    rating = models.IntegerField(default=5)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # For backward compatibility with existing seeds that might use 'name' instead of User
    # We'll keep 'name' for anonymous/legacy feedback
    name = models.CharField(max_length=100, default='Anonymous')

    def __str__(self):
        return f"{self.name} - {self.rating}★"


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    industrial = models.ForeignKey(Industrial, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    plan = models.CharField(max_length=20, default='full')  # full or advance
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=50, blank=True)
    payment_status = models.CharField(max_length=20, default='pending')  # Added
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)  # This is booking_date

    def __str__(self):
        return f"{self.name} - {self.industrial.name}"


class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} for Booking {self.booking.id}"


class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class ProjectStat(models.Model):
    title = models.CharField(max_length=100)
    count = models.IntegerField(default=0)
    suffix = models.CharField(max_length=20, blank=True)
    icon = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.title
class Enquiry(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('contacted', 'Contacted'),
        ('closed', 'Closed'),
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True) # Adding email as well
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    whatsapp = models.CharField(max_length=20, blank=True)
    option = models.CharField(max_length=100, blank=True)
    travel_date = models.DateField()
    no_of_people = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Enquiry from {self.name} - {self.city}"
class NewsEvent(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    date = models.DateField()
    image = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
