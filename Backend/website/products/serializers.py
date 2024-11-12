from rest_framework import serializers, generics, permissions
from .models import Product, Category, ProductImage, Review, Brand


class CategorySerializer(serializers.ModelSerializer):

    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'children', 'icon', 'image',]

    def get_children(self, obj):
        return CategorySerializer(obj.children, many=True).data

#---------------------------------------------------------------------------

class ProductImageSerializer(serializers.ModelSerializer):

    image_url = serializers.ImageField(source='image', read_only=True)

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

#---------------------------------------------------------------------------

class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'comment', 'created_at']


#---------------------------------------------------------------------------

class ProductSerializer(serializers.ModelSerializer):

    images = ProductImageSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()  
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'seller', 'category', 'name', 'description', 'price', 'stock',
            'image', 'date_added', 'average_rating', 'total_ratings', 'in_sale', 
            'sale_price', 'images', 'reviews', 'image_url'
        ]
        
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

    def validate(self, data):
        if data.get("in_sale") and data.get("sale_price") >= data.get("price"):
            raise serializers.ValidationError("Sale price must be less than the original price.")
        return data
#---------------------------------------------------------------------------

class BrandSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()  

    class Meta:
        model = Brand 
        fields = ['image_url', 'name', 'image']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None