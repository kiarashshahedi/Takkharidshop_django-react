from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Order, OrderItem, Notification
from .serializers import OrderSerializer, NotificationSerializer
from cart.models import CartItem

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        customer_profile = user.customer_profile
        cart_items = CartItem.objects.filter(user=user, ordered=False)

        if not cart_items.exists():
            return Response({"error": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        order = Order.objects.create(
            user=user, 
            total_amount=total_amount,
            shipping_address=f"{customer_profile.address1}, {customer_profile.address2}",
            city=customer_profile.city,
            zipcode=customer_profile.zipcode
        )

        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            cart_item.ordered = True
            cart_item.save()

            seller = cart_item.product.seller
            Notification.objects.create(
                user=seller.user,
                message=f"New order for product '{cart_item.product.name}' with quantity {cart_item.quantity}. Shipping to {order.shipping_address}, {order.city}, {order.zipcode}."
            )

        CartItem.objects.filter(user=user, ordered=True).delete()
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

