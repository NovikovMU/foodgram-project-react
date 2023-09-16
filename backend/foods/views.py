from django.shortcuts import get_object_or_404
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Ingredients, Favorites, ShoppingCart, Recipes, Tags
from .pagination import CommonResultPagination
from .perimissions import IsAuthenticatedIsOwnerOrReadOnly
from .serializers import IngredientSerializer, FavoriteSerializer, ShoppingCartSerializer, RecipesReadSerializer, RecipesCreateUpdateSerializer, TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesCreateUpdateSerializer
    pagination_class = CommonResultPagination
    http_method_names = ('patch', 'get', 'post', 'delete')
    permission_classes = (IsAuthenticatedIsOwnerOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipesReadSerializer
        return self.serializer_class

    @action(detail=True, methods=('post', 'delete'), permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipes, id=pk)
        user = self.request.user
        data = {
                'user': user.pk,
                'recipe': recipe.pk,
            }
        serializer = FavoriteSerializer(data=data)
        if self.request.method == 'DELETE':
            if not Favorites.objects.filter(
                user=user, recipe=recipe
            ).exists():
                raise serializers.ValidationError(
                    {'error': 'Вы не подписаны на этот рецепт.'}
                )
            Favorites.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=('post', 'delete'), permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipes, id=pk)
        user = self.request.user
        data = {
                'user': user.pk,
                'recipe': recipe.pk,
            }
        serializer = ShoppingCartSerializer(data=data)
        if self.request.method == 'DELETE':
            if not ShoppingCart.objects.filter(
                user=user, recipe=recipe
            ).exists():
                raise serializers.ValidationError(
                    {'error': 'Вы не подписаны на этот рецепт.'}
                )
            ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=('get',), permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        response = Response(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=yourreceipes.txt'
        line = 'Test txt file.'
        response.writelines(line)
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer
