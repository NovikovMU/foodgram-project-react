from djoser.serializers import UserSerializer as CustomUserSerializer
from rest_framework import serializers

from users.models import Follow, User


class UserSerializer(CustomUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        return (
            not self.context['request'].user.is_anonymous
            and Follow.objects.filter(
                user__follower__author=obj
            ).exists())

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
