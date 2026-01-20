from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import RegisterView, LoginView, MeView, LogoutView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('token/', LoginView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('token/verify/', TokenVerifyView.as_view()),
    path('me/', MeView.as_view()),
    path('logout/', LogoutView.as_view()),
]