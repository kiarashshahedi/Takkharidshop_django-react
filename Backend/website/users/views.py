
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
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token

# files
from .models import MyUser, Customer, Seller
from products.models import Product
from products.serializers import ProductSerializer
from . import kavesms 
from .kavesms import get_random_otp, check_otp_expiration
from .permissions import IsCustomer, IsSeller

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
    
# Utility function to generate JWT tokens
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# Utility function to send OTP (placeholder for actual implementation)
def send_otp(mobile, otp):
    print(f"Sending OTP {otp} to mobile {mobile}")  # Replace with actual sending logic
    
# Customer Registration/Login---------------------------------------------------------------------------------------
class CustomerRegisterLoginView(APIView):
    permission_classes = []  # No authentication required

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
    permission_classes = []  # No authentication required

    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            otp = serializer.validated_data['otp']
            user = get_object_or_404(MyUser, mobile=mobile)
            if user.is_otp_valid(otp):
                tokens = get_tokens_for_user(user)
                if not hasattr(user, 'customer_profile'):
                    return Response({'message': 'Profile completion required.', 'tokens': tokens}, status=status.HTTP_200_OK)
                return Response({'message': 'Login successful.', 'tokens': tokens}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Complete Customer Profile
class CompleteCustomerProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsCustomer]

    def post(self, request):
        user = request.user
        serializer = CompleteCustomerProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response({'message': 'Profile completed successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Seller Registration (Step 1)
class SellerRegisterView(APIView):
    permission_classes = []  # No authentication required

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
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsSeller]

    def post(self, request):
        user = request.user
        serializer = CompleteSellerProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response({'message': 'Profile completed successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Seller Login
class SellerLoginView(APIView):
    permission_classes = []  # No authentication required

    def post(self, request):
        serializer = SellerLoginSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            meli_code = serializer.validated_data['meli_code']
            otp = serializer.validated_data['otp']
            user = get_object_or_404(MyUser, mobile=mobile, meli_code=meli_code)
            if user.is_otp_valid(otp):
                tokens = get_tokens_for_user(user)
                return Response({'message': 'Login successful.', 'tokens': tokens}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Delete the user's token to log them out
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Failed to log out.'}, status=status.HTTP_400_BAD_REQUEST)