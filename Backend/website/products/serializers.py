from rest_framework import serializers
from .models import Product, Category, ProductImage, Review

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'comment', 'created_at']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'seller', 'category', 'name', 'description', 'price', 'stock',
            'image', 'date_added', 'average_rating', 'total_ratings', 'in_sale', 
            'sale_price', 'images', 'reviews'
        ]

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'children']

    def get_children(self, obj):
        return CategorySerializer(obj.children, many=True).data
