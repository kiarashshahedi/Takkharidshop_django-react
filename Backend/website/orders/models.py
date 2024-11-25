from django.db import models
from users.models import MyUser
from products.models import Product


class Order(models.Model):

    customer = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending')
    shipping_address = models.TextField()
    city = models.CharField(max_length=200)
    zipcode = models.CharField(max_length=10)

    def __str__(self):
        return f"Order {self.id} - {self.MyUser.mobile}"
    
    def complete_order(self):
        self.status = "Completed"
        self.save()
        for item in self.items.all():
            product = item.product
            product.sold_quantity += item.quantity
            product.save()

    def create_order_from_cart(self, cart):
        self.customer = cart.customer
        self.total_price = sum(item.total_price() for item in cart.items.all())
        self.save()
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=self,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
        cart.items.all().delete()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in order {self.order.id}"

class Notification(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}"
