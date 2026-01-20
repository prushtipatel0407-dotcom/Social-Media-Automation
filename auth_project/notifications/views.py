from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .tasks import send_email_task
# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache
from .utils import generate_otp, send_otp_email

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

class SendEmailView(APIView):
    def post(self, request):
        to = request.data.get("to")
        subject = request.data.get("subject")
        message = request.data.get("message")

        if not to or not subject or not message:
            return Response(
                {"error": "to, subject, message required"},
                status=400
            )

        # 🔥 background task
        send_email_task.delay(subject, message, to)

        return Response(
            {"status": "Email queued"},
            status=status.HTTP_202_ACCEPTED
        )
