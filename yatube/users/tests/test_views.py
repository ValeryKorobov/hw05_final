from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='AuthUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def setUp(self) -> None:
        cache.clear()

    def test_pages_users_template(self):
        """
        URL-адреса используют соответствующие шаблоны:
        users/signup.html; users/login.html;
        users/password_change_form.html;
        users/password_reset_form.html;
        users/password_reset_done.html;
        users/password_reset_confirm.html;
        users/password_reset_complete.html;
        users/password_change_done.html;
        users/logged_out.html

        """
        templates_pages_names = {
            reverse('users:signup'):
                'users/signup.html',
            reverse('users:login'):
                'users/login.html',
            reverse('users:password_change_form'):
                'users/password_change_form.html',
            reverse('users:password_reset_form'):
                'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse('users:password_reset_complete'):
                'users/password_reset_complete.html',
            reverse('users:password_change_done'):
                'users/password_change_done.html',
            reverse('users:logout'):
                'users/logged_out.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_form_users_signup(self):
        """
        Проверка передачи формы users:signup для создания
        нового пользователя.

        """
        response = self.guest_client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
            'password1': forms.fields.CharField,
            'password2': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_user_create_signup(self):
        """
        Тест на создание нового пользователя.

        """
        user_content = {
            'username': 'Bobr',
            'password1': 'Bobr13!#',
            'password2': 'Bobr13!#'
        }
        user_before_creation = User.objects.count()
        self.guest_client.post(
            reverse('users:signup'),
            data=user_content,
        )
        user_after_creation = User.objects.count()
        self.assertNotEqual(
            user_before_creation,
            user_after_creation
        )
