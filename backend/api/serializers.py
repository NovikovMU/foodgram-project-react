from rest_framework import serializers

from users.models import User
from foods.models import Receipt, Tag, Ingridient


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + ('id',)
        # fields = (
        #     'email',
        #     'id',
        #     'username',
        #     'first_name',
        #     'last_name',
        #     'is_subscribed'
        # )
