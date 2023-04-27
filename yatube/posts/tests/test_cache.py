from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, get_user_model

User = get_user_model()


class TestCache(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            text='Test',
            author=cls.user
        )
        cls.INDEX = reverse('posts:index')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache(self):
        response = self.authorized_client.get(self.INDEX)
        Post.objects.create(
            text='new text',
            author=self.user
        )
        new_response = self.authorized_client.get(self.INDEX)
        self.assertEqual(response.content, new_response.content)
        cache.clear()
        new_response = self.authorized_client.get(self.INDEX)
        self.assertNotEqual(response.content, new_response.content)
