# notifications/throttles.py
from rest_framework.throttling import SimpleRateThrottle

class ApiKeyRateThrottle(SimpleRateThrottle):
    scope = "api_key"

    def get_cache_key(self, request, view):
        api_key = request.headers.get("X-API-KEY")
        if not api_key:
            return None
        return f"throttle_api_key_{api_key}"
