from django.test import TestCase

from ..models import Group, Post, Comment, Follow, get_user_model

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author
        )
        cls.comment = Comment.objects.create(
            text='Тест комментария',
            post=cls.post,
            author=cls.user
        )

    def test_models_have_correct_object_names(self):
        self.assertEqual(self.group.title, str(self.group))
        self.assertEqual(self.post.text, str(self.post))
        self.assertEqual(self.comment.text, str(self.comment))
        self.assertEqual(f'{self.user} подписался на {self.author}',
                         str(self.follow))
