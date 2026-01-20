from rest_framework import serializers, generics, permissions
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Q

from .models import User


# ----------------------------
# Serializers
# ----------------------------

class RegisterSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=128,
        validators=[
            RegexValidator(
                regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])',
                message=(
                    "Password must contain at least "
                    "1 uppercase, 1 lowercase, 1 number, "
                    "and 1 special character."
                )
            )
        ]
    )

    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']


    # ✅ Normalize + validate username
    def validate_username(self, value):
        value = value.strip()

        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already exists")

        return value

    # ✅ Normalize + validate email (CASE-INSENSITIVE)
    def validate_email(self, value):
        email = value.strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("Email already exists")

        return email

    # ✅ Ensure lowercase email is saved
    def create(self, validated_data):
        validated_data['email'] = validated_data['email'].lower()

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class EmailUsernameTokenSerializer(TokenObtainPairSerializer):
    """
    Login via username OR email (case-insensitive)
    """
    def validate(self, attrs):
        username_or_email = attrs.get("username").strip()
        password = attrs.get("password")

        # Try username first
        user = authenticate(
            request=self.context.get("request"),
            username=username_or_email,
            password=password
        )

        # Try email (case-insensitive)
        if not user:
            try:
                user_obj = User.objects.get(email__iexact=username_or_email)
                user = authenticate(
                    request=self.context.get("request"),
                    username=user_obj.username,
                    password=password
                )
            except User.DoesNotExist:
                pass

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        data = super().validate({
            "username": user.username,
            "password": password
        })
        return data


# ----------------------------
# Register View
# ----------------------------

class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint.

    Validates:
    - Case-insensitive unique username
    - Case-insensitive unique email
    - Strong password
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]