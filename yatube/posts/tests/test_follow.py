from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Post, Follow

User = get_user_model()


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.user_2 = User.objects.create(username='auth_2')
        cls.follow = Follow.objects.create(
            author=cls.user,
            user=cls.user_2
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='new text'
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='Super',
            author=cls.user
        )
        cls.FOLLOW_INDEX = reverse('posts:follow_index')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)

    def test_follow_and_unfollow(self):
        follow_count = Follow.objects.count()
        self.authorized_client.get(
            reverse('posts:profile_follow', args=(self.user_2,)))
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.authorized_client.get(
            reverse('posts:profile_unfollow', args=(self.user_2,)))
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_following_index(self):
        following = User.objects.create(username='following')
        Follow.objects.create(user=self.user, author=following)
        post = Post.objects.create(author=following, text=self.post.text)
        response = self.authorized_client.get(self.FOLLOW_INDEX)
        self.assertIn(post, response.context['page_obj'].object_list)
        response_2 = self.authorized_client_2.get(self.FOLLOW_INDEX)
        self.assertNotIn(post, response_2.context['page_obj'].object_list)

