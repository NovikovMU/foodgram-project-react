import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import (
    Ingredients, Favorites, ShoppingCart, Recipes, RecipesIngredients, Tags
)
from users.serializers import UserSerializer
from users.models import Follow

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')  
            ext = format.split('/')[-1]  
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class RecipesFavoriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    image = Base64ImageField()
    
    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='recipe.id', read_only=True)
    name = serializers.CharField(source='recipe.name', read_only=True)
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True
    )
    class Meta:
        model = Favorites
        fields = (
            'user',
            'recipe',
            'id',
            'name',
            'image',
            'cooking_time',
        )
        extra_kwargs = {
            'user': {'write_only': True},
            'recipe': {'write_only': True},
        }

    def validate(self, attrs):
        if Favorites.objects.filter(
            recipe=attrs.get('recipe'), user=attrs.get('user')
        ).exists():
            raise serializers.ValidationError(
                {'error': 'Вы уже подписались на этот рецепт.'}
            )
        return super().validate(attrs)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')


class RecipesIngredientsReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredients.id')
    name = serializers.CharField(source='ingredients.name')
    measurement_unit = serializers.CharField(
        source='ingredients.measurement_unit'
    )
    
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
        source='ingredients_used'
    )
    image = Base64ImageField()
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    
    class Meta:
        model = Recipes
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        
        )

    def get_is_favorited(self, obj):
        return (
            not self.context['request'].user.is_anonymous
            and Favorites.objects.filter(
            user=self.context['request'].user,
            recipe=obj
        ).exists())

    def get_is_in_shopping_cart(self, obj):
        return (
            not self.context['request'].user.is_anonymous
            and ShoppingCart.objects.filter(
            user=self.context['request'].user,
            recipe=obj
        ).exists())


class RecipesM2MIngredients(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(), source='ingredients.id')
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
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def create(self, validated_data):
        author = self.context['request'].user
        ingredients = validated_data.pop('ingredients_used')
        tags = validated_data.pop('tags')
        validated_data.update(author=author)
        recipe = Recipes.objects.create(**validated_data)
        for ingredient in ingredients:
            ingredients = ingredient.get('ingredients')
            id = ingredients.get('id')
            amount = ingredient.get('amount')
            recipe.ingredients.add(id, through_defaults={'amount': amount})
        for tag in tags:
            recipe.tags.add(tag)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients_used')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        for ingredient in ingredients:
            ingredients = ingredient.get('ingredients')
            id = ingredients.get('id')
            amount = ingredient.get('amount')
            instance.ingredients.add(id, through_defaults={'amount': amount})
        instance.tags.clear()
        for tag in tags:
            instance.tags.add(tag)
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        instance.image = validated_data.get('image')
        return instance

    def to_representation(self, instance):
        obj = super(
            RecipesCreateUpdateSerializer, self
        ).to_representation(instance)
        ids = obj.get('tags')
        all_trags = []
        for id in ids:
            tag = get_object_or_404(Tags, id=id)
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
    email = serializers.CharField(source='author.email', read_only=True)
    id = serializers.IntegerField(source='author.id', read_only=True)
    username = serializers.CharField(source='author.username', read_only=True)
    first_name = serializers.CharField(
        source='author.first_name', read_only=True
    )
    last_name = serializers.CharField(
        source='author.last_name', read_only=True
    )
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'user',
            'author',
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        extra_kwargs = {
            'user': {'write_only': True},
            'author': {'write_only': True},
        }

    def validate(self, attrs):
        if Follow.objects.filter(
            user=attrs.get('user'), author=attrs.get('author')
        ).exists():
            raise serializers.ValidationError(
                {'error': 'Вы уже подписаны.'}
            )
        if attrs.get('user') == attrs.get('author'):
            raise serializers.ValidationError(
                {'error': 'Нельзя подписываться на самого себя.'}
            )
        return super().validate(attrs)

    def get_recipes(self, obj):
        limits = self.context.get('request').query_params.get('recipes_limit')
        if limits:
            return obj.author.recipes.values(
                'id',
                'name',
                'image',
                'cooking_time'
            ).order_by('-id')[:int(limits)]
        return obj.author.recipes.values()

    def get_is_subscribed(self, obj):
        return (Follow.objects.filter(
            user=obj.user_id, author=obj.author_id
        ).exists())
    
    def get_recipes_count(self, obj):
        return Recipes.objects.filter(author=obj.author).count()


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='recipe.id', read_only=True)
    name = serializers.CharField(source='recipe.name', read_only=True)
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True
    )
    class Meta:
        model = ShoppingCart
        fields = (
            'user',
            'recipe',
            'id',
            'name',
            'image',
            'cooking_time',
        )
        extra_kwargs = {
            'user': {'write_only': True},
            'recipe': {'write_only': True},
        }

    def validate(self, attrs):
        if ShoppingCart.objects.filter(
            recipe=attrs.get('recipe'), user=attrs.get('user')
        ).exists():
            raise serializers.ValidationError(
                {'error': 'Вы уже добавили этот рецепт в список покупок.'}
            )
        return super().validate(attrs)