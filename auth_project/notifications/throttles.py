# notifications/throttles.py
from rest_framework.throttling import SimpleRateThrottle

# ---------------------------
# API Key Rate Throttle
# ---------------------------

class ApiKeyRateThrottle(SimpleRateThrottle):
    scope = "api_key"

    def get_cache_key(self, request, view):
        if not hasattr(request, "service"):
            return None
        return f"throttle_{request.service.key}"
