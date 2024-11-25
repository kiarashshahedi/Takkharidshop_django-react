from rest_framework import serializers
from products.models import Product
from orders.models import Order, Notification
from payments.models import Payment 

class LastOrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'product', 'quantity', 'total_price', 'date_created']

class LastPaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'date', 'status']

class NotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'date']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'sold_quantity', 'description']

class RevenueSummarySerializer(serializers.Serializer):
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
