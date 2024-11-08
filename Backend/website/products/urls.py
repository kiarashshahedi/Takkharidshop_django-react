from django.urls import path
from .views import (
    ProductListView, ProductDetailView, AddProductView, 
    CategoryListView, ProductUpdateView, ProductDeleteView,
    BrandListView,
)

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/create/', AddProductView.as_view(), name='add_product'),
    path('<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('Brand/', BrandListView.as_view(), name='Brand_list'),

]
