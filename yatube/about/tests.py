from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_urls_about_page(self):
        """
        Страницы приложения about.
        Адреса: /about/author/ и /about/tech/.

        """
        url_adress = {
            '/about/author/': HTTPStatus.OK.value,
            '/about/tech/': HTTPStatus.OK.value,
        }
        for address, url_status in url_adress.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, url_status)


class StaticViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='BoBr')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_views_about_page(self):
        """
        URL - адреса используют соответствующие шаблоны
        about:author и about:tech.

        """
        templates_pages_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
