from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User

MIN_IN_HOUR = 60


class Tags(models.Model):
    name = models.CharField(max_length=200)
    color = ColorField(unique=True)
    slug = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self) -> str:
        return self.slug


class Ingredients(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self) -> str:
        return self.name


class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to='foods/images/'
    )
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredients,
        related_name='recipes',
        through='RecipesIngredients'
    )
    tags = models.ManyToManyField(
        Tags,
        related_name='recipes',
        through='RecipesTags'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ['-id']

    def __str__(self) -> str:
        return self.name


class RecipesIngredients(models.Model):
    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='ingredients_used'
    )
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='recipes_used'
    )
    amount = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Ingredient in recipe'
        verbose_name_plural = 'Ingredients in recipes'


class RecipesTags(models.Model):
    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='tags_used'
    )
    tags = models.ForeignKey(
        Tags,
        on_delete=models.CASCADE,
        related_name='recipes_used'
    )

    class Meta:
        verbose_name = 'Tag in recipe'
        verbose_name_plural = 'Tags in recipes'


class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes_used'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='user_is_subscribed'
    )

    class Meta:
        verbose_name = 'Recipe in favorite'
        verbose_name_plural = 'Recipes in favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_fav_fields'),
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_in_shop_cart'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='user_added_in_shop_cart'
    )

    class Meta:
        verbose_name = 'Recipe in shopping cart'
        verbose_name_plural = 'Recipes in shopping carts'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shcrd_fields'),
        ]
