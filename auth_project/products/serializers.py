from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "product_type",
            "target_audience",
            "key_benefits",
            "created_at",
        ]
