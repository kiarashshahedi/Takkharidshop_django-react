from django.urls import path
from .views import (
    CustomerDashboardView, 
    LastOrdersView, 
    LastPaymentsView, 
    NotificationsView,
    ChatSupportView,
    SellerDashboardView, 
    ProductManagementView,
    RevenueSummaryView
)

urlpatterns = [
    # Customer dashboard
    path('customers/dashboard/', CustomerDashboardView.as_view(), name='customer_dashboard'),
    path('customers/orders/', LastOrdersView.as_view(), name='customer_orders'),
    path('customers/payments/', LastPaymentsView.as_view(), name='customer_payments'),
    path('customers/notifications/', NotificationsView.as_view(), name='customer_notifications'),
    path('customers/chat-support/', ChatSupportView.as_view(), name='customer_chat_support'),

    # Seller dashboard
    path('sellers/dashboard/', SellerDashboardView.as_view(), name='seller_dashboard'),
    path('sellers/products/', ProductManagementView.as_view(), name='product_management'),
    path('sellers/revenue-summary/', RevenueSummaryView.as_view(), name='revenue_summary'),
]
