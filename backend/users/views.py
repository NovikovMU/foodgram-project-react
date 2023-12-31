from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from foods.pagination import CommonResultPagination
from foods.serializers import (SubscribeCreateSerializer,
                               SubscribeReadSerializer)
from .models import Follow, User
from .serializers import UserSerializer


class CustomUserViewSet(UserViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    pagination_class = CommonResultPagination

    def destroy(self, request, *args, **kwargs):
        return Response(
            {'error': 'Вам запрещено удалять аккаунты.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def update(self, request, *args, **kwargs):
        return Response(
            {'error': 'Вам запрещено изменять данные аккаунта.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        """Позволяет подписаться и отписаться на пользователя."""
        user = self.request.user
        author = get_object_or_404(User, id=id)
        if self.request.method == 'DELETE':
            get_object_or_404(Follow, user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        data = {
            'user': user.pk,
            'author': author.pk,
        }

        follow_serializer = SubscribeCreateSerializer(
            data=data, context={'request': request}
        )
        follow_serializer.is_valid(raise_exception=True)
        follow_serializer.save()
        return Response(follow_serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False, methods=('get',),
        pagination_class=CommonResultPagination,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        """Показывает всех пользователей, на которых пописан пользователь."""
        user = self.request.user
        following = User.objects.filter(following__user=user)
        following = self.paginate_queryset(following)
        follow_serializer = SubscribeReadSerializer(
            data=following,
            many=True,
            context={'request': request}
        )
        follow_serializer.is_valid()
        return self.get_paginated_response(follow_serializer.data)
