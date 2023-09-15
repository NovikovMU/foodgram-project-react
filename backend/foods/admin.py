from django.contrib import admin

from .models import Ingredients, Favorites, Recipes, Tags, ShoppingCart, RecipesIngredients, RecipesTags

admin.site.register(Tags)
admin.site.register(Ingredients)
admin.site.register(Recipes)
admin.site.register(RecipesIngredients)
admin.site.register(RecipesTags)
admin.site.register(Favorites)
admin.site.register(ShoppingCart)
