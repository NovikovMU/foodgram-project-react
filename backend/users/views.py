from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404, render
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from djoser.views import UserViewSet

from foods.models import Recipes
from foods.pagination import CommonResultPagination
from foods.serializers import SubscribeSerializer
from .models import Follow, User
from .serializers import UserSerializer


class CustomUserViewSet(UserViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    pagination_class = CommonResultPagination
    permission_classes = (IsAuthenticated,)
    
    @action(detail=True, methods=('post', 'delete'))
    def subscribe(self, request, id=None):
        recipes_limit = self.request.query_params.get('recipes_limit')
        user = self.request.user
        author = get_object_or_404(User, id=id)
        # data = {
        #     'user': user.pk,
        #     'author': author.pk,
        #     'recipes_limit': recipes_limit
        # }
        data = [user.pk, author.pk, recipes_limit]
        
        follow_serializer = SubscribeSerializer(data=data)
        if self.request.method == 'DELETE':
            if not Follow.objects.filter(user=user, author=author).exists():
                raise serializers.ValidationError(
                    {'error': 'Вы не подписаны на этого пользователя.'}
                )
            Follow.objects.filter(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        follow_serializer.is_valid(raise_exception=True)
        follow_serializer.save()
        return Response(follow_serializer.data)

    @action(detail=False, methods=('get',), pagination_class=CommonResultPagination, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        recipes_limit = self.request.query_params.get('recipes_limit')
        user = self.request.user
        following = Follow.objects.filter(user=user)
        following = self.paginate_queryset(following)
        print()
        print(type(following))
        print()
        follow_serializer = SubscribeSerializer({'recipes_limit': recipes_limit}, data=following, many=True,)
        follow_serializer.is_valid()
        return self.get_paginated_response(follow_serializer.data)
