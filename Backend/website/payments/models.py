from django.db import models

from django.db import models
from orders.models import Order
from users.models import MyUser
from datetime import datetime


class Payment(models.Model):
    PAYMENT_METHODS = [
        ('Credit Card', 'Credit Card'),
        ('PayPal', 'PayPal'),
        ('Stripe', 'Stripe'),
        ('Bank Transfer', 'Bank Transfer'),
        ('COD', 'Cash on Delivery'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='payments')
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment #{self.id} - {self.status}"

    def mark_as_completed(self, transaction_id):
        self.status = 'Completed'
        self.transaction_id = transaction_id
        self.save()

    def mark_as_failed(self):
        self.status = 'Failed'
        self.save()
