# accounts/views.py
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
# accounts/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache
from .utils import generate_otp, send_otp_email  # make sure utils.py exists

@api_view(['POST'])
def send_otp(request):
    email = request.data.get('email')
    if not email:
        return Response({"error": "Email is required"}, status=400)

    otp = generate_otp()
    cache.set(email, otp, timeout=300)  # 5 min expiry
    send_otp_email(email, otp)

    return Response({"message": "OTP sent successfully"})


@api_view(['POST'])
def verify_otp(request):
    email = request.data.get('email')
    user_otp = request.data.get('otp')

    if not email or not user_otp:
        return Response({"error": "Email and OTP required"}, status=400)

    stored_otp = cache.get(email)
    if stored_otp == user_otp:
        cache.delete(email)  # OTP used once
        return Response({"message": "OTP verified successfully"})
    return Response({"error": "Invalid or expired OTP"}, status=400)

from .serializers import (
    RegisterSerializer,
    UserSerializer,
    EmailUsernameTokenSerializer,
)

# -------------------------
# POST /api/auth/register/
# -------------------------
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


# -------------------------
# POST /api/auth/token/
# -------------------------
class LoginView(TokenObtainPairView):
    serializer_class = EmailUsernameTokenSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        access = response.data.get("access")
        refresh = response.data.get("refresh")

        response.set_cookie(
            key="access",
            value=access,
            httponly=True,
            samesite="Lax",
        )
        response.set_cookie(
            key="refresh",
            value=refresh,
            httponly=True,
            samesite="Lax",
        )
        return response


# -------------------------
# POST /api/auth/token/refresh/
# -------------------------
class RefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh = request.COOKIES.get("refresh")

        if not refresh:
            return Response(
                {"detail": "Refresh token not found"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            token = RefreshToken(refresh)
            access = token.access_token
        except TokenError:
            return Response(
                {"detail": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        response = Response({"access": str(access)})
        response.set_cookie(
            key="access",
            value=str(access),
            httponly=True,
            samesite="Lax",
        )
        return response


# -------------------------
# POST /api/auth/logout/
# -------------------------
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        response = Response(
            {"detail": "Successfully logged out"},
            status=status.HTTP_200_OK,
        )
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        return response


# -------------------------
# GET /api/auth/me/
# -------------------------
class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(
            UserSerializer(request.user).data,
            status=status.HTTP_200_OK,
        )