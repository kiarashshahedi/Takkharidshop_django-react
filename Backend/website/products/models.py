from django.db import models
from users.models import MyUser
from website import settings
import datetime
from mptt.models import MPTTModel, TreeForeignKey
from django.db.models import Avg


#--------------------------------------------------------------------------------------------------------

class Category(MPTTModel):
    name = models.CharField(max_length=100)
    parent = TreeForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name='children')
    icon = models.ImageField(upload_to='category_icons/', null=True, blank=True)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    
    class MPTTMeta:
        verbose_name_plural = "Categories"
        order_insertion_by = ["name"]

    def __str__(self):
        return self.name

#--------------------------------------------------------------------------------------------------------

class Brand(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='brand_images/', blank=True, null=True)

    def __str__(self):
        return self.name

#--------------------------------------------------------------------------------------------------------

class Product(models.Model):

    seller = models.ForeignKey('users.MyUser', on_delete=models.CASCADE, related_name='products')
    category = TreeForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    sold_quantity = models.PositiveIntegerField(default=0)  # New field to track sold quantity
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)  # Only auto_now_add=True
    average_rating = models.FloatField(default=0.0)
    total_ratings = models.IntegerField(default=0)
    # adding sale 
    in_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0, max_digits=9, decimal_places=3)    
    icon = models.ImageField(upload_to='product_icons/', blank=True, null=True)  # Optional icon field

    def update_ratings(self):
        reviews = self.reviews.exclude(rating__isnull=True)
        self.total_ratings = reviews.count()
        self.average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        self.save()
    
    def total_orders(self):
        return self.order_set.filter(status=True).count()

    def __str__(self):
        return f"{self.name} - {self.seller}"

#--------------------------------------------------------------------------------------------------------

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image of {self.product.name}"
    
#--------------------------------------------------------------------------------------------------------

#the rate of the product
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(null=True, blank=True)  # Rating (1 to 5 stars)
    comment = models.TextField(null=True, blank=True)  # Comment text
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')


    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username}"