# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model.
    Django automatically creates:
    - id (BigAutoField)
    - primary key
    - unique constraint
    """

    # Explicit ID field (OPTIONAL but clear)
    id = models.BigAutoField(primary_key=True)

    email = models.EmailField(
        unique=True,
        null=False,
        blank=False
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username