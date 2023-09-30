from django.urls import include, path
from rest_framework import routers

from foods.views import IngredientViewSet, RecipeViewSet, TagViewSet

app_name = 'foods'
router = routers.DefaultRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
]
