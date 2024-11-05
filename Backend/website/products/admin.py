from django.contrib import admin
from .models import Category, Product, Brand, Review, ProductImage



admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Review)
admin.site.register(ProductImage)