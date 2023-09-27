from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag,
                     ShoppingCart, Tag)


class IngredientAdmin(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1


class TagAdmin(admin.TabularInline):
    model = RecipeTag
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    list_filter = ('name', 'author', 'tags')
    list_display = ('name', 'amount_favorite')
    inlines = [IngredientAdmin, TagAdmin]

    def amount_favorite(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


class IngredientsAdmin(admin.ModelAdmin):
    list_filter = ('name',)


admin.site.register(Tag)
admin.site.register(Ingredient, IngredientsAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient)
admin.site.register(RecipeTag)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
