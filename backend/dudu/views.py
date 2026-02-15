import json
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Avg

from .models import Industrial, Feedback, Booking, Newsletter, ProjectStat, Enquiry, NewsEvent


# ─── Page Views ───────────────────────────────────────────────

def index(request):
    industrials = Industrial.objects.filter(status='active')[:6]
    feedbacks = Feedback.objects.filter(is_approved=True).order_by('-created_at')[:6]
    stats = ProjectStat.objects.all()
    return render(request, 'index.html', {
        'industrials': industrials,
        'feedbacks': feedbacks,
        'stats': stats,
    })


@login_required
def admin_dashboard(request):
    if not admin_check(request.user):
        messages.error(request, "Access denied. Admins only.")
        return redirect('index')

    context = {
        'total_bookings': Booking.objects.count(),
        'pending_enquiries': Enquiry.objects.filter(status='pending').count(),
        'active_industrials': Industrial.objects.filter(status='active').count(),
        'total_users': User.objects.filter(is_staff=False).count(),
        'recent_bookings': Booking.objects.order_by('-created_at')[:5],
        'news_items': NewsEvent.objects.filter(is_active=True).order_by('-date')[:3]
    }
    return render(request, 'admin_dashboard.html', context)

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff or (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
             return redirect('admin_dashboard')
        return redirect('index')

    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        try:
            # Flexible login: username or email
            user_obj = User.objects.filter(email=email).first()
            if not user_obj:
                 user_obj = User.objects.filter(username=email).first()
            
            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)
            else:
                user = None
        except Exception as e:
            user = None

        if user is not None:
            login(request, user)
            
            # Role-based Redirect
            if user.is_staff or (hasattr(user, 'profile') and user.profile.role == 'admin'):
                return redirect('admin_dashboard')
            
            next_url = request.GET.get('next', 'index')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'login.html')


def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'login.html')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name.split()[0] if name else '',
            last_name=' '.join(name.split()[1:]) if name and len(name.split()) > 1 else ''
        )
        # UserProfile is created automatically via signal
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        messages.success(request, 'Account created successfully!')
        return redirect('index')
    return redirect('login')


def logout_view(request):
    logout(request)
    return redirect('login')


def industrial_list(request):
    industrials = Industrial.objects.filter(status='active')
    stats = ProjectStat.objects.all()
    return render(request, 'industrial.html', {
        'industrials': industrials,
        'stats': stats,
    })


def industrial_detail(request, pk):
    industrial = get_object_or_404(Industrial, pk=pk)
    # Increment visit count
    industrial.visit_count += 1
    industrial.save()
    return render(request, 'industrial_details.html', {
        'industrial': industrial,
    })


def payment_view(request, pk):
    industrial = get_object_or_404(Industrial, pk=pk)
    return render(request, 'payment.html', {
        'industrial': industrial,
    })


def payment_list_view(request):
    industrials = Industrial.objects.filter(status='active')
    industrial = industrials.first()
    return render(request, 'payment.html', {
        'industrial': industrial,
        'industrials': industrials,
    })


def feedback_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', 'Anonymous')
        rating = int(request.POST.get('rating', 5))
        message_text = request.POST.get('comment', '')  # Form still sends 'comment'

        Feedback.objects.create(
            user=request.user if request.user.is_authenticated else None,
            name=name,
            rating=rating,
            message=message_text,
            is_approved=True,
        )
        messages.success(request, 'Thank you for your feedback!')
        return redirect('feedback')

    feedbacks = Feedback.objects.filter(is_approved=True).order_by('-created_at')
    avg_rating = feedbacks.aggregate(avg=Avg('rating'))['avg'] or 0
    return render(request, 'feedback.html', {
        'reviews': feedbacks,
        'avg_rating': round(avg_rating, 1),
    })


