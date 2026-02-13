from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

# ===== USER MODEL =====
class User(models.Model):
    """Custom User model for authentication"""
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, db_index=True)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    avatar = models.CharField(max_length=500, blank=True, null=True)  # URL to avatar
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.email})"
    
    def set_password(self, raw_password):
        """Hash and set password"""
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Verify password"""
        return check_password(raw_password, self.password)


# ===== INDUSTRIAL MODEL =====
class Industrial(models.Model):
    """Industrial Visit Industrial"""
    INDUSTRIAL_STATUS = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('upcoming', 'Upcoming'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=50)  # e.g., "1 Day", "2 Days 1 Night"
    max_participants = models.IntegerField(default=50)
    min_participants = models.IntegerField(default=10)
    image = models.CharField(max_length=500, blank=True, null=True)  # URL to image
    itinerary = models.JSONField(blank=True, null=True)  # Store itinerary as JSON
    includes = models.JSONField(blank=True, null=True)  # What's included
    excludes = models.JSONField(blank=True, null=True)  # What's not included
    status = models.CharField(max_length=20, choices=INDUSTRIAL_STATUS, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'industrials'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - ₹{self.price}"


# ===== BOOKING MODEL =====
class Booking(models.Model):
    """Booking for industrial visits"""
    BOOKING_STATUS = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_STATUS = (
        ('unpaid', 'Unpaid'),
        ('advance', 'Advance Paid'),
        ('full', 'Full Payment'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    industrial = models.ForeignKey(Industrial, on_delete=models.CASCADE, related_name='bookings')
    visit_date = models.DateField()
    num_participants = models.IntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='unpaid')
    payment_method = models.CharField(max_length=50, blank=True, null=True)  # UPI, Card, etc.
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bookings'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.name} - {self.industrial.title} ({self.visit_date})"


# ===== FEEDBACK MODEL =====
class Feedback(models.Model):
    """User feedback for industrials or overall service"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks', null=True, blank=True)
    industrial = models.ForeignKey(Industrial, on_delete=models.CASCADE, related_name='feedbacks', null=True, blank=True)
    name = models.CharField(max_length=100)  # For non-logged-in users
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    comment = models.TextField()
    is_approved = models.BooleanField(default=True)  # For moderation
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'feedbacks'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.rating}★"


# ===== ENQUIRY MODEL =====
class Enquiry(models.Model):
    """Contact/Enquiry form submissions"""
    ENQUIRY_STATUS = (
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('closed', 'Closed'),
    )
    
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15)
    whatsapp = models.CharField(max_length=15, blank=True, null=True)
    college = models.CharField(max_length=200, blank=True, null=True)
    message = models.CharField(max_length=200, blank=True, null=True)
    travel_date = models.DateField(blank=True, null=True)
    num_people = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=ENQUIRY_STATUS, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'enquiries'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.email}"


# ===== NEWSLETTER SUBSCRIPTION MODEL =====
class Newsletter(models.Model):
    """Newsletter subscribers"""
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'newsletters'
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return self.email


# ===== CHATBOT LOGS MODEL =====
class ChatbotLog(models.Model):
    """Chatbot conversation logs"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='chatbot_logs', null=True, blank=True)
    session_id = models.CharField(max_length=100)  # For anonymous users
    query = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chatbot_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.session_id} - {self.query[:50]}"
