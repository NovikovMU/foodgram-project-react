from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import CustomFilter, IngredientFilter
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)
from .pagination import CommonResultPagination
from .perimissions import IsAuthenticatedIsOwnerOrReadOnly
from .serializers import (FavoriteCreateSerializer, IngredientSerializer,
                          RecipesCreateUpdateSerializer, RecipesReadSerializer,
                          ShoppingCartCreateSerializer, TagSerializer)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipesCreateUpdateSerializer
    pagination_class = CommonResultPagination
    http_method_names = ('patch', 'get', 'post', 'delete')
    permission_classes = (IsAuthenticatedIsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CustomFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipesReadSerializer
        return self.serializer_class

    def favorite_shopping_cart_create(self, recipe, serializer, user):
        data = {
            'user': user.id,
            'recipe': recipe.id,
        }

        serializer = serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    def favorite_shopping_cart_delete(self, model, recipe, user):
        get_object_or_404(model, recipe=recipe, user=user).delete()

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        """Позволяет добавить и удалить рецепт в список любимых."""
        recipe = get_object_or_404(Recipe, id=pk)
        user = self.request.user
        if self.request.method == 'DELETE':
            self.favorite_shopping_cart_delete(
                Favorite, recipe, user
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        data = self.favorite_shopping_cart_create(
            recipe, FavoriteCreateSerializer, user
        )
        return Response(data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        """Позволяет добавить и удалить рецепт из корзины."""
        recipe = get_object_or_404(Recipe, id=pk)
        user = self.request.user
        if self.request.method == 'DELETE':
            self.favorite_shopping_cart_delete(
                ShoppingCart, recipe, user
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        data = self.favorite_shopping_cart_create(
            recipe, ShoppingCartCreateSerializer, user
        )
        return Response(data, status=status.HTTP_201_CREATED)

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
        results = RecipeIngredient.objects.filter(
            recipe__user_added_in_shop_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(Sum('amount'))
        for result in results:
            text = (
                text + f'{result["ingredient__name"]}, '
                + f'{result["amount__sum"]} '
                + f'{result["ingredient__measurement_unit"]},\n'
            )
        response.writelines(text)
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
