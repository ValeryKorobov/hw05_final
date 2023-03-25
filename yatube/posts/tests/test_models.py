from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Comment, Follow, Group, Post

User = get_user_model()
TEXT_LIMIT: int = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый топовый пост',
        )

    def test_str_post(self):
        """
        Проверяем что у модели Post корректно работает __str__.

        """
        self.assertEqual(self.post.text[:TEXT_LIMIT], self.post.__str__())

    def test_post_verbose_name(self):
        """
        Проверяем verbose_name в модели Post.

        """
        field_verboses_post = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Картинка',
        }
        for field, expected_value in field_verboses_post.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_post_help_text(self):
        """
        help_text поля title совпадает с ожидаемым.

        """
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)


class GroupodelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_str_group(self):
        """
        Проверяем, что у модели Group корректно работает __str__.

        """
        self.assertEqual(self.group.title, self.group.__str__())

    def test_group_verbose_name(self):
        """
        Проверяем verbose_name в модели Group.

        """
        field_verboses_group = {
            'title': 'Название',
            'slug': 'Тег',
            'description': 'Описание',
        }
        for field, expected_value in field_verboses_group.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field).verbose_name,
                    expected_value
                )


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост с комментарием',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий.'
        )

    def test_comment_verbose_name(self):
        """
        Проверяем verbose_name в модели Comment.

        """
        field_verboses_names = {
            'post': 'Комментарий',
            'author': 'Автор',
            'text': 'Текст',
            'created': 'Дата создания'
        }
        for field, expected_value in field_verboses_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.comment._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_comment_help_text(self):
        """
        help_text поля text совпадает с ожидаемым.

        """
        val = 'Текст нового комментария'
        self.assertEqual(self.comment._meta.get_field('text').help_text, val)


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_follower = User.objects.create_user(username='followerUser')
        cls.user_author = User.objects.create_user(username='AuthorUser')
        cls.subscription = Follow.objects.create(
            user=cls.user_follower,
            author=cls.user_author,
        )

    def test_follow_str(self):
        """
        Проверяем что у модели Follow корректно работает __str__.

        """
        string = (
            self.user_follower.username
            + ' -> ' + self.user_author.username
        )
        self.assertEqual(string, self.subscription.__str__())

    def test_follow_verbose_name(self):
        """
        Проверяем verbose_name в модели Post.

        """
        field_verboses_names = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        for field, expected_value in field_verboses_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.subscription._meta.get_field(field).verbose_name,
                    expected_value
                )
