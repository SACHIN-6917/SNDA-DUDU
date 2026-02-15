from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Industrial, Feedback, Booking, Newsletter, ProjectStat, Payment, UserProfile, Enquiry


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Industrial)
class IndustrialAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'price', 'visit_count', 'status', 'created_at')
    list_filter = ('status', 'location')
    search_fields = ('name', 'description')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'industrial', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating')
    search_fields = ('name', 'message')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('name', 'industrial', 'plan', 'amount', 'payment_status', 'status', 'created_at')
    list_filter = ('status', 'payment_status', 'plan')
    search_fields = ('name', 'email')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'payment_status', 'transaction_id', 'created_at')
    list_filter = ('payment_status',)


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at')


@admin.register(ProjectStat)
class ProjectStatAdmin(admin.ModelAdmin):
    list_display = ('title', 'count', 'suffix', 'icon')
@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'phone', 'travel_date', 'no_of_people', 'status', 'created_at')
    list_filter = ('status', 'city')
    search_fields = ('name', 'phone', 'city')
