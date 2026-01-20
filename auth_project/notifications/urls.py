# notifications/urls.py
from django.urls import path

from accounts import views
from .views import SendEmailView

urlpatterns = [
    path("email/", SendEmailView.as_view()),
     path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
]
