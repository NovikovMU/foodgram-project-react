from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User
from .constants import (MAX_COOKING_TIME, MAX_LENGTH_CHARFIELD,
                        MAX_LENGTH_CHARFIELD_NAME, MIN_AMOUNT,
                        MIN_COOKING_TIME)


class Tag(models.Model):
    name = models.CharField(max_length=MAX_LENGTH_CHARFIELD)
    color = ColorField(unique=True)
    slug = models.CharField(max_length=MAX_LENGTH_CHARFIELD)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.slug


class Ingredient(models.Model):
    name = models.CharField(max_length=MAX_LENGTH_CHARFIELD)
    measurement_unit = models.CharField(max_length=MAX_LENGTH_CHARFIELD)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_fields'),
        ]

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe'
    )
    name = models.CharField(max_length=MAX_LENGTH_CHARFIELD_NAME)
    image = models.ImageField(
        upload_to='foods/images/'
    )
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipe',
        through='RecipeIngredient',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipe',
        through='RecipeTag'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[
            MinValueValidator(MIN_COOKING_TIME),
            MaxValueValidator(MAX_COOKING_TIME)
        ]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_used'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_used',
    )
    amount = models.PositiveIntegerField(validators=[
        MinValueValidator(MIN_AMOUNT)
    ])

    class Meta:
        verbose_name = 'Ингредиент используемый в рецепте'
        verbose_name_plural = 'Ингредиенты используемые в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_recipe_fields'),
        ]

    def __str__(self) -> str:
        return f'{self.recipe} - {self.ingredient}'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='tag_used'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recipe_used',
    )

    class Meta:
        verbose_name = 'Тег указанный в рецепте'
        verbose_name_plural = 'Теги указанные в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['tag', 'recipe'],
                name='unique_tag_recipe_fields'),
        ]

    def __str__(self) -> str:
        return f'{self.recipe} - {self.tag}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_in_favorite'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='user_add_in_favorite'
    )

    class Meta:
        verbose_name = 'Рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_fav_fields'),
        ]

    def __str__(self) -> str:
        return f'{self.user} - {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_in_shop_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='user_added_in_shop_cart'
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списках покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shcrd_fields'),
        ]

    def __str__(self) -> str:
        return f'{self.user} - {self.recipe}'
