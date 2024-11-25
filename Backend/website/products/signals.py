from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order

@receiver(post_save, sender=Order)
def update_sold_quantity(sender, instance, **kwargs):
    if instance.status == "Completed":  # Check if the order is completed
        for item in instance.items.all():
            product = item.product
            product.sold_quantity += item.quantity  # Increment sold quantity
            product.save()
