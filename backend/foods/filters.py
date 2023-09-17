from django_filters import rest_framework as filters
from .models import Recipes, Tags


class CustomFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_is_in_shopping_cart'
    )
    tags_slug = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tags.objects.all()
    )

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return Recipes.objects.filter(
                user_is_subscribed__user=self.request.user
            )
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return Recipes.objects.filter(
                user_added_in_shop_cart__user=self.request.user
            )
        return queryset

    class Meta:
        model = Recipes
        fields = [
            'author',
            'is_favorited',
            'is_in_shopping_cart',
            'tags__slug'
        ]
