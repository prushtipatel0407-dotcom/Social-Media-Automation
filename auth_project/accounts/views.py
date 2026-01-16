from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, UserSerializer


# POST /api/auth/register/
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


# POST /api/auth/token/
class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        access = response.data["access"]
        refresh = response.data["refresh"]

        response.set_cookie(
            key="access",
            value=access,
            httponly=True,
            samesite="Lax"
        )
        response.set_cookie(
            key="refresh",
            value=refresh,
            httponly=True,
            samesite="Lax"
        )

        return response


# POST /api/auth/token/refresh/
class RefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh = request.COOKIES.get("refresh")
        if not refresh:
            return Response({"error": "No refresh token"}, status=401)

        token = RefreshToken(refresh)
        access = token.access_token

        response = Response({"access": str(access)})
        response.set_cookie(
            key="access",
            value=str(access),
            httponly=True,
            samesite="Lax"
        )
        return response


# GET /api/auth/me/
class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
