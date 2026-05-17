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