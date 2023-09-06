from rest_framework import serializers

from .models import Ingridients, Receipts, Tags


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')