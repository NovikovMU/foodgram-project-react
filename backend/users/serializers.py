from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField()

    class Meta:
        model = User
        fields = (User.USERNAME_FIELD, 'id') + tuple(User.REQUIRED_FIELDS)

    def create(self, validated_data):
        validated_data.pop('is_subscribed')
        return User.objects.create(**validated_data)