from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    """
    Read JWT from HTTP-only cookie instead of Authorization header
    """
    def authenticate(self, request):
        # Try header first (normal behavior)
        header = self.get_header(request)
        if header is not None:
            return super().authenticate(request)

        # 🔹 If no header, try cookie
        raw_token = request.COOKIES.get("access")

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token