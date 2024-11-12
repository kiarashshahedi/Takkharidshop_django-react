from django.urls import path
from .views import (
    ProductListView, ProductDetailView, AddProductView, 
    CategoryListView, ProductUpdateView, ProductDeleteView,
    BrandListView, ProductRetrieveUpdateDestroyView, ProductListCreateView,
    SaleProductListView,
)

urlpatterns = [
    
    # product list 
    path('products/', ProductListView.as_view(), name='product_list'),
    # product detail
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    # sale products box
    path('products/on-sale/', SaleProductListView.as_view(), name='products_on_sale'),

    # create - update - delete products for sellers
    path('products/create/', AddProductView.as_view(), name='add_product'),
    path('<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),

    # category list
    path('categories/', CategoryListView.as_view(), name='category_list'),
    # brand list
    path('Brand/', BrandListView.as_view(), name='Brand_list'),

    # additional
    path('products/<int:pk>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-detail'),
    path('products/List/', ProductListCreateView.as_view(), name='product-list-create'),


]
