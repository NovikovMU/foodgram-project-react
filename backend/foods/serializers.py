from rest_framework import serializers

from .models import Ingredients, Receipts, ReceiptsIngredients, Tags
from users.serializers import UserSerializer

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')



class ReceiptsIngredientsReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredients.id')
    name = serializers.CharField(source='ingredients.name')
    measurement_unit = serializers.CharField(source='ingredients.measurement_unit')
    class Meta:
        model = ReceiptsIngredients
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class ReceiptReadSerializer(serializers.ModelSerializer):
    ingredients = ReceiptsIngredientsReadSerializer(
                  
        many=True,
        source = 'ingredients_used'
    )
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    class Meta:
        model = Receipts
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class ReceiptsM2MIngredients(serializers.ModelSerializer):
    # id = serializers.PrimaryKeyRelatedField(
    #     queryset=Ingredients.objects.all())
    id = serializers.IntegerField(source='ingredients.id')
    name = serializers.CharField(source='ingredients.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredients.measurement_unit', read_only=True)
    class Meta:
        model = ReceiptsIngredients
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class ReceiptsCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = ReceiptsM2MIngredients(
        many=True,
        source='ingredients_used'
    )
    # tags = TagSerializer(
    #     many=True,
    #     source='tags_used'
    # )
    
    class Meta:
        model = Receipts
        fields = (
            'id',
            'ingredients',
            # 'tags',
            # 'image',
            'name',
            'text',
            'cooking_time'
        )
    
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients_used')
        author = self.context['request'].user
        validated_data.update(author=author)
        receipt = Receipts.objects.create(**validated_data)
        for ingredient in ingredients:
            ingredients = ingredient.get('ingredients')
            id = ingredients.get('id')
            amount = ingredient.get('amount')
            receipt.ingredients.add(id, through_defaults={'amount':amount})
        return receipt
