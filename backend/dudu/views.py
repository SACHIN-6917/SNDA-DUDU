from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import json
import uuid

from .models import User, Industrial, Booking, Feedback, Enquiry, Newsletter, ProjectStat
from .chatbot import get_panda_response

# Home
def index(request):
    """Render homepage"""
    industrials = Industrial.objects.filter(status='active')[:3]
    stats = ProjectStat.objects.all()
    context = {
        'industrials': industrials,
        'stats': stats,
    }
    return render(request, 'index.html', context)

# Authentication
def login_view(request):
    """Handle Login"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email and password:
            try:
                user = authenticate(request, username=email, password=password)
                if user is not None:
                    auth_login(request, user)
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    messages.success(request, f"Welcome back, {user.name}!")
                    
                    # Default redirect to home unless 'next' is specified
                    next_url = request.GET.get('next') or 'index'
                    return redirect(next_url)
                else:
                    messages.error(request, "Invalid email or password.")
            except Exception as e:
                messages.error(request, f"Login error: {str(e)}")
        else:
            messages.error(request, "Please provide both email and password.")
            
    return render(request, 'login.html')

def register_view(request):
    """Handle Registration"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('login')
            
        user = User(name=name, email=email)
        user.set_password(password)
        user.save()
        
        # Auto-login after registration
        authenticated_user = authenticate(request, username=email, password=password)
        if authenticated_user:
            auth_login(request, authenticated_user)
            request.session['user_id'] = authenticated_user.id
            request.session['user_name'] = authenticated_user.name
            messages.success(request, f"Welcome to Dudu IV Hub, {name}! Your account has been created.")
            return redirect('index')
        
        messages.success(request, "Registration successful. Please login.")
        return redirect('login')
        
    return render(request, 'login.html')

def logout_view(request):
    """Handle Logout"""
    auth_logout(request)

    messages.success(request, "Logged out successfully.")
    return redirect('index')

# Industrials
def industrial_list(request):
    """List all industrials"""
    industrials = Industrial.objects.filter(status='active')
    stats = ProjectStat.objects.all()
    return render(request, 'industrial.html', {'industrials': industrials, 'stats': stats})

def industrial_detail(request, ind_id):
    """Industrial details"""
    try:
        industrial = Industrial.objects.get(id=ind_id)
        return render(request, 'industrial_details.html', {'industrial': industrial})
    except Industrial.DoesNotExist:
        messages.error(request, "Industrial not found.")
        return redirect('industrial_list')

# Helper to bridge standard Auth User with local Dudu User
def _get_local_user(auth_user):
    """Bridge between request.user (Django Auth) and dudu.models.User (local)"""
    if auth_user.is_anonymous:
        return None
    
    # Try to find existing local user by email or username
    local_user = User.objects.filter(email=getattr(auth_user, 'email', '')).first()
    
    # If not found (e.g. if we used standard Django createsuperuser), link them
    if not local_user:
        local_user = User.objects.create(
            name=getattr(auth_user, 'first_name', '') or auth_user.username,
            email=getattr(auth_user, 'email', f"{auth_user.username}@example.com")
        )
    return local_user

# Booking & Payment
@login_required
def booking_create(request, ind_id):
    """Create a booking (renders payment page)"""
    industrial = get_object_or_404(Industrial, id=ind_id)
    
    if request.method == 'POST':
        # Process Payment Mock
        user = _get_local_user(request.user)

        
        visit_date = request.POST.get('visit_date')
        if not visit_date:
            from datetime import date
            visit_date = date.today()
            
        participants = int(request.POST.get('participants', 1))
        plan = request.POST.get('plan', 'full') # full/advance
        payment_method = request.POST.get('method', 'card')
        
        total_amount = industrial.price * participants
        paid_amount = total_amount if plan == 'full' else total_amount * 0.30
        
        # Create Booking
        booking = Booking.objects.create(
            user=user,
            industrial=industrial,
            visit_date=visit_date,
            num_participants=participants,
            total_amount=total_amount,
            paid_amount=paid_amount,
            payment_status='full' if plan == 'full' else 'advance',
            payment_method=payment_method,
            transaction_id=str(uuid.uuid4())[:8].upper(),
            booking_status='confirmed'
        )
        
        messages.success(request, "Booking confirmed! Payment successful.")
        return redirect('account')
        
    return render(request, 'payment.html', {'industrial': industrial})

def payment_view_direct(request):
    """Direct payment page access (for demo/quick pay)"""
    # Fetch a default industrial or the first active one for display purposes
    industrial = Industrial.objects.filter(status='active').first()
    if not industrial:
        # Dummy fallback if no industrials exist
        industrial = {'title': 'General Payment', 'price': 0, 'id': 0}
        
    return render(request, 'payment.html', {'industrial': industrial})

# Account
@login_required
def account_view(request):
    """User Dashboard"""
    user = _get_local_user(request.user)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Update user fields
            user.name = data.get('name', user.name)
            user.phone = data.get('phone', user.phone)
            user.dob = data.get('dob') or None
            user.address = data.get('address', user.address)
            user.city = data.get('city', user.city)
            user.state = data.get('state', user.state)
            user.zip_code = data.get('zip', user.zip_code)
            
            # Avatar handling (skip if too long or implement upload later)
            avatar = data.get('avatar')
            if avatar and len(avatar) < 500:
                user.avatar = avatar
                
            user.save()
            return JsonResponse({'status': 'success', 'message': 'Profile updated successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    bookings = Booking.objects.filter(user=user).order_by('-created_at')
    
    return render(request, 'account.html', {'user': user, 'bookings': bookings})

# Settings
def settings_view(request):
    """Account Settings & Social Connections"""
    return render(request, 'settings.html')


# Feedback
def feedback_view(request):
    """Feedback Page"""
    if request.method == 'POST':
        name = request.POST.get('name')
        comment = request.POST.get('comment')
        rating = request.POST.get('rating')
        
        Feedback.objects.create(name=name, comment=comment, rating=rating)
        messages.success(request, "Thank you for your feedback!")
        return redirect('feedback')
        
    reviews = Feedback.objects.filter(is_approved=True)
    return render(request, 'feedback.html', {'reviews': reviews})

# API for dynamic checks (Enquiry / Newsletter)
def submit_enquiry(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Create Enquiry
            Enquiry.objects.create(
                name=data.get('name'),
                city=data.get('city'),
                email=data.get('email'),
                phone=data.get('phone'),
                whatsapp=data.get('whatsapp'),
                college=data.get('college'),
                message=data.get('option'), # In index.html this is named 'option'
                travel_date=data.get('travel_date') or None,
                num_people=int(data.get('people', 1))
            )
            return JsonResponse({'status': 'success', 'message': 'Enquiry submitted successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405)
# ===== CHATBOT API =====
@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """API endpoint for Panda Bot (Gemini)"""
    try:
        data = json.loads(request.body)
        message = data.get('message')
        
        if not message:
            return JsonResponse({'error': 'Message required'}, status=400)
            
        # Get AI Response
        response_text = get_panda_response(message)
        
        return JsonResponse({
            'response': response_text,
            'status': 'success'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def google_auth(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405)
        
    try:
        data = json.loads(request.body)
        token = data.get('credential')
        
        # Verify the token
        CLIENT_ID = getattr(settings, 'GOOGLE_CLIENT_ID', 'YOUR_GOOGLE_CLIENT_ID')
        
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), CLIENT_ID)
        
        # ID token is valid. Get user's Google ID information.
        email = idinfo.get('email')
        name = idinfo.get('name')
        picture = idinfo.get('picture') # Google profile picture URL
        
        if not email:
            return JsonResponse({'status': 'error', 'message': 'Email not found in Google account'}, status=400)
            
        # 1. Handle standard Django Auth
        from django.contrib.auth.models import User as AuthUser
        auth_user, created = AuthUser.objects.get_or_create(
            username=email,
            defaults={'email': email, 'first_name': name}
        )
        auth_login(request, auth_user, backend='django.contrib.auth.backends.ModelBackend')

        # 2. Sync with local User model
        user, created = User.objects.get_or_create(
            email=email,
            defaults={'name': name, 'phone': ''}
        )
        
        # Always update name/avatar from Google if they changed or were empty
        needs_save = False
        if not user.name or user.name == email: # If name is missing or just email
            user.name = name
            needs_save = True
        if picture and not user.avatar: # Sync avatar if not already set locally
            user.avatar = picture
            needs_save = True
            
        if needs_save:
            user.save()
        
        # Set session helpers
        request.session['user_id'] = user.id
        request.session['user_name'] = user.name
        request.session['user_email'] = user.email
        
        # Determine redirect
        redirect_url = request.GET.get('next', '/')

        return JsonResponse({
            'status': 'success', 
            'message': 'Login successful',
            'redirect_url': redirect_url
        })
        
    except ValueError:
        # Invalid token
        return JsonResponse({'status': 'error', 'message': 'Invalid Google token'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

