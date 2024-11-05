from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

# Tokens
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import MyUser, Customer, Seller
from products.models import Product
from products.serializers import ProductSerializer


# serializer
from .serializers import (
    CustomerRegisterSerializer, SellerRegisterSerializer, CustomerProfileSerializer, 
    SellerProfileSerializer, OTPSerializer, LoginSerializer
)

# Customer Registration
class RegisterCustomerView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            user, created = MyUser.objects.get_or_create(mobile=mobile, is_customer=True)
            user.generate_otp()
            return Response({"message": "OTP sent to mobile"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Seller Registration
class RegisterSellerView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SellerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            user, created = MyUser.objects.get_or_create(mobile=mobile, is_seller=True)
            user.generate_otp()
            return Response({"message": "OTP sent to mobile"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Verify OTP
class VerifyOTPView(APIView):
    def post(self, request, user_type):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            otp = serializer.validated_data['otp']
            try:
                user = MyUser.objects.get(mobile=mobile, otp=otp)
                user.is_verified = True
                user.save()
                login(request, user)

                if user.is_seller:
                    return Response({"message": "Complete seller profile", "user_id": user.id}, status=status.HTTP_202_ACCEPTED)
                return Response({"message": "Complete customer profile", "user_id": user.id}, status=status.HTTP_202_ACCEPTED)
            except MyUser.DoesNotExist:
                return Response({"error": "Invalid OTP or mobile"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Complete Profile for Customer
class CompleteCustomerProfileView(APIView):
    def post(self, request, user_id):
        user = MyUser.objects.get(id=user_id, is_customer=True)
        serializer = CustomerProfileSerializer(data=request.data)
        if serializer.is_valid():
            Customer.objects.create(user=user, **serializer.validated_data)
            return Response({"message": "Customer profile completed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Complete Profile for Seller
class CompleteSellerProfileView(APIView):
    def post(self, request, user_id):
        user = MyUser.objects.get(id=user_id, is_seller=True)
        serializer = SellerProfileSerializer(data=request.data)
        if serializer.is_valid():
            Seller.objects.create(user=user, **serializer.validated_data)
            return Response({"message": "Seller profile completed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Customer dashboard
class CustomerDashboardView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        customer = request.user.customer_profile
        orders = []  # Fetch customer orders here
        return Response({
            "customer_info": CustomerProfileSerializer(customer).data,
            "orders": orders,
        })

# Seller dashboard
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

# Login
class LoginView(APIView):
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

# Logout
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
