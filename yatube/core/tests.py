from http import HTTPStatus

from django.test import TestCase


class ViewTestClass(TestCase):

    def test_error_page(self):
        """Тест шаблона и статуса несуществующей страницы."""
        content_data = {
            '/nonexist-page/': 'core/404.html',
        }
        for adress, template in content_data.items():
            with self.subTest(template=template):
                response = self.client.get(adress)
                self.assertTemplateUsed(response, template)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
