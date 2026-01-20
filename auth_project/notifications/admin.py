from django.contrib import admin
from .models import ServiceApiKey

@admin.register(ServiceApiKey)
class ServiceApiKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "key", "is_active", "rate_limit_per_minute", "created_at")
    readonly_fields = ("key",)
