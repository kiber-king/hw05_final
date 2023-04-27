import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Post, Group, get_user_model, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group_1 = Group.objects.create(
            title='test',
            slug='group_1',
            description='Тестовое описание группы 1', )
        cls.group_2 = Group.objects.create(
            title='test_2',
            slug='group_2',
            description='Новое тестовое описание группы 2'
        )
        cls.CREATE_POST = reverse('posts:create_post')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Old text',
            author=cls.user,
            group=cls.group_1,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст нового поста',
            'group': self.group_1.id,
            'image': self.uploaded
        }
        response = self.authorized_client.post(self.CREATE_POST,
                                               data=form_data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.latest('id')
        form_to_post = {
            form_data['text']: post.text,
            form_data['group']: post.group.id,
            'posts/small.gif': post.image.name
        }
        for form_value, post_value in form_to_post.items():
            with self.subTest(form_value=form_value):
                self.assertEqual(form_value, post_value)
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый текст старого поста',
            'group': self.group_2.id,

        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)), data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count)
        post = Post.objects.latest('id')
        form_to_post = {
            form_data['text']: post.text,
            form_data['group']: post.group.id
        }
        for form_value, post_value in form_to_post.items():
            with self.subTest(form_value=form_value):
                self.assertEqual(form_value, post_value)

    def test_add_comment(self):
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'New text'
        }
        self.guest_client.post(
            reverse('posts:add_comment', args=(self.post.id,)), data=form_data,
            follow=True)
        self.assertNotEqual(comments_count + 1, Comment.objects.count())
        response_2 = self.authorized_client.post(
            reverse('posts:add_comment', args=(self.post.id,)), data=form_data,
            follow=True)
        comment_latest = Comment.objects.latest('id')
        reverse('login') + '?next=' + reverse('posts:add_comment',
                                              args=(self.post.id,))
        self.assertEqual(form_data['text'], comment_latest.text)
        self.assertRedirects(response_2, reverse('posts:post_detail',
                                                 args=(self.post.id,)))
        self.assertEqual(comment_latest.post.id, self.post.id)
