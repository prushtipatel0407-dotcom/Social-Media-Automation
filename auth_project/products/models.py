from django.db import models
from business.models import BusinessProfile


class Product(models.Model):
    PRODUCT_TYPES = [
        ("product", "Product"),
        ("service", "Service"),
        ("digital", "Digital"),
    ]

    business = models.ForeignKey(
        BusinessProfile,
        on_delete=models.CASCADE,
        related_name="products"
    )

    name = models.CharField(max_length=255)
    description = models.TextField()

    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPES
    )

    target_audience = models.CharField(max_length=255)

    key_benefits = models.TextField(
        help_text="Comma separated benefits"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
