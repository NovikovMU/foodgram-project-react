# Generated by Django 3.2 on 2023-09-16 10:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0003_shoppingcart'),
    ]

    operations = [
        migrations.RenameField(
            model_name='favorites',
            old_name='recipes',
            new_name='recipe',
        ),
    ]
