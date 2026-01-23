from django.urls import path
from .views import BusinessProfileAPIView

urlpatterns = [
    path("profile/", BusinessProfileAPIView.as_view()),
]
