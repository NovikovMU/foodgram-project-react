from django.shortcuts import get_object_or_404, render
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @action(
        detail=False,
        methods=['get']
    )
    def me(self, request):
        print()
        print(self.request.user)
        print()
        user = get_object_or_404(User, username=self.request.user)
        print(self.request.user)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
