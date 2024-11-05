from django.db import models
from users.models import MyUser
from website import settings
import datetime

class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Product(models.Model):

    seller = models.ForeignKey('users.MyUser', on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)  # Only auto_now_add=True
    average_rating = models.FloatField(default=0.0)
    total_ratings = models.IntegerField(default=0)
    # adding sale 
    in_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0, max_digits=9, decimal_places=3)    

    def update_ratings(self):
        reviews = self.reviews.all()
        total_ratings = reviews.count()
        if total_ratings > 0:
            sum_ratings = sum(review.rating for review in reviews if review.rating is not None)
            self.average_rating = sum_ratings / total_ratings
        else:
            self.average_rating = 0.0
        self.total_ratings = total_ratings
        self.save()
    
    def total_orders(self):
        return self.order_set.filter(status=True).count()

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image of {self.product.name}"
    

#the rate of the product
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(null=True, blank=True)  # Rating (1 to 5 stars)
    comment = models.TextField(null=True, blank=True)  # Comment text
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = []


    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username}"