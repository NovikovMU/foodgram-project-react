from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag,
                     ShoppingCart, Tag)
from .constants import MIN_AMOUNT

class IngredientTagInLineFormset(BaseInlineFormSet):
    def clean(self):
        result_list = self.cleaned_data
        for resut in reversed(result_list):
            if not resut or resut['DELETE'] == True:
                result_list.pop(result_list.index(resut))
        if not result_list:
            raise ValidationError('Должно быть хотя бы одно поле.')
        return super().clean()

class IngredientAdmin(admin.TabularInline):
    formset = IngredientTagInLineFormset
    model = RecipeIngredient
    min_num = MIN_AMOUNT


class TagAdmin(admin.TabularInline):
    formset = IngredientTagInLineFormset
    model = RecipeTag
    min_num = MIN_AMOUNT


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
