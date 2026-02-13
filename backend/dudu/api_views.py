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

from .models import User, Industrial, Booking, Feedback, Enquiry, Newsletter, ChatbotLog
from .serializers import (
    UserSerializer, IndustrialSerializer, BookingSerializer, 
    FeedbackSerializer, EnquirySerializer, NewsletterSerializer
)
from .chatbot import get_panda_response
from .payment_utils import razorpay_client


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


class ChatbotAPIView(APIView):
    """Chatbot interaction endpoint"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        message = request.data.get('message', '')
        if not message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate session ID for anonymous users
        session_id = request.session.session_key or str(uuid.uuid4())
        
        # Get user if authenticated
        user = request.user if request.user.is_authenticated else None
        
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


class PaymentCreateAPIView(APIView):
    """Create Razorpay order for payment"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            booking_id = request.data.get('booking_id')
            amount = request.data.get('amount')  # In rupees
            
            if not booking_id or not amount:
                return Response({
                    'status': 'error',
                    'message': 'booking_id and amount are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get booking
            booking = get_object_or_404(Booking, id=booking_id, user=request.user)
            
            # Create Razorpay order
            order = razorpay_client.create_order(
                amount=float(amount),
                receipt=f'booking_{booking_id}',
                notes={
                    'booking_id': booking_id,
                    'user_id': request.user.id,
                    'industrial_id': booking.industrial.id
                }
            )
            
            # Save order ID to booking (you may want to add a field)
            booking.transaction_id = order['id']
            booking.save()
            
            return Response({
                'status': 'success',
                'order_id': order['id'],
                'amount': order['amount'],
                'currency': order['currency'],
                'razorpay_key': razorpay_client.client.auth[0] if razorpay_client.enabled else 'demo_key'
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentVerifyAPIView(APIView):
    """Verify Razorpay payment signature"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            razorpay_order_id = request.data.get('razorpay_order_id')
            razorpay_payment_id = request.data.get('razorpay_payment_id')
            razorpay_signature = request.data.get('razorpay_signature')
            booking_id = request.data.get('booking_id')
            
            if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature, booking_id]):
                return Response({
                    'status': 'error',
                    'message': 'All payment details are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify signature
            is_valid = razorpay_client.verify_payment_signature(
                razorpay_order_id,
                razorpay_payment_id,
                razorpay_signature
            )
            
            if is_valid:
                # Update booking
                booking = get_object_or_404(Booking, id=booking_id, user=request.user)
                booking.payment_status = 'full'
                booking.booking_status = 'confirmed'
                booking.transaction_id = razorpay_payment_id
                booking.save()
                
                return Response({
                    'status': 'success',
                    'message': 'Payment verified successfully',
                    'booking_id': booking_id
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'Invalid payment signature'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
