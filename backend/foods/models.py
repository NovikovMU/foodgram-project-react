from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from datetime import time

from colorfield.fields import ColorField

from users.models import User


MIN_IN_HOUR = 60


class Tag(models.Model):
    name = models.CharField(max_length=255)
    color = ColorField()
    slug = models.SlugField(max_length=255)

    def __str__(self) -> str:
        return self.Slug


class Ingridient(models.Model):
    name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    unit = models.SmallIntegerField()

    def __str__(self) -> str:
        return self.name


class Receipt(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='receipt'
    )
    name = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to='foods/images/'
    )
    description = models.TextField()
    ingridient = models.ManyToManyField(
        Ingridient,
        related_name='receipt'
    )
    tag = models.ManyToManyField(
        Tag,
        related_name='receipt'
    )
    time = models.TimeField(
        auto_now_add=False,
        auto_now=False,
    )

    # def save(self) -> None:
    #     self.time = time(minute=self.time.min + self.time.hour * MIN_IN_HOUR)
    #     return super().save(*args, **kwargs)


    def clean(self):
        if self.user == self.author:
            raise ValidationError(
                'Primary and secondary inclinations should be different.')


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='fav'
    )
    post = models.ForeignKey(
        Receipt,
        on_delete=models.CASCADE,
        related_name='favorite'
    )
