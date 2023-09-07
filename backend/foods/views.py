from rest_framework import mixins, viewsets

from .models import Ingredients, Receipts, Tags
from .serializers import IngredientSerializer, ReceiptReadSerializer, ReceiptsCreateUpdateSerializer, TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredients.objects.all()


class ReciptViewSet(viewsets.ModelViewSet):
    serializer_class = ReceiptsCreateUpdateSerializer
    queryset = Receipts.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReceiptReadSerializer
        return self.serializer_class

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tags.objects.all()