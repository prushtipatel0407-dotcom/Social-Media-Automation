# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=16, blank=True, null=True)
    
    country_code = models.CharField(max_length=2, blank=True, null=True)  # ISO code
    country_name = models.CharField(max_length=50, blank=True, null=True) # Full name
    
    is_verified = models.BooleanField(default=False)
    auth_provider = models.CharField(
        max_length=20,
        choices=(("email", "Email"), ("google", "Google")),
        default="email"
    )

    REQUIRED_FIELDS = ['email', 'country_code', 'country_name']
    USERNAME_FIELD = 'username'
