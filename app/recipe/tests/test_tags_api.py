""" Test for the Tags Api"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from core.models import Tag, Recipe
from recipe.serializers import TagSerializer
from rest_framework import status
from rest_framework.test import APIClient

TAGS_URL = reverse('recipe:tag-list')

def detail_url(tag_id):
    return reverse('recipe:tag-detail', args=[tag_id])

def create_user(email='exrc@example.com', password='pass1233'):
    return get_user_model().objects.create_user(email=email, password=password)

class PublicTagsApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_requirement(self):
        """requer de autorizacao"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagApiTests(TestCase):
    """ autenticando"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """retrieve lista de tags"""

        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.filter(user=self.user).order_by('-name')
        # tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """lista de tags e limitado ao ususario autenticado"""

        user2 = create_user(email='userr@example.com')
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):

        tag = Tag.objects.create(user=self.user, name='After Dinner')

        payload = {'name': 'Desert'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """deletar tag"""
        tag = Tag.objects.create(user=self.user, name='breakfast')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_recipe(self):
        """"""
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')
        recipe = Recipe.objects.create(
            title='Green Eggs on Toast',
            time_minutes = 8,
            price = Decimal('2.50'),
            user=self.user,
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """filtra tags e returna lista unica"""
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Dinner')
        recipe1 = Recipe.objects.create(
            title = 'Pancakes',
            time_minutes = 5,
            price = Decimal('7.00'),
            user=self.user
        )

        recipe2 = Recipe.objects.create(
            title = 'Omelete',
            time_minutes = 3,
            price = Decimal('6.30'),
            user=self.user
        )
        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)
