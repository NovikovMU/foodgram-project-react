from django.shortcuts import get_object_or_404, render
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from foods.models import Recipes
from foods.serializers import SubscribeSerializer
from .models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @action(detail=True, methods=('post', 'delete'))
    def subscribe(self, request, pk=None):
        user = self.request.user
        author = get_object_or_404(User, id=pk)
        recipes = Recipes.objects.filter(author=author).values()
        list_result = [entry for entry in recipes]
        # print()
        # print(recipe)
        # print()
        data = {
            'email': author.email,
            'id': author.pk,
            'username': author.username,
            'first_name': author.first_name,
            'last_name': author.last_name,
            'recipe': recipes
        }
        serializer = SubscribeSerializer(
            data={'id': author.pk, 'recipes': list_result}
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
