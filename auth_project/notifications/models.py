# notifications/models.py
from django.db import models
import uuid

class ServiceApiKey(models.Model):
    name = models.CharField(max_length=100)  # eg: order-service
    key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_active = models.BooleanField(default=True)

    rate_limit_per_minute = models.IntegerField(default=60)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"
