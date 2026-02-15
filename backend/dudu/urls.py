from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('industrial/', views.industrial_list, name='industrial_list'),
    path('industrial/<int:pk>/', views.industrial_detail, name='industrial_detail'),
    path('payment/<int:pk>/', views.payment_view, name='payment'),
    path('payment/', views.payment_list_view, name='payment_list'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('account/', views.account_view, name='account'),
    path('settings/', views.settings_view, name='settings'),
    path('booking/<int:pk>/create/', views.booking_create, name='booking_create'),
    path('submit-enquiry/', views.submit_enquiry, name='submit_enquiry'),
    
    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/industrials/', views.admin_industrials, name='admin_industrials'),
    path('admin-dashboard/bookings/', views.admin_bookings, name='admin_bookings'),
    path('admin-dashboard/enquiries/', views.admin_enquiries, name='admin_enquiries'),
    path('admin-dashboard/users/', views.admin_users, name='admin_users'),
    path('admin-dashboard/news/', views.admin_news, name='admin_news'),

    # Google SSO
    path('google/login/', views.google_login, name='google_login'),
    path('google/auth/', views.google_auth, name='google_auth'),

    # Chatbot API
    path('api/chat/', views.chat_api, name='chat_api'),

    # Newsletter
    path('api/newsletter/', views.newsletter_subscribe, name='newsletter_subscribe'),
]
