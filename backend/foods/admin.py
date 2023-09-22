from django.contrib import admin

from .models import Ingredients, Favorites, Recipes, Tags, ShoppingCart, RecipesIngredients, RecipesTags


class RecipesAdmin(admin.ModelAdmin):
    list_filter = ('name','author', 'tags')
    list_display = ('name', 'amount_favorite')
    def amount_favorite(self, obj):
        return Favorites.objects.filter(recipe=obj).count()


class IngredientsAdmin(admin.ModelAdmin):
    list_filter = ('name',)


admin.site.register(Tags)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Recipes, RecipesAdmin)
admin.site.register(RecipesIngredients)
admin.site.register(RecipesTags)
admin.site.register(Favorites)
admin.site.register(ShoppingCart)
