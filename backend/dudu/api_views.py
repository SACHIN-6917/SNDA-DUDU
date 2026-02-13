"""
Enhanced API Views with permissions, pagination, and payment integration
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.shortcuts import get_object_or_404
import uuid

from .models import User, Industrial, Booking, Feedback, Enquiry, Newsletter, Wish
from .serializers import (
    UserSerializer, IndustrialSerializer, BookingSerializer, 
    FeedbackSerializer, EnquirySerializer, NewsletterSerializer
)
from .chatbot import get_panda_response



# Custom Permissions
class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow read access to everyone, write access only to admins
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allow access only to object owner or admin
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user


# Custom Pagination
class StandardResultsPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ViewSets
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    pagination_class = StandardResultsPagination
    
    def get_queryset(self):
        """Show only own profile unless admin"""
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        """Get or update current user profile"""
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IndustrialViewSet(viewsets.ModelViewSet):
    queryset = Industrial.objects.all()
    serializer_class = IndustrialSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['location', 'status']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['price', 'created_at', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter active industrials for non-staff users"""
        queryset = Industrial.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(status='active')
        return queryset
    
    @action(detail=False, methods=['get'])
    def locations(self, request):
        """Get list of all unique locations"""
        locations = Industrial.objects.filter(status='active').values_list('location', flat=True).distinct()
        return Response({'locations': list(locations)})


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['booking_status', 'payment_status']
    ordering_fields = ['created_at', 'visit_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Show only own bookings unless admin"""
        if self.request.user.is_staff:
            return Booking.objects.select_related('user', 'industrial').all()
        return Booking.objects.filter(user=self.request.user).select_related('industrial')
    
    def perform_create(self, serializer):
        """Set user automatically on creation"""
        serializer.save(user=self.request.user)


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Show only approved feedbacks to non-staff"""
        if self.request.user.is_staff:
            return Feedback.objects.all()
        return Feedback.objects.filter(is_approved=True)
    
    def perform_create(self, serializer):
        """Associate user if authenticated"""
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()


class EnquiryViewSet(viewsets.ModelViewSet):
    queryset = Enquiry.objects.all()
    serializer_class = EnquirySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """Allow POST for anyone, GET/PUT/DELETE only for admin"""
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class NewsletterViewSet(viewsets.ModelViewSet):
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    pagination_class = StandardResultsPagination
    
    def get_permissions(self):
        """Allow POST (subscribe) for anyone, others only for admin"""
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


# Additional API Views (not ViewSets)
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from decimal import Decimal


@method_decorator(csrf_exempt, name='dispatch')
class ChatbotAPIView(APIView):
    """Chatbot interaction endpoint"""
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        message = request.data.get('message', '')
        if not message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate session ID for anonymous users
        session_id = request.session.session_key or str(uuid.uuid4())
        
        # Get user if authenticated (Bypass DRF, use Django Session)
        django_user = getattr(request._request, 'user', None)
        user = django_user if django_user and django_user.is_authenticated else None
        
        # Get response from chatbot
        try:
            response = get_panda_response(message, user=user, session_id=session_id)
            return Response({
                'status': 'success',
                'response': response,
                'session_id': session_id
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# ... (omitted)

class PaymentCreateAPIView(APIView):
    """Create Payment intent/order (Generic/UPI)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            booking_id = request.data.get('booking_id')
            amount = request.data.get('amount')
            
            if not booking_id or not amount:
                return Response({
                    'status': 'error',
                    'message': 'booking_id and amount are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get booking
            booking = get_object_or_404(Booking, id=booking_id, user=request.user)
            
            # For UPI/Google Pay, we might usually generate a transaction ID here
            # or simply return success to allow client-side UPI intent generation
            transaction_ref = f"TXN_{uuid.uuid4().hex[:12].upper()}"
            
            return Response({
                'status': 'success',
                'order_id': transaction_ref,
                'amount': amount,
                'currency': 'INR',
                'message': 'Ready for UPI payment'
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentVerifyAPIView(APIView):
    """Verify Payment (Generic/UPI)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            transaction_id = request.data.get('transaction_id')
            booking_id = request.data.get('booking_id')
            status_check = request.data.get('status', 'success')
            
            if not all([transaction_id, booking_id]):
                return Response({
                    'status': 'error',
                    'message': 'Transaction ID and Booking ID are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify payment logic here (e.g. check against bank API)
            # For now, we accept if client says success (Demo mode)
            
            if status_check == 'success':
                # Update booking
                booking = get_object_or_404(Booking, id=booking_id, user=request.user)
                booking.payment_status = 'full'
                booking.booking_status = 'confirmed'
                booking.transaction_id = transaction_id
                booking.save()
                
                return Response({
                    'status': 'success',
                    'message': 'Payment confirmed successfully',
                    'booking_id': booking_id
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'Payment failed'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
