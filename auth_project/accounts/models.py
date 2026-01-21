# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=15,
        unique=False,   # ❌ Ensure this is False
        validators=[RegexValidator(
            regex=r'^\+?\d{10,15}$',
            message="Phone number must be 10-15 digits, optionally starting with +"
        )]
    )
    is_verified = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['email', 'phone_number']
    USERNAME_FIELD = 'username'
