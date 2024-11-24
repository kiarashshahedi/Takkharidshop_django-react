from django.conf import settings
from django.core.exceptions import PermissionDenied

# Check api key 
class APIKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Allow OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return self.get_response(request)
        
        # Check for API key in headers
        api_key = request.headers.get("X-API-KEY")
        if api_key != settings.API_KEY:
            raise PermissionDenied("Invalid API Key")
        
        return self.get_response(request)

# def authenticate(self, request):
#     auth = get_authorization_header(request).split()
#     print(f"Authorization Header: {auth}")