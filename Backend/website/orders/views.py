from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Order, OrderItem, CartItem, Notification
from .serializers import OrderSerializer, CartItemSerializer, NotificationSerializer
from users.models import MyUser

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user, ordered=False)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Item removed from cart"}, status=status.HTTP_204_NO_CONTENT)

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

