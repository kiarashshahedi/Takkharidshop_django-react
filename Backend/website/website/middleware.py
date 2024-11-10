from django.conf import settings
from django.core.exceptions import PermissionDenied



# Check api key 
class APIKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check for API key in headers
        api_key = request.headers.get("X-API-KEY")
        if api_key != settings.API_KEY:
            raise PermissionDenied("Invalid API Key")
        return self.get_response(request)
