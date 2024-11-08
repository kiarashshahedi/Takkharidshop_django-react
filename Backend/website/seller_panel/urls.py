from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SellerProductViewSet, SellerOrderViewSet, SellerNotificationViewSet

router = DefaultRouter()
router.register(r'seller/products', SellerProductViewSet, basename='seller-products'),
router.register(r'seller/orders', SellerOrderViewSet, basename='seller-orders'),
router.register(r'seller/notifications', SellerNotificationViewSet, basename='seller-notifications')


urlpatterns = [
    path('', include(router.urls)),
]
