from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    CustomerRegisterLoginView, VerifyCustomerOTPView, CompleteCustomerProfileView,
    SellerRegisterView, CompleteSellerProfileView, SellerLoginView, LogoutView
)



urlpatterns = [
   
    # Customer URLs
    path('customers/register-login/', CustomerRegisterLoginView.as_view(), name='customer_register_login'),
    path('customers/verify-otp/', VerifyCustomerOTPView.as_view(), name='verify_customer_otp'),
    path('customers/complete-profile/', CompleteCustomerProfileView.as_view(), name='complete_customer_profile'),

    # Seller URLs
    path('sellers/register/', SellerRegisterView.as_view(), name='seller_register'),
    path('sellers/complete-profile/', CompleteSellerProfileView.as_view(), name='complete_seller_profile'),
    path('sellers/login/', SellerLoginView.as_view(), name='seller_login'),
    
    # Logout
    path('logout/', LogoutView.as_view(), name='logout'),

    # token
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
