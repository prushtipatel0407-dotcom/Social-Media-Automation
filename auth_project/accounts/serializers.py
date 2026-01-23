from django.utils import timezone
from datetime import timedelta
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
import re
import phonenumbers
import pycountry
from django.contrib.auth import get_user_model

User = get_user_model()

# ---------------------------
# Login Serializer
# ---------------------------
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email").lower()
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials")

        attrs["user"] = user
        return attrs



# ---------------------------
# Register Serializer
# ---------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    phone_number = serializers.CharField(min_length=6, max_length=16)
    country_code = serializers.CharField(write_only=True)  
    terms_accepted = serializers.BooleanField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username", "email", "phone_number", 
            "password", "confirm_password", "country_code","terms_accepted",
        ]

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_phone_number(self, value):
        try:
            phone_obj = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(phone_obj):
                raise serializers.ValidationError("Invalid phone number")
            return phonenumbers.format_number(
                phone_obj, phonenumbers.PhoneNumberFormat.E164
            )
        except phonenumbers.NumberParseException:
            raise serializers.ValidationError("Invalid phone number format")

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("Must contain an uppercase letter")
        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError("Must contain a lowercase letter")
        if not re.search(r"\d", value):
            raise serializers.ValidationError("Must contain a digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError("Must contain a special character")
        validate_password(value)
        return value

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
          #  Terms check
        if not data.get("terms_accepted"):
         raise serializers.ValidationError({
            "terms_accepted": "You must accept Terms & Conditions"
        })

        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        terms_accepted = validated_data.pop("terms_accepted")
        
        iso_code = validated_data.pop("country_code", None)
        country_name = None
        if iso_code:
            country_obj = pycountry.countries.get(alpha_2=iso_code)
            country_name = country_obj.name if country_obj else None

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"].lower(),
            password=validated_data["password"],
            phone_number=validated_data["phone_number"],
            country_code=iso_code,
            country_name=country_name,
            is_verified=False,
            terms_accepted=terms_accepted,
            terms_accepted_at=timezone.now(),
        )
        return user
