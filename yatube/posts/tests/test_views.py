import shutil
import tempfile
from typing import List

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Follow, Group, Post

User = get_user_model()
COUNT_POSTS_ON_FIRST_PAGE: int = 10
COUNT_POSTS_ON_SECOND_PAGE: int = 3
NUMBER_OF_POSTS: int = 13
ONE_FOLLOWER: int = 1
FIRST_OBJECT_PAGE: int = 0
SECOND_OBJECT_PAGE: int = 1
ZERO_COUNT_OBJECTS: int = 0
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.anonimus_client = Client()
        cls.user = User.objects.create_user(username='Bascow')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.user_not_author = User.objects.create(username='NotAuthor')
        cls.authorized_client_not_author = Client()
        cls.authorized_client_not_author.force_login(cls.user_not_author)

        cls.user_author = User.objects.create(username='Author')
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(cls.user_author)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
        )
        cls.group_second = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug_2',
            description='Тестовое описание 2',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий',
        )
        cls.comment_author = Comment.objects.create(
            post=cls.post,
            author=cls.user_author,
            text='Тестовый комментарий автору другим пользователем',
        )

    def setUp(self) -> None:
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template_auth_user(self):
        """
        URL-адреса используют шаблоны авторизованным юзером:
        posts/index.html,posts/group_list.html,
        posts/profile.html, posts/post_detail.html,
        posts/create_post.html.

        """
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.pk}
            ): 'posts/post_detail.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
        templates_pages_names_not_used = {
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_author}
            ): 'posts/profile.html',
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user_author}
            ): 'posts/profile.html',
        }
        for name, template_name in templates_pages_names_not_used.items():
            with self.subTest(template_name=template_name):
                response = self.authorized_client.get(name)
                self.assertTemplateNotUsed(response, template_name)

    def test_pages_uses_correct_template_anon_user(self):
        """
        URL-адреса используют шаблоны анонимным юзером:
        posts/index.html,posts/group_list.html,
        posts/profile.html, posts/post_detail.html,
        posts/create_post.html.

        """
        templates_pages_used_anon = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            ): 'posts/post_detail.html',
        }
        for reverse_used, template_used in templates_pages_used_anon.items():
            with self.subTest(template_used=template_used):
                response_anon = self.anonimus_client.get(reverse_used)
                self.assertTemplateUsed(response_anon, template_used)
        templates_name_not_used_anon = {
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.pk}
            ): 'posts/post_detail.html',
            reverse('posts:follow_index'): 'posts/follow.html',
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_author}
            ): 'posts/profile.html',
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user_author}
            ): 'posts/profile.html',
        }
        for reverse_name, template in templates_name_not_used_anon.items():
            with self.subTest(template=template):
                response = self.anonimus_client.get(reverse_name)
                self.assertTemplateNotUsed(response, template)

    def test_group_list_show_correct_context(self):
        """
        Шаблон group_list сформирован с правильным контекстом

        """
        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                        kwargs={'slug': self.group.slug})))
        context_data = {
            response.context.get('group').title: self.group.title,
            response.context.get('group').description:
                self.group.description,
            response.context.get('group').slug: self.group.slug,
        }
        for context, data in context_data.items():
            with self.subTest(data=data):
                self.assertEqual(context, data)

    def test_post_detail(self):
        """
        Один пост отфильтрованный по id.

        """
        response = (self.authorized_client.get(reverse(
                    'posts:post_detail',
                    kwargs={'post_id': self.post.pk}
                    )))
        post = response.context['post']
        context_data = {
            post.pub_date: self.post.pub_date,
            post.group.title: self.group.title,
            post.author: self.user,
            post.text: self.post.text,
        }
        for context, data in context_data.items():
            with self.subTest(data=data):
                self.assertEqual(context, data)

    def test_form_post_edit(self):
        """
        Форма редактирования поста, отфильтрованного по id.

        """
        response = (self.authorized_client.get(reverse(
                    'posts:post_edit',
                    kwargs={'post_id': self.post.pk}
                    )))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for field, expected in form_fields.items():
            with self.subTest(expected=expected):
                form_field = response.context.get('form').fields.get(field)
                self.assertIsInstance(
                    form_field,
                    expected
                )
        form_data = {
            response.context.get('form')['text'].value(): self.post.text,
            response.context.get('form')['group'].value(): self.post.group.pk
        }
        for data_form, data in form_data.items():
            with self.subTest(data=data):
                self.assertEqual(
                    data_form, data
                )
        edit_bool = response.context['is_edit']
        self.assertTrue(edit_bool)

    def test_post_create(self):
        """
        Форма создания поста.

        """
        response = (self.authorized_client.get(reverse('posts:post_create')))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(expected=expected):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_additional_check_when_creating_post(self):
        """
        Дополнительная проверка при создании поста
        Отображение поста на страницах если есть группа:
        posts:index, posts:profile и posts:group_list
        Проверка не попал ли пост в другую группу.

        """
        response_group_list = (
            self.authorized_client.
            get(reverse('posts:group_list', kwargs={'slug': self.group.slug}
                        )))
        response_index = (self.authorized_client.get(reverse('posts:index')))
        response_profile = (
            self.authorized_client.get(
                reverse('posts:profile', kwargs={'username': self.user})))
        post_list_self_post = {
            response_index.context['page_obj'][FIRST_OBJECT_PAGE].text:
            self.post.text,
            response_group_list.context['page_obj'][FIRST_OBJECT_PAGE].text:
            self.post.text,
            response_profile.context['page_obj'][FIRST_OBJECT_PAGE].text:
            self.post.text,
        }
        for post_list, self_post in post_list_self_post.items():
            with self.subTest(self_post=self_post):
                self.assertEqual(
                    post_list,
                    self_post,
                    'Нет поста на данной странице'
                )
        self.assertNotEqual(self.post.group.slug, self.group_second.slug)

    def test_post_picture(self):
        """
        Отображение картинки на страницах posts:index, posts:group_list
        posts:profile и posts:post_detail.

        """
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        post = Post.objects.create(
            author=self.user,
            group=self.group,
            text='Тестовый пост c картинкой',
            image=uploaded
        )
        context_data = {
            reverse('posts:index'): post.image,
            reverse(
                'posts:group_list',
                kwargs={'slug': post.group.slug}
            ): post.image,
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            ): post.image,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': post.pk}
            ): post.image,
        }
        for context, data in context_data.items():
            with self.subTest(data=data):
                response = self.authorized_client.get(context)
                try:
                    self.assertEqual(
                        response.context['page_obj']
                        [FIRST_OBJECT_PAGE].image, data
                    )
                except KeyError:
                    self.assertEqual(response.context['post'].image, data)

    def test_post_comment_author_anon_user(self):
        """
        Комментарий анонимным юзером не создается.

        """
        comments_number_before = Comment.objects.count()
        try:
            Comment.objects.create(
                post=self.post,
                author=self.anonimus_client,
                text='Тестовый комментарий автору анонимным юзером',
            )
        except ValueError:
            pass
        comments_number_after = Comment.objects.count()
        self.assertEqual(comments_number_before, comments_number_after)

    def test_cache_on_index_page(self):
        """
        Тестирование работы кэша на главной странице.

        """
        content_cache = self.anonimus_client.get(
            reverse("posts:index")).content
        Post.objects.all().delete()
        content_before = self.anonimus_client.get(
            reverse("posts:index")).content

        self.assertEqual(content_cache, content_before)

        content_data = {
            content_cache: content_before,
        }
        for content, data in content_data.items():
            with self.subTest(data=data):
                self.assertEqual(content, data)

        cache.clear()
        content_after = self.anonimus_client.get(
            reverse("posts:index")).content

        self.assertNotEqual(content_cache, content_after)

    def test_profile_follow_authorized(self):
        """
        Авторизованный пользователь может подписываться на других
        пользователей.

        """
        followers_number_before = Follow.objects.count()
        self.authorized_client.get(
            reverse(
                "posts:profile_follow", args=[self.user_not_author.username]
            )
        )
        followers_number_after = Follow.objects.count()

        count_users = {
            followers_number_after: followers_number_before
        }
        for count_after, count_before in count_users.items():
            with self.subTest(count_before=count_before):
                self.assertEqual(count_after, count_before + ONE_FOLLOWER)
        self.assertTrue(
            Follow.objects.filter(
                author=self.user_not_author,
                user=self.user
            ).exists())

        self.authorized_client.get(
            reverse(
                "posts:profile_unfollow", args=[self.user_not_author.username]
            )
        )

    def test_profile_not_follow_author_self(self):
        """
        Автор не может подписываться на самого себя.

        """
        followers_number_before = Follow.objects.count()
        self.authorized_client.get(
            reverse(
                "posts:profile_follow", args=[self.user.username]
            )
        )
        followers_number_after = Follow.objects.count()
        count_users = {
            followers_number_after: followers_number_before
        }
        for count_after, count_before in count_users.items():
            with self.subTest(count_before=count_before):
                self.assertEqual(count_after, count_before)
        self.assertFalse(
            Follow.objects.filter(
                author=self.user,
                user=self.user
            ).exists())

    def test_profile_not_follow_anon_user(self):
        """
        Гость не может подписываться на авторов.

        """
        followers_number_before = Follow.objects.count()
        self.anonimus_client.get(
            reverse(
                "posts:profile_follow", args=[self.user_author.username]
            )
        )
        followers_number_after = Follow.objects.count()
        self.assertEqual(followers_number_after, followers_number_before)

    def test_profile_unfollow_authorized(self):
        """Авторизованный пользователь может отписываться от других
        пользователей."""
        Follow.objects.create(author=self.user_not_author, user=self.user)
        followers_number_before = Follow.objects.count()
        self.authorized_client.get(
            reverse(
                "posts:profile_unfollow", args=[self.user_not_author.username]
            )
        )
        followers_number_after = Follow.objects.count()

        count_users = {
            followers_number_after: followers_number_before
        }
        for count_after, count_before in count_users.items():
            with self.subTest(count_before=count_before):
                self.assertEqual(count_after, count_before - ONE_FOLLOWER)

        self.assertFalse(
            Follow.objects.filter(
                author=self.user_not_author,
                user=self.user
            ).exists())

    def test_new_post_for_subscribers(self):
        """
        Новая запись юзера появляется в ленте тех, кто на него подписан.

        """
        Follow.objects.create(author=self.user_not_author, user=self.user)
        created_post = Post.objects.create(
            text='Пост для тестирования подписки.',
            author=self.user_not_author,
            group=self.group
        )
        response = self.authorized_client.get(reverse("posts:follow_index"))

        self.assertEqual(
            created_post,
            response.context['page_obj'][FIRST_OBJECT_PAGE]
        )

    def test_new_post_for_non_subscribers(self):
        """
        Новая запись юзера не появляется в ленте тех, кто на него не подписан.

        """
        Post.objects.create(
            text='Специальный пост для тестирования подписки.',
            author=self.user_not_author,
            group=self.group
        )
        response = self.authorized_client.get(
            reverse("posts:follow_index")
        )

        self.assertFalse(
            len(response.context['page_obj']), ZERO_COUNT_OBJECTS
        )

    def test_post_comment_self_add(self):
        """
        После успешной отправки комментарий появляется
        на странице своего же поста.

        """
        response = (self.authorized_client.get(reverse(
                    'posts:post_detail',
                    kwargs={'post_id': self.post.pk}
                    )))
        comment = response.context['comments'][FIRST_OBJECT_PAGE]
        context_data = {
            comment.created: self.comment.created,
            comment.author: self.user,
            comment.text: self.comment.text,
        }
        for context, data in context_data.items():
            with self.subTest(data=data):
                self.assertEqual(context, data)

    def test_post_comment_author_add(self):
        """
        После успешной отправки комментарий появляется
        на странице поста другого автора.

        """
        response = (self.authorized_client_author.get(reverse(
                    'posts:post_detail',
                    kwargs={'post_id': self.post.pk}
                    )))
        comment_auth = response.context['comments'][SECOND_OBJECT_PAGE]
        context_data = {
            comment_auth.created: self.comment_author.created,
            comment_auth.author: self.user_author,
            comment_auth.text: self.comment_author.text,
        }
        for context, data in context_data.items():
            with self.subTest(data=data):
                self.assertEqual(context, data)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Bascow')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        list_of_posts: List[Post] = []
        for _ in range(NUMBER_OF_POSTS):
            list_of_posts.append(
                Post(
                    author=cls.user,
                    group=cls.group,
                    text='Тестовый пост'
                )
            )
        Post.objects.bulk_create(list_of_posts)

    def setUp(self) -> None:
        cache.clear()

    def test_home_page_contains_ten_records(self):
        """
        Список постов на главной странице.

        """
        pages_counts = {
            self.authorized_client.get(
                reverse('posts:index')): COUNT_POSTS_ON_FIRST_PAGE,
            self.authorized_client.get(
                reverse('posts:index')
                + '?page=2'): COUNT_POSTS_ON_SECOND_PAGE,
        }
        for pages, counts in pages_counts.items():
            with self.subTest(counts=counts):
                self.assertEqual(
                    len(pages.context.get('page_obj')), counts
                )

    def test_profile_contains_ten_records(self):
        """
        Список постов отфильтрованных по пользователю
        Контекст страницы posts:profile.

        """
        pages_counts = {
            self.authorized_client.get(
                reverse('posts:profile', kwargs={'username': self.user})):
                    COUNT_POSTS_ON_FIRST_PAGE,
            self.authorized_client.get(
                reverse('posts:profile', kwargs={'username': self.user})
                + '?page=2'): COUNT_POSTS_ON_SECOND_PAGE,
        }
        for pages, counts in pages_counts.items():
            with self.subTest(counts=counts):
                self.assertEqual(
                    len(pages.context.get('page_obj')), counts
                )
        response = (self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user})))
        self.assertEqual(response.context['username'], self.user)

    def test_group_list_show_correct(self):
        """
        Список постов отфильтрованных по группе.
        Контекст страницы posts:group_list.

        """
        pages_counts = {
            self.authorized_client.get(
                reverse('posts:group_list',
                        kwargs={'slug': self.group.slug})):
                            COUNT_POSTS_ON_FIRST_PAGE,
            self.authorized_client.get(
                reverse('posts:group_list',
                        kwargs={'slug': self.group.slug}) + '?page=2'):
                            COUNT_POSTS_ON_SECOND_PAGE,
        }
        for pages, counts in pages_counts.items():
            with self.subTest(counts=counts):
                self.assertEqual(
                    len(pages.context.get('page_obj')), counts
                )
        response = (self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}
                    )))
        self.assertEqual(response.context['group'], self.group)
