from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import MyUser, Customer, Seller
import re


# Serializer for completing the customer profile
class CompleteCustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'meli_code', 'address1', 'address2', 'city', 'zipcode', 'date_of_birth']

# Serializer for seller registration (Step 1)
class SellerRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['mobile', 'meli_code']

# Serializer for seller additional details (Step 2)
class CompleteSellerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ['first_name', 'last_name', 'since_date', 'business_license', 'shop_name', 'shop_address', 'zipcode']

# Serializer for generating and verifying OTP
class OTPSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11)
    otp = serializers.CharField(max_length=6, required=False)
    
    def validate_mobile(self, value):
        if not re.match(r'^\d{11}$', value):
            raise serializers.ValidationError("Invalid mobile number.")
        return value
    
# Serializer for seller login
class SellerLoginSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11)
    meli_code = serializers.CharField(max_length=10)
    otp = serializers.CharField(max_length=6)

class DashboardSerializer():
    pass