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

    def __str__(self) -> str:
        return self.slug


class Ingridients(models.Model):
    name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    unit = models.SmallIntegerField()

    def __str__(self) -> str:
        return self.name


class Receipts(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='receipt'
    )
    name = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to='foods/images/'
    )
    text = models.TextField()
    ingridients = models.ManyToManyField(
        Ingridients,
        related_name='receipt',
        through='ReceiptIngridient'
    )
    tags = models.ManyToManyField(
        Tags,
        related_name='receipt'
    )
    cooking_time = models.TimeField(
        auto_now_add=False,
        auto_now=False,
    )

class ReceiptIngridient(models.Model):
    receipts = models.ForeignKey(
        Receipts,
        on_delete=models.CASCADE,
        related_name='ingridients_used'
    )
    ingridients = models.ForeignKey(
        Ingridients,
        on_delete=models.CASCADE,
        related_name='receipts_used'
    )
    amount = models.PositiveIntegerField()


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='fav'
    )
    post = models.ForeignKey(
        Receipts,
        on_delete=models.CASCADE,
        related_name='favorite'
    )
