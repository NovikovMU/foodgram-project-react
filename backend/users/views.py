from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from foods.pagination import CommonResultPagination
from foods.serializers import SubscribeSerializer

from .models import Follow, User
from .serializers import UserSerializer


class CustomUserViewSet(UserViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    pagination_class = CommonResultPagination
    # permission_classes = (IsAuthenticated,)

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

    @action(detail=True, methods=('post', 'delete'))
    def subscribe(self, request, id=None):
        """Позволяет подписаться и отписаться на пользователя."""
        user = self.request.user
        author = get_object_or_404(User, id=id)
        data = {
            'user': user.pk,
            'author': author.pk,
        }
        follow_serializer = SubscribeSerializer(
            data=data, context={'request': request}
        )
        if self.request.method == 'DELETE':
            if not Follow.objects.filter(user=user, author=author).exists():
                raise serializers.ValidationError(
                    {'error': 'Вы не подписаны на этого пользователя.'}
                )
            Follow.objects.filter(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
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
        following = Follow.objects.filter(user=user)
        following = self.paginate_queryset(following)
        follow_serializer = SubscribeSerializer(
            data=following,
            many=True,
            context={'request': request}
        )
        follow_serializer.is_valid()
        return self.get_paginated_response(follow_serializer.data)
