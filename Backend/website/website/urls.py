from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions\
# documentation
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.documentation import include_docs_urls
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
   path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
   path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
   path('admin/', admin.site.urls),
   path('api/users/', include('users.urls')),
   path('api/products/', include('products.urls')),
   path('api/orders/', include('orders.urls')),
   path('api/cart/', include('cart.urls')),
   path('api/seller/', include('seller_panel.urls')),

]