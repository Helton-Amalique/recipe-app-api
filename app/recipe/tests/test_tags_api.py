"""
"""
from django.contrib.auth import get_user_model
from django .urls import reverse
from django.test import TestCase
from core.models import Tag
from recipe.serializers import TagSerializer
from rest_framework import status
from rest_framework.test import APIClient

TAGS_URL = reverse('recipe:tag-list')

def create_user(email='exrc@example.com', password='pass1233'):
    return get_user_model().objects.create_user(email=email,password=password)


class PuclicTagsApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_requirement(self):
        """necessictta de autorizacao"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTageApiTests(TestCase):
    """nao autenticado"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """retrieve lista de tags"""

        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """lista de tags e limitado ao ususario autenticado"""

        user2 = create_user(email='userr@example.com')
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort')

        res =  self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)