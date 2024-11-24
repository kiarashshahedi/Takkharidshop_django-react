
import datetime
import time
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django.conf import settings
import logging

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
    CustomerRegisterSerializer, SellerRegisterSerializer, CustomerProfileSerializer, 
    SellerProfileSerializer, OTPSerializer, LoginSerializer, DashboardSerializer
)

logger = logging.getLogger(__name__)

# Custom APIKeyRequiredMixin
class APIKeyRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if api_key != settings.API_KEY:
            raise PermissionDenied("Invalid API Key")
        return super().dispatch(request, *args, **kwargs)

# -----------------------------------------------------------------------------------------------
# Customer Registration
@extend_schema_view(
    post=extend_schema(
        request=CustomerRegisterSerializer,
        responses={"200": {"description": "OTP sent to mobile"}, "400": "Invalid data"}
    )
)
class RegisterCustomerView(APIKeyRequiredMixin, APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = CustomerRegisterSerializer(data=request.data)

        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']

            try:
                # Check if user already exists
                user = MyUser.objects.get(mobile=mobile)

                # Generate and send OTP for existing user
                otp = get_random_otp()
                user.otp = otp
                user.save()

                # # Simulate sending OTP via SMS
                # kavesms.send_otp_soap(mobile, otp)
                # print(f"OTP sent to {mobile}: {otp}")

                # User already exists, no need to create new user
                return Response({"message": "OTP sent to existing user successfully. Please verify OTP."}, status=status.HTTP_200_OK)

            except MyUser.DoesNotExist:
                # If user does not exist, create a new user
                user = MyUser.objects.create_user(username=mobile, mobile=mobile, is_active=False, is_customer=True)

                # Generate and send OTP for new user
                otp = get_random_otp()
                user.otp = otp
                user.save()

                # # Simulate sending OTP via SMS
                # kavesms.send_otp_soap(mobile, otp)
                # print(f"OTP sent to {mobile}: {otp}")

                # Return response to complete profile after OTP verification
                return Response({"message": "New user created. OTP sent. Please verify OTP."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------------------------------------------------------------------------

# Seller Registration
@extend_schema_view(
    post=extend_schema(
        request=SellerRegisterSerializer,
        responses={"200": {"description": "OTP sent to mobile"}, "400": "Invalid data"}
    )
)
class RegisterSellerView(APIKeyRequiredMixin, APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SellerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            user, created = MyUser.objects.get_or_create(mobile=mobile, is_seller=True)
            user.generate_otp()
            return Response({"message": "OTP sent to mobile"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# -----------------------------------------------------------------------------------------------

# Verify OTP
@extend_schema_view(
    post=extend_schema(
        request=OTPSerializer,
        responses={"202": "Profile completion prompt", "400": "Invalid OTP or mobile"}
    )
)
class VerifyOTPView( APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            otp = serializer.validated_data['otp']

            try:
                user = MyUser.objects.get(mobile=mobile)

                # Check OTP expiration
                if not check_otp_expiration(user):
                    return Response({"error": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)

                # Verify OTP
                if str(user.otp) != str(otp):
                    return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

                # Mark user as active and authenticated
                user.is_active = True
                user.otp = None  # Clear OTP after successful verification
                user.otp_create_time = None
                user.save()

                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)

                # Optionally, if the user is new, redirect them to the profile completion page
                if not user.profile_completed:  # Assuming you have a flag for profile completion
                    return Response({
                        "message": "Logged in successfully. Please complete your profile.",
                        "access_token": str(refresh.access_token),
                        "refresh_token": str(refresh),
                    }, status=status.HTTP_200_OK)

                # If user has completed the profile, return success
                return Response({
                    "message": "Logged in successfully",
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                }, status=status.HTTP_200_OK)

            except MyUser.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------------------------------------------------------------------------

# Complete Profile for Customer
@extend_schema(
    request=CustomerProfileSerializer,
    responses={"200": "Profile completed successfully", "400": "Invalid data"}
)
class CompleteCustomerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        """
        Return the current profile data (if any) for the user to edit.
        """
        # Fetch the user by user_id (should match the authenticated user)
        try:
            user = MyUser.objects.get(id=user_id)
            if user != request.user:
                return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

            # Fetch associated customer profile if it exists
            customer_profile = Customer.objects.filter(user=user).first()

            # Return current profile data or an empty form for completion
            profile_data = {
                "first_name": customer_profile.first_name if customer_profile else "",
                "last_name": customer_profile.last_name if customer_profile else "",
                "meli_code": customer_profile.meli_code if customer_profile else "",
                "address1": customer_profile.address1 if customer_profile else "",
                "address2": customer_profile.address2 if customer_profile else "",
                "city": customer_profile.city if customer_profile else "",
                "zipcode": customer_profile.zipcode if customer_profile else "",
                "date_of_birth": customer_profile.date_of_birth if customer_profile else ""
            }
            
            return Response({
                "message": "Complete your profile",
                "profile_data": profile_data
            }, status=status.HTTP_200_OK)
        
        except MyUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, user_id):
        """
        Complete the user's profile with the provided data.
        """
        # Fetch the user by user_id (should match the authenticated user)
        try:
            user = MyUser.objects.get(id=user_id)
            if user != request.user:
                return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

            # Use the CustomerProfileSerializer to validate the incoming data
            serializer = CustomerProfileSerializer(data=request.data)
            if serializer.is_valid():
                # Create or update the associated customer profile
                customer_profile, created = Customer.objects.get_or_create(user=user)
                customer_profile.first_name = serializer.validated_data['first_name']
                customer_profile.last_name = serializer.validated_data['last_name']
                customer_profile.meli_code = serializer.validated_data['meli_code']
                customer_profile.address1 = serializer.validated_data['address1']
                customer_profile.address2 = serializer.validated_data['address2']
                customer_profile.city = serializer.validated_data['city']
                customer_profile.zipcode = serializer.validated_data['zipcode']
                customer_profile.date_of_birth = serializer.validated_data['date_of_birth']
                customer_profile.save()

                return Response({"message": "Profile completed successfully"}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except MyUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    

# -----------------------------------------------------------------------------------------------

# Complete Profile for Seller
@extend_schema(
    request=SellerProfileSerializer,
    responses={"200": "Profile completed successfully", "400": "Invalid data"}
)
class CompleteSellerProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, user_id):
        user = MyUser.objects.get(id=user_id, is_seller=True)
        serializer = SellerProfileSerializer(data=request.data)
        if serializer.is_valid():
            Seller.objects.create(user=user, **serializer.validated_data)
            return Response({"message": "Seller profile completed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------------------------------------------------------------------------

# Customer dashboard
@extend_schema(
    responses=DashboardSerializer,
)
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


# -----------------------------------------------------------------------------------------------

# Seller dashboard
@extend_schema(
    responses=DashboardSerializer,
)
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

# -----------------------------------------------------------------------------------------------

# Login
@extend_schema(
    request=LoginSerializer,
    responses={"200": "Login successful", "400": "Invalid credentials"}
)



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

# Logout
@extend_schema(
    request=None,
    responses={"200": "Logged out successfully", "400": "Failed to logout"}
)
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



