# accounts/views.py

from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

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