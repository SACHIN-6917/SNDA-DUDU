from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

router = DefaultRouter()
router.register(r'api/users', api_views.UserViewSet)
router.register(r'api/industrials', api_views.IndustrialViewSet)
router.register(r'api/bookings', api_views.BookingViewSet)
router.register(r'api/feedbacks', api_views.FeedbackViewSet)
router.register(r'api/enquiries', api_views.EnquiryViewSet)
router.register(r'api/newsletters', api_views.NewsletterViewSet)

urlpatterns = [
    # Pages
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    path('industrials/', views.industrial_list, name='industrial_list'),
    path('industrials/<int:ind_id>/', views.industrial_detail, name='industrial_detail'),
    
    path('book/<int:ind_id>/', views.booking_create, name='booking_create'),
    path('payment/', views.payment_view_direct, name='payment'),
    path('api/google-auth/', views.google_auth, name='google_auth'),
    path('account/', views.account_view, name='account'),
    path('feedback/', views.feedback_view, name='feedback'),
    
    # API endpoints (Specific/Legacy)
    path('api/enquiry/', views.submit_enquiry, name='submit_enquiry'),
    path('api/chat/', api_views.ChatbotAPIView.as_view(), name='chat_api'),
    
    # Payment API endpoints
    path('api/payment/create/', api_views.PaymentCreateAPIView.as_view(), name='payment_create'),
    path('api/payment/verify/', api_views.PaymentVerifyAPIView.as_view(), name='payment_verify'),
    
    # REST API Router
    path('', include(router.urls)),
]
