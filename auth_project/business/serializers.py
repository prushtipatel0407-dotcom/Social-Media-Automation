from rest_framework import serializers
from .models import BusinessProfile, BusinessCategory


class BusinessProfileSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    class Meta:
        model = BusinessProfile
        fields = [
            "id",
            "business_name",
            "category",
            "category_name",
            "website",
            "building_name",
            "street",
            "city",
            "state",
            "country",
            "created_at",
        ]
        read_only_fields = ("user",)
