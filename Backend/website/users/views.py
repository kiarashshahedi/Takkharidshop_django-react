
import datetime
import time
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django.conf import settings
import logging
from django.shortcuts import get_object_or_404

# restframework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
# Tokens
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
# files
from .models import MyUser, Customer, Seller
from products.models import Product
from products.serializers import ProductSerializer
from . import kavesms 
from .kavesms import get_random_otp, check_otp_expiration

# docs 
from drf_spectacular.utils import extend_schema, extend_schema_view

from .serializers import (
    DashboardSerializer, OTPSerializer, CompleteCustomerProfileSerializer,
    SellerRegistrationSerializer, CompleteSellerProfileSerializer,
    SellerLoginSerializer
)

logger = logging.getLogger(__name__)
# Custom APIKeyRequiredMixin
class APIKeyRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if api_key != settings.API_KEY:
            raise PermissionDenied("Invalid API Key")
        return super().dispatch(request, *args, **kwargs)
    


# Utility function to send OTP (placeholder for actual implementation)
def send_otp(mobile, otp):
    print(f"Sending OTP {otp} to mobile {mobile}")  # Replace with actual sending logic
    
# Customer Registration/Login---------------------------------------------------------------------------------------
class CustomerRegisterLoginView(APIView):
    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            user, created = MyUser.objects.get_or_create(mobile=mobile, defaults={'is_customer': True})
            otp = user.generate_otp()
            send_otp(mobile, otp)
            if created:
                return Response({'message': 'User registered. Complete profile required.', 'is_new': True}, status=status.HTTP_201_CREATED)
            return Response({'message': 'OTP sent for login.', 'is_new': False}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# OTP Verification for Customers
class VerifyCustomerOTPView(APIView):
    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            otp = serializer.validated_data['otp']
            user = get_object_or_404(MyUser, mobile=mobile)
            if user.is_otp_valid(otp):
                if not hasattr(user, 'customer_profile'):
                    return Response({'message': 'Profile completion required.'}, status=status.HTTP_200_OK)
                return Response({'message': 'Login successful.'}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Complete Customer Profile
class CompleteCustomerProfileView(APIView):
    def post(self, request):
        user = request.user
        serializer = CompleteCustomerProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response({'message': 'Profile completed successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Seller Registration (Step 1)
class SellerRegisterView(APIView):
    def post(self, request):
        serializer = SellerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            meli_code = serializer.validated_data['meli_code']
            user, created = MyUser.objects.get_or_create(mobile=mobile, meli_code=meli_code, defaults={'is_seller': True})
            otp = user.generate_otp()
            send_otp(mobile, otp)
            if created:
                return Response({'message': 'User registered. Proceed to complete profile.'}, status=status.HTTP_201_CREATED)
            return Response({'message': 'OTP sent for login.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Complete Seller Profile (Step 2)
class CompleteSellerProfileView(APIView):
    def post(self, request):
        user = request.user
        serializer = CompleteSellerProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response({'message': 'Profile completed successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Seller Login
class SellerLoginView(APIView):
    def post(self, request):
        serializer = SellerLoginSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            meli_code = serializer.validated_data['meli_code']
            otp = serializer.validated_data['otp']
            user = get_object_or_404(MyUser, mobile=mobile, meli_code=meli_code)
            if user.is_otp_valid(otp):
                return Response({'message': 'Login successful.'}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerDashboardView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    serializer_class = DashboardSerializer

    def get(self, request):
        customer = request.user.customer_profile
        orders = []  # Fetch customer orders here
        return Response({
            "customer_info": CustomerProfileSerializer(customer).data,
            "orders": orders,
        })

class SellerDashboardView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


    def get(self, request):
        seller = request.user.seller_profile
        products = Product.objects.filter(seller=request.user)
        product_serializer = ProductSerializer(products, many=True)
        return Response({
            "seller_info": SellerProfileSerializer(seller).data,
            "products": product_serializer.data,
        })


class LoginView(APIView):
    permission_classes = [AllowAny]

    @ratelimit(key='ip', rate='5/m', method='POST', block=True)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            password = serializer.validated_data['password']
            user = authenticate(request, mobile=mobile, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "Logged in successfully",
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh)
                })
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------------------------------------------------------------------------
class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Failed to logout"}, status=status.HTTP_400_BAD_REQUEST)



