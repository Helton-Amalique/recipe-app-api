"""mapea urls das receitas"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from recipe import views

router = DefaultRouter()
router.register('recipe', views.RecipeViewSet)
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewset)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
]
