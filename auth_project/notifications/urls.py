from django.urls import path
from .views import SendMultipleEmailAPIView, SendOTPAPIView, VerifyMultipleOTPAPIView

urlpatterns = [
    path("send-otp/", SendOTPAPIView.as_view(), name="send-otp"),
    path("otp/verify-multiple/", VerifyMultipleOTPAPIView.as_view(), name="verify-multiple-otp"),
    path("send/", SendMultipleEmailAPIView.as_view(), name="send-multiple-email"),
]
