from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions\
# documentation
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.documentation import include_docs_urls

# schema_view = get_schema_view(
#    openapi.Info(
#       title="Your API Title",
#       default_version='v1',
#       description="Test description",
#       terms_of_service="https://www.google.com/policies/terms/",
#       contact=openapi.Contact(email="contact@yourapi.local"),
#       license=openapi.License(name="BSD License"),
#    ),
#    public=True,
#    permission_classes=(permissions.AllowAny,),
# )

urlpatterns = [
   path('admin/', admin.site.urls),
   path('api/users/', include('users.urls')),
   path('api/products/', include('products.urls')),
   path('api/orders/', include('orders.urls')),
   path('api/cart/', include('cart.urls')),
   path('api/seller/', include('seller_panel.urls')),
#  path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
#  path('docs/', include_docs_urls(title='API Documentation')),


]