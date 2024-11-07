from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterCustomerView, RegisterSellerView, VerifyOTPView, 
    LoginView, LogoutView, CustomerDashboardView, SellerDashboardView, CompleteCustomerProfileView,
    CompleteSellerProfileView, 
)



urlpatterns = [
   
    path('register/customer/', RegisterCustomerView.as_view(), name='register_customer'),
    path('register/seller/', RegisterSellerView.as_view(), name='register_seller'),
    path('verify-otp/<str:user_type>/', VerifyOTPView.as_view(), name='verify-otp'),
    path('profile/customer/<int:user_id>/', CompleteCustomerProfileView.as_view(), name='complete_customer_profile'),
    path('profile/seller/<int:user_id>/', CompleteSellerProfileView.as_view(), name='complete_seller_profile'),
    path('dashboard/customer/', CustomerDashboardView.as_view(), name='customer_dashboard'),
    path('dashboard/seller/', SellerDashboardView.as_view(), name='seller_dashboard'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    
    # token
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
