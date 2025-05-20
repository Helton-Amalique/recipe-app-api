"""Tests para api receitas"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')

def details_url(recipe_id):
    """cria e retorna 'os detalher da receita URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])

def creat_user(**params):
    return get_user_model().objects.create_user(**params)


def create_recipe(user, **params):
    """cria e retorna um simples receita"""
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal(5.25),
        'description': 'Sample description',
        'link': 'http://example.com/recepi.pdf',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe

class PublicRecipeAPITest(TestCase):
    """Test nao autenticado API request"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeApiTest(TestCase):
    """"""
    def setUp(self):
        self.client = APIClient()
        self.user =  creat_user(email='user@example.com', password='test1223')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """"""
        other_user = creat_user(email='userr@example.com', password='seraa123')
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res= self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes,many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """0"""
        recipe=create_recipe(user=self.user)

        url = details_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test cria um receita"""

        payload= {
            'title': 'Samole recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
            'description': 'delicius'
        }
        res = self.client.post(RECIPES_URL, payload)

        print(res.status_code)
        print(res.data)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user,  self.user)

    def test_partial_update(self):
        """"""
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link=original_link,
        )

        payload = {'title': 'New recipe tiile'}
        url = details_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """test para update"""
        recipe = create_recipe(
            user=self.user,
            title='Simpl recipe title',
            link='https://example.com/receipe.pdf',
            description='sample recipe description'
        )

        payload = {
            'title': "New recipe title",
            'link': 'https://example.com/new-receipe.pdf',
            'description': 'New recipe description',
            'time_minutes': 15,
            'price': Decimal('2.50')
        }
        url = details_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user,  self.user)

    def test_update_user_returns_error(self):
        """"""
        new_user= creat_user(email='uuser@example.com', password='passs12')
        recipe =  create_recipe(user=self.user)

        payload = {'user': new_user.id}
        url = details_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """"""
        recipe = create_recipe(user=self.user)

        url = details_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_recipe_outher_user_recipe_error(self):

        new_user = creat_user(email='exer@example.com', password='asssd123')
        recipe = create_recipe(user=new_user)

        url =  details_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())