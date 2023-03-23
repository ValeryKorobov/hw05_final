import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()
ONE_POST: int = 1
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
SMALL_GIF_EDIT = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
)

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.anonimus_client = Client()
        cls.user = User.objects.create(username='BoBr')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='some-slug',
            description='Тестовое описание',
        )

    def setUp(self) -> None:
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_creating_post_authorized_user(self):
        """
        Создание поста авторизованным юзером.

        """
        post_content = {
            'text': 'Созданный пост',
            'group': self.group.pk
        }
        posts_before_creation = Post.objects.count()
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=post_content,
        )
        posts_after_creation = Post.objects.count()
        post = get_object_or_404(
            Post.objects.select_related('group', 'author')
        )
        forms_data = {
            post.text: post_content['text'],
            post.group.pk: post_content['group'],
            post.author.username: self.user.username,
            posts_after_creation: posts_before_creation + ONE_POST,
        }
        for f_data, data in forms_data.items():
            with self.subTest(data=data):
                self.assertEqual(f_data, data)

    def test_editing_post_authorized_user(self):
        """
        Редактирование поста авторизованным юзером.

        """
        post = Post.objects.create(
            author=self.user,
            group=self.group,
            text='Тестовый пост',
        )
        post_content = {
            'text': 'Пост отредактирован',
            'group': self.group.pk
        }
        self.authorized_client.post(
            reverse('posts:post_edit', args=(post.pk,)),
            data=post_content,
        )
        new_post = get_object_or_404(
            Post.objects.select_related('group', 'author'))
        self.assertNotEqual(post.text, new_post.text)

    def test_editing_and_create_post_anonimus_user(self):
        """
        Редактирование и создание поста анонимными юзерами.

        """
        post = Post.objects.create(
            author=self.user,
            group=self.group,
            text='Тестовый пост',
        )
        post_content_edit = {
            'text': 'Пост отредактирован анонимусом',
            'group': self.group.pk
        }
        self.anonimus_client.post(
            reverse('posts:post_edit', args=(post.pk,)),
            data=post_content_edit,
        )
        edit_post = get_object_or_404(
            Post.objects.select_related('group', 'author'))
        data = {
            edit_post.text: post.text,
        }
        for post_before, post_after in data.items():
            with self.subTest(data=data):
                self.assertEqual(post_after, post_before)

        post_content_create = {
            'text': 'Анонимный пост',
            'group': self.group.pk
        }
        posts_after_creation = Post.objects.count()
        self.anonimus_client.post(
            reverse('posts:post_create'),
            data=post_content_create,
        )
        posts_before_creation = Post.objects.count()
        self.assertEqual(posts_after_creation, posts_before_creation)

    def test_creating_post_picture_authorized_user(self):
        """
        Создание поста с картинкой авторизованным юзером.

        """
        uploaded = SimpleUploadedFile(
            name='small_like_3.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        post_content = {
            'text': 'Созданный пост',
            'group': self.group.pk,
            'image': uploaded,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=post_content,
        )

        self.assertTrue(
            Post.objects.filter(
                text=post_content['text'],
                group=self.group.pk,
                image='posts/small_like_3.gif',
            ).exists()
        )

    def test_editing_picture_post_authorized_user(self):
        """
        Редактирование поста с картинкой авторизованным юзером.

        """
        uploaded = SimpleUploadedFile(
            name='small_like_2.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        uploaded_edit = SimpleUploadedFile(
            name='small_edit.gif',
            content=SMALL_GIF_EDIT,
            content_type='image/gif'
        )
        post = Post.objects.create(
            author=self.user,
            group=self.group,
            text='Тестовый пост с картинкой',
            image=uploaded
        )
        post_content = {
            'text': 'Пост отредактирован',
            'group': self.group.pk,
            'image': uploaded_edit
        }
        self.authorized_client.post(
            reverse('posts:post_edit', args=(post.pk,)),
            data=post_content,
        )

        self.assertTrue(
            Post.objects.filter(
                text=post_content['text'],
                group=self.group.pk,
                image='posts/small_edit.gif',
            ).exists()
        )

    def test_creating_post_picture_anonimus_user(self):
        """
        Создание поста с картинкой анонимным юзером.

        """
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        post_content = {
            'text': 'Созданный пост',
            'group': self.group.pk,
            'image': uploaded,
        }
        self.anonimus_client.post(
            reverse('posts:post_create'),
            data=post_content,
        )

        self.assertFalse(
            Post.objects.filter(
                text=post_content['text'],
                group=self.group.pk,
                image='posts/small.gif',
            ).exists()
        )

    def test_editing_picture_post_anonimus_user(self):
        """
        Редактирование поста с картинкой авторизованным юзером.

        """
        uploaded = SimpleUploadedFile(
            name='small_like.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        post = Post.objects.create(
            author=self.user,
            group=self.group,
            text='Тестовый пост',
            image=uploaded
        )
        uploaded_edit = SimpleUploadedFile(
            name='small_edit.gif',
            content=SMALL_GIF_EDIT,
            content_type='image/gif'
        )
        post_content = {
            'text': 'Пост отредактирован',
            'group': self.group.pk,
            'image': uploaded_edit
        }
        self.anonimus_client.post(
            reverse('posts:post_edit', args=(post.pk,)),
            data=post_content,
        )
        self.assertTrue(
            Post.objects.filter(
                text=post.text,
                group=self.group.pk,
                image='posts/small_like.gif',
            ).exists()
        )

    def test_creating_comment_authorized_user(self):
        """
        Создание комментария только авторизованным пользователем.

        """
        post = Post.objects.create(
            author=self.user,
            group=self.group,
            text='Тестовый пост с комментарием',
        )
        comment_content = {
            'text': 'Новый комментарий',
        }
        comment_content_anon = {
            'text': 'Новый комментарий от анонима',
        }
        comments_before_creation_anon = Comment.objects.count()
        self.authorized_client.post(
            reverse('posts:add_comment', args=(post.pk,)),
            data=comment_content,
        )
        comments_after_creation = Comment.objects.count()

        forms_data = {
            comments_before_creation_anon: comments_after_creation,
        }
        for f_data, data in forms_data.items():
            with self.subTest(data=data):
                self.assertNotEqual(f_data, data)
        try:
            self.anonimus_client.post(
                reverse('posts:add_comment', args=(post.pk,)),
                data=comment_content_anon,
            )
        except ValueError:
            pass
        comments_after_creation_anon = Comment.objects.count()
        self.assertEqual(comments_after_creation, comments_after_creation_anon)
