from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from foods.views import IngredientViewSet, RecipeViewSet, TagViewSet
from users.views import CustomUserViewSet

router = routers.DefaultRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('djoser.urls.authtoken')),
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
