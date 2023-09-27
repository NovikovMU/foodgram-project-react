from django.contrib.auth.models import AbstractUser
from django.db import models

from foods.constants import MAX_CHAR_EMAIL_LENGTH as MCHEL
from foods.constants import MAX_CHAR_LENGTH as MCHL


class User(AbstractUser):
    password = models.CharField(max_length=MCHL)
    email = models.EmailField(max_length=MCHEL, unique=True)
    first_name = models.CharField(max_length=MCHL)
    last_name = models.CharField(max_length=MCHL)
    REQUIRED_FIELDS = ['username', 'id', 'first_name', 'last_name']
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self) -> str:
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_fields'),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='follow_prevent_self_follow'
            )
        ]

    def __str__(self) -> str:
        return f'{self.user} - {self.author}'
