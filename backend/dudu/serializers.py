from rest_framework import serializers
from .models import User, Industrial, Booking, Feedback, Enquiry, Newsletter

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phone', 'dob', 'address', 'city', 'state', 'zip_code', 'avatar', 'created_at']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            name=validated_data['name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class IndustrialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Industrial
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.name')
    industrial_title = serializers.ReadOnlyField(source='industrial.title')

    class Meta:
        model = Booking
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'name', 'rating', 'comment', 'created_at']

class EnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiry
        fields = '__all__'

class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = '__all__'
