from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail

from .utils import generate_otp, store_otp, verify_otp, can_send_otp
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

        results = []

        for email in serializer.validated_data["emails"]:
            if not can_send_otp(email):
                results.append({
                    "email": email,
                    "status": "blocked",
                    "message": "Wait 1 minute before requesting OTP again"
                })
                continue

            otp = generate_otp()
            store_otp(email, otp)

            send_mail(
                subject="Your OTP Code",
                message=f"Your OTP is {otp}. It expires in 5 minutes.",
                from_email=None,
                recipient_list=[email],
                fail_silently=False,
            )

            results.append({
                "email": email,
                "status": "sent"
            })

        return Response({
            "results": results
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
