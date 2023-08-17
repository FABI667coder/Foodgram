from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import RegexValidator


class User(AbstractUser):
    username = models.CharField(
        'Имя пользователя',
        max_length=settings.MAX_VAL150,
        unique=True,
        blank=False,
        null=False,
        validators=[
            RegexValidator(
                regex=r"^[\w.@+-]+$",
                message="Допустимые символы: буквы, цифры и @/./+/-/_",
            )
        ],
    )
    email = models.EmailField(
        'Эл.Почта',
        max_length=settings.MAX_VAL200,
        null=False,
        blank=False,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=settings.MAX_VAL150,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.MAX_VAL150,
        blank=False,
        null=False,
    )
    password = models.CharField(
        'Пароль',
        max_length=settings.MAX_VAL150,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователь'


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='user',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='author',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписка'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscribe',
            ),
        ]
