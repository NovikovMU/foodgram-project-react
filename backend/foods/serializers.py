from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Ingredients, Favorites, Recipes, RecipesIngredients, Tags
from users.serializers import UserSerializer
from users.models import User


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class RecipesFavoriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Recipes
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
            'recipes',
        )
    def validate(self, attrs):
        if Favorites.objects.filter(recipes=attrs.get('recipes'), user=attrs.get('user')).exists():
            raise serializers.ValidationError(
                {'error': 'Вы уже подписались на этот рецепт.'}
            )
        return super().validate(attrs)

    def is_valid_on_delete(self, attrs):
        if not Favorites.objects.filter(recipes=attrs.get('recipes'), user=attrs.get('user')).exists():
            raise serializers.ValidationError(
                {'error': 'Вы не подписаны на этот рецепт.'}
            )
        return


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')


class RecipesIngredientsReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredients.id')
    name = serializers.CharField(source='ingredients.name')
    measurement_unit = serializers.CharField(source='ingredients.measurement_unit')
    class Meta:
        model = RecipesIngredients
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipesReadSerializer(serializers.ModelSerializer):
    ingredients = RecipesIngredientsReadSerializer(
                  
        many=True,
        source = 'ingredients_used'
    )
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    class Meta:
        model = Recipes
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


class RecipesM2MIngredients(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(), source='ingredients.id')
    # id = serializers.IntegerField(source='ingredients.id')
    name = serializers.CharField(source='ingredients.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredients.measurement_unit', read_only=True)
    class Meta:
        model = RecipesIngredients
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipesCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = RecipesM2MIngredients(
        many=True,
        source='ingredients_used'
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tags.objects.all(),
    )
    
    class Meta:
        model = Recipes
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
        recipes = Recipes.objects.create(**validated_data)
        for ingredient in ingredients:
            ingredients = ingredient.get('ingredients')
            id = ingredients.get('id')
            amount = ingredient.get('amount')
            recipes.ingredients.add(id, through_defaults={'amount':amount})
        for tag in tags:
            recipes.tags.add(tag)
        return recipes

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
        obj = super(RecipesCreateUpdateSerializer, self).to_representation(instance)
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


class SubscribeSerializer(serializers.ModelSerializer):
    recipes = RecipesFavoriteSerializer(many=True, source='user_is_subscribed')
    # recipes_count = serializers.IntegerField()
    id = serializers.IntegerField()
    class Meta:
        model = Favorites
        fields = ('id', 'recipes')

    def get_recipes_count():
        pass