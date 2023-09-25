
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import CustomFilter, IngredientFilter
from .models import (Favorites, Ingredients, Recipes, RecipesIngredients,
                     ShoppingCart, Tags)
from .pagination import CommonResultPagination
from .perimissions import IsAuthenticatedIsOwnerOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipesCreateUpdateSerializer, RecipesReadSerializer,
                          ShoppingCartSerializer, TagSerializer)


def favorite_shopping_cart_method(self, pk, serializer, model):
    recipe = get_object_or_404(Recipes, id=pk)
    user = self.request.user
    data = {
        'user': user.pk,
        'recipe': recipe.pk,
    }
    serializer = serializer(data=data)
    if self.request.method == 'DELETE':
        if not model.objects.filter(
            user=user, recipe=recipe
        ).exists():
            raise serializers.ValidationError(
                {'error': 'Рецепта нет в списке.'}
            )
        model.objects.filter(user=user, recipe=recipe).delete()
        return
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.data


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipesCreateUpdateSerializer
    pagination_class = CommonResultPagination
    http_method_names = ('patch', 'get', 'post', 'delete')
    permission_classes = (IsAuthenticatedIsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CustomFilter

    def get_queryset(self):
        return Recipes.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipesReadSerializer
        return self.serializer_class

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        """Позволяет добавить и удалить рецепт в список любимых."""
        data = favorite_shopping_cart_method(
            self, pk, FavoriteSerializer, Favorites)
        if data:
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        """Позволяет добавить и удалить рецепт из корзины."""
        data = favorite_shopping_cart_method(
            self,
            pk,
            ShoppingCartSerializer,
            ShoppingCart
        )
        if data:
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Позволяет скачать весь список из корзины."""
        response = HttpResponse(content_type='text/plain')
        response[
            'Content-Disposition'
        ] = 'attachment; filename=yourreceipes.txt'
        text = ''
        results = RecipesIngredients.objects.filter(
            recipes__user_added_in_shop_cart__user=request.user
        )
        results = results.values(
            'ingredients__name',
            'ingredients__measurement_unit'
        ).annotate(Sum('amount'))
        for result in results:
            text = (
                text + f'{result["ingredients__name"]}, '
                + f'{result["amount__sum"]} '
                + f'{result["ingredients__measurement_unit"]},\n'
            )
        response.writelines(text)
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer
