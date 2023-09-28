import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from users.models import Follow
from users.serializers import UserSerializer

from .constants import MAX_LENGTH_FOR_CHARFIELD as MLFCH
from .constants import POSITIVE_MAX_COOKING_TIME, POSITIVE_MIN_NUMBER
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag,
                     ShoppingCart, Tag)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipesIngredientsReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipesReadSerializer(serializers.ModelSerializer):
    ingredients = RecipesIngredientsReadSerializer(
        many=True,
        source='ingredient_used'
    )
    image = Base64ImageField()
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
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
            and Favorite.objects.filter(
                user=self.context['request'].user,
                recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return (
            not self.context['request'].user.is_anonymous
            and ShoppingCart.objects.filter(
                user=self.context['request'].user,
                recipe=obj
            ).exists()
        )


class RecipesM2MIngredients(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount',
        )

    def validate(self, attrs):
        get_object_or_404(Ingredient, id=attrs.get('ingredient')['id'])
        if POSITIVE_MIN_NUMBER > attrs.get('amount'):
            raise serializers.ValidationError(
                {'ingredient_error': 'Количество должно быть больше 1.'}
            )
        return super().validate(attrs)


class RecipesCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = RecipesM2MIngredients(
        many=True,
        source='ingredient_used'
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def add_ingredinets_into_recipe(self, ingredients, recipe):
        array = [
            RecipeIngredient(
                ingredient=Ingredient.objects.get(
                    id=ingredient.get('ingredient').get('id')
                ),
                amount=ingredient.get('amount'),
                recipe=recipe
            ) for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(array)
        return

    def add_tags_into_recipe(self, recipe, tags):
        array = [RecipeTag(recipe=recipe, tag=tag) for tag in tags]
        RecipeTag.objects.bulk_create(array)
        return

    def validate(self, attrs):
        name = attrs.get('name')
        if not name:
            raise serializers.ValidationError(
                {'name_error': 'Введите имя.'}
            )
        if len(name) > MLFCH:
            raise serializers.ValidationError(
                {'name_error': 'Превышено кол-во символов в имени.'}
            )
        ingredients = attrs.get('ingredient_used')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredient_error': 'Должен быть хотя бы один ингредиент.'}
            )
        ingredient_array = [x.get('ingredient')['id'] for x in ingredients]
        if len(ingredient_array) != len(set(ingredient_array)):
            raise serializers.ValidationError(
                {'tag_error': 'Ингредиент должны быть разными.'}
            )
        tags = attrs.get('tags')
        if not tags:
            raise serializers.ValidationError(
                {'tag_error': 'Должен быть хотя бы один тег.'}
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {'tag_error': 'Теги должны быть разными.'}
            )
        cooking_time = attrs.get('cooking_time')
        if cooking_time < POSITIVE_MIN_NUMBER:
            raise serializers.ValidationError(
                {
                    'cooking_time_error':
                    'Время приготовления должно быть больше 1 минуты.'
                }
            )
        if cooking_time > POSITIVE_MAX_COOKING_TIME:
            raise serializers.ValidationError(
                {
                    'cooking_time_error':
                    'Время приготовления должно быть меньше 240 минут.'
                }
            )
        return super().validate(attrs)

    def create(self, validated_data):
        author = self.context['request'].user
        ingredients = validated_data.pop('ingredient_used')
        tags = validated_data.pop('tags')
        validated_data.update(author=author)
        recipe = Recipe.objects.create(**validated_data)

        self.add_ingredinets_into_recipe(ingredients, recipe)
        self.add_tags_into_recipe(recipe, tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredient_used')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        self.add_ingredinets_into_recipe(ingredients, instance)
        instance.tags.clear()
        self.add_tags_into_recipe(instance, tags)
        instance = super().update(instance, validated_data)
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipesReadSerializer(instance, context=context).data


class LiteRecipesSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class SubscribeReadSerializer(serializers.ModelSerializer):
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

    def get_recipes(self, obj):
        limits = self.context.get('request').query_params.get('recipes_limit')
        recipe = obj.author.recipe
        if limits:
            return LiteRecipesSerializer(
                recipe, many=True
            ).data[:int(limits)]
        return LiteRecipesSerializer(recipe, many=True).data

    def get_is_subscribed(self, obj):
        return (Follow.objects.filter(
            user=obj.user_id, author=obj.author_id
        ).exists())

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class SubscribeCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = (
            'user',
            'author',
        )

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return SubscribeReadSerializer(instance, context=context).data

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
