from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from datetime import time

from colorfield.fields import ColorField

from users.models import User


MIN_IN_HOUR = 60


class Tags(models.Model):
    name = models.CharField(max_length=200)
    color = ColorField()
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
    cooking_time = models.PositiveIntegerField()


    class Meta:
        verbose_name = 'Recipes'
        verbose_name_plural = 'Recipess'

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
    amount = models.PositiveIntegerField()

    class Meta:
        pass


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


class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes_used'
    )
    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='user_is_subscribed'
    )
