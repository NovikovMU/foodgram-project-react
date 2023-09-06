from rest_framework import mixins, viewsets

from .models import Ingridients, Receipts, Tags
from .serializers import TagSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tags.objects.all()