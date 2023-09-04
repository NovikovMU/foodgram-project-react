from django.shortcuts import get_object_or_404, render
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from .serializers import UserSerializer

def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {'access': str(refresh.access_token)}


@api_view(['POST'])
def create_token(request):
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    print(username)
    password = serializer.validated_data.get('password')
    print(password)
    if User.objects.filter(username=username, password=password).exists():
        token = get_token_for_user(username)
        return Response(token, status=status.HTTP_200_OK)
    return Response('oops', status=status.HTTP_400_BAD_REQUEST)

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
