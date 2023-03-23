from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='AuthUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )
        cache.clear()

    def tests_all_page(self):
        """
        Проверка всех страниц для неавторизованных юзеров.

        """
        url_adress = {
            '/': HTTPStatus.OK.value,
            '/group/test-slug/': HTTPStatus.OK.value,
            '/profile/AuthUser/': HTTPStatus.OK.value,
            f'/posts/{self.post.pk}/': HTTPStatus.OK.value,
            '/unexisting_page/': HTTPStatus.NOT_FOUND.value,
        }
        for address, url_status in url_adress.items():
            with self.subTest(url_status=url_status):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, url_status)

    def test_post_id_edit(self):
        """
        Страница /posts/<post_id>/edit/ доступ автору поста.

        """
        response = self.authorized_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_create_page(self):
        """
        Страница /create/ доступ авторизованному юзеру.

        """
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_urls_uses_correct_template_auth_user(self):
        """
        URL-адрес использует соответствующий шаблон авторизованным юзером.

        """
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/AuthUser/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_anon_user(self):
        """
        URL-адрес использует соответствующий шаблон анонимным юзером.

        """
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/AuthUser/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
        templates_url_not_used = {
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address_second, template_second in templates_url_not_used.items():
            with self.subTest(template_second=template_second):
                response = self.guest_client.get(address_second)
                self.assertTemplateNotUsed(response, template_second)
