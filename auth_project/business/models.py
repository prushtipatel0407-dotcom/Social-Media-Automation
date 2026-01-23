from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class BusinessProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="business"
    )

    business_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)

    website = models.URLField(blank=True, null=True)

    # Address (structured)
    building_name = models.CharField(max_length=255, blank=True)
    street = models.CharField(max_length=255)
    area = models.CharField(max_length=255, blank=True)

    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)

    timezone = models.CharField(max_length=50, default="UTC")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.business_name
