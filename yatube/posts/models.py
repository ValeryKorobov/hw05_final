from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel, PubDateModel

User = get_user_model()
TEXT_LIMIT: int = 15


class Post(PubDateModel):
    """Модель для постов автора."""
    text = models.TextField(
        'Текст',
        help_text='Введите текст поста'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        'Group',
        models.SET_NULL,
        blank=True, null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )

    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Публикацию'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.text[:TEXT_LIMIT]


class Group(models.Model):
    """Модель груп к которым относятся посты."""
    title = models.CharField(
        'Название',
        max_length=200
    )
    slug = models.SlugField(
        'Тег',
        max_length=100,
        unique=True
    )
    description = models.TextField(
        'Описание'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Группу'
        verbose_name_plural = 'Группы'


class Comment(CreatedModel):
    """Модель для комментариев пользователей."""
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField('Текст', help_text='Текст нового комментария')

    class Meta:
        ordering = ['-created']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    """Модель для подписок пользователей."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписчиков'
        verbose_name_plural = 'Подписчики'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique appversion')
        ]

    def __str__(self):
        return f'{self.user.username} -> {self.author.username}'
