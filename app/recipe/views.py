"""
view para recipe api
"""
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient

from recipe import serializers

class RecipeViewSet(viewsets.ModelViewSet):
    """gerencia receita da API"""
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve receitas autenticadas de user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):

        """if self.action == 'list':
            return serializers.RecipeSerializer
        return self.serializer_class"""
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        return serializers.RecipeSerializer

    def perform_create(self, serializer):
        """cria uma nova receita"""
        serializer.save(user=self.request.user)

class BaseRecipeAttrViewSet(mixins.DestroyModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """Base viewset for recipe atriibutes"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """filtra querys para user authenticado"""
        return self.queryset.filter(user=self.request.user).order_by('-name')


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()

class IngredientViewset(BaseRecipeAttrViewSet):
    """Manage ingredients in Database"""

    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
