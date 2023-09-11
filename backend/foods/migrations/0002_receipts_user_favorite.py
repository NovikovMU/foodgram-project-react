# Generated by Django 3.2 on 2023-09-11 16:19

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('foods', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='receipts',
            name='user_favorite',
            field=models.ManyToManyField(related_name='favorite', through='foods.Favorites', to=settings.AUTH_USER_MODEL),
        ),
    ]
