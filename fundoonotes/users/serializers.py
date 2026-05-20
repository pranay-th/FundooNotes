from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        # id excluded — internal identifier, not shown to the user
        fields = ["username", "email", "phone_number", "password"]

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone_number(self, value: str) -> str:
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    def create(self, validated_data: dict) -> User:
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            phone_number=validated_data["phone_number"],
            is_verified=False,
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Step 1: validate credentials and trigger OTP dispatch."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data: dict) -> dict:
        from .services import initiate_login

        email = initiate_login(data["username"], data["password"])
        return {"email": email}


class OTPVerifySerializer(serializers.Serializer):
    """Step 2: verify the OTP and return JWT tokens."""

    username = serializers.CharField(help_text="The email address used to log in.")
    otp = serializers.CharField(max_length=6, min_length=6)

    def validate(self, data: dict) -> dict:
        from .services import verify_login_otp

        return verify_login_otp(data["username"], data["otp"])


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # id excluded — internal identifier, not shown to the user
        fields = ["username", "email", "phone_number", "is_verified"]
        read_only_fields = ["email", "is_verified"]


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data: dict) -> dict:
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data
