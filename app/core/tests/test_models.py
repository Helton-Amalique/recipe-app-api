"""
Test for models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

class ModelsTests(TestCase):
    """Test models"""

    def test_create_user_with_email_sucessful(self):
        """"Este teste cria user com email com sucesso"""
        email = 'test@example.com'
        password = 'test123'
        user= get_user_model().objects.creat_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))