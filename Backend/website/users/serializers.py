from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import MyUser, Customer, Seller

class CustomerRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['mobile']

class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'meli_code', 'address1', 'address2', 'city', 'zipcode', 'date_of_birth']

class SellerRegisterSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(required=True)
    meli_code = serializers.CharField(required=True)
    mobile = serializers.CharField(required=True)
    class Meta:
        model = MyUser
        fields = ['first_name', 'last_name', 'meli_code', 'email', 'shop_name', 'mobile']

class SellerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ['first_name', 'last_name', 'meli_code', 'email', 'shop_name']

class OTPSerializer(serializers.Serializer):
    mobile = serializers.CharField()
    otp = serializers.IntegerField(required=False)

class LoginSerializer(serializers.Serializer):
    mobile = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        mobile = data.get("mobile")
        password = data.get("password")
        user = authenticate(mobile=mobile, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid login credentials")
        if not user.is_verified:
            raise serializers.ValidationError("Account not verified")
        data['user'] = user
        return data
    

class DashboardSerializer():
    pass