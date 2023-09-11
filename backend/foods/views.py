from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Ingredients, Receipts, Tags
from .serializers import IngredientSerializer, FavoriteSerializer, ReceiptReadSerializer, ReceiptsCreateUpdateSerializer, TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer


class ReciptViewSet(viewsets.ModelViewSet):
    queryset = Receipts.objects.all()
    serializer_class = ReceiptsCreateUpdateSerializer
    http_method_names = ('patch', 'get', 'post', 'delete')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReceiptReadSerializer
        return self.serializer_class

    @action(detail=True, methods=('post', 'delete'))
    def favorite(self, request, pk=None):
        receipt = get_object_or_404(Receipts, id=pk)
        user = self.request.user
        serializer = FavoriteSerializer(
            data={
                'user': user.pk,
                'receipts': receipt.pk,
            },
        )
        serializer.is_valid(raise_exception=True)
        receipt.user_favorite.add(user)
        response = {
            'id': receipt.pk,
            'name': receipt.name,
            # 'image': receipt.image,
            'cooking_time': receipt.cooking_time
        }
        return Response(response, status=status.HTTP_200_OK)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer
