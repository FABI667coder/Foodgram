from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=settings.MAX_VAL150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[\w.@+-]+$",
                message="Letters, numbers or @/./+/-/_ allowed only.",
            )
        ],
    )
    email = models.EmailField(
        'Эл.Почта',
        max_length=settings.MAX_VAL200,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=settings.MAX_VAL150,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.MAX_VAL150,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователь'


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='subscriber',
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
                fields=('user', 'author'), name='unique_follow'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')), name='no_self_follow'
            )
        ]