@login_required
def account_view(request):
    if request.method == 'POST':
        try:
            # Handle both JSON and Multipart (for files)
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST

            # Update User model
            full_name = data.get('name', '')
            if full_name:
                parts = full_name.strip().split()
                request.user.first_name = parts[0]
                request.user.last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
                request.user.save()

            # Update UserProfile model
            profile = request.user.profile
            profile.phone = data.get('phone', '')
            
            # Handle Date of Birth
            dob = data.get('dob', '')
            if dob:
                profile.dob = dob
            else:
                profile.dob = None
                
            profile.city = data.get('city', '')
            profile.address = data.get('address', '')

            # Handle Avatar Upload
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']

            profile.save()
            return JsonResponse({'status': 'success', 'message': 'Profile updated successfully!'})
        except json.JSONDecodeError:
             return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    bookings = []
    profile = None
    if request.user.is_authenticated:
        bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
        profile = request.user.profile
        # Add name property for template compatibility
        profile.name = request.user.get_full_name() or request.user.username
        
    return render(request, 'account.html', {
        'bookings': bookings,
        'profile': profile
    })


def settings_view(request):
    return render(request, 'settings.html')


def booking_create(request, pk):
    industrial = get_object_or_404(Industrial, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        plan = request.POST.get('plan', 'full')
        payment_method = request.POST.get('payment_method', '')

        amount = industrial.price if plan == 'full' else industrial.price * 30 / 100

        # Create Booking
        booking = Booking.objects.create(
            user=request.user if request.user.is_authenticated else None,
            industrial=industrial,
            name=name,
            email=email,
            phone=phone,
            plan=plan,
            amount=amount,
            payment_method=payment_method,
            payment_status='completed', # Assuming successful for now
            status='confirmed',
        )

        # Create Payment Record
        from .models import Payment
        Payment.objects.create(
            booking=booking,
            amount=amount,
            payment_status='completed',
            transaction_id=f"TXN-{booking.id}-{int(amount)}" # Mock txn ID
        )

        return JsonResponse({'status': 'success', 'message': 'Booking confirmed!'})

    return redirect('payment', pk=pk)


@require_POST
def submit_enquiry(request):
    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        
        # Save Enquiry to DB
        Enquiry.objects.create(
            name=data.get('name', ''),
            city=data.get('city', ''),
            phone=data.get('phone', ''),
            whatsapp=data.get('whatsapp', ''),
            option=data.get('option', ''),
            travel_date=data.get('travel_date', None) or '2026-01-01', # Default if missing
            no_of_people=int(data.get('people', 0))
        )
        return JsonResponse({'status': 'success', 'message': 'Enquiry submitted successfully!'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def google_login(request):
    return redirect('/accounts/google/login/')


@require_POST
def google_auth(request):
    # Delegate to allauth's Google login flow
    return JsonResponse({'status': 'success', 'redirect_url': '/'})


@require_POST
def newsletter_subscribe(request):
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    email = data.get('email', '')
    if email:
        Newsletter.objects.get_or_create(email=email)
        return JsonResponse({'status': 'success', 'message': 'Subscribed!'})
    return JsonResponse({'status': 'error', 'message': 'Email required'}, status=400)


# ─── Chatbot API ──────────────────────────────────────────────

# Keyword → response mapping for website-only chatbot
CHATBOT_RESPONSES = {
    # Industrial Visit Topics
    'industrial': (
        "We offer industrial visits across Tamil Nadu including Bengaluru, Chennai, Coimbatore, "
        "Kodaikanal, Madurai, Ooty, Pondicherry, Salem, Tirunelveli, Trichy, and Kochi. "
        "You can browse all available visits on our Industrials page. "
        "Each visit includes transport, accommodation, meals, and guided factory/company tours."
    ),
    'visit': (
        "Our industrial visits are designed for students and groups. Each package includes "
        "travel, stay, food, and guided tours of factories and companies. "
        "Check the Industrials page for available destinations and pricing."
    ),
    'destination': (
        "We cover many destinations across South India for industrial visits! "
        "Popular choices include Chennai (manufacturing), Bengaluru (tech), "
        "Ooty (tea estates), Coimbatore (textiles), and Kochi (port logistics). "
        "Visit the Industrials page to explore all options."
    ),

    # Enquiry
    'enquir': (
        "To submit an enquiry, scroll down to the 'Enquire' section on our Home page. "
        "Fill in your name, email, phone number, and your message, then click Submit. "
        "Our team will get back to you within 24 hours."
    ),
    'contact': (
        "You can reach us through the Enquiry form on the Home page, or use the "
        "WhatsApp button on the Industrials page for instant support. "
        "Fill in your details and we'll respond promptly."
    ),

    # Booking
    'book': (
        "To book an industrial visit: 1) Browse our Industrials page, 2) Click on a "
        "destination to see details, 3) Click 'Book Now', 4) Choose Full Payment or "
        "Advance Payment (30%), 5) Complete payment via UPI. "
        "You'll receive a confirmation once your booking is processed."
    ),
    'booking status': (
        "You can check your booking status on the Account page. "
        "Log in to your account and navigate to the Account section — "
        "all your bookings and their statuses will be displayed there."
    ),

    # Payment
    'payment': (
        "We accept payments via UPI apps including Google Pay, PhonePe, Paytm, BHIM, "
        "Amazon Pay, WhatsApp Pay, CRED, and more. You can choose to pay the full amount "
        "or pay 30% as an advance. Go to the Payment page after selecting your industrial visit."
    ),
    'pay': (
        "Payment can be made on the Payment page. We support two plans: "
        "Full Payment (100% now) or Advance Payment (30% now, rest later). "
        "We accept UPI payments through all major apps."
    ),
    'upi': (
        "We accept all major UPI apps: Google Pay, PhonePe, Paytm, BHIM UPI, "
        "Amazon Pay, WhatsApp Pay, CRED, JioPay, MobiKwik, and Freecharge. "
        "Simply select your preferred app on the Payment page."
    ),
    'price': (
        "Pricing varies by destination. You can see the exact price on each industrial "
        "visit card on the Industrials page. We offer full payment and 30% advance options. "
        "Prices typically range from ₹1,500 to ₹4,000 depending on the destination and duration."
    ),
    'refund': (
        "For refund queries, please contact our support team through the Enquiry form on "
        "the Home page or via WhatsApp. Refund policies depend on the timing of cancellation."
    ),

    # Login / Logout / Account
    'login': (
        "To log in: 1) Click 'Login' in the navigation bar, 2) Enter your registered email "
        "and password, 3) Click the Login button. "
        "You can also sign in with Google using the 'Continue with Google' option."
    ),
    'sign up': (
        "To create an account: 1) Go to the Login page, 2) Click 'Sign Up', "
        "3) Enter your full name, email, and password, 4) Click the Sign Up button. "
        "You can also register with your Google account."
    ),
    'register': (
        "To register: 1) Go to the Login page, 2) Click 'Sign Up', "
        "3) Enter your full name, email, and password, 4) Click the Sign Up button. "
        "You'll be logged in automatically after registration."
    ),
    'logout': (
        "To log out: Click on your profile icon in the top-right corner of the navbar, "
        "then select 'Logout' from the dropdown menu. You can also log out from the "
        "Account page or the Settings page."
    ),
    'password': (
        "To change your password: 1) Go to Settings (click your profile icon → Settings), "
        "2) Click 'Change Password', 3) Follow the instructions. "
        "If you forgot your password, click 'Forgot Password?' on the Login page."
    ),
    'account': (
        "Your Account page shows your profile details and booking history. "
        "Click on your profile icon in the navbar and select 'My Account'. "
        "From there, you can view your bookings and update your profile information."
    ),
    'profile': (
        "You can view and edit your profile on the Account page. "
        "Click your profile icon in the navbar → 'My Account'. "
        "Your name, email, and booking history are all displayed there."
    ),
    'settings': (
        "In Settings, you can manage your email, change your password, "
        "and manage connected social accounts (Google). "
        "Access it from your profile dropdown → Settings."
    ),

    # Navigation Help
    'navigate': (
        "Our website has these main pages: Home (landing page with enquiry form), "
        "Industrials (browse all visits), Payment (complete your booking payment), "
        "Feedback (read and submit reviews), Account (your profile & bookings), "
        "and Settings (manage your account). Use the navbar at the top to navigate."
    ),
    'home': (
        "The Home page is our landing page. It features an overview of DUDU IV Hub, "
        "quick access to industrial visits, an enquiry form, and a newsletter subscription. "
        "Click 'Home' in the navbar to return to it anytime."
    ),
    'page': (
        "Our website has these sections: Home, Industrials, Payment, Feedback, Account, "
        "and Settings. Use the navigation bar at the top of the page to switch between them."
    ),

    # Feedback
    'feedback': (
        "To leave feedback: 1) Go to the Feedback page from the navbar, 2) Scroll down "
        "to the feedback form, 3) Enter your name, select a star rating, write your review, "
        "4) Click Submit. Your feedback helps us improve our services!"
    ),
    'review': (
        "You can read reviews from other travelers on our Feedback page. "
        "You can also submit your own review after completing a trip. "
        "Navigate to Feedback from the navbar to get started."
    ),

    # About / General Website
    'about': (
        "DUDU IV Hub is a platform that organizes industrial visits and educational tours "
        "for students across Tamil Nadu and South India. We handle everything — transport, "
        "accommodation, food, and guided tours — so you can focus on learning."
    ),
    'dudu': (
        "DUDU IV Hub is your one-stop platform for industrial visits. "
        "We coordinate travel, accommodation, meals, and guided industrial tours "
        "for students and college groups across South India."
    ),
    'what': (
        "DUDU IV Hub organizes industrial visits for students. Our website lets you "
        "browse available visits, make enquiries, book and pay online, and track your bookings. "
        "Use the navbar to explore the different sections."
    ),
    'how': (
        "Here's how to use our website: Browse industrial visits on the Industrials page, "
        "click on one to see details, book it with the 'Book Now' button, and complete payment "
        "on the Payment page. You can also enquire from the Home page or leave feedback!"
    ),
    'help': (
        "I can help you with: \n"
        "• Industrial visit details and destinations\n"
        "• How to make an enquiry\n"
        "• Booking and payment process\n"
        "• Login, sign up, and account management\n"
        "• Navigating the website\n"
        "• Leaving feedback and reviews\n\n"
        "Just ask me about any of these topics!"
    ),
    'hi': (
        "Hello! 👋 Welcome to DUDU IV Hub. I can help you with information about our "
        "industrial visits, booking process, payments, account management, and navigating "
        "the website. What would you like to know?"
    ),
    'hello': (
        "Hi there! 👋 I'm Panda Bot, your assistant for DUDU IV Hub. "
        "I can help you with industrial visits, enquiries, bookings, payments, and more. "
        "How can I assist you today?"
    ),
    'thank': (
        "You're welcome! 😊 If you have any more questions about our website or services, "
        "feel free to ask. Happy to help!"
    ),
    
    # Cities / Destinations
    'chennai': (
        "Chennai is a major hub for manufacturing and automobile industries. "
        "Our visits there cover top factories and production units. "
        "Check the Industrials page for specific packages!"
    ),
    'bangalore': (
        "Bengaluru (Bangalore) is the tech capital! We offer visits to IT parks, "
        "startups, and innovation centers. Browse the Industrials page for details."
    ),
    'bengaluru': (
        "Bengaluru (Bangalore) is the tech capital! We offer visits to IT parks, "
        "startups, and innovation centers. Browse the Industrials page for details."
    ),
    'coimbatore': (
        "Coimbatore is known for its textile and engineering industries. "
        "Perfect for mechanical and textile engineering students. See packages on the Industrials page."
    ),
    'ooty': (
        "Ooty offers visits to tea factories and botanical research centers, "
        "plus a great climate! Check our Ooty packages on the Industrials page."
    ),
    'kodaikanal': (
        "Kodaikanal visits focus on environmental science and solar observatories. "
        "A great mix of learning and nature. Details are on the Industrials page."
    ),
    'madurai': (
        "Madurai offers insights into cultural heritage and small-scale industries. "
        "Check available visits on the Industrials page."
    ),
    'trichy': (
        "Trichy is home to major public sector enterprises like BHEL and NIT. "
        "Great for engineering visits. Browse packages on the Industrials page."
    ),
    'salem': (
        "Salem is famous for steel and mineral processing. "
        "Explore our industrial visit options there on the Industrials page."
    ),
    'pondicherry': (
        "Pondicherry offers a mix of French culture, Auroville architecture, "
        "and small-scale manufacturing. Check packages on the Industrials page."
    ),
    'kochi': (
        "Kochi is a hub for port logistics, shipping, and seafood processing. "
        "Ideal for logistics and commerce students. See details on the Industrials page."
    ),
    
    # Admin / Help
    'admin': (
        "To access the Admin Dashboard, please log in with your credentials. "
        "If you are an administrator, you will be automatically redirected to the dashboard."
    ),
    'login': (
        "You can log in or sign up by clicking the 'Login' button in the navbar. "
        "We support email and Google login."
    ),
    'help': (
        "I can help you with Industrial Visits, Booking Status, Payments, and more. "
        "Try asking 'Show me Chennai visits' or 'How to book'."
    ),
    'whatsapp': (
        "You can reach us on WhatsApp at +91 9940764517 for any queries or custom requirements!"
    ),
    'phone': (
        "You can call or WhatsApp us at +91 9940764517. We're here to help!"
    ),
    'contact': (
        "For support, you can contact us via the enquiry form on the home page, "
        "or reach us directly on WhatsApp at +91 9940764517."
    ),
}

FALLBACK_RESPONSE = "Sorry, this question is not based on our website."


def _match_chatbot_response(message):
    """
    Match user message to a chatbot response using keyword matching.
    Returns the best matching response or the fallback message.
    """
    msg = message.lower().strip()

    # Empty message
    if not msg:
        return "Please type a question and I'll do my best to help! You can ask about industrial visits, booking, payment, login, and more."

    # Try exact multi-word matches first (higher priority)
    multi_word_keys = [k for k in CHATBOT_RESPONSES if ' ' in k]
    for key in multi_word_keys:
        if key in msg:
            return CHATBOT_RESPONSES[key]

    # Try single-word keyword matches
    single_word_keys = [k for k in CHATBOT_RESPONSES if ' ' not in k]
    for key in single_word_keys:
        if key in msg:
            return CHATBOT_RESPONSES[key]

    # No match found — strict fallback
    return FALLBACK_RESPONSE


@require_POST
def chat_api(request):
    """
    Chatbot API endpoint.
    Responds ONLY to website-related questions.
    Rejects all other queries with a strict fallback message.
    """
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
    except (json.JSONDecodeError, AttributeError):
        message = request.POST.get('message', '')

    response = _match_chatbot_response(message)

    return JsonResponse({
        'status': 'success',
        'response': response,
    })
# ─── Admin Management Views ──────────────────────────────────

def admin_check(user):
    return user.is_staff or (hasattr(user, 'profile') and user.profile.role == 'admin')

@login_required
def admin_industrials(request):
    if not admin_check(request.user):
        return redirect('index')
    industrials = Industrial.objects.all().order_by('-created_at')
    return render(request, 'admin_industrials.html', {'industrials': industrials})

@login_required
def admin_bookings(request):
    if not admin_check(request.user):
        return redirect('index')
    bookings = Booking.objects.all().order_by('-created_at')
    return render(request, 'admin_bookings.html', {'bookings': bookings})

@login_required
def admin_enquiries(request):
    if not admin_check(request.user):
        return redirect('index')
    enquiries = Enquiry.objects.all().order_by('-created_at')
    return render(request, 'admin_enquiries.html', {'enquiries': enquiries})

@login_required
def admin_users(request):
    if not admin_check(request.user):
        return redirect('index')
    # Filter for customers only or all non-staff
    users = User.objects.filter(is_staff=False).order_by('-date_joined')
    return render(request, 'admin_users.html', {'users': users})

@login_required
def admin_news(request):
    if not admin_check(request.user):
        return redirect('index')
    news_items = NewsEvent.objects.all().order_by('-date')
    return render(request, 'admin_news.html', {'news_items': news_items})
