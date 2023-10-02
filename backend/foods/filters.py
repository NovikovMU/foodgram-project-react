from django_filters import rest_framework as filters

from .models import Ingredient, Recipe


class CustomFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_is_in_shopping_cart'
    )
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset.none()
        if value:
            queryset = queryset.filter(
                user_add_in_favorite__user=self.request.user
            )
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset.none()
        if value:
            queryset = queryset.filter(
                user_added_in_shop_cart__user=self.request.user
            )
        return queryset

    class Meta:
        model = Recipe
        fields = (
            'author',
            'is_favorited',
            'is_in_shopping_cart',
            'tags',
        )


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = (
            'name',
        )
