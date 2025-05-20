"""Serializacao para as recitas APis"""

from rest_framework import serializers
from core.models import Recipe

class RecipeSerializer(serializers.ModelSerializer):
    """Serializacao de receitas"""
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link',
                  'description']
        read_only_fields = ['id']

class RecipeDetailSerializer(RecipeSerializer):
    """"""
    class Meta(RecipeSerializer.Meta):
        fields =RecipeSerializer.Meta.fields +['description']
