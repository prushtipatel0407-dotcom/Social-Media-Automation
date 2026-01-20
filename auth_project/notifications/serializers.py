from rest_framework import serializers

class SendMultipleEmailSerializer(serializers.Serializer):
    emails = serializers.ListField(
        child=serializers.EmailField(),
        min_length=1
    )
    subject = serializers.CharField(max_length=255)
    message = serializers.CharField()



class SendOTPSerializer(serializers.Serializer):
    emails = serializers.ListField(
        child=serializers.EmailField(),
        min_length=1
    )


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

 # ---------------------------
# ✅ Verify MULTIPLE OTPs
# ---------------------------
class VerifyMultipleOTPSerializer(serializers.Serializer):
    otps = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        ),
        min_length=1
    )

    def validate_otps(self, value):
        for item in value:
            if "email" not in item or "otp" not in item:
                raise serializers.ValidationError(
                    "Each item must contain 'email' and 'otp'"
                )
        return value