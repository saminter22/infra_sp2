# reviews/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator

from .validators import validate_username, validate_year
from .utils import PubDateIdOrder
from api_yamdb.settings import (DEFAULT_CHAR_FIELD_LENGTH,
                                DEFAULT_EMAIL_FIELD_LENGTH,
                                MAX_CHAR_FIELD_LENGTH, MAX_SLUG_FIELD_LENGTH)


class User(AbstractUser):
    """Доработанная модель пользователя"""
    ROLE_NAME_USER = 'user'

    ROLE_NAME_MODERATOR = 'moderator'

    ROLE_NAME_ADMIN = 'admin'

    ROLES = [
        (ROLE_NAME_USER, 'Аутентифицированный пользователь'),
        (ROLE_NAME_MODERATOR, 'Модератор'),
        (ROLE_NAME_ADMIN, 'Администратор'),
    ]

    username = models.CharField(verbose_name='Имя пользователя',
                                max_length=DEFAULT_CHAR_FIELD_LENGTH,
                                unique=True,
                                blank=False,
                                null=False,
                                validators=(validate_username, ))
    password = models.CharField(
        verbose_name='Пароль',
        max_length=DEFAULT_CHAR_FIELD_LENGTH,
        blank=False,
        null=False,
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=DEFAULT_EMAIL_FIELD_LENGTH,
        unique=True,
        blank=False,
        null=False,
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=max(len(role_name) for role_name, role_desc in ROLES),
        choices=ROLES,
        default='user')
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=DEFAULT_CHAR_FIELD_LENGTH,
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=DEFAULT_CHAR_FIELD_LENGTH,
        blank=True,
        null=True,
    )
    bio = models.TextField(
        verbose_name='Биография',
        blank=True,
        null=True,
    )
    confirmation_code = models.CharField(verbose_name='Код подтверждения',
                                         max_length=DEFAULT_CHAR_FIELD_LENGTH,
                                         blank=True,
                                         null=True)

    class Meta:
        ordering = ('username', )

    def __str__(self):
        return self.username

    @property
    def is_administrator(self):
        return (self.role == self.ROLE_NAME_ADMIN or self.is_staff
                or self.is_superuser)

    @property
    def is_moderator(self):
        return (self.role == self.ROLE_NAME_MODERATOR or self.is_superuser)


class Genre(models.Model):
    name = models.CharField(max_length=MAX_CHAR_FIELD_LENGTH,
                            verbose_name='Название категории')
    slug = models.SlugField(max_length=MAX_SLUG_FIELD_LENGTH, unique=True)

    class Meta(PubDateIdOrder.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=MAX_CHAR_FIELD_LENGTH,
                            verbose_name='Название жанра')
    slug = models.SlugField(max_length=MAX_SLUG_FIELD_LENGTH, unique=True)

    class Meta(PubDateIdOrder.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=DEFAULT_CHAR_FIELD_LENGTH,
                            verbose_name='Название произведения')
    year = models.IntegerField(verbose_name='Год выпуска',
                               validators=(validate_year, ))
    description = models.TextField(verbose_name='Описание произведения')
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        related_name='genre',
        verbose_name='Жанр',
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.DO_NOTHING,
        related_name='title',
        verbose_name='Категория',
        blank=True,
        null=True,
    )

    class Meta():
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genre} {self.title}'


class Review(PubDateIdOrder):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
        related_name='reviews',
    )
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='reviews',
                               verbose_name='Автор')
    score = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        default=1,
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10),
        ),
        verbose_name='Оценка',
    )

    class Meta(PubDateIdOrder.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.CheckConstraint(check=models.Q(score__range=(0, 10)),
                                   name='valid_score'),
            models.UniqueConstraint(fields=['author', 'title'],
                                    name='rating_once'),
        ]

    def __str__(self):
        return self.text[:30]


class Comment(PubDateIdOrder):
    review = models.ForeignKey(Review,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Отзыв')
    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор')

    class Meta(PubDateIdOrder.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:30]
