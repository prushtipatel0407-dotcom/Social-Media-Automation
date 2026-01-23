from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from .utils import can_request_reset, send_email
from django.contrib.auth.password_validation import validate_password
from .serializers import RegisterSerializer, LoginSerializer


from .utils import (
    generate_otp,
    store_otp,
    can_send_otp,
    verify_otp,
    create_reset_token,
    verify_reset_token,
)
# views.py
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import RegisterSerializer
from .models import User


from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

User = get_user_model()

# ---------------------------
# Register + Send OTP
# ---------------------------

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        if can_send_otp(user.email):
            otp = generate_otp()
            store_otp(user.email, otp)
            user.email_user(
                subject="Verify Your Account",
                message=f"Your OTP is {otp}. Valid for 5 minutes."
            )

        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone_number": user.phone_number,
            "country_code": user.country_code,
            "country_name": user.country_name,
            "is_verified": user.is_verified
        }, status=status.HTTP_201_CREATED)



# ---------------------------
# Verify OTP
# ---------------------------
class VerifyOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        is_valid, message = verify_otp(email, otp)
        if not is_valid:
            return Response({"message": message}, status=400)

        try:
            user = User.objects.get(email=email)
            user.is_verified = True
            user.save()
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=404)

        return Response({"message": "OTP verified successfully"})


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

        response = Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone_number": user.phone_number,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })

        response.set_cookie("access", str(refresh.access_token), httponly=True)
        response.set_cookie("refresh", str(refresh), httponly=True)
        return response


# ---------------------------
# Logout
# ---------------------------
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({"detail": "Logged out successfully"})
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        return response


# ---------------------------
# Current User
# ---------------------------
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone_number": user.phone_number,
        })

# ---------------------------
# Reset Password
# ---------------------------
class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            token = request.data.get("token")
            new_password = request.data.get("new_password")

            if not token or not new_password:
                return Response(
                    {"message": "Token and new password required"},
                    status=400
                )

            # ❗ DO NOT DELETE TOKEN YET
            email = verify_reset_token(token)
            if not email:
                return Response(
                    {"message": "Invalid or expired token"},
                    status=400
                )

            user = User.objects.get(email=email)

            # Validate password
            validate_password(new_password, user)

            # Set password
            user.set_password(new_password)
            user.save()

            # DELETE TOKEN AFTER SUCCESS
            verify_reset_token(token, delete=True)

            return Response(
                {"message": "Password reset successful"},
                status=200
            )

        except User.DoesNotExist:
            return Response(
                {"message": "User not found"},
                status=404
            )

        except Exception as e:
            #  THIS IS WHAT CAUSED "Server error"
            return Response(
                {"message": str(e)},
                status=400
            )
# ---------------------------
# Forgot Password Reset Request
# ---------------------------
class ForgotPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email", "").lower()

        if not can_request_reset(email):
            return Response(
                {"message": "Reset already requested. Wait 1 minute"},
                status=429
            )

        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "If email exists, reset link sent"})

        token = create_reset_token(email)

        reset_link = (
            f"http://127.0.0.1:8000/static/reset-password/"
            f"reset-password.html?token={token}"
        )

        send_email(
            "Reset Password",
            f"Reset your password: {reset_link}",
            [email]
        )

        return Response({"message": "Reset link sent"})   
# ---------------------------
# Google Login
# ---------------------------
class GoogleLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")

        if not token:
            return Response({"message": "Google token required"}, status=400)

        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )

            if not idinfo.get("email_verified"):
                return Response({"message": "Email not verified"}, status=400)

            email = idinfo["email"].lower()
            name = idinfo.get("name", "")

            user, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": email.split("@")[0],
                    "first_name": name,
                    "is_verified": True,
                    "auth_provider": "google",
                }
            )

            refresh = RefreshToken.for_user(user)

            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            })

        except ValueError:
            return Response({"message": "Invalid Google token"}, status=400)
