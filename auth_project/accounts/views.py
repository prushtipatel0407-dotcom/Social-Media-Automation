from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, LoginSerializer
from .utils import generate_otp, store_otp, can_send_otp, verify_otp, create_reset_token, can_request_reset, send_email, verify_reset_token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.password_validation import validate_password
User = get_user_model()
from rest_framework_simplejwt.views import TokenObtainPairView

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer

User = get_user_model()


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone_number": getattr(user, "phone_number", ""),
            "access": str(access),
            "refresh": str(refresh)
        })



# ---------------------------
# Register + send OTP
# ---------------------------
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        if can_send_otp(user.email):
            otp = generate_otp()
            store_otp(user.email, otp)
            send_email(
                "Verify Your Account",
                f"Your OTP is {otp}. Expires in 5 minutes.",
                [user.email]
            )

# ---------------------------
# Verify OTP
# ---------------------------
class VerifyOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        is_valid, message = verify_otp(email, otp)
        if is_valid:
            try:
                user = User.objects.get(email=email)
                user.is_verified = True
                user.save()
            except User.DoesNotExist:
                return Response({"message": "User not found"}, status=404)
            return Response({"message": "OTP verified"})
        return Response({"message": message}, status=400)

# ---------------------------
# Password Reset Request
# ---------------------------
class ForgotPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email").lower()
        if not can_request_reset(email):
            return Response({"message": "Reset already requested, wait 1 minute"}, status=429)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "If email exists, reset link sent"})
        token = create_reset_token(email)
        reset_link = f"http://127.0.0.1:8000/static/reset-password/reset-password.html?token={token}"
        send_email("Reset Password", f"Reset link: {reset_link}", [email])
        return Response({"message": "Reset link sent"})

# ---------------------------
# Reset Password
# ---------------------------


class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        password = request.data.get("new_password")

        if not token or not password:
            return Response({"message": "Token and password required"}, status=400)

        email = verify_reset_token(token)
        if not email:
            return Response({"message": "Invalid or expired token"}, status=400)

        try:
            user = User.objects.get(email=email)
            validate_password(password, user)
            user.set_password(password)
            user.save()
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=404)
        except Exception as e:
            return Response({"message": str(e)}, status=400)

        return Response({"message": "Password reset successful"})



# ---------------------------
# Login
# ---------------------------
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        response = Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone_number": getattr(user, "phone_number", ""),
            "access": str(access),
            "refresh": str(refresh)
        })

        # Set cookies (optional, for web)
        response.set_cookie("access", str(access), httponly=True, samesite="Lax")
        response.set_cookie("refresh", str(refresh), httponly=True, samesite="Lax")

        return response

# ---------------------------
# MeView - current user info
# ---------------------------
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone_number": getattr(user, "phone_number", ""),
        })

# ---------------------------
# LogoutView - delete tokens
# ---------------------------
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({"detail": "Successfully logged out"}, status=200)
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        return response