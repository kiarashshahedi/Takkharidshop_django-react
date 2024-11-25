from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from products.models import Product
from orders.models import Order, Notification
from payments.models import Payment
from django.shortcuts import get_object_or_404


from .serializers import (
    LastOrdersSerializer, 
    LastPaymentsSerializer, 
    NotificationsSerializer, 
    ProductSerializer,
    RevenueSummarySerializer
)
from django.db.models import Sum, F

# Customer Views
class CustomerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.is_customer:
            return Response({"error": "Not a customer"}, status=403)
        return Response({
            "last_orders": "/api/customers/orders/",
            "last_payments": "/api/customers/payments/",
            "notifications": "/api/customers/notifications/",
            "chat_support": "/api/customers/chat-support/"
        })

class LastOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        orders = Order.objects.filter(customer=user).order_by('-date_created')[:5]
        return Response(LastOrdersSerializer(orders, many=True).data)

class LastPaymentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        payments = Payment.objects.filter(customer=user).order_by('-date')[:5]
        return Response(LastPaymentsSerializer(payments, many=True).data)

class NotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        notifications = Notification.objects.filter(user=user).order_by('-date')[:10]
        return Response(NotificationsSerializer(notifications, many=True).data)

class ChatSupportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Chat system integration placeholder"})

# Seller Views
class SellerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.is_seller:
            return Response({"error": "Not a seller"}, status=403)
        return Response({
            "product_management": "/api/sellers/products/",
            "revenue_summary": "/api/sellers/revenue-summary/"
        })

class ProductManagementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        products = Product.objects.filter(seller=user)
        return Response(ProductSerializer(products, many=True).data)

    def post(self, request):
        user = request.user
        data = request.data
        data['seller'] = user.id
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        user = request.user
        product = get_object_or_404(Product, id=pk, seller=user)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        user = request.user
        product = Product.objects.get(id=pk, seller=user)
        product.delete()
        return Response({"message": "Product deleted successfully"})

class RevenueSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.is_seller:
            return Response({"error": "Not a seller"}, status=403)

        revenue = Product.objects.filter(seller=user).aggregate(
            total_revenue=Sum(F('price') * F('sold_quantity'))
        )

        return Response({"total_revenue": revenue['total_revenue'] or 0})