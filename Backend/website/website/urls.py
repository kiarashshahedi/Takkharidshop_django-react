from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# documentation with spectacular package
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
   path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
   path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
   path('admin/', admin.site.urls),
   path('api/users/', include('users.urls')),
   path('api/products/', include('products.urls')),
   path('api/orders/', include('orders.urls')),
   path('api/seller/', include('seller_panel.urls')),


   # docs
   path('api/schema/', SpectacularAPIView.as_view(), name="schema"),
   path('api/schema/docs', SpectacularSwaggerView.as_view(url_name='schema')),



]