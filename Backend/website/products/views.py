from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Product, Category, ProductImage, Review
from .serializers import ProductSerializer, CategorySerializer, ReviewSerializer, ProductImageSerializer

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# Seller add-update-remove products
class AddProductView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if not self.request.user.is_seller:
            raise PermissionError("Only sellers can add products.")
        serializer.save(seller=self.request.user)

class ProductUpdateView(generics.UpdateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Ensure the user can only update their own products
        return Product.objects.filter(seller=self.request.user)

class ProductDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Ensure the user can only delete their own products
        return Product.objects.filter(seller=self.request.user)

class AddReviewView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        product_id = self.kwargs['pk']
        product = Product.objects.get(pk=product_id)
        serializer.save(user=self.request.user, product=product)
        product.update_ratings()

class AddProductImageView(generics.CreateAPIView):
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        product_id = self.kwargs['pk']
        product = Product.objects.get(pk=product_id)
        serializer.save(product=product)

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(parent=None) 
    serializer_class = CategorySerializer