# Generated by Django 3.2 on 2023-09-26 17:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0003_auto_20230926_1952'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipeingredient',
            old_name='ingredients',
            new_name='ingredient',
        ),
    ]
