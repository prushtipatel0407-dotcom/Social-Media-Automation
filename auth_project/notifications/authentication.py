# notifications/authentication.py
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import ServiceApiKey

class ApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get("X-API-KEY")

        if not api_key:
            raise AuthenticationFailed("API key missing")

        try:
            service = ServiceApiKey.objects.get(key=api_key, is_active=True)
        except ServiceApiKey.DoesNotExist:
            raise AuthenticationFailed("Invalid API key")

        return (service, None)
