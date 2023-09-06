from rest_framework import serializers

from .models import Ingredients, Receipts, ReceiptIngridient, Tags


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')

class TagM2MSerializer(serializers.ModelSerializer):
    pass

class ReceiptReadSerializer(serializers.ModelSerializer):
    tags = TagM2MSerializer(
        many=True
    )
    class Meta:
        model = ReceiptIngridient
        fields = ('id', 'tags', 'author')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')