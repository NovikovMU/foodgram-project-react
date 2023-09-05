from rest_framework import mixins, viewsets

from .models import Ingridient, Receipt, Tag
from .serializers import TagSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()