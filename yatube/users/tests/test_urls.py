from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='AuthUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def setUp(self) -> None:
        cache.clear()

    def tests_all_page_unauthorized_user(self):
        """
        Проверка страниц для неавторизованного юзера.
        Адреса: /auth/signup/; /auth/login/; /auth/password_reset/;
                /auth/password_reset/done/; /auth/reset/done/; /auth/logout/;
                /auth/reset/MTE/set-password/;
                /auth/reset/MTE/_password_reset_token/.

        """
        url_adress = {
            '/auth/signup/': HTTPStatus.OK.value,
            '/auth/login/': HTTPStatus.OK.value,
            '/auth/password_reset/': HTTPStatus.OK.value,
            '/auth/password_reset/done/': HTTPStatus.OK.value,
            '/auth/reset/done/': HTTPStatus.OK.value,
            '/auth/logout/': HTTPStatus.OK.value,
            '/auth/reset/MTE/set-password/': HTTPStatus.OK.value,
            '/auth/reset/MTE/_password_reset_token/': HTTPStatus.OK.value
        }
        for address, url_status in url_adress.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, url_status)

    def test_password_change_url_redirect_anonymous_on_login(self):
        """
        Страница перенаправит анонимного пользователя на страницу логина.
        Адреса: /auth/password_change/; /auth/password_change/done/.

        """
        url_adress = {
            '/auth/password_change/': '/auth/login/?next=',
            '/auth/password_change/done/': '/auth/login/?next=',

        }
        for address, url_status in url_adress.items():
            with self.subTest(address=address):
                response = self.guest_client.get(
                    address,
                    follow=True
                )
                self.assertRedirects(
                    response, url_status + address
                )
