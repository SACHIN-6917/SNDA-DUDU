from django.contrib import admin
from .models import User, Industrial, Booking, Feedback, Enquiry, Newsletter, Wish

# ===== USER ADMIN =====
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'city', 'created_at')
    list_filter = ('created_at', 'city', 'state')
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Personal Info', {
            'fields': ('name', 'email', 'password', 'phone', 'dob')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'zip_code')
        }),
        ('Other', {
            'fields': ('avatar', 'created_at', 'updated_at')
        }),
    )


# ===== INDUSTRIAL ADMIN =====
@admin.register(Industrial)
class IndustrialAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'price', 'duration', 'status', 'created_at')
    list_filter = ('status', 'location', 'created_at')
    search_fields = ('title', 'location', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'location', 'image', 'status')
        }),
        ('Pricing & Capacity', {
            'fields': ('price', 'duration', 'max_participants', 'min_participants')
        }),
        ('Details (JSON)', {
            'fields': ('itinerary', 'includes', 'excludes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ===== BOOKING ADMIN =====
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'industrial', 'visit_date', 'num_participants', 'total_amount', 
                    'payment_status', 'booking_status', 'created_at')
    list_filter = ('booking_status', 'payment_status', 'visit_date', 'created_at')
    search_fields = ('user__name', 'user__email', 'industrial__title', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'visit_date'
    
    fieldsets = (
        ('Booking Info', {
            'fields': ('user', 'industrial', 'visit_date', 'num_participants')
        }),
        ('Payment', {
            'fields': ('total_amount', 'paid_amount', 'payment_status', 'payment_method', 'transaction_id')
        }),
        ('Status & Notes', {
            'fields': ('booking_status', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        # Optimize queries with select_related
        qs = super().get_queryset(request)
        return qs.select_related('user', 'industrial')


# ===== FEEDBACK ADMIN =====
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'industrial', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('name', 'comment')
    readonly_fields = ('created_at',)
    list_editable = ('is_approved',)
    
    fieldsets = (
        ('Feedback Info', {
            'fields': ('user', 'industrial', 'name', 'rating', 'comment')
        }),
        ('Moderation', {
            'fields': ('is_approved', 'created_at')
        }),
    )


# ===== ENQUIRY ADMIN =====
@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'phone', 'message')
    readonly_fields = ('created_at',)
    list_editable = ('status',)
    
    fieldsets = (
        ('Contact Info', {
            'fields': ('name', 'email', 'phone', 'college')
        }),
        ('Enquiry', {
            'fields': ('message', 'status', 'created_at')
        }),
    )


# ===== NEWSLETTER ADMIN =====
@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'subscribed_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email',)
    readonly_fields = ('subscribed_at',)
    list_editable = ('is_active',)
    
    actions = ['mark_active', 'mark_inactive']
    
    def mark_active(self, request, queryset):
        queryset.update(is_active=True)
    mark_active.short_description = "Mark selected as active"
    
    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)
    mark_inactive.short_description = "Mark selected as inactive"


# ===== WISH (CHATBOT) ADMIN =====
@admin.register(Wish)
class WishAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user', 'query', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('query', 'response', 'user__username', 'user__email', 'session_id')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Session Info', {
            'fields': ('session_id', 'user', 'created_at')
        }),
        ('Conversation', {
            'fields': ('query', 'response')
        }),
    )
