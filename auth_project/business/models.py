from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class BusinessCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class BusinessProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="business"
    )

    business_name = models.CharField(max_length=255)

    category = models.ForeignKey(
        BusinessCategory,
        on_delete=models.PROTECT,
        related_name="businesses"
    )

    website = models.URLField(blank=True, null=True)

    building_name = models.CharField(max_length=255, blank=True)
    street = models.CharField(max_length=255)

    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.business_name
