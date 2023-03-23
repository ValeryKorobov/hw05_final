from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

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
        Проверяем verbose_name в моделях.

        """
        field_verboses_post = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
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
        Проверяем verbose_name в моделях.

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
