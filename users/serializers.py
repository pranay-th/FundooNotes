from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'phone_number',
            'password'
        ]

        extra_kwargs = {
            'password':{'write_only': True}
        }

    def create(self,validated_data):

        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number']
        )

        user.set_password(validated_data['password'])

        user.save()

        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()

    password = serializers.CharField(write_only=True)

    def validate(self,data):
        username=data.get('username')
        password=data.get('password')

        user=authenticate(
            username=username,
            password=password
        )

        if not user:
            raise serializers.ValidationError(
                "Invalid Credentials"
            )

        refresh=RefreshToken.for_user(user)

        return{
            'refresh':str(refresh),
            'access':str(refresh.access_token),
        }