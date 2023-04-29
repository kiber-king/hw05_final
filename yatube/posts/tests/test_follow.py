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
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_2 = Client()
        cls.authorized_client_2.force_login(cls.user_2)
        cls.FOLLOW_INDEX = reverse('posts:follow_index')
        cls.FOLLOW = reverse('posts:profile_follow', args=(cls.user_2,))
        cls.UNFOLLOW = reverse('posts:profile_unfollow', args=(cls.user_2,))

    def test_follow_and_unfollow(self):
        follow_count = Follow.objects.count()
        self.authorized_client.get(self.FOLLOW)
        self.assertEqual(Follow.objects.count(), follow_count + 1)

    def test_unfollow(self):
        Follow.objects.create(user=self.user, author=self.user_2)
        follow_count = Follow.objects.count()
        self.authorized_client.get(self.UNFOLLOW)
        self.assertEqual(Follow.objects.count(), follow_count - 1)

    def test_following_index(self):
        following = User.objects.create(username='following')
        Follow.objects.create(user=self.user, author=following)
        post = Post.objects.create(author=following, text=self.post.text)
        response = self.authorized_client.get(self.FOLLOW_INDEX)
        self.assertIn(post, response.context['page_obj'].object_list)
        response_2 = self.authorized_client_2.get(self.FOLLOW_INDEX)
        self.assertNotIn(post, response_2.context['page_obj'].object_list)
