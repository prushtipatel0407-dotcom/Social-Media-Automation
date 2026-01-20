from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail

from .utils import generate_otp, store_otp, verify_otp
from .serializers import (
    SendOTPSerializer,
    VerifyOTPSerializer,
    SendMultipleEmailSerializer,
    VerifyMultipleOTPSerializer
)


class SendMultipleEmailAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendMultipleEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        send_mail(
            subject=serializer.validated_data["subject"],
            message=serializer.validated_data["message"],
            from_email=None,
            recipient_list=serializer.validated_data["emails"],
            fail_silently=False,
        )

        return Response({"message": "Emails sent successfully"})


class SendOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        emails = serializer.validated_data["emails"]
        sent = []

        for email in emails:
            otp = generate_otp()
            store_otp(email, otp)

            send_mail(
                subject="Your OTP Code",
                message=f"Your OTP is {otp}. It expires in 5 minutes.",
                from_email=None,
                recipient_list=[email],
                fail_silently=False,
            )

            sent.append(email)

        return Response({
            "message": "OTP sent successfully",
            "emails": sent
        })


class VerifyMultipleOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyMultipleOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        results = []

        for item in serializer.validated_data["otps"]:
            email = item["email"]
            otp = item["otp"]

            is_valid, message = verify_otp(email, otp)

            results.append({
                "email": email,
                "status": "success" if is_valid else "failed",
                "message": message
            })

        return Response({"results": results})
