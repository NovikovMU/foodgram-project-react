from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Ingredients, Favorites, Receipts, ReceiptsIngredients, Tags
from users.serializers import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')

class ReceiptFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipts
        fields = (
            'id',
            'name',
            # 'image',
            'cooking_time',
        )

        
class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorites
        fields = (
            'user',
            'receipts',
        )
    def validate(self, attrs):
        if Favorites.objects.filter(receipts=attrs.get('receipts'), user=attrs.get('user')).exists():
            raise serializers.ValidationError(
                {'error': 'Вы уже подписались на этот рецепт.'}
            )
        return super().validate(attrs)

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
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(), source='ingredients.id')
    # id = serializers.IntegerField(source='ingredients.id')
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
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tags.objects.all(),
    )
    
    class Meta:
        model = Receipts
        fields = (
            'id',
            'ingredients',
            'tags',
            # 'image',
            'name',
            'text',
            'cooking_time'
        )
    
    def create(self, validated_data):
        author = self.context['request'].user
        ingredients = validated_data.pop('ingredients_used')
        tags = validated_data.pop('tags')
        validated_data.update(author=author)
        receipt = Receipts.objects.create(**validated_data)
        for ingredient in ingredients:
            ingredients = ingredient.get('ingredients')
            id = ingredients.get('id')
            amount = ingredient.get('amount')
            receipt.ingredients.add(id, through_defaults={'amount':amount})
        for tag in tags:
            receipt.tags.add(tag)
        return receipt

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients_used')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        for ingredient in ingredients:
            ingredients = ingredient.get('ingredients')
            id = ingredients.get('id')
            amount = ingredient.get('amount')
            instance.ingredients.add(id, through_defaults={'amount':amount})
        instance.tags.clear()
        for tag in tags:
            instance.tags.add(tag)
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        return instance
    
    def to_representation(self, instance):
        obj = super(ReceiptsCreateUpdateSerializer, self).to_representation(instance)
        ids = obj.get('tags')
        all_trags = []
        for id in ids:
            tag = Tags.objects.get(id=id)
            dict_tag = {
                'id': tag.id,
                'name': tag.name,
                'color': tag.color,
                'slug': tag.slug
            }
            all_trags.append(dict_tag)
        obj['tags'] = all_trags
        return obj
